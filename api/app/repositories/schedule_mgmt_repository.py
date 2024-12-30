"""
Service layer for managing schedules.

This module provides functions to interact with the database for CRUD operations on schedules.
It abstracts the database operations to maintain separation of concerns.

Functions:
- get_schedules: Retrieve all schedules from the database.
- get_schedule_by_id: Retrieve a specific schedule by its ID.
- create_schedule: Create a new schedule in the database.
- update_schedule: Update an existing schedule in the database.
- delete_schedule: Delete a schedule from the database.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db import Schedule  # Using the database model for interaction
from app.dto import ScheduleDto
from app.services.file_transfer_service import transfer_file

async def get_schedules(db: Session) -> List[ScheduleDto]:
    """
    Retrieve all schedules from the database.

    Args:
    - db (Session): The database session to use for the query.

    Returns:
    - List[ScheduleDto]: A list of all schedules in the database, mapped to DTO objects.
    """
    schedules = db.query(Schedule).all()
    return [ScheduleDto.model_validate(schedule) for schedule in schedules]

async def get_schedule_by_id(
    schedule_id: int,
    db: Session) -> Optional[ScheduleDto]:
    """
    Retrieve a specific schedule by its ID.

    Args:
    - id (int): The unique identifier of the schedule to retrieve.
    - db (Session): The database session to use for the query.

    Returns:
    - Optional[ScheduleDto]: The schedule mapped to a DTO object if found, otherwise None.
    """
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if schedule:
        return ScheduleDto.model_validate(schedule)
    return None

async def create_schedule(
    schedule: ScheduleDto,
    db: Session) -> ScheduleDto:
    """
    Create a new schedule in the database and transfer associated files.

    Args:
    - schedule (ScheduleDto): The DTO containing the details of the schedule to create.
    - db (Session): The database session to use for the operation.

    Returns:
    - ScheduleDto: The newly created schedule mapped to a DTO object.
    """
    # Transfer files to the shared location
    image_path = transfer_file(schedule.img, schedule.video_title)
    audio_path = transfer_file(schedule.audio, schedule.video_title)

    # Create a new schedule record in the database
    new_schedule = Schedule(
        upload_date=schedule.upload_date,
        executed=schedule.executed,
        video_title=schedule.video_title,
        image_location=image_path,
        audio_location=audio_path,
        date_created=datetime.now()
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return ScheduleDto.model_validate(new_schedule)

async def update_schedule(
    schedule_id: int,
    schedule: ScheduleDto,
    db: Session) -> Optional[ScheduleDto]:
    """
    Update an existing schedule in the database and transfer associated files if updated.

    Args:
    - schedule_id (int): The unique identifier of the schedule to update.
    - schedule (ScheduleDto): The DTO containing the updated details of the schedule.
    - db (Session): The database session to use for the operation.

    Returns:
    - Optional[ScheduleDto]: The updated schedule mapped to a DTO object if successful,
    otherwise None.
    """
    existing_schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not existing_schedule:
        return None

    # Transfer files if updated
    if schedule.image_location != existing_schedule.image_location:
        image_path = transfer_file(schedule.image_location, f"{schedule.video_title}_image.jpg")
        existing_schedule.image_location = image_path

    if schedule.audio_location != existing_schedule.audio_location:
        audio_path = transfer_file(schedule.audio_location, f"{schedule.video_title}_audio.mp3")
        existing_schedule.audio_location = audio_path

    # Update other fields
    existing_schedule.upload_date = schedule.upload_date
    existing_schedule.executed = schedule.executed
    existing_schedule.video_title = schedule.video_title

    db.commit()
    db.refresh(existing_schedule)
    return ScheduleDto.model_validate(existing_schedule)

async def delete_schedule(
    schedule_id: int,
    db: Session) -> bool:
    """
    Delete a schedule from the database.

    Args:
    - id (int): The unique identifier of the schedule to delete.
    - db (Session): The database session to use for the operation.

    Returns:
    - bool: True if the schedule was successfully deleted, otherwise False.
    """
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        return False
    db.delete(schedule)
    db.commit()
    return True
