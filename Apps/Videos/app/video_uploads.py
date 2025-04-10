import os
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_video(file, folder):
    if file and allowed_file(file.filename, current_app.config.get('ALLOWED_EXTENSIONS', set())):
        filename = secure_filename(file.filename)
        base_folder = current_app.config.get('UPLOAD_FOLDER')
        video_folder = os.path.join(base_folder, folder)
        if not os.path.exists(video_folder):
            os.makedirs(video_folder)
        file_path = os.path.join(video_folder, filename)
        file.save(file_path)
        return filename
    return None

def save_thumbnail(file, folder):
    if file and allowed_file(file.filename, current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())):
        filename = secure_filename(file.filename)
        base_folder = current_app.config.get('UPLOAD_FOLDER')
        video_folder = os.path.join(base_folder, folder)
        if not os.path.exists(video_folder):
            os.makedirs(video_folder)
        file_path = os.path.join(video_folder, filename)
        file.save(file_path)
        return filename
    return None

def save_logo(file):
    """
    Save an uploaded channel logo image in a dedicated 'channel_logos' folder.
    Returns just the secure filename if successful, or None if the file type is not allowed.
    """
    if file and allowed_file(file.filename, current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())):
        filename = secure_filename(file.filename)
        base_folder = current_app.config.get('UPLOAD_FOLDER')
        logos_folder = os.path.join(base_folder, 'channel_logos')
        if not os.path.exists(logos_folder):
            os.makedirs(logos_folder)
        file_path = os.path.join(logos_folder, filename)
        file.save(file_path)
        # Return just the filename (e.g., "mylogo.png")
        return filename
    return None