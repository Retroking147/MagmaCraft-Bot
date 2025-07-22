# Fix 502 Error on Render

## Updated Render Configuration

### Build Command:
```
pip install -r requirements.txt
```

### Start Command (try each one):
**Option 1 (Recommended):**
```
gunicorn run_web_only:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

**Option 2 (Alternative):**
```
python run_web_only.py
```

**Option 3 (If gunicorn issues):**
```
gunicorn -c gunicorn.conf.py run_web_only:app
```

### Environment Variables Check:
Ensure these are set in Render:
- `DISCORD_BOT_TOKEN` (your bot token)
- `DISCORD_CLIENT_ID` (your Discord app ID)
- `DISCORD_CLIENT_SECRET` (your Discord app secret)
- `FLASK_SECRET_KEY` = `discord-bot-dashboard-secret-2025`

### Database Setup:
1. In Render, add a PostgreSQL database
2. Connect it to your web service
3. Render will automatically set `DATABASE_URL`

## Common 502 Fixes:
1. **Port Issue**: Gunicorn command fixes port binding
2. **Database Connection**: Add PostgreSQL database in Render
3. **Dependencies**: requirements.txt is now correct
4. **Timeout**: Increased timeout to 120 seconds

Try Option 1 start command first, then redeploy manually in Render.