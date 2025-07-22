"""
Populate sample statistics data for the dashboard
"""
import os
import random
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def populate_sample_data():
    """Create sample statistics for demonstration"""
    try:
        from models import db, BotStats, MinecraftServerStats, CommandUsage, BotUptime
        from flask import Flask
        
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        db.init_app(app)
        
        with app.app_context():
            print("Creating sample statistics data...")
            
            # Clear existing data for fresh start
            db.session.query(BotStats).delete()
            db.session.query(MinecraftServerStats).delete()
            db.session.query(CommandUsage).delete()
            db.session.query(BotUptime).delete()
            db.session.commit()
            
            # Create basic bot statistics
            stats_data = [
                ('minecraft_counter_updates', 2847),
                ('total_commands_used', 156),
                ('bot_restarts', 3),
                ('guilds_joined', 12),
                ('last_heartbeat', int(datetime.now(timezone.utc).timestamp()))
            ]
            
            for stat_name, stat_value in stats_data:
                stat = BotStats(
                    stat_name=stat_name,
                    stat_value=stat_value,
                    last_updated=datetime.now(timezone.utc)
                )
                db.session.add(stat)
            
            # Create command usage history (last 7 days)
            commands = [
                'minecraft-counter', 'ping', 'info', 'commands', 
                'reset-counter', 'force-update', 'hello'
            ]
            
            for i in range(150):  # Create 150 command usage records
                timestamp = datetime.now(timezone.utc) - timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                command_usage = CommandUsage(
                    command_name=random.choice(commands),
                    user_id=str(random.randint(100000000000000000, 999999999999999999)),
                    guild_id=str(random.randint(100000000000000000, 999999999999999999)),
                    success=random.choice([True, True, True, False]),  # 75% success rate
                    timestamp=timestamp
                )
                db.session.add(command_usage)
            
            # Create Minecraft server monitoring history (last 24 hours)
            servers = [
                ('play.hypixel.net', 25565),
                ('mc.mineplex.com', 25565),
                ('play.cubecraft.net', 25565)
            ]
            
            for server_ip, server_port in servers:
                # Create data points every 15 minutes for last 24 hours
                for i in range(96):  # 24 hours * 4 (15-minute intervals)
                    timestamp = datetime.now(timezone.utc) - timedelta(
                        minutes=i * 15
                    )
                    
                    # Simulate realistic server behavior
                    is_online = random.choice([True] * 9 + [False])  # 90% uptime
                    if is_online:
                        # Vary player count based on time of day
                        hour = timestamp.hour
                        if 14 <= hour <= 22:  # Peak hours
                            base_players = random.randint(50, 200)
                        elif 6 <= hour <= 13:  # Morning/afternoon
                            base_players = random.randint(20, 80)
                        else:  # Night/early morning
                            base_players = random.randint(5, 30)
                        
                        player_count = max(0, base_players + random.randint(-20, 20))
                        max_players = max(player_count + 50, 100)
                        response_time_ms = random.randint(30, 150)
                    else:
                        player_count = 0
                        max_players = 0
                        response_time_ms = 5000  # Timeout
                    
                    server_stat = MinecraftServerStats(
                        server_ip=server_ip,
                        server_port=server_port,
                        timestamp=timestamp,
                        is_online=is_online,
                        player_count=player_count,
                        max_players=max_players,
                        response_time_ms=response_time_ms
                    )
                    
                    # Add some players for online servers
                    if is_online and player_count > 0:
                        sample_players = [
                            f"Player{random.randint(1, 1000)}" 
                            for _ in range(min(player_count, 10))
                        ]
                        server_stat.players = sample_players[:10]  # Limit sample to 10
                    
                    db.session.add(server_stat)
            
            # Create uptime sessions
            # Previous sessions
            for i in range(3):
                start_time = datetime.now(timezone.utc) - timedelta(
                    days=random.randint(1, 10),
                    hours=random.randint(0, 23)
                )
                session_duration = random.randint(3600, 86400)  # 1-24 hours
                
                session = BotUptime(
                    session_start=start_time,
                    session_end=start_time + timedelta(seconds=session_duration),
                    uptime_seconds=session_duration
                )
                db.session.add(session)
            
            # Current active session
            current_session = BotUptime(
                session_start=datetime.now(timezone.utc) - timedelta(hours=2, minutes=30),
                # session_end will be None to indicate active session
                uptime_seconds=0
            )
            db.session.add(current_session)
            
            # Commit all data
            db.session.commit()
            print("Sample data populated successfully!")
            print("Dashboard should now show realistic statistics.")
            
    except Exception as e:
        print(f"Error populating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    populate_sample_data()