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
   - `ADMIN_SECRET` = (generate a random string — required to create API keys via `POST /api-keys`; see README_API.md)
   - `FLASK_ENV` = production

5. Click "Create Web Service"

## Step 4: Background monitoring — no separate service needed

Earlier versions of this guide had you deploy a second Render service ("Background Worker") running `python -m api.workers.scheduler` for wallet monitoring. **Don't do this — it doesn't work and isn't needed.**

`api/workers/scheduler.py` has no `__main__` entrypoint, so running it standalone just imports the module and exits immediately without doing anything. It would sit in a restart loop on Render, consuming a service slot for zero benefit.

The actual wallet-monitoring scheduler starts automatically **inside the web service itself** — `create_app()` calls `start_scheduler(app)` on startup, running an in-process APScheduler job every `MONITOR_INTERVAL_SECONDS` (default 60s). As long as the web service from Step 3 is running, monitoring is running. If you previously created a separate worker service for this, it's safe to delete it.

## Step 5: Database Initialization — automatic, no action needed

Tables are created automatically the first time the app starts (`db.create_all()` runs eagerly during app startup, before the scheduler or any request). There's no `migrations/` directory in this repo, so **don't run `flask db upgrade`** — there's nothing for it to apply, and it will error since no Alembic environment is set up.

## Step 6: Test Your Deployment
```bash
# Test health endpoint (note: no /api/v1 prefix)
curl https://your-app.onrender.com/health

# Should return:
# {"status": "healthy", "database": "connected", "version": "1.0.0"}

# Create an API key (requires ADMIN_SECRET from Step 3)
curl -X POST https://your-app.onrender.com/api/v1/api-keys \
  -H "Content-Type: application/json" \
  -H "X-Admin-Secret: your_admin_secret" \
  -d '{"name": "smoke-test"}'

# Confirm the wallets endpoint requires that key
curl https://your-app.onrender.com/api/v1/wallets
# Should return 401, not wallet data
```

## Troubleshooting

- **Database connection errors:** Check `DATABASE_URL` is correct
- **`POST /api-keys` returns 401:** Check `ADMIN_SECRET` is set and you're sending it as `X-Admin-Secret`, not `X-API-Key`
- **Wallets not being monitored:** Check the *web* service logs (not a separate worker — there isn't one) for scheduler startup messages
- **Web3 errors:** Verify `WEB3_PROVIDER_URI` is valid — the app will fail to start entirely if it can't connect at boot, since the scheduler's `Web3Service` initializes eagerly
