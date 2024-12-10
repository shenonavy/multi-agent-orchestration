from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from app.utils.logger import logger

class FallbackAgent:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key
        )
        
        template = """You are a helpful insurance customer service AI assistant. 
        The user's query could not be answered using our knowledge base or API. 
        Please provide a helpful response that:
        1. Acknowledges that we may not have the specific information
        2. Provides general guidance if possible
        3. Suggests alternative ways to get the information they need
        
        Previous attempt results:
        Knowledge Base Response: {knowledge_response}
        API Response: {api_response}
        
        User Query: {query}
        
        Response:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["knowledge_response", "api_response", "query"]
        )
        
        # Create a RunnableSequence instead of LLMChain
        self.chain = prompt | self.llm

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the fallback agent when other methods fail"""
        logger.debug(f"FallbackAgent processing query: {state['query']}")
        
        try:
            # Get responses from previous attempts
            knowledge_response = state.get("knowledge_response", "No response from knowledge base")
            api_response = state.get("api_response", "No response from API")
            
            # Run the fallback chain
            logger.debug("Running fallback chain")
            response = await self.chain.ainvoke({
                "knowledge_response": knowledge_response,
                "api_response": api_response,
                "query": state["query"]
            })
            
            # Extract content from the response
            if hasattr(response, 'content'):
                fallback_response = response.content
            else:
                fallback_response = str(response)
            
            state["fallback_response"] = fallback_response
            logger.debug(f"Fallback response generated: {fallback_response}")
            
        except Exception as e:
            logger.error(f"Error in fallback agent: {str(e)}", exc_info=True)
            state["fallback_response"] = "I apologize, but I'm having trouble processing your request at the moment. Please try again later or contact our support team for assistance."
        
        return state
