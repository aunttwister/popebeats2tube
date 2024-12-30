from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
import os

from app.db import get_db_session
from app.dto import UserCreateDTO
from app.services.config_mgmt_service import load_config
from app.repositories.user_mgmt_repository import create_user_in_db

user_mgmt_router = APIRouter()

# Load configuration
CONFIG = load_config()
ADMIN = CONFIG.get("admin", {})
ADMIN_API_KEY = ADMIN.get("auth_token", "")
# ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")  # Load the API key from the environment

def verify_admin_api_key(admin_api_key: str = Header(...)):
    """
    Verifies if the provided ADMIN_API_KEY is valid.

    Args:
    -----
    admin_api_key : str
        The API key sent in the request headers.

    Raises:
    -------
    HTTPException
        If the API key is invalid.
    """
    if admin_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

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
