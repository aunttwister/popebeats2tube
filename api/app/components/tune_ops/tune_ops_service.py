from typing import List, Optional, Tuple
from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session

from app.db.db import Tune
from app.logger.logging_setup import logger

from app.dto import TuneDto

from app.components.tune_ops.tune_ops_repository import (
    delete_tune_by_id,
    get_tune_by_id,
    get_tunes,
    insert_tunes,
    mark_tune_as_executed,
    update_tune
)
from app.components.file_processing.file_processing_service import cleanup_temp_files, persistence_preparation_processing, processing_commit
from app.components.file_processing.file_processing_utils import delete_directory

from app.components.tune_ops.tune_ops_utils import map_tune_dto_to_model

async def create_tunes_service(tunes: List[TuneDto], user_id: str, db: Session) -> List[Tune]:
    db_tunes = []
    temp_paths = []
    file_mappings: List[Tuple[str, str]] = []

    logger.debug(f"Starting batch validation and preparation for {len(tunes)} tunes (user_id={user_id})")

    try:
        for tune in tunes:
            logger.debug(f"Preparing persistence paths for tune: '{tune.video_title}'")
            audio_map, img_map, base_dest_path = persistence_preparation_processing(tune, user_id)

            temp_paths.extend([audio_map[0], img_map[0]])
            file_mappings.extend([audio_map, img_map])

            logger.debug(f"Mapped tune '{tune.video_title}' to DB model with base path: {base_dest_path}")
            db_tunes.append(map_tune_dto_to_model(tune, user_id, base_dest_path=base_dest_path))

        logger.debug(f"Inserting {len(db_tunes)} tunes into the database...")
        created_tunes = await insert_tunes(db_tunes, db)

        logger.debug("Database insert successful. Committing file move operations...")
        processing_commit(file_mappings)

        logger.info(f"Batch upload successfully validated, saved, and processed for user_id={user_id}")
        return created_tunes

    except Exception as e:
        logger.error(f"Batch creation failed: {str(e)}")
        cleanup_temp_files(temp_paths)
        raise


async def get_user_tunes_service(
    user_id: str,
    page: int,
    limit: int,
    db: Session,
    upload_date_before: Optional[datetime] = None,
    executed: Optional[bool] = None
) -> Tuple[List[TuneDto], int]:
    """
    Service layer — returns serialized DTOs for use in FastAPI routes.
    """
    logger.debug(f"Fetching tunes for user: {user_id}, page: {page}, limit: {limit}, executed: {executed}, before: {upload_date_before}")
    
    tunes, total_count = await get_tunes(db, user_id, page, limit, upload_date_before, executed)

    tune_dtos = [
        TuneDto.model_validate({
            **tune.__dict__,
            "tags": json.loads(tune.tags) if tune.tags else [],
        }) for tune in tunes
    ]

    logger.debug(f"Retrieved {len(tune_dtos)} tunes for user_id: {user_id}")
    return tune_dtos, total_count

async def update_tune_service(tune_id: int, tune: TuneDto, db: Session) -> TuneDto:
    if tune.upload_date < datetime.now(timezone.utc):
        raise ValueError("Upload date is in the past")

    existing = await get_tune_by_id(tune_id, db)
    if not existing:
        raise LookupError("Tune not found")

    return await update_tune(tune_id, tune, db)

async def delete_tune_service(tune_id: int, db: Session) -> bool:
    existing = await get_tune_by_id(tune_id, db)
    if not existing:
        raise LookupError("Tune not found")

    if existing.base_dest_path:
        delete_directory(existing.base_dest_path)

    return await delete_tune_by_id(tune_id, db)

async def mark_tune_as_executed_service(tune: Tune, db: Session) -> bool:
    if (await mark_tune_as_executed(tune.id, db) == True):
            logger.debug(f"Marked tune '{tune.video_title}' as executed.")
    else:
        logger.error(f"Failed to mark tune '{tune.video_title}' as executed.")