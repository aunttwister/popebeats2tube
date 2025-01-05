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
import json
from random import Random, random
from typing import List, Optional, Tuple
from sqlalchemy import case
from sqlalchemy.orm import Session
from app.db import Schedule
from app.dto import ScheduleDto
from app.services.file_transfer_service import transfer_files
from app.logging.logging_setup import logger
from app.utils.file_util import base64_to_file, delete_directory



async def get_schedules(db: Session, user_id: str, page: int, limit: int) -> Tuple[List[ScheduleDto], int]:
    """
    Retrieve paginated schedules for a specific user from the database,
    prioritizing unexecuted schedules ordered by soonest upload_date,
    then executed schedules.

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
    """
    logger.debug(f"Fetching schedules from the database for user_id: {user_id}, page: {page}, limit: {limit}")
    try:
        # Fetch total count of schedules for pagination
        total_count = db.query(Schedule).filter(Schedule.user_id == user_id).count()

        # Conditional ordering
        schedules = (
            db.query(Schedule)
            .filter(Schedule.user_id == user_id)
            .order_by(
                case(
                    (Schedule.executed == False, 0), 
                    (Schedule.executed == True, 1)
                ),  # Prioritize unexecuted schedules
                Schedule.upload_date.asc(),  # Order by soonest upload_date within each group
            )
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        logger.debug(f"Fetched {len(schedules)} schedules for user_id: {user_id}")
        return [
            ScheduleDto.model_validate(
                {
                    **schedule.__dict__,
                    "tags": json.loads(schedule.tags) if schedule.tags else [],
                }
            )
            for schedule in schedules
        ], total_count
    except Exception as e:
        logger.error(f"Failed to fetch schedules for user_id {user_id}: {str(e)}")
        raise Exception("Error occurred while fetching schedules.")
    
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
            image_file = base64_to_file(schedule.img_file, schedule.video_title + '.' + schedule.img_type)
            audio_file = base64_to_file(schedule.audio_file, schedule.video_title + '.' + schedule.audio_type)
            
            base_destination_path = transfer_files([image_file, audio_file], current_user_id, schedule.video_title)
            
            logger.debug(f"File transfers completed for {schedule.video_title}.")

            new_schedule = Schedule(
                upload_date=schedule.upload_date,
                executed=schedule.executed,
                video_title=schedule.video_title,
                base_dest_path=base_destination_path,
                img_name=schedule.img_name,
                img_type=schedule.img_type,
                audio_name=schedule.audio_name,
                audio_type=schedule.audio_type,
                date_created=datetime.now(timezone.utc),
                user_id=current_user_id,
                privacy_status=schedule.privacy_status,
                embeddable=schedule.embeddable,
                license=schedule.license,
                category=schedule.category,
                tags=json.dumps(schedule.tags),
                video_description=schedule.video_description
            )
            db.add(new_schedule)
            created_schedules.append(new_schedule)

        db.commit()
        for schedule in created_schedules:
            db.refresh(schedule)
        logger.debug("Batch creation transaction committed successfully.")
        return [
            ScheduleDto.model_validate(
                {
                    **schedule.__dict__,
                    "tags": json.loads(schedule.tags) if schedule.tags else [],
                }
            )
            for schedule in created_schedules
        ]
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create schedules in batch: {str(e)}")
        raise Exception("Error occurred during batch creation of schedules.")


async def update_schedule(schedule_id: int, schedule: ScheduleDto, db: Session) -> Optional[ScheduleDto]:
    """
    Update an existing schedule with new details excluding audio and video fields.

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
    - ERROR: Failures during database operations.
    """
    logger.debug(f"Updating schedule with ID: {schedule_id}.")
    try:
        # Fetch the existing schedule
        existing_schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not existing_schedule:
            logger.debug(f"Schedule not found: ID {schedule_id}.")
            return None

        # Update fields excluding audio and image
        existing_schedule.upload_date = schedule.upload_date
        existing_schedule.executed = schedule.executed
        existing_schedule.video_title = schedule.video_title
        existing_schedule.video_description = schedule.video_description
        existing_schedule.privacy_status = schedule.privacy_status
        existing_schedule.embeddable = schedule.embeddable
        existing_schedule.license = schedule.license
        existing_schedule.category = schedule.category
        existing_schedule.tags = json.dumps(schedule.tags)  # Serialize tags as JSON

        # Commit changes to the database
        db.commit()
        db.refresh(existing_schedule)

        logger.debug(f"Schedule ID {schedule_id} updated successfully.")
        logger.info(f"Updated schedule: {existing_schedule.video_title}.")
        return ScheduleDto.model_validate(
                {
                    **schedule.__dict__
                }
            )

    except Exception as e:
        logger.error(f"Failed to update schedule ID {schedule_id}: {str(e)}")
        db.rollback()  # Rollback in case of failure
        raise Exception("Error occurred while updating the schedule.")



# Function to delete a schedule and its files
async def delete_schedule(schedule_id: int, db: Session) -> bool:
    """
    Delete a schedule from the database and its associated files.

    Args:
    -----
    schedule_id : int
        The ID of the schedule to delete.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    bool
        True if the schedule and its files were deleted, otherwise False.

    Logs:
    -----
    - DEBUG: Start and success of schedule deletion.
    - INFO: Details of the deleted schedule and files.
    - ERROR: Failures during schedule deletion.
    """
    logger.debug(f"Deleting schedule with ID: {schedule_id}.")
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            logger.debug(f"Schedule not found for deletion: ID {schedule_id}.")
            return False

        delete_directory(schedule.base_dest_path)

        db.delete(schedule)
        db.commit()
        logger.debug(f"Schedule ID {schedule_id} deleted successfully.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete schedule ID {schedule_id}: {str(e)}")
        raise Exception("Error occurred while deleting the schedule.")
