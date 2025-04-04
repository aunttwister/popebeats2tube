from datetime import timedelta
import os
import re
import subprocess
from app.logger.logging_setup import logger
from app.services.file_processing_service import get_mp4_path
from app.settings.env_settings import FFMPEG_PATH, FFMPEG_PROBE_PATH


def probe_audio_duration(audio_path: str) -> float:
    """
    Uses ffprobe to extract the duration of the audio file.
    """
    logger.debug(f"Probing audio file: {audio_path}")
    probe_cmd = [FFMPEG_PROBE_PATH, '-i', audio_path, '-show_format', '-v', 'quiet']

    try:
        probe_output = subprocess.check_output(probe_cmd, stderr=subprocess.STDOUT)
        logger.info(f"FFProbe output for audio file '{audio_path}': {probe_output.decode()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error probing audio file '{audio_path}': {e.output.decode()}")
        raise RuntimeError(f"Failed to probe audio file: {audio_path}")

    return extract_duration_from_probe_output(probe_output.decode())


def extract_duration_from_probe_output(probe_output: str) -> float:
    """
    Extracts duration from the ffprobe output.
    """
    duration_match = re.search(r"duration=([\d\.]+)", probe_output)
    if not duration_match:
        logger.error("Could not determine audio file duration from ffprobe output.")
        raise ValueError("Invalid audio file duration.")
    duration = float(duration_match.group(1))
    logger.debug(f"Extracted duration: {duration} seconds")
    return duration


def build_ffmpeg_command(audio_path: str, image_path: str, mp4_path: str, duration_seconds: float) -> list:
    """
    Constructs the ffmpeg command for generating a video.
    """
    return [
        FFMPEG_PATH,
        '-loop', '1',
        '-framerate', '1',
        '-i', image_path,
        '-i', audio_path,
        '-vf', 'scale=ceil(iw/2)*2:ceil(ih/2)*2',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-t', str(duration_seconds),
        '-preset', 'ultrafast',
        '-qp', '0',
        '-f', 'mp4',
        mp4_path
    ]


def generate_video(audio_path: str, image_path: str, output_path: str, video_title: str) -> str:
    """
    Generates a video using FFmpeg by combining an audio file and an image.
    """
    
    mp4_path = get_mp4_path(output_path, video_title)
    logger.debug(f"Generating video for title: {video_title}.")

    duration_seconds = probe_audio_duration(audio_path)
    logger.info(f"Audio duration: {duration_seconds} seconds")

    ffmpeg_cmd = build_ffmpeg_command(audio_path, image_path, mp4_path, duration_seconds)
    logger.debug(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        logger.info(f"Video successfully generated at: {mp4_path}")
        return mp4_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed to generate video: {e.output.decode()}")
        raise RuntimeError("Video generation failed.") from e
