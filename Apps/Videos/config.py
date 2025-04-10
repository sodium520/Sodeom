import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Save uploads inside the static folder so they can be directly served.
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max upload size
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}  # Allowed video file types
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Allowed thumbnail types