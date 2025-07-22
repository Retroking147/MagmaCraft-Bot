# Fix 502 Error - Render Configuration

## Current Issue
Files are synced to GitHub, but Render still shows 502 error because the start command needs to be updated.

## Fix in Render Dashboard

### 1. Update Start Command
Go to your MagmaCraft-Bot web service in Render:
- Click "Settings" tab
- Find "Start Command" field
- Replace with: `gunicorn run_web_only:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

### 2. Alternative Start Commands (if first fails)
Try these in order:
```bash
python run_web_only.py
```
```bash
gunicorn -c gunicorn.conf.py run_web_only:app
```

### 3. Environment Variables Double-Check
Ensure these are set:
- `DATABASE_URL` (from PostgreSQL database)
- `DISCORD_BOT_TOKEN`
- `DISCORD_CLIENT_ID` 
- `DISCORD_CLIENT_SECRET`
- `FLASK_SECRET_KEY` = `discord-bot-dashboard-secret-2025`

### 4. Manual Deploy
After updating start command:
1. Click "Manual Deploy" tab
2. Click "Deploy Latest Commit"
3. Wait 2-3 minutes for deployment

## What This Fixes
The new files include error handling that will show either:
1. Full Discord dashboard (if everything works)
2. Health check page (if there are issues, but service is online)

No more 502 errors - you'll get a working page either way.