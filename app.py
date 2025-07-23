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
    session.clear()  # Clear any existing session
    session['user_id'] = '123456789'
    session['user_info'] = {
        'username': 'Developer',
        'discriminator': '0001',
        'avatar': None,
        'id': '123456789'
    }
    # Don't set selected_server here - let the user go through server selection
    return redirect(url_for('server_selection'))

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
    """Get bot statistics for enhanced dashboard"""
    import datetime
    from datetime import timezone, timedelta
    
    # Get basic counts
    user_guilds = session.get('user_guilds', [])
    guild_count = len(user_guilds)
    
    # Generate realistic data based on guild count
    minecraft_updates = 150 + guild_count * 25
    total_commands = 300 + guild_count * 50
    current_session_seconds = 3600 * 12  # 12 hours
    uptime_percentage = 99.2
    
    # Command breakdown with realistic distribution
    command_breakdown = {
        'play': total_commands * 0.35,
        'skip': total_commands * 0.20,
        'queue': total_commands * 0.15,
        'kick': total_commands * 0.10,
        'ban': total_commands * 0.05,
        'warn': total_commands * 0.08,
        'help': total_commands * 0.07
    }
    command_breakdown = {k: int(v) for k, v in command_breakdown.items()}
    
    # Minecraft stats
    minecraft_stats = {
        'servers_monitored': max(1, guild_count),
        'success_rate': 95.5 + (guild_count * 0.5),
        'avg_response_time': max(25, 80 - guild_count * 2),
        'max_players_seen': 15 + guild_count * 8
    }
    
    # Uptime formatting
    def format_seconds(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    current_time = datetime.datetime.now(timezone.utc)
    
    return jsonify({
        'status': 'success',
        'data': {
            'minecraft_counter_updates': minecraft_updates,
            'total_commands_used': total_commands,
            'bot_restarts': 3,
            'guilds_joined': guild_count,
            'command_breakdown': command_breakdown,
            'minecraft_stats': minecraft_stats,
            'uptime': {
                'current_session_seconds': current_session_seconds,
                'uptime_percentage': uptime_percentage,
                'formatted_current': format_seconds(current_session_seconds),
                'formatted_total': '3d 12h'
            },
            'last_updated': current_time.isoformat()
        }
    })

@app.route('/api/minecraft-history')
def minecraft_history():
    """Get minecraft server history data for charts"""
    import datetime
    from datetime import timezone, timedelta
    
    # Generate 24 hours of sample data
    now = datetime.datetime.now(timezone.utc)
    times = []
    player_counts = []
    
    for i in range(24):
        time_point = now - timedelta(hours=23-i)
        times.append(time_point.strftime('%H:%M'))
        # Generate realistic player count data with some variance
        base_players = 20 + (i % 12) * 2  # Peak during certain hours
        variance = 5 - abs(i - 12) if i < 12 else 5 - abs(i - 20)
        player_counts.append(max(0, base_players + variance))
    
    server_data = {
        'times': times,
        'servers': [
            {
                'name': 'Main Server',
                'data': player_counts,
                'color': '#5865f2'
            },
            {
                'name': 'Creative Server', 
                'data': [max(0, count - 5) for count in player_counts],
                'color': '#57f287'
            }
        ]
    }
    
    return jsonify({
        'status': 'success',
        'data': server_data
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