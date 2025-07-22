# Final Steps to Fix 502 Error

## Copy Database URL

From your database screen:

1. **Copy the External Database URL** (the long masked string)
2. Click the copy icon next to "External Database URL"

## Add to Web Service

1. Go back to **MagmaCraft-Bot** web service
2. **Environment** tab
3. In the **DATABASE_URL** value field, paste the External Database URL
4. Click **"Save Changes"**

## Redeploy

1. Go to **"Manual Deploy"** tab
2. Click **"Deploy Latest Commit"**
3. Wait for deployment to complete

## Your Dashboard Will Be Live

After deployment completes, your Discord dashboard will be available at:
`https://magmacraft-bot.onrender.com`

With features:
- Professional Discord OAuth login
- Music player controls
- Moderation tools
- Minecraft server monitoring
- Bot management interface

The External Database URL contains all the connection info (host, port, username, password, database name) that your Flask app needs to connect to PostgreSQL.