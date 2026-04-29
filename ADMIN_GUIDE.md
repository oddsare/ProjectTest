# Admin Panel Guide - Roomi

Complete guide to using and setting up the admin panel for the Roomi roommate matching platform.

---

## Table of Contents

1. [Making Your First Admin](#making-your-first-admin)
2. [Accessing the Admin Panel](#accessing-the-admin-panel)
3. [Admin Panel Features](#admin-panel-features)
4. [Managing Users](#managing-users)
5. [Managing Matches](#managing-matches)
6. [Creating Matches Manually](#creating-matches-manually)
7. [Security Considerations](#security-considerations)
8. [API Endpoints Reference](#api-endpoints-reference)

---

## Making Your First Admin

Before you can use the admin panel, you need to create your first admin account.

### Option 1: Using the Make Admin Portal (Recommended for First Admin)

1. **Register a regular user account first**
   - Go to: `https://your-app.railway.app/register.html`
   - Create account with your Ole Miss email
   - Complete profile and survey (optional but recommended)

2. **Visit the Make Admin Portal**
   - Go to: `https://your-app.railway.app/make_admin.html`
   - Enter your email address
   - Click "GRANT ADMIN ACCESS"

3. **Done!**
   - Log out and log back in
   - You'll now see the "Admin" link in the navigation bar

### Option 2: Using Python Script (Database Access Required)

If you have direct database access:

```python
import sqlite3

# Connect to database
db = sqlite3.connect('roomi.db')
cursor = db.cursor()

# Grant admin to specific email
email = 'your-email@go.olemiss.edu'
cursor.execute('UPDATE users SET is_admin = 1 WHERE email = ?', (email,))
db.commit()
db.close()

print(f'✓ Admin access granted to {email}')
```

### Option 3: Making Additional Admins (After First Admin)

Once you have one admin account:

1. Log in as admin
2. Go to Admin Panel
3. Click "Users" tab
4. Find the user you want to make admin
5. Click "Make Admin" button
6. Confirm the action

---

## Accessing the Admin Panel

### For Admin Users

1. **Log in** to your Roomi account
2. Look for the **"Admin"** link in the navigation bar (red text)
3. Click it to access the admin panel

**Note:** The Admin link is only visible to users with `is_admin = 1` in the database.

### Direct URLs

- **Admin Dashboard:** `https://your-app.railway.app/admin.html`
- **Make Admin Portal:** `https://your-app.railway.app/make_admin.html`

---

## Admin Panel Features

The admin panel has three main tabs:

### 1. Users Tab

**View all users in the system with:**
- User ID
- Full name
- Email address
- Profile completion status
- Survey completion status
- Admin status badge

**Actions available:**
- **Edit** - Modify user profile (bio, year, major, hobbies)
- **Make Admin** - Grant admin access to the user
- **Remove Admin** - Revoke admin access from the user
- **Delete** - Permanently delete user and all their data

### 2. All Matches Tab

**View all confirmed roommate matches:**
- Match ID
- User 1 name and email
- User 2 name and email
- Match date
- Message count (how many messages they've exchanged)

**Actions available:**
- **Break Up** - Delete the match (makes them unmatched)

### 3. Potential Matches Tab

**View users available for matching:**
- User ID and name
- Email
- Year
- Major
- Survey completion status
- Match status (Matched or Available)

**Features:**
- **Match Creator** - Manually create matches between two users
- See which users are available vs. already matched

---

## Managing Users

### Editing User Profiles

1. Go to **Users** tab
2. Click **Edit** next to the user
3. Modify the fields:
   - **Bio** - Personal description
   - **Year** - Freshman, Sophomore, Junior, Senior
   - **Major** - Field of study
   - **Hobbies** - Interests and activities
4. Click **Save Changes**

**Note:** This only edits profile data, not survey responses.

### Deleting Users

1. Go to **Users** tab
2. Click **Delete** next to the user
3. Confirm the deletion
4. User and all associated data will be permanently removed:
   - Profile
   - Survey responses
   - Match requests
   - Matches
   - Messages
   - Blocked users

**Warning:** This action cannot be undone!

### Making/Removing Admins

1. Go to **Users** tab
2. Click **Make Admin** (green) or **Remove Admin** (red)
3. Confirm the action

**Restrictions:**
- You cannot modify your own admin status
- There should always be at least one admin

---

## Managing Matches

### Breaking Up Matches

If two users are matched and you need to separate them:

1. Go to **All Matches** tab
2. Find the match
3. Click **Break Up**
4. Confirm the action

**What happens:**
- The match is deleted from the database
- All associated messages are deleted
- Both users become unmatched and can find new matches
- They will see each other in potential matches again (unless blocked)

---

## Creating Matches Manually

You can manually match two users together:

### Step 1: Check Availability

1. Go to **Potential Matches** tab
2. Look for users with "Available" status (not already matched)
3. Note their names/emails

### Step 2: Create the Match

1. In the **Match Creator** section at the top
2. Select **User 1** from the dropdown
3. Select **User 2** from the dropdown
4. Click **Create Match**

**Requirements:**
- Both users must have completed profiles
- Neither user can already have a match
- Users cannot be matched with themselves

**What happens after creating:**
- Users immediately become roommates
- They appear in each other's "Your Roommate" card
- Any pending match requests between them are deleted
- They are removed from potential matches list

---

## Security Considerations

### Production Deployment

**IMPORTANT:** For production, you should secure or disable the Make Admin portal:

#### Option 1: Remove Public Access

Delete or move `make_admin.html` after creating your first admin:

```bash
rm Public_html/make_admin.html
```

#### Option 2: Add Authentication

Modify `/api/make-admin` endpoint in `api/auth.py` to require a secret token:

```python
@app.route('/api/make-admin', methods=['POST'])
def make_admin():
    data = request.json
    email = data.get('email')
    secret = data.get('secret')

    # Check secret token
    ADMIN_SETUP_SECRET = os.environ.get('ADMIN_SETUP_SECRET')
    if not ADMIN_SETUP_SECRET or secret != ADMIN_SETUP_SECRET:
        return jsonify({'error': 'Unauthorized'}), 403

    # ... rest of the code
```

Then set `ADMIN_SETUP_SECRET` in Railway environment variables.

#### Option 3: IP Whitelist

Configure Railway to only allow access to `make_admin.html` from specific IPs.

### Admin Responsibilities

As an admin, you can:
- View all user data (emails, profiles, survey responses)
- Delete any user account
- View all matches and messages
- Manually create or break matches

**Best Practices:**
- Only grant admin access to trusted individuals
- Don't share admin credentials
- Document any manual matches you create
- Be cautious when deleting users or matches

---

## API Endpoints Reference

All admin endpoints require authentication and admin status.

### Check Admin Status

```
GET /api/admin/check
```

**Response:**
```json
{
  "is_admin": true
}
```

### System Statistics

```
GET /api/admin/stats
```

**Response:**
```json
{
  "total_users": 150,
  "total_matches": 45,
  "total_messages": 1203,
  "completed_profiles": 120,
  "completed_surveys": 110
}
```

### Get All Users

```
GET /api/admin/users
```

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@go.olemiss.edu",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2024-01-15 10:30:00",
      "is_admin": 0,
      "profile_completed": 1,
      "has_survey": 1
    }
  ]
}
```

### Get User Details

```
GET /api/admin/user/<user_id>
```

**Response:**
```json
{
  "user": { ... },
  "profile": { ... },
  "has_survey": true,
  "matches": [ ... ]
}
```

### Update User Profile

```
PUT /api/admin/user/<user_id>/profile

Body:
{
  "bio": "Updated bio",
  "year": "Junior",
  "major": "Computer Science",
  "hobbies": "Gaming, Reading"
}
```

### Toggle Admin Status

```
POST /api/admin/user/<user_id>/toggle-admin
```

**Response:**
```json
{
  "success": true,
  "is_admin": true
}
```

### Delete User

```
DELETE /api/admin/user/<user_id>/delete
```

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

### Get All Matches

```
GET /api/admin/matches
```

**Response:**
```json
{
  "matches": [
    {
      "id": 1,
      "user1_id": 5,
      "user2_id": 12,
      "user1_first": "Alice",
      "user1_last": "Smith",
      "user1_email": "alice@go.olemiss.edu",
      "user2_first": "Bob",
      "user2_last": "Jones",
      "user2_email": "bob@go.olemiss.edu",
      "matched_at": "2024-01-20 14:30:00",
      "message_count": 25
    }
  ]
}
```

### Delete Match

```
DELETE /api/admin/match/<match_id>/delete
```

**Response:**
```json
{
  "success": true,
  "message": "Match deleted successfully"
}
```

### Create Match

```
POST /api/admin/match/create

Body:
{
  "user1_id": 5,
  "user2_id": 12
}
```

**Response:**
```json
{
  "success": true,
  "message": "Match created successfully"
}
```

**Errors:**
- Both user IDs required
- Cannot match user with themselves
- One or both users already have a match

### Get Potential Matches

```
GET /api/admin/potential-matches
```

**Response:**
```json
{
  "users": [
    {
      "id": 5,
      "email": "user@go.olemiss.edu",
      "first_name": "Alice",
      "last_name": "Smith",
      "year": "Sophomore",
      "major": "Biology",
      "has_survey": 1,
      "already_matched": 0
    }
  ]
}
```

### Grant Admin Access (Setup Endpoint)

```
POST /api/make-admin

Body:
{
  "email": "user@go.olemiss.edu"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Admin access granted to user@go.olemiss.edu"
}
```

**Note:** This endpoint does NOT require authentication. Secure it in production!

---

## Troubleshooting

### "Admin access required" Error

**Cause:** You're not logged in as an admin.

**Fix:**
1. Make sure you've been granted admin access
2. Log out and log back in
3. Check database: `SELECT is_admin FROM users WHERE email = 'your-email'`

### Admin Link Not Showing

**Cause:** JavaScript not detecting admin status.

**Fix:**
1. Open browser console (F12)
2. Check for errors
3. Verify `/api/admin/check` endpoint returns `{"is_admin": true}`
4. Hard refresh page (Ctrl + F5)

### Cannot Make First Admin

**Cause:** Make admin portal not working.

**Fix:**
1. Check Railway logs for errors
2. Verify `/api/make-admin` endpoint exists
3. Use Python script method instead (see above)

### Match Creation Failed

**Cause:** One or both users already matched or missing profile.

**Fix:**
1. Check "Potential Matches" tab for user status
2. If already matched, break up their existing match first
3. Ensure both users have completed profiles

---

## Database Schema Reference

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    email_verified BOOLEAN DEFAULT 0,
    email_verification_token TEXT,
    is_admin BOOLEAN DEFAULT 0,  -- Admin flag
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Field:**
- `is_admin`: 0 = regular user, 1 = admin

### Matches Table

```sql
CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES users(id),
    FOREIGN KEY (user2_id) REFERENCES users(id),
    UNIQUE(user1_id, user2_id)
);
```

**Note:** Always stores lower user_id as user1_id.

---

## Best Practices

### Managing Users

1. **Don't delete users unnecessarily** - Deletion is permanent
2. **Document manual actions** - Keep notes on why you edited/deleted
3. **Verify before deleting** - Double-check user email
4. **Limit admin access** - Only grant to trusted individuals

### Managing Matches

1. **Let organic matching work first** - Only manually create matches when necessary
2. **Communicate with users** - Let them know if you're breaking up their match
3. **Check compatibility** - Review survey responses before manually matching
4. **Monitor messages** - See if manually created matches are working out

### Security

1. **Disable make_admin portal** after creating your first admin
2. **Use strong passwords** for admin accounts
3. **Don't share admin credentials**
4. **Regular audits** - Check who has admin access periodically
5. **Log admin actions** - Consider adding logging for admin operations

---

## Future Enhancements

Potential features to add:

- [ ] Admin action logging/audit trail
- [ ] Bulk operations (delete multiple users, etc.)
- [ ] Advanced filtering and search
- [ ] Export data to CSV
- [ ] View and moderate messages
- [ ] Analytics dashboard with charts
- [ ] Email notifications to users
- [ ] Scheduled reports

---

## Support

If you encounter issues with the admin panel:

1. Check Railway logs for backend errors
2. Check browser console for frontend errors
3. Verify database connectivity
4. Review API endpoint responses
5. Test with different browsers

---

**End of Admin Guide**

*Keep this guide secure - it contains information about admin capabilities.*

**Quick Links:**
- [Main Documentation](PROJECT_SUMMARY.md)
- [Deployment Guide](QUICK_START_GUIDE.md)
- [Railway Dashboard](https://railway.app/dashboard)
