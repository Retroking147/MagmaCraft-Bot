# Add PostgreSQL Database to Render

## Step-by-Step Database Setup

### 1. Create Database
1. In your Render dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. Configure:
   - **Name**: `magmacraft-bot-db`
   - **Database**: `magmacraft_bot`
   - **User**: `magmacraft_user`
   - **Plan**: **Free** (good for 90 days, then $7/month)
4. Click **"Create Database"**

### 2. Connect Database to Web Service
1. Go to your web service (`magmacraft-bot`)
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. **Key**: `DATABASE_URL`
5. **Value**: Click **"Add from Database"** → Select your PostgreSQL database
6. Save changes

### 3. Alternative: Auto-Connect Method
1. In your web service settings
2. Go to **"Environment"** tab
3. Scroll to **"Add from Database"**
4. Select your PostgreSQL database
5. It automatically adds `DATABASE_URL`

### 4. Verify Environment Variables
Your web service should now have:
- `DISCORD_BOT_TOKEN`
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `FLASK_SECRET_KEY`
- `DATABASE_URL` (auto-added from database)

### 5. Deploy
Click **"Manual Deploy"** to restart with database connection.

## Database Connection String Format
The `DATABASE_URL` will look like:
```
postgresql://user:password@host:port/database
```

## Free Tier Limits
- **Storage**: 1GB
- **Duration**: 90 days free, then $7/month
- **Connections**: Up to 97 concurrent

Your Discord dashboard will then have a working database for storing user sessions, bot statistics, and configuration data.