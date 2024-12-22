# Module-level docstring
"""
This module contains the API endpoint definitions for managing schedules. 
It includes operations to get, create, update, and delete schedules.
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.dto import ScheduleDto
from app.http_response import (
    response_200,
    response_201,
    response_204
)
from app.services.schedule_mgmt_service import (
    get_schedules,
    get_schedule_by_id,
    create_schedule,
    update_schedule,
    delete_schedule,
)

router = APIRouter()

# # /upload_tune/single - POST single tune upload
# @router.post("/single")
# async def upload_single(tune: TuneDto):
#     result = await upload_single_tune(tune)
#     if not result:
#         raise HTTPException(status_code=400, detail="Upload failed")
#     return {"message": "Upload successful"}

# # /upload_tune/batch - POST batch tune upload
# @router.post("/batch")
# async def upload_batch(tunes: list[TuneDto]):
#     result = await upload_batch_tunes(tunes)
#     if not result:
#         raise HTTPException(status_code=400, detail="Batch upload failed")
#     return {"message": "Batch upload successful"}

# /schedule_upload/get - GET list of schedules
@router.get("/get")
async def get_schedules_list(db: Session = Depends(get_db_session)):
    """
    Retrieve a list of all schedules from the database.

    Args:
    - db (Session): The database session used for querying.

    Returns:
    - A dictionary with the schedules in the system.
    """
    schedules = await get_schedules(db)
    return response_200("Success.", schedules)

# /schedule_upload/get/{id} - GET schedule by ID
@router.get("/get/{schedule_id}")
async def get_schedule_by_id_route(
    schedule_id: int,
    db: Session = Depends(get_db_session)):
    """
    Retrieve a specific schedule by its ID.

    Args:
    - id (int): The ID of the schedule.
    - db (Session): The database session used for querying.

    Returns:
    - A dictionary with the requested schedule if found.
    - HTTPException with a 404 status code if the schedule is not found.
    """
    schedule = await get_schedule_by_id(schedule_id, db)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return response_200("Success.", schedule)

# /schedule_upload/create - POST create new schedule
@router.post("/create")
async def create_schedule_entry(
    schedule: ScheduleDto,
    db: Session = Depends(get_db_session)):
    """
    Create a new schedule entry.

    Args:
    - schedule (ScheduleDto): The schedule data to be created.
    - db (Session): The database session used for committing the new schedule.

    Returns:
    - A dictionary with the creation result and the new schedule.
    - HTTPException with a 400 status code if the upload date is in the past.
    """
    if datetime.fromisoformat(schedule.upload_date) < datetime.now():
        raise HTTPException(status_code=400, detail="Upload date is in the past")
    result = await create_schedule(schedule, db)
    return response_201("Upload schedule created.", result)

# /schedule_upload/update/{id} - PUT update schedule by ID
@router.put("/update/{schedule_id}")
async def update_schedule_entry(
    schedule_id: int,
    schedule: ScheduleDto,
    db: Session = Depends(get_db_session)):
    """
    Update an existing schedule entry by its ID.

    Args:
    - id (int): The ID of the schedule to update.
    - schedule (ScheduleDto): The new schedule data to update the existing schedule.
    - db (Session): The database session used for committing the update.

    Returns:
    - A dictionary with the update result and the updated schedule.
    - HTTPException with a 404 status code if the schedule is not found.
    - HTTPException with a 400 status code if the upload date is in the past.
    """
    if datetime.fromisoformat(schedule.upload_date) < datetime.now():
        raise HTTPException(status_code=400, detail="Upload date is in the past")
    result = await update_schedule(schedule_id, schedule, db)
    if not result:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return response_204("Upload schedule updated.")

# /schedule_upload/delete/{id} - DELETE schedule by ID
@router.delete("/delete/{schedule_id}")
async def delete_schedule_entry(
    schedule_id: int,
    db: Session = Depends(get_db_session)):
    """
    Delete a specific schedule entry by its ID.

    Args:
    - id (int): The ID of the schedule to delete.
    - db (Session): The database session used for deleting the schedule.

    Returns:
    - A dictionary with a deletion message.
    - HTTPException with a 404 status code if the schedule is not found.
    """
    result = await delete_schedule(schedule_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return response_204("Upload schedule deleted.")
