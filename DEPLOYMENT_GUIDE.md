# Deployment Guide for Discord Bot Dashboard

## Overview
Your Discord Bot Dashboard is ready for deployment. Here's how to deploy the updated version to Render or other platforms.

## For Render Deployment

### Step 1: Update Your Repository
Ensure your GitHub repository has all the latest files:

1. **Required Files for Production:**
   - `render.yaml` (updated with production config)
   - `requirements.txt` 
   - `run_web_only.py`
   - `web_app.py` (updated with fixes)
   - `gunicorn.conf.py`
   - All `/templates/` and `/static/` folders

### Step 2: Set Environment Variables in Render Dashboard

In your Render dashboard (https://dashboard.render.com), you need to set these environment variables:

```
DISCORD_CLIENT_ID=your_discord_app_client_id
DISCORD_CLIENT_SECRET=your_discord_app_client_secret
DISCORD_BOT_TOKEN=your_bot_token
FLASK_SECRET_KEY=any_random_secret_key
FLASK_ENV=production
```

### Step 3: Discord App Configuration
1. Go to https://discord.com/developers/applications
2. Select your bot application
3. In OAuth2 settings, add redirect URI: `https://magmacraft-bot.onrender.com/api/auth/callback`

### Step 4: Deploy
1. Push changes to your GitHub repository
2. Render will automatically redeploy
3. Wait for deployment to complete (5-10 minutes)

## For Other Platforms (Docker)

Use the included `Dockerfile` and `docker-compose.yml`:

```bash
docker-compose up -d
```

## Testing Production Deployment

1. Visit your Render URL: https://magmacraft-bot.onrender.com
2. You should see the new login interface
3. Click "Continue with Discord" to test OAuth
4. After login, you'll see the full dashboard with working buttons

## Troubleshooting

### Issue: Still seeing old version
- Force refresh browser (Ctrl+F5)
- Check that git repository is updated
- Verify Render is pulling from correct branch

### Issue: Discord login fails
- Verify environment variables are set in Render dashboard
- Check Discord app redirect URI is correct
- Ensure Discord app is not in development mode

### Issue: Database errors
- Render automatically creates PostgreSQL database
- Check DATABASE_URL environment variable exists
- Verify database service is running in Render

## Development Testing

For local testing, use the development login bypass:
- Visit `/dev-login` to skip Discord OAuth
- This only works when `FLASK_ENV=development`

## Production Features

Your dashboard now includes:
- Discord OAuth authentication
- Music player controls
- Moderation tools interface
- Minecraft server monitoring
- Real-time server statistics
- Professional Discord-styled UI
- Responsive design for mobile/desktop