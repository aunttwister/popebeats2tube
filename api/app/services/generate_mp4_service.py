from datetime import datetime, timedelta
import os
import re
import subprocess
from app.logging.logging_setup import logger

from app.services.config_mgmt_service import load_config

# Load configuration
config = load_config()

# Extract FFmpeg and FFprobe paths from configuration
FFMPEG_PATH = config.get("ffmpeg", {}).get("path", "ffmpeg")
FFPROBE_PATH = config.get("ffmpeg", {}).get("probe_path", "ffprobe")

def generate_video(audio_path, image_path, output_path, video_title) -> str:
    """
    Generates a video using FFmpeg by combining an audio file and an image.
    """
    logger.debug(f"Generating video for title: {video_title}.")

    # Probe audio file for duration
    logger.debug(f"Probing audio file using FFmpeg.")
    probe_cmd = [FFPROBE_PATH, '-i', audio_path, '-show_format', '-v', 'quiet']
    print(probe_cmd)
    try:
        probe_output = subprocess.check_output(probe_cmd, stderr=subprocess.STDOUT)
        logger.info(f"FFProbe output for audio file '{audio_path}': {probe_output.decode()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error probing audio file '{audio_path}': {e.output.decode()}")
        raise

    # Extract duration
    duration_match = re.search(r"duration=([\d\.]+)", probe_output.decode())
    if not duration_match:
        logger.error(f"Could not determine the duration of the audio file '{audio_path}'.")
        raise ValueError("Invalid audio file duration.")

    # Extract duration in seconds
    duration_seconds = float(duration_match.group(1))
    logger.info(f"Extracted audio file duration: {duration_seconds} seconds")

    delta = timedelta(seconds=duration_seconds)

    # Construct FFmpeg command
    ffmpeg_cmd = [
        FFMPEG_PATH,
        '-loop', '1',
        '-framerate', '1',
        '-i', image_path,
        '-i', audio_path,
        '-vf', 'scale=ceil(iw/2)*2:ceil(ih/2)*2',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-t', str(delta.total_seconds()),
        '-preset', 'ultrafast',
        '-qp', '0',
        '-f', 'mp4',
        output_path
    ]
    logger.debug(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

    # Run FFmpeg
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        logger.info(f"Video successfully generated at: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed to generate video: {e.output.decode()}")
        raise
