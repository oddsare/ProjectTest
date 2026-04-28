from flask import request, jsonify, session
from werkzeug.utils import secure_filename
import os

def register_routes(app, get_db, login_required, allowed_file, UPLOAD_FOLDER):
    """Profile management API endpoints"""

    @app.route('/api/profile', methods=['GET'])
    @login_required
    def get_profile():
        db = get_db()
        user_id = session['user_id']

        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        profile = db.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,)).fetchone()
        db.close()

        # Build full URL for profile picture
        profile_pic_url = None
        if profile and profile['profile_picture']:
            profile_pic_url = f"/uploads/profile_pictures/{profile['profile_picture']}"

        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'bio': profile['bio'] if profile else None,
                'year_in_school': profile['year'] if profile else None,
                'major': profile['major'] if profile else None,
                'hobbies': profile['hobbies'] if profile else None,
                'profile_picture': profile_pic_url,
                'profile_completed': bool(profile['profile_completed']) if profile else False,
                'created_at': user['created_at']
            }
        })

    @app.route('/api/profile', methods=['PUT'])
    @login_required
    def update_profile():
        data = request.json
        user_id = session['user_id']

        db = get_db()

        # Update user info
        if 'first_name' in data or 'last_name' in data:
            db.execute(
                'UPDATE users SET first_name = ?, last_name = ? WHERE id = ?',
                (data.get('first_name'), data.get('last_name'), user_id)
            )

        # Update profile
        bio = data.get('bio')
        year = data.get('year') or data.get('year_in_school')  # Accept both field names
        major = data.get('major')
        hobbies = data.get('hobbies')

        # Check if profile is complete
        profile_completed = bool(bio and year and major and hobbies)

        db.execute('''
            UPDATE profiles
            SET bio = ?, year = ?, major = ?, hobbies = ?, profile_completed = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (bio, year, major, hobbies, profile_completed, user_id))

        db.commit()
        db.close()

        return jsonify({'success': True, 'profile_completed': profile_completed})

    @app.route('/api/profile/<int:user_id>', methods=['GET'])
    @login_required
    def get_user_profile(user_id):
        """Get another user's public profile"""
        db = get_db()

        user = db.execute('SELECT id, first_name, last_name, email FROM users WHERE id = ?', (user_id,)).fetchone()
        profile = db.execute('SELECT bio, year, major, hobbies, profile_picture FROM profiles WHERE user_id = ?', (user_id,)).fetchone()

        db.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Build full URL for profile picture
        profile_pic_url = None
        if profile and profile['profile_picture']:
            profile_pic_url = f"/uploads/profile_pictures/{profile['profile_picture']}"

        return jsonify({
            'user': {
                'id': user['id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'bio': profile['bio'] if profile else None,
                'year': profile['year'] if profile else None,
                'major': profile['major'] if profile else None,
                'hobbies': profile['hobbies'] if profile else None,
                'profile_picture': profile_pic_url
            }
        })

    @app.route('/api/upload-profile-picture', methods=['POST'])
    @login_required
    def upload_profile_picture():
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename):
            user_id = session['user_id']
            filename = secure_filename(f"{user_id}_{file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Update database
            db = get_db()
            db.execute('UPDATE profiles SET profile_picture = ? WHERE user_id = ?',
                      (filename, user_id))
            db.commit()
            db.close()

            return jsonify({'success': True, 'filename': filename})

        return jsonify({'error': 'Invalid file type'}), 400
