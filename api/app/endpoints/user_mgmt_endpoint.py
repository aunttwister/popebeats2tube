from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session

from app.db.db import get_db_session
from app.schemas.user_schema import UserIn
from app.logger.logging_setup import logger
from app.services.user_mgmt_service import create_user_service
from app.settings.env_settings import ADMIN_AUTH_TOKEN


user_mgmt_router = APIRouter()

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
    if admin_api_key != ADMIN_AUTH_TOKEN:
        logger.error("Invalid admin API key provided.")
        raise HTTPException(status_code=403, detail="Invalid API key")
    logger.debug("Admin API key verification successful.")

@user_mgmt_router.post("", dependencies=[Depends(verify_admin_api_key)])
def create_user(user_dto: UserIn, db: Session = Depends(get_db_session)):
    """
    API endpoint to create a new user.

    Args:
    -----
    user_dto : UserIn
        The data transfer object containing the user details.
    db : Session
        The database session dependency.

    Returns:
    --------
    dict
        The created user details.
    """
    try:
        return create_user_service(user_dto, db)
    except Exception as e:
        return HTTPException(status_code=400, detail=e)
