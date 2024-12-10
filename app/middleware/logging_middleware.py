import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Response: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.2f}s"
            )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(f"Error processing request: {request.method} {request.url} - Error: {str(e)}")
            raise
