from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from emailsender import send_email

app = Flask(__name__)
# Use a strong secret key
app.secret_key = 'y7788HUHGG657BYHBHBHyy&ghy&G3474rg347ygrhasujkawbv34ygwiwefc9w3zsjdyun'

# Database configuration.
# Uses the environment variable DATABASE_URL if available (for PostgreSQL),
# otherwise falls back to an SQLite database file (app.db).
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Domain for generated email addresses.
EMAIL_DOMAIN = "sodeom.com"

# ------------------------------
# Database Models
# ------------------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # Generated email will be unique and created from the username.
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # One-to-many: a user can receive many emails.
    messages_received = db.relationship('Message', backref='recipient_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(120), nullable=False)      # Sender's email
    recipient = db.Column(db.String(120), nullable=False)     # Recipient's email
    subject = db.Column(db.String(256), nullable=True)        # Optional subject
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

@app.route('/')
def home():
    if current_user.is_authenticated:
        # Retrieve emails where the current user is the recipient.
        messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
        return render_template('account_inbox.html', messages=messages)
    else:
        return render_template('messages.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('register'))
        # Check if username already exists.
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'warning')
            return redirect(url_for('register'))
        # Automatically generate an email address.
        generated_email = f"{username.lower()}@{EMAIL_DOMAIN}"
        user = User(username=username, email=generated_email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'Registration successful. Your email address is: {generated_email}', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', EMAIL_DOMAIN=EMAIL_DOMAIN)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Login now uses username instead of email.
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Logged in successfully. Your email: {user.email}', 'success')
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
    return redirect(url_for('home'))

from flask import jsonify

# Replace with a better method (like API keys in headers or OAuth) in production
API_KEY = os.environ.get("EMAIL_API_KEY", "supersecretapikey123")

@app.route('/api/send', methods=['POST'])
def api_send_email():
    data = request.get_json()
    
    # Basic API key check
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    sender = data.get('sender')
    recipient_email = data.get('recipient')
    subject = data.get('subject', '')
    body = data.get('body')

    if not sender or not recipient_email or not body:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Check if recipient is an internal user
        recipient_user = User.query.filter_by(email=recipient_email).first()
        new_msg = Message(
            sender=sender,
            recipient=recipient_email,
            subject=subject,
            body=body,
            recipient_id=recipient_user.id if recipient_user else None
        )
        db.session.add(new_msg)
        db.session.commit()

        # External email delivery (optional)
        if not recipient_user:
            send_email(sender, recipient_email, recipient_email, subject, body)

        return jsonify({"success": True, "message": "Email sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send', methods=['GET', 'POST'])
@login_required
def send_message():
    if request.method == 'POST':
        sender = current_user.email
        recipient_email = request.form.get('recipient')
        subject = request.form.get('subject')
        body = request.form.get('message')

        if not recipient_email or not body:
            flash('Recipient and message body are required', 'danger')
            return redirect(url_for('send_message'))

        # Check if recipient email is within our domain.
        if recipient_email.endswith('@' + EMAIL_DOMAIN):
            # Internal email: ensure the recipient exists.
            recipient_user = User.query.filter_by(email=recipient_email).first()
            if recipient_user:
                new_message = Message(
                    sender=sender,
                    recipient=recipient_email,
                    subject=subject,
                    body=body,
                    recipient_id=recipient_user.id
                )
                db.session.add(new_message)
                db.session.commit()
                flash('Email sent successfully to internal user!', 'success')
            else:
                flash('Recipient not found in our email system!', 'danger')
        else:
            # External email: use send_email function and store the email.
            try:
                # Call external email sender.
                send_email(sender, recipient_email, recipient_email, subject, body)
                # Store external email in database with recipient_id as None.
                new_message = Message(
                    sender=sender,
                    recipient=recipient_email,
                    subject=subject,
                    body=body,
                    recipient_id=None
                )
                db.session.add(new_message)
                db.session.commit()
                flash('External email sent successfully and stored in your sent folder!', 'success')
            except Exception as e:
                flash(f'Error sending external email: {e}', 'danger')

        return redirect(url_for('account_sent'))

    return render_template('send.html')

@app.route('/account/inbox')
@login_required
def account_inbox():
    # Retrieve emails where current user is the recipient.
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('account_inbox.html', messages=messages)

@app.route('/account/sent')
@login_required
def account_sent():
    # Retrieve emails where current user is the sender.
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
    
# Note: In a production environment, set debug=False and use a proper WSGI server like Gunicorn or uWSGI.
# Also, ensure to set up proper logging and error handling.