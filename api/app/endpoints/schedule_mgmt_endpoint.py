"""
Endpoint Layer: Schedule Management
===================================
This module defines the API endpoints for managing schedules.

Responsibilities:
-----------------
- Retrieve all schedules.
- Retrieve a specific schedule by ID.
- Create a new schedule entry.
- Update an existing schedule entry.
- Delete a schedule entry.

Logging:
--------
- DEBUG: Logs the start and success of operations.
- INFO: Includes sensitive details like schedule metadata.
- ERROR: Logs meaningful error descriptions without exposing sensitive information.

Endpoints:
----------
- `GET /schedule-upload`: Retrieve all schedules.
- `GET /schedule-upload/{schedule_id}`: Retrieve a specific schedule.
- `POST /schedule-upload`: Create a new schedule.
- `PUT /schedule-upload/{schedule_id}`: Update a specific schedule.
- `DELETE /schedule-upload/{schedule_id}`: Delete a specific schedule.
"""

from datetime import datetime, timezone
from math import ceil
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.auth_dependencies import get_current_user
from app.db import get_db_session
from app.dto import ScheduleDto
from app.utils.http_response_util import (
    response_200,
    response_201,
    response_204
)
from app.repositories.schedule_mgmt_repository import (
    create_schedules_in_batch,
    get_schedules,
    get_schedule_by_id,
    create_schedule,
    update_schedule,
    delete_schedule,
)
from app.logging.logging_setup import logger

schedule_mgmt_router = APIRouter(dependencies=[Depends(get_current_user)])

