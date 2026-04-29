from flask import request, jsonify, session
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for email_utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from email_utils import send_message_notification

def register_routes(app, get_db, login_required):
    """Chat API endpoints - polling based"""

    @app.route('/api/chat/conversations', methods=['GET'])
    @login_required
    def get_conversations():
        """Get all chat conversations"""
        user_id = session['user_id']
        db = get_db()

        conversations = []

        # Get confirmed matches
        confirmed = db.execute('''
            SELECT
                m.id as match_id,
                CASE
                    WHEN m.user1_id = ? THEN m.user2_id
                    ELSE m.user1_id
                END as other_user_id,
                CASE
                    WHEN m.user1_id = ? THEN u2.first_name
                    ELSE u1.first_name
                END as first_name,
                CASE
                    WHEN m.user1_id = ? THEN u2.last_name
                    ELSE u1.last_name
                END as last_name,
                1 as confirmed,
                (SELECT COUNT(*) FROM messages
                 WHERE match_id = m.id AND sender_id != ? AND read_at IS NULL) as unread_count,
                (SELECT message FROM messages WHERE match_id = m.id
                 ORDER BY sent_at DESC LIMIT 1) as last_message,
                (SELECT sent_at FROM messages WHERE match_id = m.id
                 ORDER BY sent_at DESC LIMIT 1) as last_message_at
            FROM matches m
            JOIN users u1 ON m.user1_id = u1.id
            JOIN users u2 ON m.user2_id = u2.id
            WHERE (m.user1_id = ? OR m.user2_id = ?)
            AND NOT EXISTS (
                SELECT 1 FROM blocked_users b
                WHERE (b.blocker_id = ? AND b.blocked_id = CASE WHEN m.user1_id = ? THEN m.user2_id ELSE m.user1_id END)
                   OR (b.blocker_id = CASE WHEN m.user1_id = ? THEN m.user2_id ELSE m.user1_id END AND b.blocked_id = ?)
            )
        ''', (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id)).fetchall()

        conversations.extend([dict(c) for c in confirmed])

        # Get mutual pending requests
        pending = db.execute('''
            SELECT DISTINCT
                CASE WHEN r1.to_user_id < ? THEN r1.to_user_id ELSE ? END * 1000000 +
                CASE WHEN r1.to_user_id > ? THEN r1.to_user_id ELSE ? END as match_id,
                r1.to_user_id as other_user_id,
                u.first_name,
                u.last_name,
                0 as confirmed,
                0 as unread_count,
                NULL as last_message,
                r1.created_at as last_message_at
            FROM match_requests r1
            JOIN match_requests r2 ON r1.from_user_id = r2.to_user_id AND r1.to_user_id = r2.from_user_id
            JOIN users u ON r1.to_user_id = u.id
            LEFT JOIN matches m ON (m.user1_id = ? AND m.user2_id = r1.to_user_id) OR (m.user2_id = ? AND m.user1_id = r1.to_user_id)
            WHERE r1.from_user_id = ? AND m.id IS NULL
            AND NOT EXISTS (
                SELECT 1 FROM blocked_users b
                WHERE (b.blocker_id = ? AND b.blocked_id = r1.to_user_id)
                   OR (b.blocker_id = r1.to_user_id AND b.blocked_id = ?)
            )
        ''', (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id)).fetchall()

        conversations.extend([dict(p) for p in pending])

        # Sort by last activity
        conversations.sort(key=lambda x: x.get('last_message_at') or '', reverse=True)

        db.close()

        return jsonify({
            'conversations': conversations
        })

    @app.route('/api/chat/<int:match_id>/messages', methods=['GET'])
    @login_required
    def get_messages(match_id):
        """Get messages for a match"""
        user_id = session['user_id']
        db = get_db()

        # Verify user is part of this match
        match = db.execute('''
            SELECT * FROM matches
            WHERE id = ? AND (user1_id = ? OR user2_id = ?)
        ''', (match_id, user_id, user_id)).fetchone()

        if not match:
            db.close()
            return jsonify({'error': 'Match not found'}), 404

        # Get messages
        messages = db.execute('''
            SELECT m.*, u.first_name, u.last_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.match_id = ?
            ORDER BY m.sent_at ASC
        ''', (match_id,)).fetchall()

        # Mark messages as read
        db.execute('''
            UPDATE messages
            SET read_at = CURRENT_TIMESTAMP
            WHERE match_id = ? AND sender_id != ? AND read_at IS NULL
        ''', (match_id, user_id))
        db.commit()
        db.close()

        return jsonify({
            'messages': [dict(m) for m in messages],
            'current_user_id': user_id
        })

    @app.route('/api/chat/<int:match_id>/send', methods=['POST'])
    @login_required
    def send_message(match_id):
        """Send a message"""
        user_id = session['user_id']
        data = request.json
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        db = get_db()

        # Verify user is part of this match
        match = db.execute('''
            SELECT * FROM matches
            WHERE id = ? AND (user1_id = ? OR user2_id = ?)
        ''', (match_id, user_id, user_id)).fetchone()

        if not match:
            db.close()
            return jsonify({'error': 'Match not found'}), 404

        # Insert message
        cursor = db.execute('''
            INSERT INTO messages (match_id, sender_id, message)
            VALUES (?, ?, ?)
        ''', (match_id, user_id, message))

        message_id = cursor.lastrowid
        db.commit()

        # Get created message
        new_message = db.execute('''
            SELECT m.*, u.first_name, u.last_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.id = ?
        ''', (message_id,)).fetchone()

        # Get recipient info
        recipient_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
        recipient = db.execute('''
            SELECT email, first_name, last_name FROM users WHERE id = ?
        ''', (recipient_id,)).fetchone()

        db.close()

        # Send email notification
        if recipient:
            sender_name = f"{new_message['first_name']} {new_message['last_name'] or ''}".strip() if new_message['first_name'] else "Someone"
            message_preview = message[:100] + '...' if len(message) > 100 else message
            base_url = request.host_url.rstrip('/')
            send_message_notification(recipient['email'], sender_name, message_preview, base_url)

        return jsonify({
            'success': True,
            'message': dict(new_message)
        })

    @app.route('/api/chat/<int:match_id>/typing', methods=['POST'])
    @login_required
    def update_typing_status(match_id):
        """Update typing indicator"""
        user_id = session['user_id']

        db = get_db()

        db.execute('''
            INSERT OR REPLACE INTO typing_status (match_id, user_id, last_typing_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (match_id, user_id))
        db.commit()
        db.close()

        return jsonify({'success': True})

    @app.route('/api/chat/<int:match_id>/typing-status', methods=['GET'])
    @login_required
    def get_typing_status(match_id):
        """Check if other user is typing"""
        user_id = session['user_id']
        db = get_db()

        # Get typing status
        typing = db.execute('''
            SELECT user_id, last_typing_at
            FROM typing_status
            WHERE match_id = ? AND user_id != ?
            AND datetime(last_typing_at) > datetime('now', '-3 seconds')
        ''', (match_id, user_id)).fetchone()

        db.close()

        return jsonify({
            'is_typing': typing is not None
        })
