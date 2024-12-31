"""
This module defines the FastAPI application and its routing. It includes the setup
for schedule management endpoints to create, retrieve, update, and delete schedules.

Modules:
    - schedule_upload: Handles schedule-related operations (CRUD functionality).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints.schedule_mgmt_endpoint import schedule_mgmt_router
from app.endpoints.config_mgmt_endpoint import config_mgmt_router
from app.endpoints.auth_endpoint import auth_router
from app.endpoints.instant_upload_endpoint import instant_upload_router
from app.endpoints.user_mgmt_endpoint import user_mgmt_router
from app.services.config_mgmt_service import load_config
from app.logging.logging_setup import logger
from app.utils.http_response_util import (
    not_found_handler,
    forbidden_handler,    unauthorized_handler,
    bad_request_handler,
    internal_server_error_handler
)


# Log application initialization
logger.debug("Initializing the application...")

# Load configuration during startup
CONFIG = load_config()

# Create FastAPI app instance
app = FastAPI()

origins = [
    "http://localhost:3000",  # Your React frontend
    "http://127.0.0.1:3000",  # Alternative localhost format
    # Add more origins as needed
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies to be included
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response

# Include routers
app.include_router(schedule_mgmt_router, prefix="/schedule-upload", tags=["schedule-upload"])
app.include_router(config_mgmt_router, prefix="/config-management", tags=["config-management"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(instant_upload_router, prefix="/instant-upload", tags=["instant-upload"])
app.include_router(user_mgmt_router, prefix="/user-mgmt", tags=["user-mgmt"])

# Register exception handlers
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(403, forbidden_handler)
app.add_exception_handler(401, unauthorized_handler)
app.add_exception_handler(400, bad_request_handler)
app.add_exception_handler(500, internal_server_error_handler)

# Add startup and shutdown event handlers
@app.on_event("startup")
async def startup_event():
    logger.debug("Application has started.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.debug("Application is stopping.")
