import asyncio
import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone
from collections import defaultdict
from app.db.db import get_db_session_context, User
from app.components.tune_ops.tune_ops_repository import get_tunes
from app.components.upload.upload_processing.upload_processing_service import process_and_upload_tunes
from app.logger.logging_setup import logger
from app.settings.env_settings import SCHEDULER_INTERVAL_MINUTES

scheduler = AsyncIOScheduler()

async def scan_and_process_tunes():
    logger.debug("Scheduler Job: Starting scheduled job to scan and process tunes.")
    now = datetime.now(timezone.utc)

    try:
        with get_db_session_context() as db:
            # 1. Fetch all unexecuted tunes across users
            tunes, _ = await get_tunes(
                db,
                user_id=None,
                page=1,
                limit=1000,
                upload_date_before=now,
                executed=False
            )

            if not tunes:
                logger.debug("Scheduler Job: No tunes found to process.")
                return

            logger.debug(f"Scheduler Job: Found {len(tunes)} tunes to process.")

            # 2. Group by user_id
            grouped_tunes = defaultdict(list)
            for tune in tunes:
                grouped_tunes[tune.user_id].append(tune)

            # 3. Define async tasks per user
            async def process_user_group(user_id: str, user_tunes):
                try:
                    user: User = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        logger.warning(f"User not found for user_id={user_id}, skipping {len(user_tunes)} tunes.")
                        return
                    logger.debug(f"Processing {len(user_tunes)} tunes for user {user_id}")
                    await process_and_upload_tunes(user_tunes, user)
                except Exception as e:
                    logger.error(f"Error processing tunes for user_id={user_id}: {e}")
                    logger.debug(traceback.format_exc())

            # 4. Launch all user-grouped tasks concurrently
            await asyncio.gather(*(process_user_group(uid, tunes) for uid, tunes in grouped_tunes.items()))

    except Exception as e:
        logger.error(f"Scheduler Job: Failed during execution: {e}")
        logger.debug(traceback.format_exc())

def start_scheduler():
    logger.debug("Scheduler Job: Starting the scheduler.")
    scheduler.add_job(scan_and_process_tunes, 'interval', minutes=SCHEDULER_INTERVAL_MINUTES)
    scheduler.start()
