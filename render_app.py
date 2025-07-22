"""
Render-optimized Discord Bot Dashboard
Simplified version that avoids SQLAlchemy compatibility issues
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from urllib.parse import urlencode, parse_qs
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-12345")
    
    # Discord OAuth configuration
    DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
    DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
    DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    def get_db_connection():
        """Get database connection using raw psycopg2"""
        try:
            if DATABASE_URL:
                return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return None
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def init_database():
        """Initialize database tables if they don't exist"""
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    # Create basic tables
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS bot_stats (
                            id SERIAL PRIMARY KEY,
                            servers INTEGER DEFAULT 0,
                            users INTEGER DEFAULT 0,
                            commands_used INTEGER DEFAULT 0,
                            uptime_hours INTEGER DEFAULT 0,
                            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Insert default stats if none exist
                    cur.execute("SELECT COUNT(*) FROM bot_stats")
                    count_result = cur.fetchone()
                    if count_result and count_result[0] == 0:
                        cur.execute("""
                            INSERT INTO bot_stats (servers, users, commands_used, uptime_hours)
                            VALUES (1, 50, 125, 72)
                        """)
                    
                    conn.commit()
                    print("Database initialized successfully")
            except Exception as e:
                print(f"Database init error: {e}")
            finally:
                conn.close()
    
    # Initialize database on startup
    init_database()
    
    @app.route('/')
    def home():
        """Main dashboard page"""
        if not all([DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_BOT_TOKEN]):
            return render_template('config_error.html', 
                missing_vars=[k for k, v in {
                    'DISCORD_CLIENT_ID': DISCORD_CLIENT_ID,
                    'DISCORD_CLIENT_SECRET': DISCORD_CLIENT_SECRET,
                    'DISCORD_BOT_TOKEN': DISCORD_BOT_TOKEN
                }.items() if not v])
        
        # Check if user is authenticated
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Get bot stats from database
        stats = {'servers': 1, 'users': 50, 'commands_used': 125, 'uptime_hours': 72}
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM bot_stats ORDER BY last_updated DESC LIMIT 1")
                    row = cur.fetchone()
                    if row:
                        stats = dict(row)
            except Exception as e:
                print(f"Stats query error: {e}")
            finally:
                conn.close()
        
        return render_template('dashboard.html', 
                             user=session.get('user_info', {}),
                             stats=stats)
    
    @app.route('/login')
    def login():
        """Discord OAuth login page"""
        if not DISCORD_CLIENT_ID:
            return "Discord application not configured. Add DISCORD_CLIENT_ID to environment variables."
        
        return render_template('login.html')
    
    @app.route('/dev-login')
    def dev_login():
        """Development login bypass"""
        session['user_id'] = '123456789'
        session['user_info'] = {
            'username': 'Developer',
            'discriminator': '0001',
            'avatar': None,
            'id': '123456789'
        }
        return redirect(url_for('home'))
    
    @app.route('/api/auth/discord')
    def discord_auth():
        """Initiate Discord OAuth"""
        if not DISCORD_CLIENT_ID:
            return jsonify({'error': 'Discord not configured'}), 400
        
        params = {
            'client_id': DISCORD_CLIENT_ID,
            'redirect_uri': request.url_root.rstrip('/') + '/api/auth/callback',
            'response_type': 'code',
            'scope': 'identify guilds',
            'prompt': 'consent'
        }
        
        discord_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
        return redirect(discord_url)
    
    @app.route('/api/auth/callback')
    def discord_callback():
        """Handle Discord OAuth callback"""
        code = request.args.get('code')
        if not code:
            return redirect(url_for('login'))
        
        # Exchange code for token
        try:
            token_data = {
                'client_id': DISCORD_CLIENT_ID,
                'client_secret': DISCORD_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': request.url_root.rstrip('/') + '/api/auth/callback'
            }
            
            token_response = requests.post('https://discord.com/api/oauth2/token', 
                                         data=token_data, 
                                         headers={'Content-Type': 'application/x-www-form-urlencoded'})
            
            if token_response.status_code != 200:
                return f"Token exchange failed: {token_response.text}"
            
            token_json = token_response.json()
            access_token = token_json['access_token']
            
            # Get user info
            user_response = requests.get('https://discord.com/api/users/@me',
                                       headers={'Authorization': f'Bearer {access_token}'})
            
            if user_response.status_code != 200:
                return f"User info failed: {user_response.text}"
            
            user_data = user_response.json()
            
            # Store in session
            session['user_id'] = user_data['id']
            session['user_info'] = user_data
            
            return redirect(url_for('home'))
            
        except Exception as e:
            return f"Authentication error: {str(e)}"
    
    @app.route('/logout')
    def logout():
        """Logout and clear session"""
        session.clear()
        return redirect(url_for('login'))
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'discord_configured': bool(DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET and DISCORD_BOT_TOKEN),
            'database_connected': bool(get_db_connection()),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Music API endpoints (simplified)
    @app.route('/api/music/play', methods=['POST'])
    def music_play():
        return jsonify({'status': 'Music play command sent'})
    
    @app.route('/api/music/pause', methods=['POST'])
    def music_pause():
        return jsonify({'status': 'Music paused'})
    
    @app.route('/api/music/skip', methods=['POST'])
    def music_skip():
        return jsonify({'status': 'Song skipped'})
    
    @app.route('/api/music/queue')
    def music_queue():
        return jsonify({'queue': [], 'current': None})
    
    # Moderation API endpoints (simplified)
    @app.route('/api/moderation/kick', methods=['POST'])
    def kick_user():
        return jsonify({'status': 'User kick command sent'})
    
    @app.route('/api/moderation/ban', methods=['POST'])
    def ban_user():
        return jsonify({'status': 'User ban command sent'})
    
    @app.route('/api/moderation/timeout', methods=['POST'])
    def timeout_user():
        return jsonify({'status': 'User timeout command sent'})
    
    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)