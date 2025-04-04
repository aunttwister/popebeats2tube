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
from datetime import datetime
from math import ceil
from typing import Optional
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
from app.services.schedule_tune_service import (
    get_user_tunes_service,
    validate_and_create_scheduled_batch_service,
    validate_and_update_tune_service,
    delete_user_tune_service,
)
from app.logger.logging_setup import logger

schedule_tune_router = APIRouter(dependencies=[Depends(get_current_user)])

@schedule_tune_router.get("")
async def get_user_tunes(
    db: Session = Depends(get_db_session),
    current_user_id: str = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    executed: Optional[bool] = Query(None),
    upload_date_before: Optional[datetime] = Query(None)
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
    try:
        tunes, total_count = await get_user_tunes_service(
            str(current_user_id),
            page,
            limit,
            db,
            upload_date_before=upload_date_before,
            executed=executed
        )
        total_pages = ceil(total_count / limit)

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
    try:
        results = await validate_and_create_scheduled_batch_service(tunes, str(current_user_id), db)
        return response_201(
            "Success",
            "Batch upload tunes created successfully.",
            jsonable_encoder([t.model_dump() for t in results])
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch tune creation failed: {e}")
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
    try:
        await validate_and_update_tune_service(tune_id, tune, db)
        return response_204()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Update failed: {e}")
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
    try:
        await delete_user_tune_service(tune_id, db)
        return response_204()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
