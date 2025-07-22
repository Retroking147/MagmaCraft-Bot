"""
Discord Bot Statistics Web Dashboard
"""
import os
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, BotStats, MinecraftServerStats, CommandUsage, BotUptime
import json

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
        """Main dashboard page"""
        return render_template('dashboard.html')
    
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