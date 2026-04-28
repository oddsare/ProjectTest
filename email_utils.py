"""
Email utility for sending notifications
Configure via environment variables:
  - SMTP_HOST (default: smtp.gmail.com)
  - SMTP_PORT (default: 587)
  - SMTP_USER (your email)
  - SMTP_PASSWORD (your app password)
  - SMTP_FROM (sender email, defaults to SMTP_USER)
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration from environment
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SMTP_FROM = os.environ.get('SMTP_FROM', SMTP_USER)
SMTP_ENABLED = os.environ.get('SMTP_ENABLED', 'False').lower() == 'true'

def send_email(to_email, subject, html_body, text_body=None):
    """
    Send an email

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of the email
        text_body: Plain text fallback (optional, will strip HTML if not provided)

    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not SMTP_ENABLED:
        print(f"[Email] SMTP disabled. Would have sent to {to_email}: {subject}")
        print(f"[Email] Body: {text_body or html_body}")
        return False

    if not SMTP_USER or not SMTP_PASSWORD:
        print("[Email] SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD environment variables.")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add plain text version
        if text_body:
            part1 = MIMEText(text_body, 'plain')
            msg.attach(part1)

        # Add HTML version
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())

        print(f"[Email] Successfully sent to {to_email}: {subject}")
        return True

    except Exception as e:
        print(f"[Email] Failed to send to {to_email}: {e}")
        return False

def send_password_reset_email(to_email, reset_token, base_url='http://localhost:8000'):
    """Send password reset email"""
    reset_link = f"{base_url}/reset-password.html?token={reset_token}"

    subject = "Roomi - Password Reset Request"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #CE1141; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">Roomi</h1>
                <p style="margin: 10px 0 0 0;">Ole Miss Roommate Matching</p>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
                <h2 style="color: #CE1141; margin-top: 0;">Password Reset Request</h2>

                <p>You requested to reset your password. Click the button below to create a new password:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background: #CE1141; color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">Reset Password</a>
                </div>

                <p style="color: #666; font-size: 14px;">Or copy and paste this link into your browser:</p>
                <p style="background: white; padding: 12px; border: 1px solid #ddd; border-radius: 4px; word-break: break-all; font-size: 13px;">{reset_link}</p>

                <p style="color: #999; font-size: 13px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Roomi - Password Reset Request

    You requested to reset your password. Visit this link to create a new password:
    {reset_link}

    This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.
    """

    return send_email(to_email, subject, html_body, text_body)

def send_match_notification(to_email, match_name, base_url='http://localhost:8000'):
    """Send new match notification email"""
    subject = f"Roomi - You have a new match with {match_name}!"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #CE1141; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">Roomi</h1>
                <p style="margin: 10px 0 0 0;">Ole Miss Roommate Matching</p>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
                <h2 style="color: #CE1141; margin-top: 0;">New Match!</h2>

                <p>Great news! <strong>{match_name}</strong> wants to connect with you.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/chat.html" style="background: #CE1141; color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">View Messages</a>
                </div>

                <p style="color: #666; font-size: 14px;">Log in to Roomi to start chatting and see if you're a good fit!</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Roomi - New Match!

    Great news! {match_name} wants to connect with you.

    Log in to Roomi to start chatting: {base_url}/chat.html
    """

    return send_email(to_email, subject, html_body, text_body)

def send_message_notification(to_email, sender_name, message_preview, base_url='http://localhost:8000'):
    """Send new message notification email"""
    subject = f"Roomi - New message from {sender_name}"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #CE1141; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">Roomi</h1>
                <p style="margin: 10px 0 0 0;">Ole Miss Roommate Matching</p>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
                <h2 style="color: #CE1141; margin-top: 0;">New Message</h2>

                <p><strong>{sender_name}</strong> sent you a message:</p>

                <div style="background: white; padding: 16px; border-left: 4px solid #CE1141; margin: 20px 0; font-style: italic;">
                    {message_preview}
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/chat.html" style="background: #CE1141; color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">Reply Now</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Roomi - New Message

    {sender_name} sent you a message:
    "{message_preview}"

    Reply now: {base_url}/chat.html
    """

    return send_email(to_email, subject, html_body, text_body)