@schedule_mgmt_router.get("")
async def get_schedules_list(
    db: Session = Depends(get_db_session),
    current_user_id: str = Depends(get_current_user),
    page: int = Query(1, ge=1),  # Page number, default 1, must be >= 1
    limit: int = Query(10, ge=1, le=100),  # Limit, default 10, must be between 1 and 100
):
    """
    Retrieve a paginated list of schedules for the current user.

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
        A dictionary containing the paginated list of schedules, current page, and total pages.
    """
    logger.debug(f"Retrieving schedules for user_id: {current_user_id}, page: {page}, limit: {limit}")
    try:
        schedules, total_count = await get_schedules(db, str(current_user_id), page, limit)
        total_pages = ceil(total_count / limit)

        logger.debug(f"Retrieved {len(schedules)} schedules for user_id: {current_user_id}")
        return response_200(
            "Success.",
            "Successfully fetched schedules.",
            {
                "data": jsonable_encoder(schedules),
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
            },
        )
    except Exception as e:
        logger.error(f"Failed to retrieve schedules for user_id {current_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@schedule_mgmt_router.get("/{schedule_id}")
async def get_schedule_by_id_route(schedule_id: int, db: Session = Depends(get_db_session)):
    """
    Retrieve a specific schedule by its ID.

    Args:
    -----
    schedule_id : int
        The ID of the schedule to retrieve.
    db : Session
        The database session used for querying.

    Returns:
    --------
    dict
        A dictionary containing the schedule.

    Logs:
    -----
    - DEBUG: Start and success of schedule retrieval.
    - INFO: The ID of the schedule being retrieved.
    - ERROR: Logs failures when the schedule is not found or other issues occur.
    """
    logger.debug(f"Retrieving schedule with ID: {schedule_id}.")
    try:
        schedule = await get_schedule_by_id(schedule_id, db)
        if not schedule:
            logger.error(f"Schedule not found: ID {schedule_id}.")
            raise HTTPException(status_code=404, detail="Schedule not found")
        logger.debug(f"Schedule retrieved: ID {schedule_id}.")
        return response_200("Success.", schedule)
    except Exception as e:
        logger.error(f"Failed to retrieve schedule ID {schedule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@schedule_mgmt_router.post("")
async def create_schedule_entry(schedule: ScheduleDto, db: Session = Depends(get_db_session)):
    """
    Create a new schedule entry.

    Args:
    -----
    schedule : ScheduleDto
        The schedule data to create.
    db : Session
        The database session used for committing the new schedule.

    Returns:
    --------
    dict
        A dictionary containing the creation result and the new schedule.

    Logs:
    -----
    - DEBUG: Start and success of schedule creation.
    - INFO: The details of the created schedule.
    - ERROR: Logs failures during schedule creation.

    Raises:
    -------
    HTTPException
        400: If the upload date is in the past.
    """
    logger.debug(f"Creating new schedule: {schedule.video_title}.")
    try:
        if datetime.fromisoformat(schedule.upload_date) < datetime.now(timezone.utc):
            logger.error("Upload date is in the past.")
            raise HTTPException(status_code=400, detail="Upload date is in the past")
        result = await create_schedule(schedule, db)
        logger.debug("Schedule creation successful.")
        logger.info(f"Created schedule: {result.video_title}.")
        return response_201("Upload schedule created.", result)
    except Exception as e:
        logger.error(f"Failed to create schedule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@schedule_mgmt_router.post("/batch")
async def create_batch_schedule_entry(
    schedules: list[ScheduleDto], 
    db: Session = Depends(get_db_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create multiple schedule entries in a single batch operation.

    Args:
    -----
    schedules : List[ScheduleDto]
        The list of schedule data to create.
    db : Session
        The database session used for committing the new schedules.

    Returns:
    --------
    dict
        A dictionary containing the result of the batch operation.

    Logs:
    -----
    - DEBUG: Start and success of schedule batch creation.
    - INFO: The details of the created schedules.
    - ERROR: Logs failures during batch schedule creation.

    Raises:
    -------
    HTTPException
        400: If any upload date is in the past.
    """
    logger.debug(f"Creating batch schedule entries: {len(schedules)} schedules.")
    try:
        for schedule in schedules:
            current_time = datetime.now(timezone.utc)
            if schedule.upload_date < current_time:
                logger.error(f"Upload date is in the past for {schedule.video_title}.")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Upload date is in the past for {schedule.video_title}"
                )
        results = await create_schedules_in_batch(schedules, str(current_user_id), db)
        logger.debug("Batch schedule creation successful.")
        logger.info(f"Created schedules: {[schedule.video_title for schedule in schedules]}.")
        
        to_return = [schedule.model_dump() for schedule in results]
        return response_201(
            "Success",
            "Batch upload schedules created successfully.",
            jsonable_encoder(to_return)
        )
    except Exception as e:
        logger.error(f"Failed to create batch schedules: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@schedule_mgmt_router.put("/{schedule_id}")
async def update_schedule_entry(schedule_id: int, schedule: ScheduleDto, db: Session = Depends(get_db_session)):
    """
    Update an existing schedule entry.

    Args:
    -----
    schedule_id : int
        The ID of the schedule to update.
    schedule : ScheduleDto
        The updated schedule data.
    db : Session
        The database session used for committing the update.

    Returns:
    --------
    dict
        A dictionary containing the updated schedule.

    Logs:
    -----
    - DEBUG: Start and success of schedule update.
    - INFO: The details of the updated schedule.
    - ERROR: Logs failures during schedule update.

    Raises:
    -------
    HTTPException
        400: If the upload date is in the past.
        404: If the schedule is not found.
    """
    logger.debug(f"Updating schedule with ID: {schedule_id}.")
    try:
        if datetime.fromisoformat(schedule.upload_date) < datetime.now(timezone.utc):
            logger.error("Upload date is in the past.")
            raise HTTPException(status_code=400, detail="Upload date is in the past")
        result = await update_schedule(schedule_id, schedule, db)
        if not result:
            logger.error(f"Schedule not found: ID {schedule_id}.")
            raise HTTPException(status_code=404, detail="Schedule not found")
        logger.debug(f"Schedule update successful: ID {schedule_id}.")
        logger.info(f"Updated schedule: {result.video_title}.")
        return response_204("Upload schedule updated.")
    except Exception as e:
        logger.error(f"Failed to update schedule ID {schedule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@schedule_mgmt_router.delete("/{schedule_id}")
async def delete_schedule_entry(schedule_id: int, db: Session = Depends(get_db_session)):
    """
    Delete a specific schedule entry.

    Args:
    -----
    schedule_id : int
        The ID of the schedule to delete.
    db : Session
        The database session used for deleting the schedule.

    Returns:
    --------
    dict
        A dictionary confirming the deletion.

    Logs:
    -----
    - DEBUG: Start and success of schedule deletion.
    - ERROR: Logs failures during schedule deletion.

    Raises:
    -------
    HTTPException
        404: If the schedule is not found.
    """
    logger.debug(f"Deleting schedule with ID: {schedule_id}.")
    try:
        result = await delete_schedule(schedule_id, db)
        if not result:
            logger.error(f"Schedule not found for deletion: ID {schedule_id}.")
            raise HTTPException(status_code=404, detail="Schedule not found")
        logger.debug(f"Schedule deletion successful: ID {schedule_id}.")
        return response_204("Upload schedule deleted.")
    except Exception as e:
        logger.err(f"Failed to delete schedule ID {schedule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
