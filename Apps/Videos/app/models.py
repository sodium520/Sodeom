from datetime import datetime
from app import db

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    logo = db.Column(db.String(120), nullable=True)  # channel logo filename
    videos = db.relationship('Video', backref='channel', lazy=True)

    def __repr__(self):
        return f'<Channel {self.name}>'

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder = db.Column(db.String(120), unique=True, nullable=False)  # Unique folder for each video
    filename = db.Column(db.String(120), nullable=False)             # Video file name (saved inside the folder)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, nullable=False)
    thumbnail = db.Column(db.String(120), nullable=True)             # Thumbnail file name (saved in the same folder)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    comments = db.relationship('Comment', backref='video', lazy=True)
    likes = db.relationship('Like', backref='video', lazy=True)

    def __repr__(self):
        return f'<Video {self.title}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.id} on Video {self.video_id}>'

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Like {self.id} on Video {self.video_id}>'