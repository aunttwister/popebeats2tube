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
        raise Exception("Error occurred while fetching tunes.")
    
    
async def get_tune_by_id(tune_id: int, db: Session) -> Optional[Tune]:
    return db.query(Tune).filter(Tune.id == tune_id).first()


async def insert_tunes_batch(tunes: List[Tune], db: Session) -> List[TuneDto]:
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
    created_tunes = []
    try:
        db.add_all(tunes)
        db.commit()

        created_tunes = tunes
        for tune in created_tunes:
            db.refresh(tune)
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
        raise Exception(f"Error occurred during batch creation of tunes: {str(e)}")


async def delete_tune_by_id(tune_id: int, db: Session) -> bool:
    tune = db.query(Tune).filter(Tune.id == tune_id).first()
    if not tune:
        return False

    db.delete(tune)
    db.commit()
    return True

async def update_tune_fields(tune_id: int, tune: TuneDto, db: Session) -> Optional[TuneDto]:
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
    tune_obj = await get_tune_by_id(tune_id, db)
    if not tune_obj:
        return None

    tune_obj.upload_date = tune.upload_date
    tune_obj.executed = tune.executed
    tune_obj.video_title = tune.video_title
    tune_obj.video_description = tune.video_description
    tune_obj.privacy_status = tune.privacy_status
    tune_obj.embeddable = tune.embeddable
    tune_obj.license = tune.license
    tune_obj.category = tune.category
    tune_obj.tags = json.dumps(tune.tags)

    db.commit()
    db.refresh(tune_obj)

    return TuneDto.model_validate({
        **tune_obj.__dict__,
        "tags": json.loads(tune_obj.tags) if tune_obj.tags else [],
    })

