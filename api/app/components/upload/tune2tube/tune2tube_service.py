from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from app.logger.logging_setup import logger
from app.settings.env_settings import (
    YOUTUBE_ACCESS_SERVICE_NAME,
    YOUTUBE_ACCESS_SERVICE_VERSION,
    GOOGLE_OAUTH_CLIENT_ID,
    GOOGLE_OAUTH_CLIENT_SECRET,
    GOOGLE_OAUTH_TOKEN_URL
)

def upload_video(
    access_token: str,
    refresh_token: str,
    video_file: str,
    video_title: str,
    description: str,
    category: str,
    license: str,
    embeddable: bool,
    privacy_status: str = "unlisted",
    tags: list[str] = None
):
    logger.debug("Initializing YouTube upload")

    credentials = _get_credentials(access_token, refresh_token)
    youtube = _get_youtube_client(credentials)
    media_body = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    body = {
        "snippet": {
            "title": video_title,
            "description": description,
            "tags": tags or [],
            "categoryId": category,
            "embeddable": embeddable,
            "license": license
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    try:
        logger.debug("Sending upload request to YouTube")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media_body)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.debug(f"Upload progress: {int(status.progress() * 100)}%")
        logger.info(f"Video uploaded successfully. Video ID: {response['id']}")
    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected upload error: {e}")
        raise

def _get_credentials(token, refresh_token):
    try:
        return Credentials(
            token=token,
            refresh_token=refresh_token,
            token_uri=GOOGLE_OAUTH_TOKEN_URL,
            client_id=GOOGLE_OAUTH_CLIENT_ID,
            client_secret=GOOGLE_OAUTH_CLIENT_SECRET
        )
    except Exception as e:
        logger.error(f"Failed to create credentials: {e}")
        raise

def _get_youtube_client(credentials):
    try:
        return build(YOUTUBE_ACCESS_SERVICE_NAME, YOUTUBE_ACCESS_SERVICE_VERSION, credentials=credentials)
    except Exception as e:
        logger.error(f"Failed to initialize YouTube client: {e}")
        raise
