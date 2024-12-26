"""
This module provides FastAPI endpoints for managing and retrieving configuration data. 

Endpoints:
----------
- `/config`: A GET endpoint to retrieve the current configuration.
- `/reload`: A POST endpoint to reload the configuration from environment variables or a config file. This endpoint is protected and requires an admin API key for access.

The module provides functionality to fetch and update configuration settings such as log level and retry count, while ensuring sensitive configurations like the database password and API secret are managed securely.
"""

from fastapi import APIRouter, FastAPI, Header, HTTPException
import os

from app.services.config_mgmt_service import load_config

config_mgmt_router = APIRouter()

# Example current configuration
current_config = {"log_level": "INFO", "retry_count": 3}

# Sensitive configurations from environment variables
db_password = os.getenv("DB_PASSWORD")
api_secret = os.getenv("API_SECRET")

@config_mgmt_router.get("/config")
def get_config():
    """
    Retrieve and return the current configuration.

    This endpoint returns the configuration data in the form of a dictionary containing key-value pairs,
    which represent various application settings such as log level and retry count.

    Returns:
    --------
    dict
        The current configuration loaded from the config file or environment variables.
    """
    return load_config()

@config_mgmt_router.post("/reload")
def load_configuration(admin_api_key: str = Header(...)):
    """
    Reload the application configuration from environment variables or configuration files.

    This endpoint is protected and can only be accessed with a valid admin API key. If the provided API key
    does not match the one stored in the environment, a 403 Forbidden error will be raised. Upon successful
    authorization, the configuration values such as log level and retry count will be reloaded.

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
    # Reload logic (from env variables or configuration file)
    current_config["log_level"] = os.getenv("LOG_LEVEL", current_config["log_level"])
    current_config["retry_count"] = int(os.getenv("RETRY_COUNT", current_config["retry_count"]))
    
    return {"message": "Configuration reloaded successfully.", "config": current_config}