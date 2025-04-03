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
from app.services.user_mgmt_service import verify_user_id_service
from app.services.google_oauth_service import validate_and_refresh_token
from app.services.upload_service import process_and_upload_tunes
from app.logger.logging_setup import logger

instant_upload_router = APIRouter(dependencies=[Depends(get_current_user)])

@instant_upload_router.post("/batch")
async def upload_batch(
    tunes: list[TuneDto],
    db: Session = Depends(get_db_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Handles the upload of a batch of tunes.
    """
    logger.debug("Received batch upload request.")

    user = verify_user_id_service(current_user_id, db)
    if not user:
        logger.error("User verification failed.")
        raise HTTPException(status_code=400, detail="Invalid user ID")

    await validate_and_refresh_token(user, db)

    try:
        await process_and_upload_tunes(tunes, user)
        return {"message": "Batch upload successful"}
    except Exception as e:
        logger.error(f"Batch upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
