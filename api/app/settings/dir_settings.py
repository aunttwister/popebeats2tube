"""
Settings for the application.

Defines the paths for the base directory, log directory, and upload directories (including subdirectories for audio and image files).
Ensures the necessary directories exist, creating them if necessary.
"""
import os

# Define the base directory for the application
BASE_DIR = os.path.dirname(os.path.abspath("C:/Users/pavle/Documents/Hobby/MyProjects/Soundframe/backend/mock-host/"))

# Define the directories for logs and uploads
LOG_DIR = os.path.join(BASE_DIR, 'logs')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# Define subdirectories for audio and image files
AUDIO_DIR = os.path.join(UPLOAD_DIR, 'audio')
IMAGE_DIR = os.path.join(UPLOAD_DIR, 'images')

# Create the directories if they do not exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)