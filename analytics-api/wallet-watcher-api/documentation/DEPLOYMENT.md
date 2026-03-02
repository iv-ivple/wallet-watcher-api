# Deployment Guide

## Prerequisites
- GitHub account
- Render account (free tier)
- Alchemy API key for Ethereum access

## Step 1: Prepare Your Code

1. Make sure all files are committed to Git
2. Push to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Step 2: Set Up Render Database

1. Go to render.com and log in
2. Click "New +" → "PostgreSQL"
3. Name it: `wallet-watcher-db`
4. Select free tier
5. Click "Create Database"
6. Copy the "Internal Database URL" (you'll need this)

## Step 3: Deploy Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** wallet-watcher-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api.app:app`
4. Add Environment Variables:
   - `DATABASE_URL` = (paste the database URL from step 2)
   - `WEB3_PROVIDER_URI` = your Alchemy URL
   - `SECRET_KEY` = (generate a random string)
   - `FLASK_ENV` = production

5. Click "Create Web Service"

## Step 4: Deploy Worker Service

1. Click "New +" → "Background Worker"
2. Connect same repository
3. Configure:
   - **Name:** wallet-monitor-worker
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m api.workers.scheduler`
4. Add same environment variables as web service
5. Click "Create"

## Step 5: Initialize Database

Once deployed, run migrations:
```bash
# SSH into your Render service or use Render shell
flask db upgrade
```

## Step 6: Test Your Deployment
```bash
# Test health endpoint
curl https://your-app.onrender.com/health

# Should return:
# {"status": "healthy", "database": "connected", "version": "1.0.0"}
```

## Troubleshooting

- **Database connection errors:** Check DATABASE_URL is correct
- **Worker not running:** Check worker logs in Render dashboard
- **Web3 errors:** Verify WEB3_PROVIDER_URI is valid
