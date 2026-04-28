from flask import request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import secrets
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for email_utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from email_utils import send_password_reset_email

def register_routes(app, get_db):
    """Authentication API endpoints"""

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.json
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name') or data.get('firstName')  # Accept both formats
        last_name = data.get('last_name') or data.get('lastName')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        # Server-side email domain validation
        if not email.endswith('@go.olemiss.edu'):
            return jsonify({'error': 'Must use Ole Miss email (@go.olemiss.edu)'}), 400

        db = get_db()
        try:
            # Create user
            cursor = db.execute(
                'INSERT INTO users (email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?)',
                (email, generate_password_hash(password), first_name, last_name)
            )
            user_id = cursor.lastrowid

            # Create empty profile
            db.execute('INSERT INTO profiles (user_id) VALUES (?)', (user_id,))
            db.commit()

            # Auto-login
            session['user_id'] = user_id

            return jsonify({
                'success': True,
                'user': {
                    'id': user_id,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            }), 201

        except sqlite3.IntegrityError:
            return jsonify({'error': 'Email already registered'}), 400
        finally:
            db.close()

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        # Server-side email domain validation
        if not email.endswith('@go.olemiss.edu'):
            return jsonify({'error': 'Must use Ole Miss email (@go.olemiss.edu)'}), 400

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        db.close()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401

        session['user_id'] = user['id']

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        })

    @app.route('/api/logout', methods=['POST'])
    def logout():
        session.pop('user_id', None)
        return jsonify({'success': True})

    @app.route('/api/check-auth', methods=['GET'])
    def check_auth():
        if 'user_id' in session:
            db = get_db()
            user = db.execute('SELECT id, email, first_name, last_name FROM users WHERE id = ?',
                            (session['user_id'],)).fetchone()
            db.close()

            if user:
                return jsonify({
                    'authenticated': True,
                    'user': dict(user)
                })

        return jsonify({'authenticated': False}), 401

    @app.route('/api/forgot-password', methods=['POST'])
    def forgot_password():
        """Generate password reset token"""
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email required'}), 400

        # Server-side email domain validation
        if not email.endswith('@go.olemiss.edu'):
            return jsonify({'error': 'Must use Ole Miss email (@go.olemiss.edu)'}), 400

        db = get_db()
        user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()

        if not user:
            # Don't reveal if email exists - return success anyway for security
            return jsonify({'message': 'If that email exists, a reset link will be provided'}), 200

        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)

        # Store token
        db.execute(
            'INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user['id'], token, expires_at)
        )
        db.commit()
        db.close()

        # Send reset email
        base_url = request.host_url.rstrip('/')
        email_sent = send_password_reset_email(email, token, base_url)

        # For development, return the token in response if email is disabled
        response = {'message': 'If that email exists, a reset link has been sent'}
        if not email_sent:
            # Email disabled or failed - return token for development
            response['token'] = token
            response['message'] = 'Email disabled. Reset link generated'

        return jsonify(response), 200

    @app.route('/api/reset-password', methods=['POST'])
    def reset_password():
        """Reset password using token"""
        data = request.json
        token = data.get('token')
        new_password = data.get('password')

        if not token or not new_password:
            return jsonify({'error': 'Token and password required'}), 400

        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400

        db = get_db()

        # Verify token
        reset_token = db.execute('''
            SELECT * FROM password_reset_tokens
            WHERE token = ? AND used = 0 AND datetime(expires_at) > datetime('now')
        ''', (token,)).fetchone()

        if not reset_token:
            db.close()
            return jsonify({'error': 'Invalid or expired token'}), 400

        # Update password
        db.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (generate_password_hash(new_password), reset_token['user_id'])
        )

        # Mark token as used
        db.execute('UPDATE password_reset_tokens SET used = 1 WHERE id = ?', (reset_token['id'],))

        db.commit()
        db.close()

        return jsonify({'message': 'Password reset successfully'}), 200

    @app.route('/api/change-password', methods=['POST'])
    def change_password():
        """Change password for logged-in user"""
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401

        data = request.json
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')

        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password required'}), 400

        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404

        # Verify current password
        if not check_password_hash(user['password_hash'], current_password):
            db.close()
            return jsonify({'error': 'Current password is incorrect'}), 401

        # Update password
        db.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (generate_password_hash(new_password), session['user_id'])
        )
        db.commit()
        db.close()

        return jsonify({'message': 'Password changed successfully'}), 200
