from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from typing import Dict, Any, Optional
from app.utils.auth import get_current_user
from app.models.user import User
from app.utils.logger import logger
from app.orchestrator.state_machine import AgentOrchestrator
from app.models.conversation import ConversationState
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

router = APIRouter()

# Initialize the orchestrator
orchestrator = AgentOrchestrator(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    db_connection_string=os.getenv("DATABASE_URL"),
    api_spec_path=os.getenv("API_SPEC_PATH"),
    api_base_url=os.getenv("API_BASE_URL")
)

# Store conversation states in memory (in production, use Redis or a database)
conversation_states: Dict[str, Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    source: str
    details: Dict[str, Any]
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None
    conversation_id: str

@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.debug(f"Chat request received - User: {current_user.username}, Query: {request.query}")
        
        # Get or create conversation state
        conversation_id = request.conversation_id or f"conv_{current_user.username}_{len(conversation_states)}"
        conversation_state = conversation_states.get(conversation_id)

        try:
            # Process query with conversation state
            result = orchestrator.process_query(request.query, conversation_state)
            
            # Store updated conversation state
            conversation_states[conversation_id] = result.get("full_state", {})
            
            response = ChatResponse(
                response=result["response"],
                source=result["source"],
                details=result.get("full_state", {}),
                requires_confirmation=result.get("requires_confirmation", False),
                confirmation_message=result.get("confirmation_message"),
                conversation_id=conversation_id
            )
            logger.info(f"Sending response to user {current_user.username}")
            return response
            
        except Exception as inner_e:
            logger.error(f"Error creating response object: {str(inner_e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error creating response: {str(inner_e)}"
            )

    except ValueError as ve:
        # Handle validation errors from pydantic
        raise HTTPException(
            status_code=422,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        logger.error(f"Request data: {request.dict()}")
        logger.error(f"User data: {current_user}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )
