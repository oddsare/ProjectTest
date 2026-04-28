# Railway Deployment Guide for Roomi

## Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- Your code pushed to a GitHub repository

## Security Checklist ✅

### Before Deploying:
1. ✅ Passwords are properly hashed using `werkzeug.security`
2. ✅ No hard-coded secrets in the code
3. ✅ `.gitignore` prevents sensitive files from being committed
4. ✅ Environment variables will be configured in Railway dashboard
5. ⚠️ **IMPORTANT:** Do NOT commit `roomi.db` - Railway will create a new one
6. ⚠️ **IMPORTANT:** Do NOT run `create_test_accounts.py` in production

## Step-by-Step Deployment

### 1. Push Your Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Ready for Railway deployment"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy to Railway

1. Go to https://railway.app and log in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect it's a Python app

### 3. Configure Environment Variables

In your Railway project dashboard:

1. Click on your project
2. Go to "Variables" tab
3. Add the following variables:

**Required:**
```
SECRET_KEY = <generate a random 64-character hex string>
FLASK_ENV = production
FLASK_DEBUG = False
```

**Optional (for email functionality):**
```
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
SMTP_USER = your-email@gmail.com
SMTP_PASSWORD = your-app-specific-password
```

**How to generate SECRET_KEY:**
Run this command locally:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste it as your SECRET_KEY value.

### 4. Database Setup

Railway uses ephemeral storage, so your SQLite database will be recreated on each deployment. For production, consider:

**Option 1: Use Railway's PostgreSQL** (Recommended)
- Add a PostgreSQL database from Railway's service catalog
- Update your app to use PostgreSQL instead of SQLite

**Option 2: Keep SQLite** (Simpler, but data lost on redeploys)
- Database will auto-initialize via `init_db()` in app.py
- You'll need to recreate users after each deployment

### 5. Verify Deployment

1. Railway will provide a public URL (e.g., `https://your-app.railway.app`)
2. Visit the URL to test your application
3. Try registering a new account to verify everything works
4. Check the deployment logs in Railway dashboard if there are issues

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | ✅ Yes | Flask session encryption key | `a1b2c3d4...` (64 chars) |
| `FLASK_ENV` | ✅ Yes | Environment mode | `production` |
| `FLASK_DEBUG` | ✅ Yes | Debug mode | `False` |
| `SMTP_HOST` | ❌ No | Email server host | `smtp.gmail.com` |
| `SMTP_PORT` | ❌ No | Email server port | `587` |
| `SMTP_USER` | ❌ No | Email username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | ❌ No | Email app password | `your-app-password` |

## Security Best Practices

### ✅ What's Already Secure:
- Passwords are hashed with `generate_password_hash()`
- SECRET_KEY uses environment variables
- Password reset tokens are cryptographically secure
- Sessions are properly managed
- Email validation ensures Ole Miss domains only

### 🔒 Additional Security Recommendations:
1. **Never commit `.env` files** - Already in `.gitignore`
2. **Use strong SECRET_KEY** - Generate with `secrets.token_hex(32)`
3. **Monitor Railway logs** - Check for suspicious activity
4. **Regular updates** - Keep dependencies updated
5. **HTTPS only** - Railway provides this automatically

## Troubleshooting

### Common Issues:

**Issue: "500 Internal Server Error"**
- Check Railway logs for detailed error messages
- Verify all required environment variables are set
- Ensure SECRET_KEY is properly set

**Issue: "Database is locked"**
- SQLite has concurrency limitations
- Consider upgrading to PostgreSQL for production

**Issue: "Email not sending"**
- If SMTP variables not set, tokens will be returned in API response
- Check SMTP credentials are correct
- Verify "Less secure app access" or "App passwords" for Gmail

**Issue: "Lost database after redeploy"**
- This is expected with SQLite on Railway's ephemeral storage
- Upgrade to PostgreSQL for persistent storage

## Email Setup (Gmail)

If using Gmail for password reset emails:

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account → Security
   - 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the 16-character app password as `SMTP_PASSWORD`

## Next Steps

After successful deployment:

1. ✅ Test user registration
2. ✅ Test login/logout
3. ✅ Test profile creation
4. ✅ Test survey completion
5. ✅ Test password reset (if email configured)
6. 🚀 Share your app URL with users!

## Support

- Railway Documentation: https://docs.railway.app
- Flask Documentation: https://flask.palletsprojects.com
- Roomi Repository: [Your GitHub URL]

---

**Last Updated:** April 2026
**Deployment Status:** ✅ Production Ready
