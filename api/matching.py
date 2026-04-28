from flask import request, jsonify, session
import sys
import os
sys.path.append('.')
from Matching import calculate_match_score
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from email_utils import send_match_notification

def register_routes(app, get_db, login_required):
    """Survey and matching API endpoints"""

    @app.route('/api/survey', methods=['POST'])
    @login_required
    def submit_survey():
        data = request.json
        user_id = session['user_id']

        db = get_db()

        # Check profile completed
        profile = db.execute('SELECT profile_completed FROM profiles WHERE user_id = ?',
                           (user_id,)).fetchone()

        if not profile or not profile['profile_completed']:
            db.close()
            return jsonify({'error': 'Complete your profile first', 'code': 'PROFILE_INCOMPLETE'}), 400

        # Save survey responses
        questions = {f'question{i}': data.get(f'question{i}') for i in range(1, 22)}

        db.execute('''
            INSERT OR REPLACE INTO survey_responses
            (user_id, question1, question2, question3, question4, question5,
             question6, question7, question8, question9, question10,
             question11, question12, question13, question14, question15,
             question16, question17, question18, question19, question20, question21)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, *[questions[f'question{i}'] for i in range(1, 22)]))

        db.commit()
        db.close()

        return jsonify({'success': True})

    @app.route('/api/matches', methods=['GET'])
    @login_required
    def get_matches():
        user_id = session['user_id']
        db = get_db()

        # Check profile completed
        profile = db.execute('SELECT profile_completed FROM profiles WHERE user_id = ?',
                           (user_id,)).fetchone()

        if not profile or not profile['profile_completed']:
            db.close()
            return jsonify({'error': 'Complete your profile first', 'code': 'PROFILE_INCOMPLETE'}), 400

        # Check survey completed
        survey = db.execute('SELECT * FROM survey_responses WHERE user_id = ?',
                          (user_id,)).fetchone()

        if not survey:
            db.close()
            return jsonify({'error': 'Complete the survey first', 'code': 'SURVEY_INCOMPLETE'}), 400

        # Get current user's survey data
        current_user_survey = dict(survey)

        # Get all other users who completed survey (exclude already matched)
        already_matched = db.execute('''
            SELECT CASE
                WHEN user1_id = ? THEN user2_id
                WHEN user2_id = ? THEN user1_id
            END as matched_user_id
            FROM matches
            WHERE user1_id = ? OR user2_id = ?
        ''', (user_id, user_id, user_id, user_id)).fetchall()

        matched_ids = [row['matched_user_id'] for row in already_matched]
        matched_ids.append(user_id)  # Exclude self

        # Exclude blocked users (both directions: users I blocked and users who blocked me)
        blocked = db.execute('''
            SELECT blocked_id AS user_id FROM blocked_users WHERE blocker_id = ?
            UNION
            SELECT blocker_id AS user_id FROM blocked_users WHERE blocked_id = ?
        ''', (user_id, user_id)).fetchall()
        matched_ids.extend([row['user_id'] for row in blocked])

        # Get potential matches
        placeholders = ','.join('?' * len(matched_ids))
        potential_matches = db.execute(f'''
            SELECT u.id, u.first_name, u.last_name, u.email, s.*
            FROM users u
            JOIN survey_responses s ON u.id = s.user_id
            JOIN profiles p ON u.id = p.user_id
            WHERE u.id NOT IN ({placeholders})
            AND p.profile_completed = 1
        ''', matched_ids).fetchall()

        # Calculate match scores using Matching.py algorithm
        matches = []
        for user in potential_matches:
            user_survey = dict(user)
            score = calculate_match_score(current_user_survey, user_survey)

            if score != float('inf'):  # Valid match (passed hard filters)
                compatibility = max(0, 100 - int(score * 5))  # Convert distance to %

                # Get shared traits (for display)
                shared_traits = []
                if current_user_survey.get('question4') == user_survey.get('question4'):
                    shared_traits.append('Greek Life')
                if current_user_survey.get('question7') == user_survey.get('question7'):
                    shared_traits.append('Sleep Schedule')
                if current_user_survey.get('question14') == user_survey.get('question14'):
                    shared_traits.append('Bedtime')

                matches.append({
                    'userId': user['id'],
                    'firstName': user['first_name'],
                    'lastName': user['last_name'],
                    'email': user['email'],
                    'compatibility': compatibility,
                    'score': round(score, 2),
                    'sharedTraits': shared_traits[:3]  # Top 3
                })

        # Sort by compatibility (highest first)
        matches.sort(key=lambda x: x['compatibility'], reverse=True)

        db.close()

        return jsonify({'matches': matches[:10]})  # Top 10 matches

    @app.route('/api/match/accept', methods=['POST'])
    @login_required
    def accept_match():
        """Send match request - unlocks chat, doesn't finalize match"""
        data = request.json
        user_id = session['user_id']
        target_user_id = data.get('userId')

        if not target_user_id:
            return jsonify({'error': 'userId required'}), 400

        db = get_db()

        # Create match request (bidirectional for chat)
        try:
            db.execute('''
                INSERT INTO match_requests (from_user_id, to_user_id)
                VALUES (?, ?)
            ''', (user_id, target_user_id))
            db.commit()
        except:
            pass  # Already exists

        # Check if mutual request exists
        mutual = db.execute('''
            SELECT id FROM match_requests
            WHERE from_user_id = ? AND to_user_id = ?
        ''', (target_user_id, user_id)).fetchone()

        # Send email notification to target user
        sender = db.execute('SELECT first_name, last_name FROM users WHERE id = ?', (user_id,)).fetchone()
        target = db.execute('SELECT email, first_name, last_name FROM users WHERE id = ?', (target_user_id,)).fetchone()

        db.close()

        if target and sender:
            sender_name = f"{sender['first_name']} {sender['last_name'] or ''}".strip() if sender['first_name'] else "Someone"
            base_url = request.host_url.rstrip('/')
            send_match_notification(target['email'], sender_name, base_url)

        return jsonify({'success': True, 'mutual': bool(mutual), 'message': 'Request sent! You can now chat.'})

    @app.route('/api/match/confirm', methods=['POST'])
    @login_required
    def confirm_match():
        """Confirm exclusive match after chatting"""
        data = request.json
        user_id = session['user_id']
        target_user_id = data.get('userId')

        if not target_user_id:
            return jsonify({'error': 'userId required'}), 400

        db = get_db()

        # Check if user already has confirmed match
        existing_match = db.execute('''
            SELECT id FROM matches
            WHERE user1_id = ? OR user2_id = ?
        ''', (user_id, user_id)).fetchone()

        if existing_match:
            db.close()
            return jsonify({'error': 'You already have a confirmed match', 'code': 'ALREADY_MATCHED'}), 400

        # Check mutual request exists
        mutual_request = db.execute('''
            SELECT id FROM match_requests
            WHERE (from_user_id = ? AND to_user_id = ?)
               OR (from_user_id = ? AND to_user_id = ?)
        ''', (user_id, target_user_id, target_user_id, user_id)).fetchone()

        if not mutual_request:
            db.close()
            return jsonify({'error': 'No pending request with this user'}), 400

        # Check target hasn't confirmed with someone else
        target_match = db.execute('''
            SELECT id FROM matches
            WHERE user1_id = ? OR user2_id = ?
        ''', (target_user_id, target_user_id)).fetchone()

        if target_match:
            db.close()
            return jsonify({'error': 'This user already confirmed with someone else'}), 400

        # Create confirmed match
        try:
            user_ids = sorted([user_id, target_user_id])
            db.execute('''
                INSERT INTO matches (user1_id, user2_id)
                VALUES (?, ?)
            ''', (user_ids[0], user_ids[1]))
            db.commit()
            db.close()
            return jsonify({'success': True, 'message': 'Match confirmed!'})
        except:
            db.close()
            return jsonify({'error': 'Failed to confirm match'}), 500

    @app.route('/api/match/requests/incoming', methods=['GET'])
    @login_required
    def get_incoming_requests():
        """Get incoming match requests"""
        user_id = session['user_id']
        db = get_db()

        requests = db.execute('''
            SELECT mr.id as request_id, mr.from_user_id, u.first_name, u.last_name, u.email,
                   p.bio, p.year, p.hobbies, p.profile_picture, mr.created_at
            FROM match_requests mr
            JOIN users u ON mr.from_user_id = u.id
            JOIN profiles p ON u.id = p.user_id
            WHERE mr.to_user_id = ?
            AND NOT EXISTS (
                SELECT 1 FROM match_requests mr2
                WHERE mr2.from_user_id = ? AND mr2.to_user_id = mr.from_user_id
            )
            AND NOT EXISTS (
                SELECT 1 FROM blocked_users b
                WHERE (b.blocker_id = ? AND b.blocked_id = mr.from_user_id)
                   OR (b.blocker_id = mr.from_user_id AND b.blocked_id = ?)
            )
            ORDER BY mr.created_at DESC
        ''', (user_id, user_id, user_id, user_id)).fetchall()

        db.close()

        # Build full URLs for profile pictures
        result = []
        for r in requests:
            req_dict = dict(r)
            if req_dict['profile_picture']:
                req_dict['profile_picture'] = f"/uploads/profile_pictures/{req_dict['profile_picture']}"
            result.append(req_dict)

        return jsonify({'requests': result})

    @app.route('/api/match/requests/accepted', methods=['GET'])
    @login_required
    def get_accepted_requests():
        """Get requests user sent that were accepted (mutual pending)"""
        user_id = session['user_id']
        db = get_db()

        # Find mutual requests where user initiated (sent first)
        accepted = db.execute('''
            SELECT mr.to_user_id, u.first_name, u.last_name, u.email,
                   p.profile_picture
            FROM match_requests mr
            JOIN match_requests mr2 ON mr.from_user_id = mr2.to_user_id AND mr.to_user_id = mr2.from_user_id
            JOIN users u ON mr.to_user_id = u.id
            JOIN profiles p ON u.id = p.user_id
            WHERE mr.from_user_id = ?
            AND NOT EXISTS (
                SELECT 1 FROM matches m
                WHERE (m.user1_id = ? AND m.user2_id = mr.to_user_id)
                   OR (m.user2_id = ? AND m.user1_id = mr.to_user_id)
            )
            ORDER BY mr2.created_at DESC
        ''', (user_id, user_id, user_id)).fetchall()

        db.close()

        # Build full URLs for profile pictures
        result = []
        for r in accepted:
            acc_dict = dict(r)
            if acc_dict['profile_picture']:
                acc_dict['profile_picture'] = f"/uploads/profile_pictures/{acc_dict['profile_picture']}"
            result.append(acc_dict)

        return jsonify({'accepted': result})

    @app.route('/api/match/request/accept', methods=['POST'])
    @login_required
    def accept_incoming_request():
        """Accept incoming request - creates mutual request for chat"""
        data = request.json
        user_id = session['user_id']
        from_user_id = data.get('fromUserId')

        if not from_user_id:
            return jsonify({'error': 'fromUserId required'}), 400

        db = get_db()

        # Verify request exists
        req = db.execute('''
            SELECT id FROM match_requests
            WHERE from_user_id = ? AND to_user_id = ?
        ''', (from_user_id, user_id)).fetchone()

        if not req:
            db.close()
            return jsonify({'error': 'Request not found'}), 404

        # Create reverse request (mutual for chat)
        try:
            db.execute('''
                INSERT INTO match_requests (from_user_id, to_user_id)
                VALUES (?, ?)
            ''', (user_id, from_user_id))
            db.commit()
        except:
            pass  # Already exists

        db.close()
        return jsonify({'success': True, 'message': 'Request accepted! You can now chat.'})

    @app.route('/api/match/request/deny', methods=['POST'])
    @login_required
    def deny_incoming_request():
        """Deny incoming request - deletes it"""
        data = request.json
        user_id = session['user_id']
        from_user_id = data.get('fromUserId')

        if not from_user_id:
            return jsonify({'error': 'fromUserId required'}), 400

        db = get_db()

        db.execute('''
            DELETE FROM match_requests
            WHERE from_user_id = ? AND to_user_id = ?
        ''', (from_user_id, user_id))
        db.commit()
        db.close()

        return jsonify({'success': True, 'message': 'Request denied'})

    @app.route('/api/match/reject', methods=['POST'])
    @login_required
    def reject_match():
        # Just don't create a match request - no action needed
        return jsonify({'success': True})

    @app.route('/api/match/check/<int:other_user_id>', methods=['GET'])
    @login_required
    def check_mutual_match(other_user_id):
        """Check if mutually matched with another user"""
        user_id = session['user_id']
        db = get_db()

        # Check if mutual match exists
        user_ids = sorted([user_id, other_user_id])
        match = db.execute('''
            SELECT id FROM matches
            WHERE user1_id = ? AND user2_id = ?
        ''', (user_ids[0], user_ids[1])).fetchone()

        db.close()

        return jsonify({
            'mutualMatch': match is not None,
            'matchId': match['id'] if match else None
        })
