from typing import Dict, Any
import yaml
import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openapi_agent
from langchain_community.agent_toolkits import OpenAPIToolkit
from langchain_community.utilities import RequestsWrapper
from langchain.tools import APIOperation
from langchain_community.tools.json.tool import JsonSpec
from app.utils.logger import logger
from app.models.conversation import ConversationState, ClaimDetails

class APIAgent:
    def __init__(self, openai_api_key: str, api_spec_path: str, base_url: str):
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key,
            request_timeout=30,
            max_retries=3
        )
        
        # Load and parse YAML spec
        with open(api_spec_path) as f:
            raw_api_spec = yaml.safe_load(f)
        
        # Create JsonSpec from raw spec
        json_spec = JsonSpec(dict_=raw_api_spec, max_value_length=4000)
            
        # Configure RequestsWrapper
        requests_wrapper = RequestsWrapper(
            headers={}
        )

        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                toolkit = OpenAPIToolkit.from_llm(
                    llm=self.llm,
                    json_spec=json_spec,
                    requests_wrapper=requests_wrapper,
                    base_url=base_url,
                    allow_dangerous_requests=True,
                    verbose=True
                )
                
                self.agent_executor = create_openapi_agent(
                    llm=self.llm,
                    toolkit=toolkit,
                    verbose=True
                )
                break
            except Exception as e:
                if "rate limit exceeded" in str(e).lower() and attempt < max_retries - 1:
                    logger.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                    asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Error creating API agent: {str(e)}", exc_info=True)
                    raise e

    def _handle_claim_submission(self, state: ConversationState) -> ConversationState:
        """Handle the claim submission workflow"""
        if state.current_step == "initial":
            # Start gathering claim details
            state.current_step = "gathering_details"
            state.claim_details = ClaimDetails()
            state.api_response = (
                "I'll help you submit a new claim. Please provide the following details:\n"
                "1. Vehicle information (make, model, year)\n"
                "2. Description of the damage\n"
                "3. Any photos of the damage\n\n"
                "Let's start with your vehicle information. What is the make, model, and year of your vehicle?"
            )
            return state

        elif state.current_step == "gathering_details":
            if not state.claim_details.vehicle:
                # Process vehicle information
                state.claim_details.vehicle = state.query
                state.api_response = "Thank you. Now, please describe the damage to your vehicle."
                return state
            
            elif not state.claim_details.damage_description:
                # Process damage description
                state.claim_details.damage_description = state.query
                state.api_response = "Got it. Please upload any photos of the damage."
                return state
            
            elif len(state.claim_details.photos) == 0:
                # Process photo upload
                # Note: In a real implementation, you'd handle file uploads here
                state.claim_details.photos.append("damage.jpg")
                state.current_step = "confirmation"
                state.requires_user_confirmation = True
                state.confirmation_message = (
                    f"I have the following details:\n"
                    f"Vehicle: {state.claim_details.vehicle}\n"
                    f"Damage Description: {state.claim_details.damage_description}\n"
                    f"Uploaded Photos: {', '.join(state.claim_details.photos)}\n\n"
                    f"Shall I proceed to submit this claim?"
                )
                state.api_response = state.confirmation_message
                return state

        elif state.current_step == "confirmation":
            if "yes" in state.query.lower():
                # Submit the claim
                try:
                    # Here you would make the actual API call to submit the claim
                    # For now, we'll simulate a successful submission
                    claim_id = "CLM123456"
                    state.current_step = "complete"
                    state.api_success = True
                    state.api_response = f"Your claim has been successfully submitted. Your claim ID is: {claim_id}"
                except Exception as e:
                    logger.error(f"Error submitting claim: {str(e)}", exc_info=True)
                    state.api_success = False
                    state.api_response = "I apologize, but there was an error submitting your claim. Please try again later."
            else:
                state.current_step = "initial"
                state.api_response = "Claim submission cancelled. Let me know if you'd like to start over."
            
            return state

        return state

    def run(self, state: ConversationState) -> ConversationState:
        """Run the API agent and determine next steps"""
        logger.debug(f"APIAgent processing query: {state.query}")
        
        # Skip if knowledge was found
        if state.knowledge_found:
            logger.debug("Knowledge was found, skipping API agent")
            return state

        try:
            # Check if this is a claim submission request
            if "submit" in state.query.lower() and "claim" in state.query.lower():
                logger.debug("Handling claim submission workflow")
                return self._handle_claim_submission(state)

            # For other API requests
            logger.debug("Running API agent executor")
            result = self.agent_executor.run(state.query)
            state.api_response = result
            state.api_success = True
            logger.debug(f"API call successful: {result}")
        except Exception as e:
            logger.error(f"API call failed: {str(e)}", exc_info=True)
            state.api_success = False
            state.api_error = str(e)
            state.api_response = "I apologize, but I encountered an error while trying to process your request."
        
        return state
