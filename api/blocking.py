from flask import request, jsonify, session
import sqlite3

def register_routes(app, get_db, login_required):
    """User blocking API endpoints"""

    @app.route('/api/block/<int:user_id>', methods=['POST'])
    @login_required
    def block_user(user_id):
        """Block a user"""
        blocker_id = session['user_id']
        data = request.json or {}
        reason = data.get('reason', '')

        if blocker_id == user_id:
            return jsonify({'error': 'Cannot block yourself'}), 400

        db = get_db()

        try:
            db.execute(
                'INSERT INTO blocked_users (blocker_id, blocked_id, reason) VALUES (?, ?, ?)',
                (blocker_id, user_id, reason)
            )
            db.commit()
            db.close()

            return jsonify({'success': True, 'message': 'User blocked successfully'})

        except sqlite3.IntegrityError:
            db.close()
            return jsonify({'error': 'User already blocked'}), 400

    @app.route('/api/unblock/<int:user_id>', methods=['POST'])
    @login_required
    def unblock_user(user_id):
        """Unblock a user"""
        blocker_id = session['user_id']

        db = get_db()
        db.execute(
            'DELETE FROM blocked_users WHERE blocker_id = ? AND blocked_id = ?',
            (blocker_id, user_id)
        )
        db.commit()
        db.close()

        return jsonify({'success': True, 'message': 'User unblocked successfully'})

    @app.route('/api/blocked-users', methods=['GET'])
    @login_required
    def get_blocked_users():
        """Get list of blocked users"""
        blocker_id = session['user_id']

        db = get_db()
        blocked = db.execute('''
            SELECT u.id, u.first_name, u.last_name, u.email, b.created_at, b.reason
            FROM blocked_users b
            JOIN users u ON b.blocked_id = u.id
            WHERE b.blocker_id = ?
            ORDER BY b.created_at DESC
        ''', (blocker_id,)).fetchall()
        db.close()

        return jsonify({
            'blocked_users': [dict(row) for row in blocked]
        })

    @app.route('/api/check-blocked/<int:user_id>', methods=['GET'])
    @login_required
    def check_blocked(user_id):
        """Check if a user is blocked"""
        blocker_id = session['user_id']

        db = get_db()
        blocked = db.execute(
            'SELECT 1 FROM blocked_users WHERE blocker_id = ? AND blocked_id = ?',
            (blocker_id, user_id)
        ).fetchone()
        db.close()

        return jsonify({'is_blocked': blocked is not None})
