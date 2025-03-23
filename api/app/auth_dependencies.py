import os
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi import Depends, HTTPException
import jwt
from app.services.jwt_mgmt_service import extract_user_id_from_token
from app.logger.logging_setup import logger

# Load configuration
TOKEN_URL = "/auth/token"
SECRET_KEY = os.getenv("POPEBEATS2TUBE_LOCAL_AUTH_JWT_SECRET")  
ALGORITHM = os.getenv("POPEBEATS2TUBE_LOCAL_AUTH_ALGORITHM")  


class OAuth2PasswordBearerWithScopes(OAuth2):
    def __init__(self, tokenUrl: str, scopes: dict = None):
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes or {}})
        super().__init__(flows=flows)


oauth2_scheme = OAuth2PasswordBearerWithScopes(tokenUrl=TOKEN_URL)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to extract the current user ID from the JWT token.

    Args:
    -----
    token : str
        The JWT token containing user claims.

    Returns:
    --------
    UUID
        The user ID extracted from the token.

    Raises:
    -------
    HTTPException
        If the token is invalid or expired.
    """
    logger.debug("Token received.")
    logger.info(f"Token received: {token}")
    token = token.replace('Bearer', '').strip()
    logger.debug("Token stripped.")
    logger.info(f"Token stripped. Propagating token: {token}...")
    try:
        return extract_user_id_from_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


def custom_openapi(app):
    """
    Modify the OpenAPI schema to include Bearer token authentication.

    Args:
    -----
    app : FastAPI
        The FastAPI application instance.

    Returns:
    --------
    dict
        The updated OpenAPI schema.
    """
    if app.openapi_schema:
        return app.openapi_schema

    # Use the original OpenAPI function to get the default schema
    openapi_schema = app._original_openapi()

    # Add Bearer token authentication scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Apply BearerAuth to all paths
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    # Cache the updated schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema
