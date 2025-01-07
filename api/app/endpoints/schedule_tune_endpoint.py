"""
Endpoint Layer: tune Management
===================================
This module defines the API endpoints for managing tunes.

Responsibilities:
-----------------
- Retrieve all tunes.
- Retrieve a specific tune by ID.
- Create a new tune entry.
- Update an existing tune entry.
- Delete a tune entry.

Logging:
--------
- DEBUG: Logs the start and success of operations.
- INFO: Includes sensitive details like tune metadata.
- ERROR: Logs meaningful error descriptions without exposing sensitive information.

Endpoints:
----------
- `GET /tune-upload`: Retrieve all tunes.
- `GET /tune-upload/{tune_id}`: Retrieve a specific tune.
- `POST /tune-upload`: Create a new tune.
- `PUT /tune-upload/{tune_id}`: Update a specific tune.
- `DELETE /tune-upload/{tune_id}`: Delete a specific tune.
"""

from datetime import datetime, timezone
from math import ceil
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.auth_dependencies import get_current_user
from app.db.db import get_db_session
from app.dto import TuneDto
from app.utils.http_response_util import (
    response_200,
    response_201,
    response_204
)
from app.repositories.schedule_tune_repository import (
    create_tunes_in_batch,
    get_tunes,
    update_tune,
    delete_tune,
)
from app.logging.logging_setup import logger

schedule_tune_router = APIRouter(dependencies=[Depends(get_current_user)])

@schedule_tune_router.get("")
async def get_tunes_list(
    db: Session = Depends(get_db_session),
    current_user_id: str = Depends(get_current_user),
    page: int = Query(1, ge=1),  # Page number, default 1, must be >= 1
    limit: int = Query(10, ge=1, le=100),  # Limit, default 10, must be between 1 and 100
):
    """
    Retrieve a paginated list of tunes for the current user.

    Args:
    -----
    db : Session
        The database session used for querying.
    current_user_id : str
        The ID of the current user extracted from the token.
    page : int
        The page number for pagination.
    limit : int
        The number of items per page for pagination.

    Returns:
    --------
    dict
        A dictionary containing the paginated list of tunes, current page, and total pages.
    """
    logger.debug(f"Retrieving tunes for user_id: {current_user_id}, page: {page}, limit: {limit}")
    try:
        tunes, total_count = await get_tunes(db, str(current_user_id), page, limit)
        total_pages = ceil(total_count / limit)

        logger.debug(f"Retrieved {len(tunes)} tunes for user_id: {current_user_id}")
        return response_200(
            "Success.",
            "Successfully fetched tunes.",
            {
                "data": jsonable_encoder(tunes),
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
            },
        )
    except Exception as e:
        logger.error(f"Failed to retrieve tunes for user_id {current_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@schedule_tune_router.post("/batch")
async def create_batch_tune_entry(
    tunes: list[TuneDto], 
    db: Session = Depends(get_db_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create multiple tune entries in a single batch operation.

    Args:
    -----
    tunes : List[TuneDto]
        The list of tune data to create.
    db : Session
        The database session used for committing the new tunes.

    Returns:
    --------
    dict
        A dictionary containing the result of the batch operation.

    Logs:
    -----
    - DEBUG: Start and success of tune batch creation.
    - INFO: The details of the created tunes.
    - ERROR: Logs failures during batch tune creation.

    Raises:
    -------
    HTTPException
        400: If any upload date is in the past.
    """
    logger.debug(f"Creating batch tune entries: {len(tunes)} tunes.")
    try:
        for tune in tunes:
            current_time = datetime.now(timezone.utc)
            if tune.upload_date < current_time:
                logger.error(f"Upload date is in the past for {tune.video_title}.")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Upload date is in the past for {tune.video_title}"
                )
        results = await create_tunes_in_batch(tunes, str(current_user_id), db)
        logger.debug("Batch tune creation successful.")
        logger.info(f"Created tunes: {[tune.video_title for tune in tunes]}.")
        
        to_return = [tune.model_dump() for tune in results]
        return response_201(
            "Success",
            "Batch upload tunes created successfully.",
            jsonable_encoder(to_return)
        )
    except Exception as e:
        logger.error(f"Failed to create batch tunes: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@schedule_tune_router.put("/{tune_id}")
async def update_tune_entry(tune_id: int, tune: TuneDto, db: Session = Depends(get_db_session)):
    """
    Update an existing tune entry.

    Args:
    -----
    tune_id : int
        The ID of the tune to update.
    tune : TuneDto
        The updated tune data.
    db : Session
        The database session used for committing the update.

    Returns:
    --------
    dict
        A dictionary containing the updated tune.

    Logs:
    -----
    - DEBUG: Start and success of tune update.
    - INFO: The details of the updated tune.
    - ERROR: Logs failures during tune update.

    Raises:
    -------
    HTTPException
        400: If the upload date is in the past.
        404: If the tune is not found.
    """
    logger.debug(f"Updating tune with ID: {tune_id}.")
    try:
        if tune.upload_date < datetime.now(timezone.utc):
            logger.error("Upload date is in the past.")
            raise HTTPException(status_code=400, detail="Upload date is in the past")
        result = await update_tune(tune_id, tune, db)
        if not result:
            logger.error(f"tune not found: ID {tune_id}.")
            raise HTTPException(status_code=404, detail="tune not found")
        logger.debug(f"tune update successful: ID {tune_id}.")
        logger.info(f"Updated tune: {result.video_title}.")
        return response_204()
    except Exception as e:
        logger.error(f"Failed to update tune ID {tune_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@schedule_tune_router.delete("/{tune_id}")
async def delete_tune_entry(tune_id: int, db: Session = Depends(get_db_session)):
    """
    Delete a specific tune entry.

    Args:
    -----
    tune_id : int
        The ID of the tune to delete.
    db : Session
        The database session used for deleting the tune.

    Returns:
    --------
    dict
        A dictionary confirming the deletion.

    Logs:
    -----
    - DEBUG: Start and success of tune deletion.
    - ERROR: Logs failures during tune deletion.

    Raises:
    -------
    HTTPException
        404: If the tune is not found.
    """
    logger.debug(f"Deleting tune with ID: {tune_id}.")
    try:
        result = await delete_tune(tune_id, db)
        if not result:
            logger.error(f"tune not found for deletion: ID {tune_id}.")
            raise HTTPException(status_code=404, detail="tune not found")
        logger.debug(f"tune deletion successful: ID {tune_id}.")
        return response_204()
    except Exception as e:
        logger.error(f"Failed to delete tune ID {tune_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
