"""
This module defines authentication endpoints for the application using FastAPI.

Functions:
----------
- google_auth(auth_request: AuthRequestDto): Authenticates a user via Google OAuth, validates the user's existence, and returns a JWT token for authorized access.

The module integrates with the `auth_service` to verify the Google token, check the user in the database, and generate a JWT token for authenticated users.

It also raises appropriate HTTP exceptions if the Google token is invalid, the user cannot be found, or any other authentication issues arise.
"""
from fastapi import APIRouter, HTTPException
from app.dto import AuthRequestDto
from app.services.auth_service import create_jwt, verify_google_token, verify_user

auth_router = APIRouter()

@auth_router.post("/google")
async def google_auth(auth_request: AuthRequestDto):
    """
    Handles the Google OAuth authentication process for a user.

    This function performs the following steps:
    1. Verifies the Google OAuth token using the `verify_google_token` function.
    2. Extracts the user's email from the verified Google token.
    3. Checks the existence of the user in the database using the `verify_user` function.
    4. If the user is found, generates a JWT token using the `create_jwt` function and returns it to the client.

    Arguments:
    ----------
    - auth_request (AuthRequestDto): The request object containing the Google OAuth token.

    Returns:
    --------
    - dict: A dictionary containing the generated JWT token if authentication is successful.

    Raises:
    -------
    - HTTPException: 
    - 401: If the Google token is invalid or the email is missing.
    - 401: If the user does not exist in the database or is unauthorized.
    """
    # Layer 1: Verify Google OAuth Token
    try:
        idinfo = verify_google_token(auth_request.token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Token.")
    
    if "email" not in idinfo:
        raise HTTPException(status_code=401, detail="Invalid Google Token: Missing email")
    email = str(idinfo["email"])
    
    # Layer 2: Validate YouTube API Key
    user = verify_user(email)
    if not user:
        raise HTTPException(status_code=401, detail=f"User with email '{email}' is not authorized for access.")

    # Generate JWT
    jwt_token = create_jwt(user_id=user.id)
    return {"jwt": jwt_token}