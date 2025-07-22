# Step-by-Step Render Deployment Fix

## Current Issue
Your Render deployment at https://magmacraft-bot.onrender.com is showing the old simple version instead of the updated dashboard.

## Required Files to Push to GitHub
Make sure these files are in your repository:

1. `app.py` (NEW - main entry point)
2. `render.yaml` (UPDATED - with new start command)
3. `Procfile` (NEW - alternative start method)
4. `web_app.py` (UPDATED - with fixes)
5. `templates/` folder (login.html, server_selection.html, dashboard.html)
6. `static/` folder (CSS and JS files)
7. `requirements.txt`

## Step 1: Verify Files Are Pushed
Run these commands in your terminal:

```bash
git add .
git commit -m "Fix Render deployment with new app.py entry point"
git push origin main
```

## Step 2: Update Render Service Configuration

Go to https://dashboard.render.com and find your service, then:

1. **Settings Tab** → **Build & Deploy**
2. Change "Start Command" to: `gunicorn --config gunicorn.conf.py app:app`
3. Click "Save Changes"

## Step 3: Add Environment Variables

In Render Dashboard → **Environment** tab, add:

```
FLASK_SECRET_KEY = any_random_string_here
DISCORD_CLIENT_ID = your_discord_application_id
DISCORD_CLIENT_SECRET = your_discord_application_secret
DISCORD_BOT_TOKEN = your_bot_token
FLASK_ENV = production
```

## Step 4: Manual Deploy

1. Go to **Deploys** tab
2. Click "Deploy latest commit"
3. Wait for deployment to complete

## Step 5: Test

After deployment, visit https://magmacraft-bot.onrender.com

- If you see configuration error page → Environment variables missing
- If you see login page → Success! Discord OAuth working
- If still old version → Start command not updated

## Alternative: Force Render Update

If still not working, in Render dashboard:

1. **Settings** → **General**
2. Click "Suspend Service"
3. Wait 30 seconds
4. Click "Resume Service"

This forces a complete restart with new configuration.

## Debug Information

Visit https://magmacraft-bot.onrender.com/api/health after deployment to see current status and missing configuration.