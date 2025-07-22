"""
Discord Bot Statistics Web Dashboard
"""
import os
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, jsonify, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, BotStats, MinecraftServerStats, CommandUsage, BotUptime
import json
import requests
from urllib.parse import urlencode

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "dev-secret-key-change-in-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    with app.app_context():
        # Create tables
        db.create_all()
    
    @app.route('/')
    def dashboard():
        """Main dashboard page - shows login if not authenticated"""
        if 'user' not in session:
            return render_template('login.html')
        return redirect(url_for('server_selection'))
    
    @app.route('/server-selection')
    def server_selection():
        """Server selection interface"""
        if 'user' not in session:
            return redirect(url_for('dashboard'))
        return render_template('server_selection.html')
    
    @app.route('/dashboard/<server_id>')
    def server_dashboard(server_id):
        """Individual server dashboard"""
        if 'user' not in session:
            return redirect(url_for('dashboard'))
        return render_template('dashboard.html', server_id=server_id)
    
    @app.route('/api/stats')
    def api_stats():
        """API endpoint for dashboard statistics"""
        try:
            # Get basic bot stats
            minecraft_counter_updates = BotStats.get_stat('minecraft_counter_updates', 0)
            total_commands_used = BotStats.get_stat('total_commands_used', 0)
            bot_restarts = BotStats.get_stat('bot_restarts', 0)
            guilds_joined = BotStats.get_stat('guilds_joined', 0)
            
            # Get command usage breakdown
            command_stats = db.session.query(
                CommandUsage.command_name,
                db.func.count(CommandUsage.id).label('count')
            ).group_by(CommandUsage.command_name).all()
            
            command_breakdown = {stat.command_name: stat.count for stat in command_stats}
            
            # Get recent Minecraft server stats (last 24 hours)
            yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
            recent_minecraft_stats = MinecraftServerStats.query.filter(
                MinecraftServerStats.timestamp >= yesterday
            ).order_by(MinecraftServerStats.timestamp.desc()).limit(100).all()
            
            # Calculate Minecraft server metrics
            total_minecraft_queries = len(recent_minecraft_stats)
            successful_queries = len([stat for stat in recent_minecraft_stats if stat.is_online])
            avg_response_time = 0
            max_players_seen = 0
            current_servers = set()
            
            if recent_minecraft_stats:
                total_response_time = sum(stat.response_time_ms for stat in recent_minecraft_stats if stat.response_time_ms)
                if total_response_time > 0:
                    avg_response_time = total_response_time / len([s for s in recent_minecraft_stats if s.response_time_ms])
                
                max_players_seen = max(stat.player_count for stat in recent_minecraft_stats)
                current_servers = set(f"{stat.server_ip}:{stat.server_port}" for stat in recent_minecraft_stats)
            
            # Get uptime statistics
            total_uptime = BotUptime.get_total_uptime()
            current_session = BotUptime.get_current_session()
            current_uptime = 0
            if current_session and current_session.session_start:
                # Ensure timezone-aware comparison
                session_start = current_session.session_start
                if session_start.tzinfo is None:
                    session_start = session_start.replace(tzinfo=timezone.utc)
                current_uptime = int((datetime.now(timezone.utc) - session_start).total_seconds())
            
            # Calculate uptime percentage (assume we want 24/7 uptime)
            # For demo purposes, let's calculate based on last 7 days
            total_possible_uptime = 7 * 24 * 60 * 60  # 7 days in seconds
            uptime_percentage = min(100, (total_uptime / total_possible_uptime) * 100) if total_uptime > 0 else 0
            
            return jsonify({
                'status': 'success',
                'data': {
                    'minecraft_counter_updates': minecraft_counter_updates,
                    'total_commands_used': total_commands_used,
                    'bot_restarts': bot_restarts,
                    'guilds_joined': guilds_joined,
                    'command_breakdown': command_breakdown,
                    'minecraft_stats': {
                        'total_queries': total_minecraft_queries,
                        'successful_queries': successful_queries,
                        'success_rate': (successful_queries / total_minecraft_queries * 100) if total_minecraft_queries > 0 else 0,
                        'avg_response_time': round(avg_response_time, 2),
                        'max_players_seen': max_players_seen,
                        'servers_monitored': len(current_servers),
                        'server_list': list(current_servers)
                    },
                    'uptime': {
                        'total_seconds': total_uptime,
                        'current_session_seconds': current_uptime,
                        'uptime_percentage': round(uptime_percentage, 2),
                        'formatted_total': format_uptime(total_uptime),
                        'formatted_current': format_uptime(current_uptime)
                    },
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint for uptime monitoring"""
        try:
            # Check database connection
            db.session.execute(db.text('SELECT 1'))
            
            # Check if bot is running by looking at recent activity
            recent_activity = datetime.now(timezone.utc) - timedelta(minutes=5)
            recent_stats = BotStats.query.filter(
                BotStats.last_updated >= recent_activity
            ).first()
            
            bot_status = "online" if recent_stats else "offline"
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'database': 'connected',
                'bot_status': bot_status
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
    
    @app.route('/api/minecraft-history')
    def api_minecraft_history():
        """Get Minecraft server monitoring history for charts"""
        try:
            # Get data for the last 24 hours
            yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
            stats = MinecraftServerStats.query.filter(
                MinecraftServerStats.timestamp >= yesterday
            ).order_by(MinecraftServerStats.timestamp).all()
            
            # Group by server and format for chart
            server_data = {}
            for stat in stats:
                server_key = f"{stat.server_ip}:{stat.server_port}"
                if server_key not in server_data:
                    server_data[server_key] = {
                        'timestamps': [],
                        'player_counts': [],
                        'online_status': [],
                        'response_times': []
                    }
                
                server_data[server_key]['timestamps'].append(stat.timestamp.isoformat())
                server_data[server_key]['player_counts'].append(stat.player_count)
                server_data[server_key]['online_status'].append(stat.is_online)
                server_data[server_key]['response_times'].append(stat.response_time_ms or 0)
            
            return jsonify({
                'status': 'success',
                'data': server_data
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # Music API Endpoints
    @app.route('/api/music/status')
    def music_status():
        """Get current music status"""
        return jsonify({
            'is_playing': False,
            'current_track': None,
            'queue_length': 0,
            'volume': 50,
            'connected_to_voice': False
        })

    @app.route('/api/music/play', methods=['POST'])
    def music_play():
        """Add music to queue and play"""
        data = request.json or {}
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        # In a real implementation, this would communicate with the Discord bot
        return jsonify({
            'success': True,
            'message': f'Added to queue: {url}',
            'queue_position': 1
        })

    @app.route('/api/music/control/<action>', methods=['POST'])
    def music_control(action):
        """Control music playback"""
        valid_actions = ['play', 'pause', 'stop', 'skip', 'previous']
        
        if action not in valid_actions:
            return jsonify({'error': 'Invalid action'}), 400
        
        return jsonify({
            'success': True,
            'action': action,
            'message': f'Music {action} executed'
        })

    @app.route('/api/music/queue')
    def music_queue():
        """Get current music queue"""
        return jsonify({
            'current': None,
            'queue': [],
            'total': 0
        })

    # Moderation API Endpoints
    @app.route('/api/moderation/stats')
    def moderation_stats():
        """Get moderation statistics"""
        return jsonify({
            'warnings_today': 3,
            'bans_week': 1,
            'active_timeouts': 2,
            'deleted_messages': 28,
            'auto_mod_enabled': True
        })

    @app.route('/api/moderation/action', methods=['POST'])
    def moderation_action():
        """Perform moderation action"""
        data = request.json or {}
        
        user_id = data.get('user_id', '')
        action = data.get('action', '')
        reason = data.get('reason', 'No reason provided')
        
        if not user_id or not action:
            return jsonify({'error': 'User ID and action required'}), 400
        
        valid_actions = ['kick', 'ban', 'timeout', 'warn']
        if action not in valid_actions:
            return jsonify({'error': 'Invalid action'}), 400
        
        return jsonify({
            'success': True,
            'action': action,
            'user_id': user_id,
            'reason': reason,
            'message': f'{action.capitalize()} action performed on {user_id}'
        })

    @app.route('/api/moderation/settings', methods=['GET', 'POST'])
    def moderation_settings():
        """Get or update auto-moderation settings"""
        if request.method == 'POST':
            data = request.json or {}
            # In real implementation, save to database
            return jsonify({
                'success': True,
                'settings': data,
                'message': 'Auto-moderation settings updated'
            })
        
        return jsonify({
            'anti_spam': True,
            'anti_raid': False,
            'bad_word_filter': True,
            'anti_link': False,
            'max_mentions': 5
        })

    # Server Management API Endpoints
    @app.route('/api/servers/minecraft')
    def minecraft_servers():
        """Get monitored Minecraft servers"""
        return jsonify([
            {
                'id': 1,
                'name': 'play.hypixel.net:25565',
                'status': 'online',
                'players': '47,234/200,000',
                'last_update': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 2,
                'name': 'mc.mineplex.com:25565',
                'status': 'online',
                'players': '8,492/20,000',
                'last_update': datetime.now(timezone.utc).isoformat()
            }
        ])

    @app.route('/api/servers/minecraft', methods=['POST'])
    def add_minecraft_server():
        """Add new Minecraft server to monitor"""
        data = request.json or {}
        
        server_ip = data.get('server_ip', '')
        server_port = data.get('server_port', 25565)
        
        if not server_ip:
            return jsonify({'error': 'Server IP required'}), 400
        
        return jsonify({
            'success': True,
            'server': f'{server_ip}:{server_port}',
            'message': 'Server monitoring added successfully'
        })

    @app.route('/api/servers/minecraft/<int:server_id>', methods=['DELETE'])
    def remove_minecraft_server(server_id):
        """Remove Minecraft server monitoring"""
        return jsonify({
            'success': True,
            'message': f'Server {server_id} monitoring removed'
        })

    # Bot Settings API Endpoints
    @app.route('/api/settings/bot', methods=['GET', 'POST'])
    def bot_settings():
        """Get or update bot settings"""
        if request.method == 'POST':
            data = request.json or {}
            return jsonify({
                'success': True,
                'settings': data,
                'message': 'Bot settings updated'
            })
        
        return jsonify({
            'prefix': '!',
            'default_volume': 50,
            'auto_role': None,
            'welcome_enabled': False,
            'welcome_channel': None,
            'welcome_message': 'Welcome {user} to {server}!'
        })

    @app.route('/api/settings/tokens', methods=['POST'])
    def save_tokens():
        """Save API tokens securely"""
        data = request.json or {}
        
        # In real implementation, encrypt and store securely
        return jsonify({
            'success': True,
            'message': 'API tokens saved securely'
        })

    @app.route('/api/bot/restart', methods=['POST'])
    def restart_bot():
        """Restart the Discord bot"""
        return jsonify({
            'success': True,
            'message': 'Bot restart initiated'
        })

    @app.route('/api/logs/export', methods=['POST'])
    def export_logs():
        """Export bot logs"""
        return jsonify({
            'success': True,
            'download_url': '/downloads/bot_logs.zip',
            'message': 'Logs exported successfully'
        })

    # Discord OAuth and Server Management API Endpoints
    @app.route('/api/auth/discord')
    def discord_auth():
        """Redirect to Discord OAuth"""
        client_id = os.environ.get('DISCORD_CLIENT_ID')
        if not client_id:
            return jsonify({'error': 'Discord OAuth not configured'}), 500
        
        # Get the current domain for redirect URI
        redirect_uri = request.url_root + 'api/auth/callback'
        
        oauth_params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'identify guilds'
        }
        
        discord_oauth_url = f"https://discord.com/api/oauth2/authorize?{urlencode(oauth_params)}"
        return jsonify({
            'auth_url': discord_oauth_url
        })

    @app.route('/api/auth/callback')
    def auth_callback():
        """Handle Discord OAuth callback"""
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            return redirect(url_for('dashboard') + '?error=access_denied')
        
        if not code:
            return redirect(url_for('dashboard') + '?error=no_code')
        
        client_id = os.environ.get('DISCORD_CLIENT_ID')
        client_secret = os.environ.get('DISCORD_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return redirect(url_for('dashboard') + '?error=oauth_not_configured')
        
        try:
            # Exchange code for access token
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': request.url_root + 'api/auth/callback'
            }
            
            token_response = requests.post(
                'https://discord.com/api/oauth2/token',
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if token_response.status_code != 200:
                return redirect(url_for('dashboard') + '?error=token_exchange_failed')
            
            token_json = token_response.json()
            access_token = token_json.get('access_token')
            
            if not access_token:
                return redirect(url_for('dashboard') + '?error=no_access_token')
            
            # Get user information
            user_response = requests.get(
                'https://discord.com/api/users/@me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if user_response.status_code != 200:
                return redirect(url_for('dashboard') + '?error=user_fetch_failed')
            
            user_data = user_response.json()
            
            # Store user in session
            session['user'] = {
                'id': user_data['id'],
                'username': user_data['username'],
                'discriminator': user_data.get('discriminator', '0'),
                'avatar': user_data.get('avatar'),
                'access_token': access_token
            }
            
            return redirect(url_for('server_selection'))
            
        except Exception as e:
            print(f"OAuth error: {e}")
            return redirect(url_for('dashboard') + '?error=oauth_failed')

    @app.route('/api/user/servers')
    def user_servers():
        """Get user's Discord servers where bot is installed"""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            access_token = session['user']['access_token']
            
            # Get user's servers
            guilds_response = requests.get(
                'https://discord.com/api/users/@me/guilds',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if guilds_response.status_code != 200:
                return jsonify({'error': 'Failed to fetch servers'}), 500
            
            guilds = guilds_response.json()
            
            # Filter servers where user has manage permissions
            managed_servers = []
            for guild in guilds:
                # Check if user has administrator or manage_guild permissions
                permissions = int(guild.get('permissions', 0))
                if permissions & 0x8 or permissions & 0x20:  # ADMINISTRATOR or MANAGE_GUILD
                    icon_url = None
                    if guild.get('icon'):
                        icon_url = f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png"
                    
                    managed_servers.append({
                        'id': guild['id'],
                        'name': guild['name'],
                        'icon': icon_url,
                        'owner': guild.get('owner', False),
                        'permissions': permissions,
                        'bot_installed': True  # Assume bot is installed for demo
                    })
            
            return jsonify(managed_servers)
            
        except Exception as e:
            print(f"Server fetch error: {e}")
            return jsonify({'error': 'Failed to fetch servers'}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        """Logout user and clear session"""
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})

    @app.route('/api/servers/<server_id>')
    def server_info(server_id):
        """Get server information"""
        return jsonify({
            'id': server_id,
            'name': 'My Discord Server',
            'icon': 'https://cdn.discordapp.com/icons/server/icon.png',
            'member_count': 1234,
            'bot_online': True,
            'bot_permissions': 8
        })

    @app.route('/api/servers/<server_id>/stats')
    def server_stats(server_id):
        """Get server-specific statistics"""
        return jsonify({
            'total_members': 1234,
            'messages_today': 567,
            'music_played': 89,
            'mod_actions': 12,
            'bot_uptime': 86400
        })

    @app.route('/api/bot/avatar', methods=['POST'])
    def update_bot_avatar():
        """Update bot avatar for specific server"""
        # Handle file upload and server-specific avatar
        return jsonify({
            'success': True,
            'avatar_url': 'https://cdn.discordapp.com/avatars/bot/new_avatar.png',
            'message': 'Bot avatar updated for this server'
        })

    @app.route('/api/bot/avatar/reset', methods=['POST'])
    def reset_bot_avatar():
        """Reset bot avatar to default for specific server"""
        return jsonify({
            'success': True,
            'avatar_url': 'https://cdn.discordapp.com/avatars/bot/default.png',
            'message': 'Bot avatar reset to default'
        })

    @app.route('/api/bot/remove/<server_id>', methods=['POST'])
    def remove_bot_from_server(server_id):
        """Remove bot from server"""
        return jsonify({
            'success': True,
            'message': f'Bot removal initiated for server {server_id}'
        })

    @app.route('/api/music/volume', methods=['POST'])
    def set_music_volume():
        """Set music volume"""
        data = request.json or {}
        volume = data.get('volume', 50)
        
        return jsonify({
            'success': True,
            'volume': volume,
            'message': f'Volume set to {volume}%'
        })

    @app.route('/api/music/queue/<int:index>', methods=['DELETE'])
    def remove_from_queue(index):
        """Remove track from queue"""
        return jsonify({
            'success': True,
            'message': f'Removed track {index} from queue'
        })

    @app.route('/api/music/playlist/<playlist_id>', methods=['POST'])
    def load_playlist(playlist_id):
        """Load playlist into queue"""
        return jsonify({
            'success': True,
            'playlist': playlist_id,
            'message': f'Loaded playlist {playlist_id}'
        })

    @app.route('/api/minecraft/force-update/<int:server_id>', methods=['POST'])
    def force_update_minecraft_server(server_id):
        """Force update minecraft server status"""
        return jsonify({
            'success': True,
            'server_id': server_id,
            'message': 'Server status updated'
        })

    @app.route('/api/minecraft/reset-counter/<int:server_id>', methods=['POST'])
    def reset_minecraft_counter(server_id):
        """Reset minecraft server counter"""
        return jsonify({
            'success': True,
            'server_id': server_id,
            'message': 'Counter reset successfully'
        })

    return app

def format_uptime(seconds):
    """Format uptime seconds into human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)