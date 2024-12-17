"""
Main FastAPI application.

This file contains the FastAPI application initialization and startup events. The logger is also set up at the start to handle logging throughout the application.
"""
from fastapi import FastAPI
from services.upload_service import app as upload_service_app
from config.log_config import setup_logging

# Initialize the logger once
logger = setup_logging()

# Create the FastAPI app
app = FastAPI()

# Include the upload service router
app.include_router(upload_service_app)

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.

    This function is executed when the FastAPI application starts. It logs a message indicating that the application has started.
    """
    # Log something at the startup if needed
    logger.info("Application started.")

logger.info("Main app initialized")
