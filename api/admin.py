from flask import request, jsonify, session

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401

        # Check if user is admin
        from app import get_db
        db = get_db()
        user = db.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        db.close()

        if not user or not user['is_admin']:
            return jsonify({'error': 'Admin access required'}), 403

        return f(*args, **kwargs)
    return decorated_function

def register_routes(app, get_db, login_required):
    """Admin panel API endpoints"""

    @app.route('/api/admin/stats', methods=['GET'])
    @admin_required
    def get_admin_stats():
        """Get system statistics"""
        db = get_db()

        total_users = db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
        total_matches = db.execute('SELECT COUNT(*) as count FROM matches').fetchone()['count']
        total_messages = db.execute('SELECT COUNT(*) as count FROM messages').fetchone()['count']
        completed_profiles = db.execute('SELECT COUNT(*) as count FROM profiles WHERE profile_completed = 1').fetchone()['count']
        completed_surveys = db.execute('SELECT COUNT(*) as count FROM survey_responses').fetchone()['count']

        db.close()

        return jsonify({
            'total_users': total_users,
            'total_matches': total_matches,
            'total_messages': total_messages,
            'completed_profiles': completed_profiles,
            'completed_surveys': completed_surveys
        })

    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def get_all_users():
        """Get all users with basic info"""
        db = get_db()

        users = db.execute('''
            SELECT u.id, u.email, u.first_name, u.last_name, u.created_at, u.is_admin,
                   p.profile_completed,
                   (SELECT COUNT(*) FROM survey_responses WHERE user_id = u.id) as has_survey
            FROM users u
            LEFT JOIN profiles p ON u.id = p.user_id
            ORDER BY u.created_at DESC
        ''').fetchall()

        db.close()

        return jsonify({
            'users': [dict(u) for u in users]
        })

    @app.route('/api/admin/user/<int:user_id>', methods=['GET'])
    @admin_required
    def get_user_details(user_id):
        """Get detailed info about a specific user"""
        db = get_db()

        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404

        profile = db.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,)).fetchone()
        survey = db.execute('SELECT * FROM survey_responses WHERE user_id = ?', (user_id,)).fetchone()

        # Get matches
        matches = db.execute('''
            SELECT m.id, m.matched_at,
                   CASE WHEN m.user1_id = ? THEN u2.first_name ELSE u1.first_name END as match_first_name,
                   CASE WHEN m.user1_id = ? THEN u2.last_name ELSE u1.last_name END as match_last_name
            FROM matches m
            JOIN users u1 ON m.user1_id = u1.id
            JOIN users u2 ON m.user2_id = u2.id
            WHERE m.user1_id = ? OR m.user2_id = ?
        ''', (user_id, user_id, user_id, user_id)).fetchall()

        db.close()

        return jsonify({
            'user': dict(user),
            'profile': dict(profile) if profile else None,
            'has_survey': bool(survey),
            'matches': [dict(m) for m in matches]
        })

    @app.route('/api/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
    @admin_required
    def toggle_admin(user_id):
        """Toggle admin status for a user"""
        if user_id == session['user_id']:
            return jsonify({'error': 'Cannot modify your own admin status'}), 400

        db = get_db()

        user = db.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404

        new_status = not user['is_admin']
        db.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
        db.commit()
        db.close()

        return jsonify({
            'success': True,
            'is_admin': new_status
        })

    @app.route('/api/admin/user/<int:user_id>/delete', methods=['DELETE'])
    @admin_required
    def delete_user(user_id):
        """Delete a user and all their data"""
        if user_id == session['user_id']:
            return jsonify({'error': 'Cannot delete your own account'}), 400

        db = get_db()

        # Delete in order: messages, typing_status, match_requests, matches, blocked_users, survey_responses, profiles, users
        db.execute('DELETE FROM messages WHERE sender_id = ?', (user_id,))
        db.execute('DELETE FROM typing_status WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM match_requests WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
        db.execute('DELETE FROM matches WHERE user1_id = ? OR user2_id = ?', (user_id, user_id))
        db.execute('DELETE FROM blocked_users WHERE blocker_id = ? OR blocked_id = ?', (user_id, user_id))
        db.execute('DELETE FROM password_reset_tokens WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM survey_responses WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM profiles WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))

        db.commit()
        db.close()

        return jsonify({'success': True, 'message': 'User deleted successfully'})

    @app.route('/api/admin/matches', methods=['GET'])
    @admin_required
    def get_all_matches():
        """Get all matches in the system"""
        db = get_db()

        matches = db.execute('''
            SELECT m.id, m.matched_at,
                   u1.first_name as user1_first, u1.last_name as user1_last, u1.email as user1_email,
                   u2.first_name as user2_first, u2.last_name as user2_last, u2.email as user2_email,
                   (SELECT COUNT(*) FROM messages WHERE match_id = m.id) as message_count
            FROM matches m
            JOIN users u1 ON m.user1_id = u1.id
            JOIN users u2 ON m.user2_id = u2.id
            ORDER BY m.matched_at DESC
            LIMIT 100
        ''').fetchall()

        db.close()

        return jsonify({
            'matches': [dict(m) for m in matches]
        })
