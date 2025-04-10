import uuid
import os
from datetime import datetime
from flask import (Blueprint, request, render_template, redirect, url_for, 
                   flash, send_from_directory, current_app)
from app import db
from app.models import Video, Channel, Comment, Like
from app.video_uploads import save_video, save_thumbnail, save_logo

main = Blueprint('main', __name__)

@main.route('/')
def index():
    videos = Video.query.order_by(Video.upload_date.desc()).all()
    return render_template('index.html', videos=videos)

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    channels = Channel.query.order_by(Channel.name).all()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Missing video file')
            return redirect(request.url)
        
        video_file = request.files['file']
        thumbnail_file = request.files.get('thumbnail')
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        channel_id = request.form.get('channel_id')

        if not channel_id:
            flash('Please select a channel')
            return redirect(request.url)

        channel = Channel.query.get(channel_id)
        if not channel:
            flash('Selected channel not found')
            return redirect(request.url)

        if video_file.filename == '':
            flash('No video file selected')
            return redirect(request.url)
        
        unique_folder = str(uuid.uuid4())
        video_filename = save_video(video_file, unique_folder)
        if not video_filename:
            flash('Video file type not allowed')
            return redirect(request.url)

        thumbnail_filename = None
        if thumbnail_file and thumbnail_file.filename:
            thumbnail_filename = save_thumbnail(thumbnail_file, unique_folder)

        video = Video(
            folder=unique_folder,
            filename=video_filename,
            title=title,
            description=description,
            upload_date=datetime.utcnow(),
            thumbnail=thumbnail_filename,
            channel_id=channel.id
        )
        db.session.add(video)
        db.session.commit()

        flash('Video uploaded successfully')
        return redirect(url_for('main.index'))
    
    return render_template('upload.html', channels=channels)

@main.route('/play/<int:video_id>')
def play_video(video_id):
    video = Video.query.get_or_404(video_id)
    up_next_videos = Video.query.filter(Video.id != video_id).order_by(Video.upload_date.desc()).limit(5).all()
    comments = Comment.query.filter_by(video_id=video.id).order_by(Comment.created_at.desc()).all()
    like_count = Like.query.filter_by(video_id=video.id).count()
    return render_template('play.html', video=video, up_next_videos=up_next_videos, comments=comments, like_count=like_count)

@main.route('/like/<int:video_id>', methods=['POST'])
def like_video(video_id):
    video = Video.query.get_or_404(video_id)
    new_like = Like(video_id=video.id)
    db.session.add(new_like)
    db.session.commit()
    flash('You liked the video.')
    return redirect(url_for('main.play_video', video_id=video.id))

@main.route('/comment/<int:video_id>', methods=['POST'])
def comment_video(video_id):
    video = Video.query.get_or_404(video_id)
    content = request.form.get('content')
    if not content:
        flash('Comment cannot be empty.')
        return redirect(url_for('main.play_video', video_id=video.id))
    new_comment = Comment(video_id=video.id, content=content)
    db.session.add(new_comment)
    db.session.commit()
    flash('Comment added.')
    return redirect(url_for('main.play_video', video_id=video.id))

@main.route('/create_channel', methods=['GET', 'POST'])
def create_channel():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        logo_file = request.files.get('logo')
        if not name:
            flash('Channel name is required')
            return redirect(request.url)
        existing = Channel.query.filter_by(name=name).first()
        if existing:
            flash('Channel with this name already exists')
            return redirect(request.url)
        logo_filename = None
        if logo_file and logo_file.filename:
            logo_filename = save_logo(logo_file)
        channel = Channel(name=name, description=description, logo=logo_filename)
        db.session.add(channel)
        db.session.commit()
        flash('Channel created successfully')
        return redirect(url_for('main.index'))
    return render_template('create_channel.html')

@main.route('/media/<folder>/<filename>')
def media(folder, filename):
    base_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(os.path.join(base_folder, folder), filename)

@main.route('/channel_media/<filename>')
def channel_media(filename):
    base_folder = current_app.config['UPLOAD_FOLDER']
    logos_folder = os.path.join(base_folder, 'channel_logos')
    return send_from_directory(logos_folder, filename)