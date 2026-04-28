# Quick Start Guide - Deploy Any Project to Railway

**For future reference when deploying new projects**

---

## Part 1: Upload Code to GitHub

### Step 1: Initialize Git in Your Project

```bash
cd "path/to/your/project"
git init
git branch -M main
```

### Step 2: Configure Git (First Time Only)

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 3: Create .gitignore File

**Create file:** `.gitignore`

**Add these lines:**
```
# Secrets
.env
.env.local
*.txt (files with passwords/secrets)

# Database
*.db
*.sqlite

# Python
__pycache__/
*.pyc
venv/
env/

# Uploads/User content
uploads/
*.jpg
*.png
*.pdf

# IDE
.vscode/
.idea/
```

### Step 4: Commit Your Code

```bash
git add .
git commit -m "Initial commit"
```

### Step 5: Create GitHub Repository

**Option A - GitHub Website:**
1. Go to: https://github.com/new
2. Repository name: `your-project-name`
3. Description: Brief description
4. Public or Private: Choose
5. **DO NOT** check "Add README" (you already have files)
6. Click "Create repository"

**Option B - GitHub CLI (if installed):**
```bash
gh repo create your-project-name --public --source=. --push
```

### Step 6: Push to GitHub

**Copy commands from GitHub page:**
```bash
git remote add origin https://github.com/yourusername/your-project-name.git
git push -u origin main
```

**Done!** Code now on GitHub: `https://github.com/yourusername/your-project-name`

---

## Part 2: Deploy to Railway

### Step 1: Sign Up / Log In

1. Go to: https://railway.app
2. Click "Login"
3. Choose "Login with GitHub"
4. Authorize Railway

### Step 2: Create New Project

1. Click **"New Project"** (big purple button)
2. Select **"Deploy from GitHub repo"**
3. Find your repository: `yourusername/your-project-name`
4. Click it

**Railway auto-detects:**
- Python → installs from `requirements.txt`
- Node.js → installs from `package.json`
- Looks for `Procfile` to start app

### Step 3: Add Environment Variables

**After Railway starts building:**

1. Click your project name
2. Click **"Variables"** tab (top menu)
3. Click **"+ New Variable"**
4. Add each variable one by one:

**Example for Flask app:**
```
SECRET_KEY = (your generated secret key)
FLASK_ENV = production
FLASK_DEBUG = False
```

**Example for Node app:**
```
NODE_ENV = production
PORT = 3000
DATABASE_URL = (if using database)
```

5. Railway auto-redeploys after adding variables

### Step 4: Get Your URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Railway gives you URL: `https://your-app-production.up.railway.app`

**Done!** App is live.

---

## Part 3: Update Your Deployed App

**Every time you make changes:**

```bash
git add .
git commit -m "Description of what you changed"
git push origin main
```

**Railway automatically:**
- Detects new commit
- Rebuilds app
- Redeploys (~2-3 minutes)

**Check deployment:**
1. Go to Railway dashboard
2. Click "Deployments" tab
3. See latest deployment status:
   - 🟡 Building
   - 🟢 Active (success)
   - 🔴 Failed (check logs)

---

## Part 4: Required Files for Railway

### For Python/Flask Apps

**1. `requirements.txt`** (required)
```
Flask==3.0.0
Flask-CORS==4.0.0
gunicorn==21.2.0
```

**Generate automatically:**
```bash
pip freeze > requirements.txt
```

**2. `Procfile`** (required)
```
web: gunicorn app:app
```

**Format:** `web: gunicorn <your-python-file>:app`

**3. `.gitignore`** (recommended)
```
.env
*.db
__pycache__/
venv/
```

### For Node.js Apps

**1. `package.json`** (required)
```json
{
  "name": "your-app",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

**2. `Procfile`** (optional, Railway auto-detects)
```
web: npm start
```

**3. `.gitignore`** (recommended)
```
node_modules/
.env
*.log
```

---

## Part 5: Generate Secret Keys

**For Flask (SECRET_KEY):**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**For Node.js (JWT_SECRET, etc):**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Copy output → Paste into Railway Variables**

---

## Part 6: Common Issues & Fixes

### Issue: "Application Error" on Railway

**Fix:**
1. Click "Deployments" → Latest deployment
2. Click "View Logs"
3. Look for error message
4. Common causes:
   - Missing environment variable
   - Wrong `Procfile` command
   - Missing dependency in `requirements.txt`

### Issue: Changes Not Showing

**Fix:**
1. Check Railway "Deployments" - is it building?
2. Hard refresh browser: `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
3. Clear browser cache
4. Check correct URL (Railway gives new URL sometimes)

### Issue: Database Not Persisting

**Cause:** SQLite on Railway uses ephemeral storage

**Fix:**
1. Add Railway PostgreSQL addon
2. Update code to use PostgreSQL
3. Or: Accept data loss on redeploy (fine for demos)

### Issue: Files (uploads) Not Persisting

**Cause:** Railway ephemeral storage

