from datetime import datetime, timedelta, timezone
from requests import Session

from app.db.db import User
from app.dto import TuneDto
from app.logger.logging_setup import logger
from app.repositories.user_mgmt_repository import persist_credentials
from app.services.file_transfer_service import transfer_files
from app.services.generate_mp4_service import generate_video
from app.services.google_oauth_service import refresh_google_access_token
from app.services.tune2tube_service import upload_video
from app.utils.file_util import base64_to_file


async def validate_and_refresh_token(user: User, db: Session):
    """
    Validates the user's access token and refreshes it if expired.
    """
    logger.debug("Starting token validation.")
    if datetime.now(timezone.utc) >= user.youtube_token_expiry:
        logger.debug("Access token expired. Refreshing token...")
        try:
            token_response = await refresh_google_access_token(user.youtube_refresh_token)
            new_access_token = token_response['access_token']
            
            new_refresh_token = token_response.get("refresh_token")
            if new_refresh_token is None:
                new_refresh_token = user.youtube_refresh_token
            
            new_token_expiry = datetime.now(timezone.utc) + timedelta(seconds=token_response['expires_in'])
            persist_credentials(
                user_id=user.id,
                youtube_access_token=new_access_token,
                youtube_refresh_token=new_refresh_token,
                youtube_token_expiry=new_token_expiry,
                db=db
            )
            logger.info("Access token refreshed and persisted successfully.")
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise

async def process_and_upload_tune(tune: TuneDto, user: User):
    """
    Handles the process of generating a video and uploading it to YouTube.
    """
    logger.debug(f"Started processing tune: {tune.video_title} for user: {user.id}")
    
    try:     
        audio_file = base64_to_file(tune.audio_file_base64, tune.audio_name)
        img_file = base64_to_file(tune.img_file_base64, tune.img_name)
        
        destination_path = transfer_files([audio_file, img_file], user.id, tune.video_title)
        destination_path = destination_path.replace("\\", "/")

        img_path = destination_path + '/' + tune.img_name
        audio_path = destination_path + '/' + tune.audio_name
        video_output_path = destination_path + '/' + tune.video_title + '.' + 'mp4'
        
        # Generate video
        logger.debug(f"Starting video generation for title: {tune.video_title}")
        mp4_output_path = generate_video(audio_path, img_path, video_output_path, tune.video_title)
        logger.info(f"Video generation completed: {mp4_output_path}")

        # Upload to YouTube
        logger.debug(f"Initiating YouTube upload for video: {mp4_output_path}")
        upload_video(
            access_token=user.youtube_access_token,
            refresh_token=user.youtube_refresh_token,
            video_file=mp4_output_path,
            video_title=tune.video_title,
            description=tune.video_description,
            category=tune.category,
            license=tune.license,
            embeddable=tune.embeddable,
            privacy_status=tune.privacy_status,
            tags=tune.tags
        )
        logger.info(f"Successfully uploaded video '{tune.video_title}' to YouTube.")
    except Exception as e:
        logger.error(f"Failed to process and upload tune '{tune.video_title}': {str(e)}")
        raise
