from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException
from app.db.db import User
from app.dto import UserCreateDTO
from app.logging.logging_setup import logger

def create_user_in_db(user_dto: UserCreateDTO,
                      db: Session) -> dict:
    """
    Handles the business logic for creating a new user.

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

    Raises:
    -------
    HTTPException
        If a user with the same email already exists.
    """
    logger.debug("Initializing user creation...")
    # Check if user already exists
    logger.debug("Checking if user already exists in database.")
    logger.info(f"Checking if user {user_dto.email} already exists in database.")
    existing_user = db.query(User).filter(User.email == user_dto.email).first()
    if existing_user:
        logger.error("User with this email already exists.")
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create the new user
    new_user = User(
        email=user_dto.email,
        date_created=datetime.now(timezone.utc),
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

        
    new_user_data = {
        "id": new_user.id,
        "email": new_user.email,
        "date_created": new_user.date_created,
        "is_active": new_user.is_active
    }

    logger.debug("User successfully created.")
    logger.info(f"User successfully created with following data: {new_user_data}")

    return new_user_data
