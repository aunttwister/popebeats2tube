"""
This module defines the FastAPI application and its routing. It includes the setup
for schedule management endpoints to create, retrieve, update, and delete schedules.

Modules:
    - schedule_upload: Handles schedule-related operations (CRUD functionality).
"""

from fastapi import FastAPI
from app.controllers import router
from app.http_response import (
    not_found_handler,
    forbidden_handler,
    unauthorized_handler,
    bad_request_handler,
    internal_server_error_handler
)

app = FastAPI()

# Include the upload_tune router
# app.include_router(router, prefix="/upload_tune", tags=["upload_tune"])
# Include the schedule_upload router
app.include_router(router, prefix="/schedule_upload", tags=["schedule_upload"])

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint of the application.

    Returns:
    - A welcome message indicating that the API is up and running.
    """
    return {"message": "Welcome to the Schedule Management API!"}

# Register exception handlers
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(403, forbidden_handler)
app.add_exception_handler(401, unauthorized_handler)
app.add_exception_handler(400, bad_request_handler)
app.add_exception_handler(500, internal_server_error_handler)
