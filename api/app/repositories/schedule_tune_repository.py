"""
Repository Layer: tune Management
======================================
This module provides functions for interacting with the database for CRUD operations on tunes.

Responsibilities:
-----------------
- Retrieve all tunes from the database.
- Retrieve a specific tune by ID.
- Create a new tune, including file transfers.
- Update an existing tune, handling updated files.
- Delete a tune.

Logging:
--------
- DEBUG: Logs the start, intermediate steps, and success of operations.
- INFO: Includes sensitive details like tune metadata.
- ERROR: Logs meaningful error descriptions without exposing sensitive information.

Functions:
----------
- get_tunes: Retrieve all tunes from the database.
- get_tune_by_id: Retrieve a specific tune by its ID.
- create_tune: Create a new tune and handle associated file transfers.
- update_tune: Update an existing tune, including file updates.
- delete_tune: Delete a tune from the database.
"""

from datetime import datetime, timezone
import json
from typing import List, Optional, Tuple
from sqlalchemy import case
from sqlalchemy.orm import Session
from app.db.db import Tune
from app.dto import TuneDto
from app.services.file_transfer_service import transfer_files
from app.logging.logging_setup import logger
from app.utils.file_util import base64_to_file, delete_directory



async def get_tunes(db: Session, user_id: str, page: int, limit: int) -> Tuple[List[TuneDto], int]:
    """
    Retrieve paginated tunes for a specific user from the database,
    prioritizing unexecuted tunes ordered by soonest upload_date,
    then executed tunes.

    Args:
    -----
    db : Session
        The database session used for querying.
    user_id : str
        The ID of the user whose tunes are to be fetched.
    page : int
        The page number for pagination.
    limit : int
        The number of items per page for pagination.

    Returns:
    --------
    Tuple[List[TuneDto], int]
        A tuple containing the paginated list of tunes and the total count of tunes.
    """
    logger.debug(f"Fetching tunes from the database for user_id: {user_id}, page: {page}, limit: {limit}")
    try:
        # Fetch total count of tunes for pagination
        total_count = db.query(Tune).filter(Tune.user_id == user_id).count()

        # Conditional ordering
        tunes = (
            db.query(Tune)
            .filter(Tune.user_id == user_id)
            .order_by(
                case(
                    (Tune.executed == False, 0), 
                    (Tune.executed == True, 1)
                ),  # Prioritize unexecuted tunes
                Tune.upload_date.asc(),  # Order by soonest upload_date within each group
            )
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        logger.debug(f"Fetched {len(tunes)} tunes for user_id: {user_id}")
        return [
            TuneDto.model_validate(
                {
                    **tune.__dict__,
                    "tags": json.loads(tune.tags) if tune.tags else [],
                }
            )
            for tune in tunes
        ], total_count
    except Exception as e:
        logger.error(f"Failed to fetch tunes for user_id {user_id}: {str(e)}")
        raise Exception("Error occurred while fetching tunes.")
    
async def create_tunes_in_batch(tunes: List[TuneDto], current_user_id: str, db: Session) -> List[TuneDto]:
    """
    Create multiple tunes in a single database transaction.

    Args:
    -----
    tunes : List[TuneDto]
        The list of tune details to create.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    List[TuneDto]
        The list of created tunes mapped to DTO objects.

    Logs:
    -----
    - DEBUG: Start and completion of batch tune creation.
    - INFO: Details of the created tunes.
    - ERROR: Failures during the batch operation.
    """
    logger.debug(f"Starting batch creation for {len(tunes)} tunes.")
    created_tunes = []
    try:
        for tune in tunes:
            image_file = base64_to_file(tune.img_file_base64, tune.video_title + '.' + tune.img_type)
            audio_file = base64_to_file(tune.img_file_base64, tune.video_title + '.' + tune.audio_type)
            
            base_destination_path = transfer_files([image_file, audio_file], current_user_id, tune.video_title)
            
            logger.debug(f"File transfers completed for {tune.video_title}.")

            new_tune = Tune(
                upload_date=tune.upload_date,
                executed=tune.executed,
                video_title=tune.video_title,
                base_dest_path=base_destination_path,
                img_name=tune.img_name,
                img_type=tune.img_type,
                audio_name=tune.audio_name,
                audio_type=tune.audio_type,
                date_created=datetime.now(timezone.utc),
                user_id=current_user_id,
                privacy_status=tune.privacy_status,
                embeddable=tune.embeddable,
                license=tune.license,
                category=tune.category,
                tags=json.dumps(tune.tags),
                video_description=tune.video_description
            )
            db.add(new_tune)
            created_tunes.append(new_tune)

        db.commit()
        for tune in created_tunes:
            db.refresh(tune)
        logger.debug("Batch creation transaction committed successfully.")
        return [
            TuneDto.model_validate(
                {
                    **tune.__dict__,
                    "tags": json.loads(tune.tags) if tune.tags else [],
                }
            )
            for tune in created_tunes
        ]
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create tunes in batch: {str(e)}")
        raise Exception("Error occurred during batch creation of tunes.")


async def update_tune(tune_id: int, tune: TuneDto, db: Session) -> Optional[TuneDto]:
    """
    Update an existing tune with new details excluding audio and video fields.

    Args:
    -----
    tune_id : int
        The ID of the tune to update.
    tune : TuneDto
        The updated details of the tune.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    Optional[TuneDto]
        The updated tune mapped to a DTO object if successful, otherwise None.

    Logs:
    -----
    - DEBUG: Start and success of tune update.
    - INFO: Details of the updated tune.
    - ERROR: Failures during database operations.
    """
    logger.debug(f"Updating tune with ID: {tune_id}.")
    try:
        # Fetch the existing tune
        existing_tune = db.query(Tune).filter(tune.id == tune_id).first()
        if not existing_tune:
            logger.debug(f"tune not found: ID {tune_id}.")
            return None

        # Update fields excluding audio and image
        existing_tune.upload_date = tune.upload_date
        existing_tune.executed = tune.executed
        existing_tune.video_title = tune.video_title
        existing_tune.video_description = tune.video_description
        existing_tune.privacy_status = tune.privacy_status
        existing_tune.embeddable = tune.embeddable
        existing_tune.license = tune.license
        existing_tune.category = tune.category
        existing_tune.tags = json.dumps(tune.tags)  # Serialize tags as JSON

        # Commit changes to the database
        db.commit()
        db.refresh(existing_tune)

        logger.debug(f"tune ID {tune_id} updated successfully.")
        logger.info(f"Updated tune: {existing_tune.video_title}.")
        return TuneDto.model_validate(
                {
                    **tune.__dict__
                }
            )

    except Exception as e:
        logger.error(f"Failed to update tune ID {tune_id}: {str(e)}")
        db.rollback()  # Rollback in case of failure
        raise Exception("Error occurred while updating the tune.")



# Function to delete a tune and its files
async def delete_tune(tune_id: int, db: Session) -> bool:
    """
    Delete a tune from the database and its associated files.

    Args:
    -----
    tune_id : int
        The ID of the tune to delete.
    db : Session
        The database session used for the operation.

    Returns:
    --------
    bool
        True if the tune and its files were deleted, otherwise False.

    Logs:
    -----
    - DEBUG: Start and success of tune deletion.
    - INFO: Details of the deleted tune and files.
    - ERROR: Failures during tune deletion.
    """
    logger.debug(f"Deleting tune with ID: {tune_id}.")
    try:
        tune = db.query(Tune).filter(Tune.id == tune_id).first()
        if not tune:
            logger.debug(f"Tune not found for deletion: ID {tune_id}.")
            return False

        delete_directory(tune.base_dest_path)

        db.delete(tune)
        db.commit()
        logger.debug(f"tune ID {tune_id} deleted successfully.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete tune ID {tune_id}: {str(e)}")
        raise Exception("Error occurred while deleting the tune.")