**Fix:**
1. Use cloud storage: AWS S3, Cloudinary, etc.
2. Or: Accept file loss on redeploy (fine for demos)

---

## Part 7: Railway Free Tier Limits

**Free tier includes:**
- $5 credit per month (FREE)
- ~500 hours uptime per month
- HTTPS automatic
- Auto-deploy from GitHub
- Environment variables
- Logs and monitoring

**When you pay:**
- App uses more than $5/month in resources
- Heavy traffic (hundreds of concurrent users)
- Running 24/7 all month might exceed $5

**For school projects:** Free tier = plenty

**Cost management:**
- Pause app when not using: Railway dashboard → "Pause"
- Delete old projects: Frees up resources

---

## Part 8: Checklist for New Project

**Before deploying:**

- [ ] Code works locally
- [ ] Created `requirements.txt` or `package.json`
- [ ] Created `Procfile`
- [ ] Created `.gitignore`
- [ ] No secrets in code (use env vars)
- [ ] No database files committed
- [ ] Generated SECRET_KEY

**Deploy to GitHub:**

- [ ] `git init`
- [ ] `git add .`
- [ ] `git commit -m "Initial commit"`
- [ ] Created GitHub repo
- [ ] `git push origin main`

**Deploy to Railway:**

- [ ] Signed up for Railway
- [ ] Connected GitHub repo
- [ ] Added environment variables
- [ ] Generated domain
- [ ] Tested live URL

**After deployment:**

- [ ] Tested all features
- [ ] Checked logs for errors
- [ ] Documented environment variables
- [ ] Created README with live URL

---

## Part 9: Working with AI Assistants

**Tell AI to deploy your project:**

```
I have a [Flask/Node/etc] app I want to deploy to Railway.

Files in my project:
- [list main files]

Please help me:
1. Create necessary deployment files (.gitignore, Procfile, etc)
2. Push to GitHub
3. Deploy to Railway
4. Configure environment variables

Project location: [path to your project]
```

**AI will:**
- Create deployment files
- Generate secret keys
- Guide you through Railway setup
- Fix deployment issues

**Tips:**
- Give AI your project path
- Mention what type of app (Flask, Express, etc)
- Share error messages if deployment fails
- Ask for explanations if confused

---

## Part 10: Quick Command Reference

### Git Commands

```bash
# Initialize git
git init
git branch -M main

# Check status
git status

# Add all files
git add .

# Commit changes
git commit -m "Message here"

# Push to GitHub
git push origin main

# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See changes before committing
git diff
```

### Generate Secrets

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Python/Flask

```bash
# Create requirements.txt
pip freeze > requirements.txt

# Install dependencies
pip install -r requirements.txt

# Run local server
python app.py
```

### Node.js

```bash
# Initialize package.json
npm init -y

# Install dependency
npm install express

# Run app
npm start
```

---

## Part 11: Example .env File Template

**Create `.env` file locally (never commit):**

```bash
# Flask App
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///app.db

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# API Keys (example)
OPENAI_API_KEY=sk-...
STRIPE_KEY=sk_test_...
```

**In Railway:** Add same variables (without quotes)

---

## Part 12: Railway vs Other Platforms

| Platform | Free Tier | Best For | Notes |
|----------|-----------|----------|-------|
| **Railway** | $5/month credit | All apps | Easy, auto-deploy |
| **Render** | Free tier | Static sites, APIs | Slower cold starts |
| **Vercel** | Free | Next.js, frontend | Serverless |
| **Netlify** | Free | Static sites | Great for React/Vue |
| **Heroku** | No free tier | N/A | Paid only now |
| **PythonAnywhere** | Limited free | Python apps | Simpler setup |

**Recommendation:** Railway = best for school projects

---

## Part 13: Save This Guide

**Location of this file:**
```
Desktop > GroupProjectRoomi > QUICK_START_GUIDE.md
```

**Or copy to:**
```
C:\Users\Gilbe\Documents\Railway_Guide.md
```

**Bookmark these:**
- Railway Dashboard: https://railway.app/dashboard
- GitHub Repos: https://github.com/yourusername?tab=repositories
- Railway Docs: https://docs.railway.app

---

## Summary - The 5-Minute Deploy

**Fastest deployment process:**

```bash
# 1. Push to GitHub (2 min)
cd your-project
git init && git add . && git commit -m "Deploy"
git remote add origin https://github.com/user/repo.git
git push -u origin main

# 2. Deploy on Railway (2 min)
# - Visit railway.app
# - Click "New Project" → "Deploy from GitHub"
# - Select your repo
# - Add SECRET_KEY environment variable
# - Generate domain

# 3. Done (1 min)
# - Visit your Railway URL
# - Test the app
```

**Total time:** ~5 minutes for simple apps

---

**End of Quick Start Guide**

*Keep this file for future projects!*

**Next time you deploy:**
1. Read Part 1 (GitHub upload)
2. Read Part 2 (Railway deploy)
3. Reference Part 10 (commands)

Good luck! 🚀
