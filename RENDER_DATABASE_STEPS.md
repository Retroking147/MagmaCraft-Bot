# Add PostgreSQL Database - Exact Steps

## From Your Current Render Dashboard:

### Step 1: Create Database
1. Click the **"Create +"** button (top right, next to your profile)
2. Select **"PostgreSQL"**
3. Fill in:
   - **Name**: `magmacraft-bot-database`
   - **Database**: `magmacraft_bot`
   - **User**: `magmacraft_user`
   - **Region**: Same as your web service (likely Oregon)
   - **Plan**: **Free** (good for development)
4. Click **"Create Database"**

### Step 2: Connect Database to Web Service
1. Wait for database to finish creating (shows "Live" status)
2. Click on your **"MagmaCraft-Bot"** web service
3. Go to **"Environment"** tab (left sidebar)
4. Click **"Add Environment Variable"**
5. For the DATABASE_URL:
   - **Key**: `DATABASE_URL`
   - **Value**: Click **"Add from Database"** dropdown
   - Select your new PostgreSQL database
   - This auto-fills the connection string

### Step 3: Verify All Environment Variables
Make sure you have all these in your web service Environment:
- `DISCORD_BOT_TOKEN`
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `FLASK_SECRET_KEY`
- `DATABASE_URL` (from database)

### Step 4: Redeploy
1. Go to **"Manual Deploy"** tab
2. Click **"Deploy Latest Commit"**
3. Wait for deployment to complete

Your dashboard will then be live at the URL shown in your service!