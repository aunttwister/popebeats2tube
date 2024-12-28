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
from app.utils.http_response_util import (
    not_found_handler,
    forbidden_handler,
    unauthorized_handler,
    bad_request_handler,
    internal_server_error_handler
)

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

# Include the upload_tune router
# app.include_router(router, prefix="/upload_tune", tags=["upload_tune"])
# Include the schedule_upload router
app.include_router(schedule_mgmt_router, prefix="/schedule_upload", tags=["schedule_upload"])
app.include_router(config_mgmt_router, prefix="/config_management", tags=["config_management"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(instant_upload_router, prefix="/instant_upload", tags=["instant_upload"])
app.include_router(user_mgmt_router, prefix="/user_mgmt", tags=["user_mgmt"])

# Register exception handlers
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(403, forbidden_handler)
app.add_exception_handler(401, unauthorized_handler)
app.add_exception_handler(400, bad_request_handler)
app.add_exception_handler(500, internal_server_error_handler)
