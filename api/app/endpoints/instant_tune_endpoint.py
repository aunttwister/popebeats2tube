"""
Module: instant_upload_endpoint
===============================
This module defines FastAPI endpoints for uploading tunes.

Endpoints:
----------
1. `/instant_upload/single`:
   - Handles the upload of a single tune via a POST request.
2. `/instant_upload/batch`:
   - Handles the upload of a batch of tunes via a POST request.

Logging:
--------
- DEBUG: Logs the start and success of upload processes.
- INFO: Logs sensitive information such as tune details (visible only if advanced logging is enabled).
- ERROR: Excludes sensitive information and logs high-level failure details.

Functions:
----------
- upload_single(tune: TuneDto): Handles the upload of a single tune.
- upload_batch(tunes: list[TuneDto]): Handles the upload of a batch of tunes.
"""

from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from app.auth_dependencies import get_current_user
from app.db.db import get_db_session
from app.dto import TuneDto
from app.repositories.user_mgmt_repository import verify_user_id
from app.services.upload_service import process_and_upload_tune, validate_and_refresh_token
from app.utils.http_response_util import response_200
from app.logging.logging_setup import logger

instant_upload_router = APIRouter(dependencies=[Depends(get_current_user)])

@instant_upload_router.post("/single")
async def upload_single(tune: TuneDto):
    """
    Handles the upload of a single tune.

    Args:
    -----
    tune : TuneDto
        The data transfer object containing the details of the tune to be uploaded.

    Returns:
    --------
    dict
        A JSON response with a success message if the upload is successful.

    Logs:
    -----
    - DEBUG: Start and successful completion of the upload process.
    - INFO: Detailed information about the uploaded tune (if advanced logging is enabled).
    - ERROR: Logs high-level failure details without exposing sensitive information.

    Raises:
    -------
    HTTPException
        400: If the upload fails or the result is empty.
    """
    logger.debug("Starting single tune upload.")
    logger.info(f"Uploading tune: {tune.model_dump()}")

    try:
        # Simulate tune upload processing
        #result = await upload_single_tune(tune)
        result: str = "Simulated Upload Success"  # Replace with actual upload logic
        if not result:
            logger.error("Single tune upload failed.")
            raise HTTPException(status_code=400, detail="Upload failed")

        logger.debug("Single tune upload successful.")
        return response_200("Upload successful")
    except Exception as e:
        logger.error(f"Unexpected error during single tune upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@instant_upload_router.post("/batch")
async def upload_batch(
    tunes: list[TuneDto],
    db: Session = Depends(get_db_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Handles the upload of a batch of tunes.
    """
    logger.debug("Starting batch tune upload.")

    # Verify user and refresh token if necessary
    user = verify_user_id(current_user_id)
    if not user:
        logger.error("Invalid user ID")
        raise HTTPException(status_code=400, detail="Invalid user ID")

    await validate_and_refresh_token(user, db)

    try:
        for tune in tunes:
            await process_and_upload_tune(tune, user)

        logger.debug("Batch tune upload successful.")
        return {"message": "Batch upload successful"}
    except Exception as e:
        logger.error(f"Unexpected error during batch tune upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
