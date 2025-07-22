"""
Debug the API stats endpoint
"""
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

def debug_stats():
    """Debug the stats API"""
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
            print("Debugging API stats...")
            
            # Test basic stats
            print("1. Testing BotStats...")
            minecraft_counter_updates = BotStats.get_stat('minecraft_counter_updates', 0)
            print(f"   Minecraft counter updates: {minecraft_counter_updates}")
            
            # Test command stats
            print("2. Testing CommandUsage...")
            command_stats = db.session.query(
                CommandUsage.command_name,
                db.func.count(CommandUsage.id).label('count')
            ).group_by(CommandUsage.command_name).all()
            print(f"   Command stats count: {len(command_stats)}")
            
            # Test Minecraft stats with datetime handling
            print("3. Testing MinecraftServerStats...")
            yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
            print(f"   Yesterday timestamp: {yesterday}")
            print(f"   Yesterday timezone: {yesterday.tzinfo}")
            
            recent_minecraft_stats = MinecraftServerStats.query.filter(
                MinecraftServerStats.timestamp >= yesterday
            ).order_by(MinecraftServerStats.timestamp.desc()).limit(5).all()
            print(f"   Recent minecraft stats count: {len(recent_minecraft_stats)}")
            
            if recent_minecraft_stats:
                first_stat = recent_minecraft_stats[0]
                print(f"   First stat timestamp: {first_stat.timestamp}")
                print(f"   First stat timezone: {first_stat.timestamp.tzinfo}")
            
            # Test uptime stats
            print("4. Testing BotUptime...")
            current_session = BotUptime.get_current_session()
            print(f"   Current session exists: {current_session is not None}")
            
            if current_session:
                print(f"   Session start: {current_session.session_start}")
                print(f"   Session start timezone: {current_session.session_start.tzinfo}")
                
                # Test the problematic calculation
                now = datetime.now(timezone.utc)
                print(f"   Current time: {now}")
                print(f"   Current time timezone: {now.tzinfo}")
                
                # Fix timezone if needed
                session_start = current_session.session_start
                if session_start.tzinfo is None:
                    session_start = session_start.replace(tzinfo=timezone.utc)
                    print(f"   Fixed session start: {session_start}")
                
                # Try the calculation
                try:
                    diff = now - session_start
                    current_uptime = int(diff.total_seconds())
                    print(f"   Current uptime calculation successful: {current_uptime} seconds")
                except Exception as e:
                    print(f"   Current uptime calculation failed: {e}")
            
            print("Debugging completed successfully!")
            
    except Exception as e:
        print(f"Error in debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_stats()