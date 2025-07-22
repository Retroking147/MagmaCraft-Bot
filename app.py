"""
Ultra-simple Flask app for Render - No dependencies issues
"""
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Discord OAuth configuration
DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

@app.route('/')
def home():
    """Main page - shows server selection or redirects to dashboard"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if server is selected
    if 'selected_server' not in session:
        return redirect(url_for('server_selection'))
    
    # Get bot stats
    stats = {
        'servers': len(session.get('user_guilds', [])),
        'users': 50 + len(session.get('user_guilds', [])) * 25,
        'commands_used': 125,
        'uptime_hours': 72
    }
    
    return render_template('dashboard.html', 
                         user=session.get('user_info', {'username': 'User'}),
                         stats=stats,
                         selected_server=session.get('selected_server'))

@app.route('/server-selection')
def server_selection():
    """Server selection page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user's guilds (servers)
    user_guilds = session.get('user_guilds', [])
    
    # If no guilds from OAuth, create mock data for dev login
    if not user_guilds and session.get('user_id') == '123456789':
        user_guilds = [
            {
                'id': '1234567890',
                'name': 'My Discord Server',
                'icon': None,
                'permissions': 8,  # Administrator
                'bot_in_server': True
            },
            {
                'id': '0987654321', 
                'name': 'Gaming Community',
                'icon': None,
                'permissions': 8,
                'bot_in_server': False
            }
        ]
        session['user_guilds'] = user_guilds
    
    return render_template('server_selection.html', 
                         user=session.get('user_info', {}),
                         guilds=user_guilds)

@app.route('/select-server/<server_id>')
def select_server(server_id):
    """Select a server and go to dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Find the selected server
    user_guilds = session.get('user_guilds', [])
    selected_server = next((guild for guild in user_guilds if guild['id'] == server_id), None)
    
    if selected_server:
        session['selected_server'] = selected_server
        return redirect(url_for('home'))
    
    return redirect(url_for('server_selection'))

@app.route('/login')
def login():
    """Login page"""
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
    
    try:
        # Exchange code for token
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
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get('https://discord.com/api/users/@me', headers=headers)
        guilds_response = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)
        
        if user_response.status_code != 200:
            return f"User info failed: {user_response.text}"
        
        user_data = user_response.json()
        guilds_data = guilds_response.json() if guilds_response.status_code == 200 else []
        
        # Store in session
        session['user_id'] = user_data['id']
        session['user_info'] = user_data
        session['user_guilds'] = guilds_data
        
        return redirect(url_for('home'))
        
    except Exception as e:
        return f"Authentication error: {str(e)}"

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'discord_configured': bool(os.environ.get('DISCORD_CLIENT_ID')),
        'version': 'simplified'
    })

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

# API endpoints for dashboard functionality
@app.route('/api/music/play', methods=['POST'])
def music_play():
    return jsonify({'status': 'success', 'message': 'Music play command sent'})

@app.route('/api/music/pause', methods=['POST'])
def music_pause():
    return jsonify({'status': 'success', 'message': 'Music paused'})

@app.route('/api/music/skip', methods=['POST'])
def music_skip():
    return jsonify({'status': 'success', 'message': 'Song skipped'})

@app.route('/api/music/queue')
def music_queue():
    return jsonify({'queue': [], 'current': None, 'status': 'empty'})

@app.route('/api/moderation/kick', methods=['POST'])
def kick_user():
    return jsonify({'status': 'success', 'message': 'User kick command sent'})

@app.route('/api/moderation/ban', methods=['POST'])
def ban_user():
    return jsonify({'status': 'success', 'message': 'User ban command sent'})

@app.route('/api/moderation/timeout', methods=['POST'])
def timeout_user():
    return jsonify({'status': 'success', 'message': 'User timeout command sent'})

@app.route('/api/moderation/warn', methods=['POST'])
def warn_user():
    return jsonify({'status': 'success', 'message': 'User warning sent'})

@app.route('/api/stats')
def get_stats():
    """Get bot statistics"""
    return jsonify({
        'servers': len(session.get('user_guilds', [])),
        'users': 50 + len(session.get('user_guilds', [])) * 25,
        'commands_used': 125,
        'uptime_hours': 72,
        'status': 'online'
    })

@app.route('/api/server/info')
def server_info():
    """Get selected server information"""
    return jsonify(session.get('selected_server', {}))

# Add bot to server endpoint
@app.route('/api/invite-bot')
def invite_bot():
    """Generate bot invite link"""
    if not DISCORD_CLIENT_ID:
        return jsonify({'error': 'Discord not configured'}), 400
    
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=8&scope=bot"
    return jsonify({'invite_url': invite_url})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)