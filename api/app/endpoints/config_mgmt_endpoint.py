"""
This module provides FastAPI endpoints for managing and retrieving configuration data. 

Endpoints:
----------
- `/`: A GET endpoint to retrieve the current configuration.
- `/reload`: A POST endpoint to reload the configuration from the configuration file. 
  This endpoint is protected and requires an admin API key for access.

Features:
---------
- Fetch and update configuration settings dynamically.
- Protect sensitive operations like configuration reloads with an admin API key.
"""

from fastapi import APIRouter, Header, HTTPException
import os

from app.services.config_mgmt_service import load_config

config_mgmt_router = APIRouter()

# Global variable to store the current configuration
current_config = load_config()  # Initial load of the configuration

@config_mgmt_router.get("")
def get_config():
    """
    Retrieve and return the current configuration.

    This endpoint returns the configuration data in the form of a dictionary containing key-value pairs,
    representing various application settings loaded from the configuration file.

    Returns:
    --------
    dict
        The current configuration loaded from the cached configuration.
    """
    return current_config

@config_mgmt_router.post("/reload")
def reload_configuration(admin_api_key: str = Header(...)):
    """
    Reload the application configuration from the configuration file.

    This endpoint is protected and can only be accessed with a valid admin API key. If the provided API key
    does not match the one stored in the environment, a 403 Forbidden error will be raised. Upon successful
    authorization, the cached configuration is cleared, and the configuration file is reloaded.

    Args:
    -----
    admin_api_key : str
        The admin API key passed via the request header to authorize the reload operation.

    Returns:
    --------
    dict
        A success message along with the updated configuration data.

    Raises:
    -------
    HTTPException (403)
        If the provided admin API key is invalid or missing.
    """
    if admin_api_key != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid admin API key.")
    
    global current_config
    global _config  # Access the global cached variable from load_config

    # Clear the cached configuration and reload
    _config = None  # Reset cached configuration
    current_config = load_config()

    return {"message": "Configuration reloaded successfully.", "config": current_config}
