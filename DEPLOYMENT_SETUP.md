# Discord Bot Dashboard Deployment Setup

## 🔗 Your Dashboard Links

### Development Link (Current)
- **Login Page**: http://localhost:5000
- **Direct Server Selection**: http://localhost:5000/server-selection

### Production Link (After Deployment)
When deployed on Replit, your dashboard will be available at:
- **Public Login Link**: `https://YOUR-REPL-NAME.YOUR-USERNAME.replit.app`
- This link can be shared with anyone who needs to manage your Discord servers

## 🛠️ Required Discord Developer Portal Setup

To complete the public login system, you need to update your Discord application settings:

### 1. Go to Discord Developer Portal
Visit: https://discord.com/developers/applications

### 2. Select Your Bot Application
Click on the application you created for this bot

### 3. Configure OAuth2 Settings
Navigate to **OAuth2** → **General**

### 4. Add Redirect URIs
Add these redirect URIs (replace with your actual Replit app URL):

**For Development:**
```
http://localhost:5000/api/auth/callback
```

**For Production:**
```
https://YOUR-REPL-NAME.YOUR-USERNAME.replit.app/api/auth/callback
```

### 5. Required OAuth2 Scopes
Ensure these scopes are selected:
- `identify` - Read user's Discord profile
- `guilds` - Access user's Discord servers

## 🎯 How Users Will Login

1. Users visit your dashboard link
2. Click "Continue with Discord"
3. Authorize your application on Discord
4. Get redirected back to your dashboard
5. Can manage all Discord servers where they have admin permissions

## 🔐 Security Features

- ✅ Discord OAuth2 authentication
- ✅ Session-based user management
- ✅ Server permission validation
- ✅ Secure token handling
- ✅ Automatic logout functionality

## 📱 Dashboard Features Available After Login

- **Server Management**: View and manage all Discord servers
- **Music Control**: YouTube music player with queue management
- **Moderation Tools**: User management, auto-moderation settings
- **Minecraft Monitoring**: Real-time server status tracking
- **Bot Configuration**: Settings, tokens, and preferences
- **Analytics**: Command usage, uptime, and performance metrics

## 🚀 Next Steps

1. **Update Discord OAuth settings** (see steps above)
2. **Deploy to Replit** using the deploy button
3. **Share your public dashboard link** with server administrators
4. **Test the complete flow** by logging in through Discord

## 🆘 Troubleshooting

**"OAuth not configured" error:**
- Verify DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET are set in Replit Secrets

**"Redirect URI mismatch" error:**
- Double-check the redirect URIs in Discord Developer Portal match exactly

**"No servers found" error:**
- User needs admin permissions in at least one Discord server
- Bot must be invited to the servers first

**Login fails:**
- Clear browser cookies and try again
- Verify Discord application status is not disabled