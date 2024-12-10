from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class ClaimDetails(BaseModel):
    vehicle: Optional[str] = None
    damage_description: Optional[str] = None
    photos: List[str] = []

class ConversationState(BaseModel):
    query: str
    current_step: str = "initial"
    claim_details: Optional[ClaimDetails] = None
    collected_info: Dict[str, Any] = {}
    knowledge_found: bool = False
    api_success: bool = False
    api_error: Optional[str] = None
    knowledge_response: Optional[str] = None
    api_response: Optional[str] = None
    fallback_response: Optional[str] = None
    requires_user_confirmation: bool = False
    confirmation_message: Optional[str] = None
