from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime, timedelta
import secrets

app = Flask(__name__, static_folder='Public_html', static_url_path='')

# Require SECRET_KEY environment variable for security
if not os.environ.get('SECRET_KEY'):
    # Generate a random secret key for development if not set
    print("WARNING: SECRET_KEY not set in environment. Using generated key for this session only.")
    print("Set SECRET_KEY environment variable for production!")
    app.secret_key = secrets.token_hex(32)
else:
    app.secret_key = os.environ.get('SECRET_KEY')

CORS(app, supports_credentials=True)

# Config
DATABASE = 'roomi.db'
UPLOAD_FOLDER = 'uploads/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database with schema"""
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            email_verified BOOLEAN DEFAULT 0,
            email_verification_token TEXT,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            bio TEXT,
            year TEXT,
            major TEXT,
            hobbies TEXT,
            profile_picture TEXT,
            profile_completed BOOLEAN DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS survey_responses (
            user_id INTEGER PRIMARY KEY,
            question1 TEXT, question2 TEXT, question3 TEXT, question4 TEXT, question5 TEXT,
            question6 TEXT, question7 TEXT, question8 TEXT, question9 TEXT, question10 TEXT,
            question11 TEXT, question12 TEXT, question13 TEXT, question14 TEXT, question15 TEXT,
            question16 TEXT, question17 TEXT, question18 TEXT, question19 TEXT, question20 TEXT,
            question21 TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS match_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users(id),
            FOREIGN KEY (to_user_id) REFERENCES users(id),
            UNIQUE(from_user_id, to_user_id)
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user1_id) REFERENCES users(id),
            FOREIGN KEY (user2_id) REFERENCES users(id),
            UNIQUE(user1_id, user2_id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (sender_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS typing_status (
            match_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            last_typing_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (match_id, user_id),
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS blocked_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blocker_id INTEGER NOT NULL,
            blocked_id INTEGER NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blocker_id) REFERENCES users(id),
            FOREIGN KEY (blocked_id) REFERENCES users(id),
            UNIQUE(blocker_id, blocked_id)
        );
    ''')
    db.commit()
    db.close()

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes - Serve HTML files
@app.route('/')
def index():
    return send_from_directory('Public_html', 'login_improved.html')

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory('uploads', filename)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('Public_html', path)

# Import and register API routes
from api import auth, profile, matching, chat, blocking, admin

auth.register_routes(app, get_db)
profile.register_routes(app, get_db, login_required, allowed_file, UPLOAD_FOLDER)
matching.register_routes(app, get_db, login_required)
chat.register_routes(app, get_db, login_required)
blocking.register_routes(app, get_db, login_required)
admin.register_routes(app, get_db, login_required)

# Initialize database on startup
with app.app_context():
    init_db()

if __name__ == '__main__':
    # Only enable debug mode in development
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    if debug_mode:
        print("WARNING: Running in DEBUG mode. Disable for production!")

    app.run(debug=debug_mode, port=8000)
