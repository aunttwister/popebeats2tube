from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from app.db import User
from app.dto import UserCreateDTO

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
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_dto.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create the new user
    new_user = User(
        email=user_dto.email,
        youtube_api_key="",  # Leave empty as per requirements
        date_created=datetime.now(),
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "date_created": new_user.date_created,
        "is_active": new_user.is_active
    }
