from fastapi import HTTPException
from app.db.db import User
from app.logger.logging_setup import logger

def validate_user_exists(user: User):
    logger.debug("Validating the user.")
    if not user:
        logger.error("User verification failed.")
        raise HTTPException(status_code=400, detail="Invalid user ID")