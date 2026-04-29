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

        # Delete all user data
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
            SELECT m.id, m.matched_at, m.user1_id, m.user2_id,
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

    @app.route('/api/admin/match/<int:match_id>/delete', methods=['DELETE'])
    @admin_required
    def delete_match(match_id):
        """Break up a match (admin action)"""
        db = get_db()

        # Delete associated data
        db.execute('DELETE FROM messages WHERE match_id = ?', (match_id,))
        db.execute('DELETE FROM typing_status WHERE match_id = ?', (match_id,))

        # Delete the match
        db.execute('DELETE FROM matches WHERE id = ?', (match_id,))
        db.commit()
        db.close()

        return jsonify({'success': True, 'message': 'Match deleted successfully'})

    @app.route('/api/admin/match/create', methods=['POST'])
    @admin_required
    def create_match():
        """Create a match between two users (admin action)"""
        data = request.json
        user1_id = data.get('user1_id')
        user2_id = data.get('user2_id')

        if not user1_id or not user2_id:
            return jsonify({'error': 'Both user IDs required'}), 400

        if user1_id == user2_id:
            return jsonify({'error': 'Cannot match user with themselves'}), 400

        db = get_db()

        # Check if already matched
        existing = db.execute('''
            SELECT id FROM matches
            WHERE user1_id = ? OR user2_id = ? OR user1_id = ? OR user2_id = ?
        ''', (user1_id, user1_id, user2_id, user2_id)).fetchone()

        if existing:
            db.close()
            return jsonify({'error': 'One or both users already have a match'}), 400

        # Create the match
        user_ids = sorted([user1_id, user2_id])
        try:
            db.execute('''
                INSERT INTO matches (user1_id, user2_id)
                VALUES (?, ?)
            ''', (user_ids[0], user_ids[1]))

            # Remove any pending requests
            db.execute('''
                DELETE FROM match_requests
                WHERE (from_user_id = ? AND to_user_id = ?)
                   OR (from_user_id = ? AND to_user_id = ?)
            ''', (user1_id, user2_id, user2_id, user1_id))

            db.commit()
            db.close()
            return jsonify({'success': True, 'message': 'Match created successfully'})
        except Exception as e:
            db.close()
            return jsonify({'error': f'Failed to create match: {str(e)}'}), 500

    @app.route('/api/admin/potential-matches', methods=['GET'])
    @admin_required
    def get_potential_matches():
        """Get all users who could potentially be matched"""
        db = get_db()

        users = db.execute('''
            SELECT u.id, u.email, u.first_name, u.last_name,
                   p.year, p.major,
                   CASE WHEN sr.user_id IS NOT NULL THEN 1 ELSE 0 END as has_survey,
                   CASE WHEN m.id IS NOT NULL THEN 1 ELSE 0 END as already_matched
            FROM users u
            LEFT JOIN profiles p ON u.id = p.user_id
            LEFT JOIN survey_responses sr ON u.id = sr.user_id
            LEFT JOIN matches m ON u.id = m.user1_id OR u.id = m.user2_id
            WHERE u.is_admin = 0
            AND p.profile_completed = 1
            ORDER BY u.first_name, u.last_name
        ''').fetchall()

        db.close()

        return jsonify({
            'users': [dict(u) for u in users]
        })

    @app.route('/api/admin/user/<int:user_id>/profile', methods=['PUT'])
    @admin_required
    def update_user_profile(user_id):
        """Update user profile information (admin action)"""
        data = request.json
        db = get_db()

        # Check if profile exists
        profile = db.execute('SELECT user_id FROM profiles WHERE user_id = ?', (user_id,)).fetchone()

        if profile:
            # Update existing profile
            db.execute('''
                UPDATE profiles
                SET bio = ?, year = ?, major = ?, hobbies = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (data.get('bio'), data.get('year'), data.get('major'), data.get('hobbies'), user_id))
        else:
            # Create new profile
            db.execute('''
                INSERT INTO profiles (user_id, bio, year, major, hobbies, profile_completed)
                VALUES (?, ?, ?, ?, ?, 0)
            ''', (user_id, data.get('bio'), data.get('year'), data.get('major'), data.get('hobbies')))

        db.commit()
        db.close()

        return jsonify({'success': True, 'message': 'Profile updated successfully'})

    @app.route('/api/admin/user/<int:user_id>/survey', methods=['PUT'])
    @admin_required
    def update_user_survey(user_id):
        """Update user survey responses (admin action)"""
        data = request.json
        db = get_db()

        # Build the survey data
        questions = {}
        for i in range(1, 22):
            key = f'question{i}'
            if key in data:
                questions[key] = data[key]

        # Check if survey exists
        survey = db.execute('SELECT user_id FROM survey_responses WHERE user_id = ?', (user_id,)).fetchone()

        if survey:
            # Build update query
            set_clauses = [f'{key} = ?' for key in questions.keys()]
            values = list(questions.values())
            values.append(user_id)

            db.execute(f'''
                UPDATE survey_responses
                SET {', '.join(set_clauses)}
                WHERE user_id = ?
            ''', values)
        else:
            # Create new survey response
            columns = ', '.join(questions.keys())
            placeholders = ', '.join(['?' for _ in questions])
            values = list(questions.values())

            db.execute(f'''
                INSERT INTO survey_responses (user_id, {columns})
                VALUES (?, {placeholders})
            ''', [user_id] + values)

        db.commit()
        db.close()

        return jsonify({'success': True, 'message': 'Survey updated successfully'})

    @app.route('/api/admin/user/<int:user_id>/survey', methods=['GET'])
    @admin_required
    def get_user_survey(user_id):
        """Get user survey responses for editing"""
        db = get_db()

        survey = db.execute('SELECT * FROM survey_responses WHERE user_id = ?', (user_id,)).fetchone()

        db.close()

        if survey:
            return jsonify({'survey': dict(survey)})
        else:
            return jsonify({'survey': None})

    @app.route('/api/admin/check', methods=['GET'])
    @login_required
    def check_admin():
        """Check if current user is admin"""
        db = get_db()
        user = db.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        db.close()

        return jsonify({
            'is_admin': bool(user and user['is_admin'])
        })
