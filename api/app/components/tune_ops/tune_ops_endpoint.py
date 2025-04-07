from datetime import datetime
from typing import Optional
from math import ceil

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from requests import Session

from app.auth_dependencies import get_current_user
from app.components.tune_ops.tune_ops_validator import validate_scheduled_tunes_upload_time
from app.components.user_mgmt.user_mgmt_validator import validate_user_exists
from app.db.db import get_db_session
from app.dto import TuneDto
from app.utils.http_response_util import (
    response_200,
    response_201,
    response_204
)

from app.components.tune_ops.tune_ops_service import (
    get_user_tunes_service,
    update_tune_service,
    delete_tune_service,
    create_tunes_service
)
from app.components.user_mgmt.user_mgmt_service import get_user_by_id_service
from app.components.auth.google_oauth.google_oauth_service import validate_and_refresh_token
from app.components.upload.upload_processing.upload_processing_service import process_and_upload_tunes
from app.logger.logging_setup import logger

tune_ops_router = APIRouter(dependencies=[Depends(get_current_user)])

@tune_ops_router.post("/instant")
async def create_instant_tune(
    tunes: list[TuneDto],
    db: Session = Depends(get_db_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Handles the instant upload of single or batch of tunes.
    """
    logger.debug("Received tune/s upload request.")

    user = get_user_by_id_service(current_user_id, db)
    validate_user_exists(user)

    await validate_and_refresh_token(user, db)

    try:
        created_tunes = await create_tunes_service(tunes, user.id, db)
        await process_and_upload_tunes(created_tunes, user)

        return response_201(
            "Success",
            "Tune/s uploaded successfully."
        )
    except Exception as e:
        logger.error(f"Tune/s upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

@tune_ops_router.get("")
async def get_all_user_tunes(
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
    
@tune_ops_router.post("/schedule")
async def create_scheduled_tune(
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
        user = get_user_by_id_service(current_user_id, db)
        validate_user_exists(user)
        validate_scheduled_tunes_upload_time(tunes)

        await create_tunes_service(tunes, str(current_user_id), db)
        return response_201(
            "Success",
            "Scheduled tunes created successfully.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch tune creation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@tune_ops_router.put("/schedule/{tune_id}")
async def update_scheduled_tune(tune_id: int, tune: TuneDto, db: Session = Depends(get_db_session)):
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
        await update_tune_service(tune_id, tune, db)
        return response_204()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Update failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@tune_ops_router.delete("/{tune_id}")
async def delete_scheduled_tune(tune_id: int, db: Session = Depends(get_db_session)):
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
        await delete_tune_service(tune_id, db)
        return response_204()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")