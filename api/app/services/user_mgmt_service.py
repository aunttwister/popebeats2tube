from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from app.logger.logging_setup import logger
from app.repositories.user_mgmt_repository import get_user_by_email, get_user_by_id, insert_user, update_user_credentials
from app.schemas.user_schema import UserIn

def verify_user_email_service(email: str, db: Session):
    """
    Check if a user exists in the database by their email.

    Args:
    -----
    email : str
        The email address of the user to verify.

    Returns:
    --------
    User or None
        The user object if a matching email is found; otherwise, None.

    Logs:
    -----
    - DEBUG: Indicate the start and end of the verification process.
    - INFO: Include the email being verified (if advanced logging is enabled).
    """
    logger.debug("Starting user verification.")
    logger.info(f"Verifying user with email: {email}")
    
    user = get_user_by_email(email, db)
    if user:
        logger.debug("User verification successful.")
        logger.info(f"User found: {email}")
    else:
        logger.warning("User verification failed. User not found.")
    return user

def verify_user_id_service(user_id: str, db: Session):
    
    """
    Check if a user exists in the database by their id.

    Args:
    -----
    user_id : str
        The id of the user to verify.

    Returns:
    --------
    User or None
        The user object if a matching email is found; otherwise, None.

    Logs:
    -----
    - DEBUG: Indicate the start and end of the verification process.
    - INFO: Include the id being verified (if advanced logging is enabled).
    """
    logger.debug("Starting user verification.")
    logger.info(f"Verifying user with id: {user_id}")
    
    user = get_user_by_id(user_id, db)
    if user:
        logger.debug("User verification successful.")
        logger.info(f"User found: {user_id}")
    else:
        logger.warning("User verification failed. User not found.")
    return user

def update_user_credentials_service(user_id: str, youtube_access_token: str, youtube_refresh_token: str, youtube_token_expiry: datetime, db: Session):
    """
    Update the user's credentials in the database.

    Args:
    -----
    user_id : str
        The ID of the user whose credentials are being updated.
    refresh_token : str
        The new refresh token.
    token_expiry : datetime
        The expiration time of the new access token.
    db : Session
        The database session.

    Returns:
    --------
    str
        The email of the user whose credentials were updated.

    Raises:
    -------
    ValueError
        If no user with the specified user ID is found.

    Logs:
    -----
    - DEBUG: Indicate the start and end of credential persistence.
    - INFO: Include the user ID and email (if advanced logging is enabled).
    - ERROR: Exclude sensitive information (e.g., email or tokens).
    """
    logger.debug(f"Persisting credentials for user ID: {user_id}.")
    try:
        user = get_user_by_id(user_id, db)
        if not user:
            logger.error("User not found for credential persistence.")
            raise ValueError(f"User with ID {user_id} not found.")

        updated_user = update_user_credentials(
            user,
            youtube_access_token,
            youtube_refresh_token,
            youtube_token_expiry,
            db
        )

        logger.debug(f"Credentials persisted successfully for user ID: {user_id}.")
        logger.info(f"Credentials persisted for user email: {user.email}")
        return updated_user
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to persist credentials for user ID {user_id}: {str(e)}")
        raise Exception("Unable to persist user credentials. Please check the logs for more details.")

def create_user_service(user_in: UserIn,
                      db: Session) -> dict:
    """
    Handles the business logic for creating a new user.

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

    Raises:
    -------
    HTTPException
        If a user with the same email already exists.
    """
    logger.debug("Initializing user creation...")
    # Check if user already exists
    logger.debug("Checking if user already exists in database.")
    logger.info(f"Checking if user {user_in.email} already exists in database.")
    existing_user = get_user_by_email(user_in.email, db)
    if existing_user:
        logger.error("User with this email already exists.")
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    new_user = insert_user(user_in.email, db)
        
    new_user_data = {
        "id": new_user.id,
        "email": new_user.email,
        "date_created": new_user.date_created,
        "is_active": new_user.is_active
    }

    logger.debug("User successfully created.")
    logger.info(f"User successfully created with following data: {new_user_data}")

    return new_user_data
