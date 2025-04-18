"""
Module: user_mgmt_repository
=============================
This module provides functions for managing user authentication and credentials in the database.

Responsibilities:
-----------------
- Verifying the existence of users by their email addresses.
- Persisting or updating user credentials such as refresh tokens and token expiry.
- Creating new users in the database.

Logging:
--------
This module includes detailed logging to assist with debugging and operational monitoring:
- DEBUG-level logs provide general operational flow information.
- INFO-level logs include details about sensitive operations (e.g., email addresses) when advanced logging is enabled.

Functions:
----------
- verify_user(email: str): Check if a user exists in the database by their email.
- persist_credentials(user_id: str, refresh_token: str, token_expiry: datetime, db: Session): Update user credentials in the database.
- create_user_in_db(user_dto: UserIn, db: Session): Add a new user to the database.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.db import User
from app.logger.logging_setup import logger

def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(user_id: str, db: Session):
    return db.query(User).filter(User.id == str(user_id)).first()

def update_user_credentials(user: User, youtube_access_token: str, youtube_refresh_token: str, youtube_token_expiry: datetime, db: Session):
    user.youtube_access_token = youtube_access_token
    user.youtube_token_expiry = youtube_token_expiry

    # Only update refresh_token if Google returned a new one
    if youtube_refresh_token:
        user.youtube_refresh_token = youtube_refresh_token

    db.commit()
    return user
    
def insert_user(email: str, db: Session):
    new_user = User(
        email=email,
        youtube_access_token=None,
        youtube_refresh_token=None,
        youtube_token_expiry=None,
        date_created=datetime.now(timezone.utc),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
