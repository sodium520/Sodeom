import os
import subprocess
from flask import current_app

def generate_thumbnail(video_path):
    """
    Generate a thumbnail from a video using FFmpeg.
    Extracts a frame at 1 second into the video.
    """
    thumbnail_path = video_path.rsplit('.', 1)[0] + '_thumb.jpg'
    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', '00:00:01.000',
        '-vframes', '1',
        thumbnail_path
    ]
    try:
        subprocess.run(command, check=True)
        return thumbnail_path
    except Exception as e:
        current_app.logger.error(f"Failed to generate thumbnail: {e}")
        return None