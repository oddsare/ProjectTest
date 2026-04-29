#!/usr/bin/env python3
"""
Make Admin Script - Roomi
Grant admin access to a user by email
"""

import sqlite3
import sys

def make_admin(email):
    """Grant admin access to a user by email"""
    try:
        # Connect to database
        db = sqlite3.connect('roomi.db')
        cursor = db.cursor()

        # Check if user exists
        cursor.execute('SELECT id, email, is_admin FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if not user:
            print(f'❌ Error: User with email "{email}" not found.')
            print('   Please register an account first at your app URL.')
            db.close()
            return False

        user_id, user_email, is_admin = user

        if is_admin:
            print(f'ℹ️  User "{email}" is already an admin.')
            db.close()
            return True

        # Grant admin access
        cursor.execute('UPDATE users SET is_admin = 1 WHERE id = ?', (user_id,))
        db.commit()
        db.close()

        print(f'✅ Success! Admin access granted to: {email}')
        print(f'   User ID: {user_id}')
        print()
        print('Next steps:')
        print('1. Log out of your account (if logged in)')
        print('2. Log back in')
        print('3. Look for the "Admin" link in the navigation bar')

        return True

    except sqlite3.Error as e:
        print(f'❌ Database error: {e}')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

def list_users():
    """List all users in the database"""
    try:
        db = sqlite3.connect('roomi.db')
        cursor = db.cursor()

        cursor.execute('''
            SELECT u.id, u.email, u.first_name, u.last_name, u.is_admin, u.created_at
            FROM users u
            ORDER BY u.created_at DESC
        ''')
        users = cursor.fetchall()

        if not users:
            print('No users found in database.')
            db.close()
            return

        print('\nUsers in database:')
        print('-' * 80)
        print(f'{"ID":<5} {"Email":<30} {"Name":<20} {"Admin":<7} {"Created"}')
        print('-' * 80)

        for user in users:
            user_id, email, first_name, last_name, is_admin, created_at = user
            name = f'{first_name or ""} {last_name or ""}'.strip() or '-'
            admin_status = '✓ Yes' if is_admin else '  No'
            created = created_at[:10] if created_at else '-'
            print(f'{user_id:<5} {email:<30} {name:<20} {admin_status:<7} {created}')

        print('-' * 80)
        print(f'Total: {len(users)} users')

        db.close()

    except sqlite3.Error as e:
        print(f'❌ Database error: {e}')
    except Exception as e:
        print(f'❌ Error: {e}')

def main():
    print('=' * 80)
    print('Roomi - Make Admin Script')
    print('=' * 80)
    print()

    if len(sys.argv) > 1:
        if sys.argv[1] == '--list' or sys.argv[1] == '-l':
            list_users()
            return

        # Email provided as command line argument
        email = sys.argv[1]
        make_admin(email)
    else:
        # Interactive mode
        print('This script grants admin access to a Roomi user account.')
        print()

        choice = input('Enter "1" to make a user admin, "2" to list all users: ').strip()

        if choice == '2':
            list_users()
            print()
            retry = input('\nWould you like to make a user admin? (y/n): ').strip().lower()
            if retry != 'y':
                print('Exiting.')
                return

        print()
        email = input('Enter the email address of the user to make admin: ').strip()

        if not email:
            print('❌ Error: Email address is required.')
            return

        if not email.endswith('@go.olemiss.edu'):
            print('⚠️  Warning: Email does not end with @go.olemiss.edu')
            confirm = input('   Continue anyway? (y/n): ').strip().lower()
            if confirm != 'y':
                print('Cancelled.')
                return

        print()
        make_admin(email)

if __name__ == '__main__':
    main()
