"""
Repository Layer: Schedule Management
======================================
This module provides functions for interacting with the database for CRUD operations on schedules.

Responsibilities:
-----------------
- Retrieve all schedules from the database.
- Retrieve a specific schedule by ID.
- Create a new schedule, including file transfers.
- Update an existing schedule, handling updated files.
- Delete a schedule.

Logging:
--------
- DEBUG: Logs the start, intermediate steps, and success of operations.
- INFO: Includes sensitive details like schedule metadata.
- ERROR: Logs meaningful error descriptions without exposing sensitive information.

Functions:
----------
- get_schedules: Retrieve all schedules from the database.
- get_schedule_by_id: Retrieve a specific schedule by its ID.
- create_schedule: Create a new schedule and handle associated file transfers.
- update_schedule: Update an existing schedule, including file updates.
- delete_schedule: Delete a schedule from the database.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db import Schedule
from app.dto import ScheduleDto
from app.services.file_transfer_service import transfer_file
from app.logging.logging_setup import logger
from app.utils.file_util import base64_to_file


async def get_schedules(db: Session, user_id: str, page: int, limit: int) -> List[ScheduleDto]:
    """
    Retrieve paginated schedules for a specific user from the database.

    Args:
    -----
    db : Session
        The database session used for querying.
    user_id : str
        The ID of the user whose schedules are to be fetched.
    page : int
        The page number for pagination.
    limit : int
        The number of items per page for pagination.

    Returns:
    --------
    Tuple[List[ScheduleDto], int]
        A tuple containing the paginated list of schedules and the total count of schedules.

    Logs:
    -----
    - DEBUG: Start and completion of fetching schedules for a user.
    - ERROR: Failure during schedule retrieval.
    """
    logger.debug(f"Fetching schedules from the database for user_id: {user_id}, page: {page}, limit: {limit}")
    try:
        total_count = db.query(Schedule).filter(Schedule.user_id == user_id).count()
        schedules = (
            db.query(Schedule)
            .filter(Schedule.user_id == user_id)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        logger.debug(f"Fetched {len(schedules)} schedules for user_id: {user_id}")
        return [ScheduleDto.model_validate(schedule) for schedule in schedules], total_count
    except Exception as e:
        logger.error(f"Failed to fetch schedules for user_id {user_id}: {str(e)}")
        raise Exception("Error occurred while fetching schedules.")


async def get_schedule_by_id(schedule_id: int, db: Session) -> Optional[ScheduleDto]:
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
    Optional[ScheduleDto]
        The schedule mapped to a DTO object if found, otherwise None.

    Logs:
    -----
    - DEBUG: Start and success of fetching the schedule.
    - INFO: The schedule ID being queried.
    - ERROR: Failure to find or retrieve the schedule.
    """
    logger.debug(f"Fetching schedule with ID: {schedule_id}.")
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            logger.debug(f"Schedule found: ID {schedule_id}.")
            logger.info(f"Schedule details: {schedule}.")
            return ScheduleDto.model_validate(schedule)
        logger.debug(f"Schedule not found: ID {schedule_id}.")
        return None
    except Exception as e:
        logger.error(f"Error fetching schedule ID {schedule_id}: {str(e)}")
        raise Exception("Error occurred while fetching schedule details.")


async def create_schedule(schedule: ScheduleDto, db: Session) -> ScheduleDto:
    """
    Create a new schedule and handle associated file transfers.

    Args:
    -----
    schedule : ScheduleDto
        The details of the schedule to create.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    ScheduleDto
        The created schedule mapped to a DTO object.

    Logs:
    -----
    - DEBUG: Start, file transfer steps, and successful completion.
    - INFO: Details of the created schedule.
    - ERROR: Failures during file transfer or database operations.
    """
    logger.debug(f"Creating new schedule for video: {schedule.video_title}.")
    try:
        image_file = base64_to_file(schedule.img)
        image_path = transfer_file(image_file, schedule.video_title)
        
        audio_file = base64_to_file(schedule.audio)
        audio_path = transfer_file(audio_file, schedule.video_title)
        logger.debug("File transfers completed successfully.")

        new_schedule = Schedule(
            upload_date=schedule.upload_date,
            executed=schedule.executed,
            video_title=schedule.video_title,
            image_location=image_path,
            audio_location=audio_path,
            date_created=datetime.now(timezone.utc)
        )
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)
        logger.debug("New schedule added to the database.")
        logger.info(f"Created schedule: {schedule.video_title}.")
        return ScheduleDto.model_validate(new_schedule)
    except Exception as e:
        logger.error(f"Failed to create schedule: {str(e)}")
        raise Exception("Error occurred while creating the schedule.")
    
