from typing import Dict, Any, Annotated, Sequence, TypeVar, Union
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.api_agent import APIAgent
from app.agents.fallback_agent import FallbackAgent
from app.utils.logger import logger
from app.models.conversation import ConversationState, ClaimDetails

StateType = TypeVar("StateType", bound=ConversationState)

class AgentOrchestrator:
    def __init__(
        self,
        openai_api_key: str,
        db_connection_string: str,
        api_spec_path: str,
        api_base_url: str
    ):
        # Initialize agents
        self.knowledge_agent = KnowledgeAgent(db_connection_string, openai_api_key)
        self.api_agent = APIAgent(openai_api_key, api_spec_path, api_base_url)
        self.fallback_agent = FallbackAgent(openai_api_key)
        
        # Create the state graph
        self.workflow = self._create_workflow()

    def _should_use_api(self, state: ConversationState) -> bool:
        """Check if the query likely needs API interaction"""
        keywords = ["status", "update", "submit", "claim", "policy", "account"]
        return (
            any(keyword in state.query.lower() for keyword in keywords) or
            state.current_step != "initial"
        )

    def _should_continue(self, state: ConversationState) -> bool:
        """Determine if we need to continue to fallback"""
        return (
            not state.knowledge_found and 
            not state.api_success and 
            state.current_step == "initial"
        )

    def _create_workflow(self) -> StateGraph:
        # Create workflow graph
        workflow = StateGraph(StateType)

        # Add nodes for each agent
        workflow.add_node("knowledge", self.knowledge_agent.run)
        workflow.add_node("api", self.api_agent.run)
        workflow.add_node("fallback", self.fallback_agent.run)

        # Define conditional edges
        workflow.add_conditional_edges(
            "knowledge",
            self._should_use_api,
            {
                True: "api",
                False: END
            }
        )
        
        workflow.add_conditional_edges(
            "api",
            self._should_continue,
            {
                True: "fallback",
                False: END
            }
        )

        workflow.add_edge("fallback", END)

        # Set entry point
        workflow.set_entry_point("knowledge")

        return workflow.compile()

    def process_query(self, query: str, conversation_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query through the agent workflow"""
        try:
            # Initialize or update conversation state
            if conversation_state is None:
                state = ConversationState(query=query)
            else:
                state = ConversationState(**conversation_state)
                state.query = query

            logger.debug(f"Starting query processing: {query}")
            logger.debug(f"Current conversation state: {state.dict()}")
            
            # Run the workflow
            result = self.workflow.invoke(state)
            
            logger.debug(f"Query processing result: {result.dict()}")
            
            # Compile final response
            if result.knowledge_found:
                final_response = result.knowledge_response
                source = "knowledge"
            elif result.api_response:
                final_response = result.api_response
                source = "api"
            elif result.fallback_response:
                final_response = result.fallback_response
                source = "fallback"
            else:
                final_response = "I apologize, but I couldn't process your request at this time."
                source = "system"
                
            return {
                "response": final_response,
                "source": source,
                "full_state": result.dict(),
                "requires_confirmation": result.requires_user_confirmation,
                "confirmation_message": result.confirmation_message
            }
        except Exception as e:
            logger.error(f"Error in process_query: {str(e)}", exc_info=True)
            raise
