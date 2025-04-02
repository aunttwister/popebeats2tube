import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

from app.logger.logging_setup import logger
from app.settings.env_settings import YOUTUBE_ACCESS_SERVICE_NAME, YOUTUBE_ACCESS_SERVICE_VERSION, GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, GOOGLE_OAUTH_TOKEN_URL

def upload_video(access_token, refresh_token, video_file, video_title, description, category, license, embeddable, privacy_status="unlisted", tags=None):
    logger.debug("Initializing YouTube upload...")

    # Create a Credentials object using the access token
    try:
        logger.debug("Creating Credentials object from access token.")
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=GOOGLE_OAUTH_TOKEN_URL,
            client_id=GOOGLE_OAUTH_CLIENT_ID,
            client_secret=GOOGLE_OAUTH_CLIENT_SECRET
        )
    except Exception as e:
        logger.error(f"Failed to create Credentials object: {e}")
        raise

    # Build the YouTube API client
    try:
        logger.debug("Building YouTube API client.")
        youtube = build(
            YOUTUBE_ACCESS_SERVICE_NAME,
            YOUTUBE_ACCESS_SERVICE_VERSION,
            credentials=credentials
        )
    except Exception as e:
        logger.error(f"Failed to build YouTube API client: {e}")
        raise

    # Prepare the request body
    logger.debug("Preparing video upload request body.")
    body = {
        'snippet': {
            'title': video_title,
            'description': description,
            'tags': tags if tags else [],
            'categoryId': category,
            'embeddable': embeddable,
            'license': license
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    # Prepare the media file upload
    try:
        logger.debug(f"Preparing media upload for file: {video_file}")
        media_body = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    except Exception as e:
        logger.error(f"Failed to prepare media upload: {e}")
        raise

    # Start the upload process
    try:
        logger.debug("Sending video upload request to YouTube API.")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media_body
        )

        response = None
        while response is None:
            logger.debug("Waiting for upload to complete...")
            status, response = request.next_chunk()
            if status:
                logger.debug(f"Upload progress: {int(status.progress() * 100)}%")
            if response:
                logger.info(f"Video uploaded successfully. Video ID: {response['id']}")
    except HttpError as e:
        logger.error(f"An error occurred during YouTube upload: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during YouTube upload: {e}")
        raise