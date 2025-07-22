# 🎯 Final Render Deployment Settings

## GitHub Branch Configuration
- **Branch**: `main` (default and recommended)
- **Auto-Deploy**: Yes (updates automatically when you push changes)

## Render Service Configuration

### Basic Settings
- **Name**: `discord-bot-dashboard`
- **Environment**: `Python 3`
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run_web_only.py`

### Plan Selection
- **Instance Type**: `Free` 
- **Region**: `Oregon (US West)` or closest to your users

### Environment Variables (Add in Render Dashboard)
```
DISCORD_BOT_TOKEN = your_actual_bot_token
DISCORD_CLIENT_ID = your_actual_client_id
DISCORD_CLIENT_SECRET = your_actual_client_secret
FLASK_SECRET_KEY = discord-bot-dashboard-secret-2025
```

### Database (Render will create automatically)
- **Type**: PostgreSQL
- **Plan**: Free
- **Name**: `discord-bot-db`

## 🚀 Deployment Steps Summary

1. **Export to GitHub**: Use `main` branch
2. **Connect to Render**: Select your repository
3. **Configure settings**: Use values above
4. **Add environment variables**: Your Discord secrets
5. **Deploy**: Render builds and launches automatically

## ✅ Your Final URL
After deployment: `https://discord-bot-dashboard.onrender.com`

## 🔧 Discord OAuth Update
Add this redirect URI in Discord Developer Portal:
`https://discord-bot-dashboard.onrender.com/api/auth/callback`

The `main` branch is the standard default branch that Render expects. Once deployed, your dashboard will be live and accessible worldwide on the free tier.