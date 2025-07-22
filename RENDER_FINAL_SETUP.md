# Get Database Connection String

## Manual DATABASE_URL Setup

Since the dropdown isn't appearing, you need to manually get the connection string:

### Step 1: Get Database Connection Info
1. Go to your PostgreSQL database (not the web service)
2. Click on your database name in the left sidebar
3. Look for **"Connections"** or **"Info"** tab
4. Copy the **"External Database URL"** or **"Connection String"**

It will look like:
```
postgresql://username:password@hostname:port/database_name
```

### Step 2: Add to Web Service
1. Go back to your MagmaCraft-Bot web service
2. Environment tab
3. Paste the connection string in the DATABASE_URL value field
4. Click "Save Changes"

### Step 3: Alternative - Environment Variable Format
If you see separate connection details, format them as:
```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Example:
```
postgresql://magmacraft_user:abc123@dpg-xyz.oregon-postgres.render.com:5432/magmacraft_bot
```

### Step 4: Redeploy
After adding DATABASE_URL:
1. Go to "Manual Deploy" tab
2. Click "Deploy Latest Commit"
3. Wait for deployment to complete

This will connect your Discord dashboard to the database and fix the 502 error.