from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
import os

from app.auth_dependencies import get_current_user
from app.db import get_db_session
from app.dto import UserCreateDTO
from app.logging.logging_setup import logger
from app.services.config_mgmt_service import load_config
from app.repositories.user_mgmt_repository import create_user_in_db

user_mgmt_router = APIRouter(dependencies=[Depends(get_current_user)])

# Load configuration
CONFIG = load_config()
ADMIN = CONFIG.get("admin", {})
ADMIN_API_KEY = ADMIN.get("auth_token", "")
# ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")  # Load the API key from the environment

def verify_admin_api_key(admin_api_key: str = Header(...)):
    """
    Validates the provided admin API key.

    Args:
    -----
    admin_api_key : str
        The API key sent in the request headers.

    Logs:
    -----
    - DEBUG: Start of API key verification.
    - ERROR: Logs invalid API key attempts.

    Raises:
    -------
    HTTPException
        403: If the provided API key is invalid.
    """
    logger.debug("Verifying admin API key.")
    if admin_api_key != ADMIN_API_KEY:
        logger.error("Invalid admin API key provided.")
        raise HTTPException(status_code=403, detail="Invalid API key")
    logger.debug("Admin API key verification successful.")

@user_mgmt_router.post("", dependencies=[Depends(verify_admin_api_key)])
def create_user(user_dto: UserCreateDTO, db: Session = Depends(get_db_session)):
    """
    API endpoint to create a new user.

    Args:
    -----
    user_dto : UserCreateDTO
        The data transfer object containing the user details.
    db : Session
        The database session dependency.

    Returns:
    --------
    dict
        The created user details.
    """
    try:
        return create_user_in_db(user_dto, db)
    except Exception as e:
        return HTTPException(status_code=400, detail=e)