async def create_schedules_in_batch(schedules: List[ScheduleDto], current_user_id: str, db: Session) -> List[ScheduleDto]:
    """
    Create multiple schedules in a single database transaction.

    Args:
    -----
    schedules : List[ScheduleDto]
        The list of schedule details to create.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    List[ScheduleDto]
        The list of created schedules mapped to DTO objects.

    Logs:
    -----
    - DEBUG: Start and completion of batch schedule creation.
    - INFO: Details of the created schedules.
    - ERROR: Failures during the batch operation.
    """
    logger.debug(f"Starting batch creation for {len(schedules)} schedules.")
    created_schedules = []
    try:
        for schedule in schedules:
            image_file = base64_to_file(schedule.img.file, schedule.video_title + '.' + schedule.img.type)
            image_path = transfer_file(image_file, current_user_id, schedule.video_title)
            
            audio_file = base64_to_file(schedule.audio.file, schedule.video_title + '.' + schedule.audio.type)
            audio_path = transfer_file(audio_file, current_user_id, schedule.video_title)
            logger.debug(f"File transfers completed for {schedule.video_title}.")

            new_schedule = Schedule(
                upload_date=schedule.upload_date,
                executed=schedule.executed,
                video_title=schedule.video_title,
                image_location=image_path,
                audio_location=audio_path,
                date_created=datetime.now(timezone.utc),
                user_id=current_user_id
            )
            db.add(new_schedule)
            created_schedules.append(new_schedule)

        db.commit()
        for schedule in created_schedules:
            db.refresh(schedule)
        logger.debug("Batch creation transaction committed successfully.")
        return [ScheduleDto.model_validate(schedule) for schedule in created_schedules]
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create schedules in batch: {str(e)}")
        raise Exception("Error occurred during batch creation of schedules.")


async def update_schedule(schedule_id: int, schedule: ScheduleDto, db: Session) -> Optional[ScheduleDto]:
    """
    Update an existing schedule and handle updated file transfers.

    Args:
    -----
    schedule_id : int
        The ID of the schedule to update.
    schedule : ScheduleDto
        The updated details of the schedule.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    Optional[ScheduleDto]
        The updated schedule mapped to a DTO object if successful, otherwise None.

    Logs:
    -----
    - DEBUG: Start and success of schedule update.
    - INFO: Details of the updated schedule.
    - ERROR: Failures during file updates or database operations.
    """
    logger.debug(f"Updating schedule with ID: {schedule_id}.")
    try:
        existing_schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not existing_schedule:
            logger.debug(f"Schedule not found: ID {schedule_id}.")
            return None

        # Handle file transfers if necessary
        if schedule.image_location != existing_schedule.image_location:
            image_path = transfer_file(schedule.image_location, f"{schedule.video_title}_image.jpg")
            existing_schedule.image_location = image_path

        if schedule.audio_location != existing_schedule.audio_location:
            audio_path = transfer_file(schedule.audio_location, f"{schedule.video_title}_audio.mp3")
            existing_schedule.audio_location = audio_path

        existing_schedule.upload_date = schedule.upload_date
        existing_schedule.executed = schedule.executed
        existing_schedule.video_title = schedule.video_title

        db.commit()
        db.refresh(existing_schedule)
        logger.debug(f"Schedule ID {schedule_id} updated successfully.")
        logger.info(f"Updated schedule: {existing_schedule.video_title}.")
        return ScheduleDto.model_validate(existing_schedule)
    except Exception as e:
        logger.error(f"Failed to update schedule ID {schedule_id}: {str(e)}")
        raise Exception("Error occurred while updating the schedule.")


async def delete_schedule(schedule_id: int, db: Session) -> bool:
    """
    Delete a schedule from the database.

    Args:
    -----
    schedule_id : int
        The ID of the schedule to delete.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    bool
        True if the schedule was deleted, otherwise False.

    Logs:
    -----
    - DEBUG: Start and success of schedule deletion.
    - ERROR: Failures during schedule deletion.
    """
    logger.debug(f"Deleting schedule with ID: {schedule_id}.")
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            logger.debug(f"Schedule not found for deletion: ID {schedule_id}.")
            return False

        db.delete(schedule)
        db.commit()
        logger.debug(f"Schedule ID {schedule_id} deleted successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to delete schedule ID {schedule_id}: {str(e)}")
        raise Exception("Error occurred while deleting the schedule.")
