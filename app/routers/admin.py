from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from app.utils.auth import get_admin_user
from app.models.user import User
from typing import Dict, Any, Optional
import os
from datetime import datetime
import shutil
import json
from app.agents.knowledge_agent import KnowledgeAgent
from app.config import get_settings
from app.utils.logger import logger

router = APIRouter()

# Create temporary upload directory if it doesn't exist
UPLOAD_DIR = "temp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/protected")
async def admin_only(current_user: User = Depends(get_admin_user)):
    return {
        "message": "This is a protected admin route",
        "user": current_user.username,
        "role": current_user.role
    }

@router.post("/upload-policy")
async def upload_policy_document(
    file: UploadFile = File(...),
    user_email: str = Form(...),
    policy_number: str = Form(...),
    policyholder_name: str = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_admin_user)
):
    """Upload a policy document and store it as vectors in PostgreSQL."""
    logger.info(f"Upload policy request received - User: {current_user.username}, Policy: {policy_number}")
    logger.debug(f"File details - Name: {file.filename}, Content-Type: {file.content_type}")
    logger.debug(f"Metadata - Email: {user_email}, Policyholder: {policyholder_name}, Title: {title}")
    
    # Validate file type
    allowed_types = ["application/pdf", "application/msword", 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "text/plain"]  # Added text/plain for testing
    
    if file.content_type not in allowed_types:
        logger.warning(f"Invalid file type attempted: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail="Only PDF, Word documents, and text files are allowed"
        )
    
    try:
        # Generate temporary file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = file.filename
        temp_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{original_name}")
        logger.debug(f"Saving file temporarily to: {temp_path}")
        
        # Save uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved successfully: {temp_path}")
        
        try:
            # Process and store document
            logger.debug("Initializing KnowledgeAgent")
            settings = get_settings()
            agent = KnowledgeAgent(
                openai_api_key=settings.OPENAI_API_KEY,
                connection_string=settings.DATABASE_URL
            )
            
            metadata = {
                "policy_number": policy_number,
                "user_email": user_email,
                "policyholder_name": policyholder_name,
                "title": title,
                "description": description,
                "original_filename": original_name,
                "uploaded_by": current_user.username,
                "upload_timestamp": timestamp
            }
            logger.debug(f"Processing document with metadata: {metadata}")
            
            result = await agent.process_and_store_document(
                file_path=temp_path,
                metadata=metadata
            )
            
            logger.info(f"Document processed successfully - Result: {result}")
            return result
            
        except Exception as inner_e:
            logger.error(f"Error processing document: {str(inner_e)}", exc_info=True)
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                logger.debug(f"Cleaning up temporary file: {temp_path}")
                os.remove(temp_path)
                logger.debug("Temporary file removed")
                
    except Exception as e:
        logger.error(f"Error in upload_policy_document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
