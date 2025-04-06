from datetime import datetime, timezone
import json
import os
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.db import Tune
from app.dto import TuneDto
from app.repositories.schedule_tune_repository import (
    delete_tune_by_id,
    get_tune_by_id,
    get_tunes,
    insert_scheduled_tunes_batch,
    mark_tune_as_executed,
    update_tune_fields
)
from app.logger.logging_setup import logger
from app.services.file_processing_service import cleanup_temp_files, persistence_preparation_processing, processing_commit
from app.utils.file_util import delete_directory


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


async def validate_and_create_scheduled_batch_service(tunes: List[TuneDto], user_id: str, db: Session) -> List[Tune]:
    current_time = datetime.now(timezone.utc)
    db_tunes = []
    temp_paths = []
    file_mappings: List[Tuple[str, str]] = []

    logger.debug(f"Starting batch validation and preparation for {len(tunes)} tunes (user_id={user_id})")

    try:
        for tune in tunes:
            logger.debug(f"Validating tune: '{tune.video_title}'")

            if not tune.upload_date:
                raise ValueError(f"Upload date is missing for '{tune.video_title}'")
            if tune.upload_date < current_time:
                raise ValueError(f"Upload date is in the past for '{tune.video_title}'")

            logger.debug(f"Preparing persistence paths for tune: '{tune.video_title}'")
            audio_map, img_map, base_dest_path = persistence_preparation_processing(tune, user_id)

            temp_paths.extend([audio_map[0], img_map[0]])
            file_mappings.extend([audio_map, img_map])

            logger.debug(f"Mapped tune '{tune.video_title}' to DB model with base path: {base_dest_path}")
            db_tunes.append(map_tune_dto_to_model(tune, user_id, base_dest_path=base_dest_path))

        logger.debug(f"Inserting {len(db_tunes)} tunes into the database...")
        created_tunes = await insert_scheduled_tunes_batch(db_tunes, db)

        logger.debug("Database insert successful. Committing file move operations...")
        processing_commit(file_mappings)

        logger.info(f"Batch upload successfully validated, saved, and processed for user_id={user_id}")
        return created_tunes

    except Exception as e:
        logger.error(f"Batch creation failed: {str(e)}")
        cleanup_temp_files(temp_paths)
        raise

def map_tune_dto_to_model(tune: TuneDto, user_id: str, base_dest_path: str) -> Tune:
    return Tune(
        upload_date=tune.upload_date,
        executed=tune.executed,
        video_title=tune.video_title,
        base_dest_path=base_dest_path,
        img_name=tune.img_name,
        img_type=tune.img_type,
        audio_name=tune.audio_name,
        audio_type=tune.audio_type,
        date_created=datetime.now(timezone.utc),
        user_id=user_id,
        privacy_status=tune.privacy_status,
        embeddable=tune.embeddable,
        license=tune.license,
        category=tune.category,
        tags=json.dumps(tune.tags),
        video_description=tune.video_description,
    )



async def validate_and_update_tune_service(tune_id: int, tune: TuneDto, db: Session) -> TuneDto:
    if tune.upload_date < datetime.now(timezone.utc):
        raise ValueError("Upload date is in the past")

    existing = await get_tune_by_id(tune_id, db)
    if not existing:
        raise LookupError("Tune not found")

    return await update_tune_fields(tune_id, tune, db)


async def delete_user_tune_service(tune_id: int, db: Session) -> bool:
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
