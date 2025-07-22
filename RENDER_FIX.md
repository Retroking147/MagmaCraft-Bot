# 🔧 Fix Render Deployment Error

## The Problem
Render can't find `requirements.txt` and is failing to install dependencies.

## Quick Fix Steps

### 1. Add requirements.txt to GitHub
You need to add a `requirements.txt` file to your GitHub repository:

1. Go to your GitHub repo: `https://github.com/Retroking147/MagmaCraft-Bot`
2. Click "Add file" → "Create new file"
3. Name it: `requirements.txt`
4. Add this content:
```
discord.py==2.3.2
flask==3.0.0
flask-migrate==4.0.5
flask-sqlalchemy==3.1.1
psycopg2-binary==2.9.9
pynacl==1.5.0
python-dotenv==1.0.0
requests==2.32.4
sqlalchemy==2.0.25
gunicorn==21.2.0
```
5. Commit the file

### 2. Update Render Settings
In your Render dashboard:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run_web_only:app --host 0.0.0.0 --port $PORT`

### 3. Add Missing Environment Variables
Make sure these are set in Render:
- `DISCORD_BOT_TOKEN`
- `DISCORD_CLIENT_ID` 
- `DISCORD_CLIENT_SECRET`
- `FLASK_SECRET_KEY`
- `DATABASE_URL` (auto-provided by Render)

### 4. Manual Deploy
Click "Manual Deploy" in Render to rebuild with the requirements.txt file.

## Alternative Start Command
If the gunicorn command doesn't work, try:
`python run_web_only.py`

Your dashboard should then be accessible at your Render URL without the 504 error.