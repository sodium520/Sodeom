from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'y7788HUHGG657BYHBHBHyy&ghy&G3474rg347ygrhasujkawbv34ygwiwefc9w3zsjdyun'  # Replace with a strong secret key

# Database configuration.
# Uses the environment variable DATABASE_URL if available (e.g. for PostgreSQL),
# otherwise falls back to an SQLite database file (app.db).
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ------------------------------
# Database Models
# ------------------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # One-to-many: a user can receive many messages.
    messages_received = db.relationship('Message', backref='recipient_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(120), nullable=False)      # Sender's email
    recipient = db.Column(db.String(120), nullable=False)   # Recipient's email
    subject = db.Column(db.String(256), nullable=True)      # Optional subject
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # If the recipient is registered, store their user id.
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------------------
# Routes
# ------------------------------

@app.route('/messages')
def messages():
    return render_template('messages.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('register'))
        # Check if user already exists.
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('User already exists', 'warning')
            return redirect(url_for('register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('account_inbox'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'success')
    return redirect(url_for('messages'))

@app.route('/send', methods=['GET', 'POST'])
@login_required
def send_message():
    if request.method=='POST':
        sender = current_user.email
        recipient_email = request.form.get('recipient')
        subject = request.form.get('subject')
        body = request.form.get('message')
        if not recipient_email or not body:
            flash('Recipient and message body are required', 'danger')
            return redirect(url_for('send_message'))
        # Check if recipient exists.
        recipient_user = User.query.filter_by(email=recipient_email).first()
        if not recipient_user:
            flash('Recipient not found. Please enter a valid registered email.', 'danger')
            return redirect(url_for('send_message'))
        new_message = Message(sender=sender, recipient=recipient_email,
                              subject=subject, body=body, recipient_id=recipient_user.id)
        db.session.add(new_message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('account_sent'))
    return render_template('send.html')

@app.route('/account/inbox')
@login_required
def account_inbox():
    # Retrieve messages where current user is the recipient.
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('account_inbox.html', messages=messages)

@app.route('/account/sent')
@login_required
def account_sent():
    # Retrieve messages where current user is the sender.
    messages = Message.query.filter_by(sender=current_user.email).order_by(Message.timestamp.desc()).all()
    return render_template('account_sent.html', messages=messages)

@app.route('/message/<int:message_id>')
@login_required
def view_message(message_id):
    msg = Message.query.get_or_404(message_id)
    # Only allow viewing if the current user is the sender or recipient.
    if msg.recipient_id != current_user.id and msg.sender != current_user.email:
        flash("Access denied", "danger")
        return redirect(url_for('account_inbox'))
    return render_template('message.html', message=msg)

@app.route('/reply/<int:message_id>', methods=['GET', 'POST'])
@login_required
def reply_message(message_id):
    original_msg = Message.query.get_or_404(message_id)
    if request.method == 'POST':
        reply_body = request.form.get('message')
        if not reply_body:
            flash("Reply message cannot be empty", "danger")
            return redirect(url_for('reply_message', message_id=message_id))
        # Prepend "Re: " to the subject if not already present.
        subject = original_msg.subject if original_msg.subject else ""
        if subject and not subject.lower().startswith("re:"):
            subject = "Re: " + subject
        sender = current_user.email
        recipient_email = original_msg.sender  # Reply to original sender.
        recipient_user = User.query.filter_by(email=recipient_email).first()
        new_reply = Message(sender=sender, recipient=recipient_email,
                            subject=subject, body=reply_body,
                            recipient_id=recipient_user.id if recipient_user else None)
        db.session.add(new_reply)
        db.session.commit()
        flash('Reply sent successfully!', 'success')
        return redirect(url_for('account_sent'))
    return render_template('reply.html', original_msg=original_msg)

# ------------------------------
# Auto Create Database Tables
# ------------------------------

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)