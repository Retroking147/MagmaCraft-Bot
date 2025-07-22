"""
Initialize database tables for the dashboard
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    """Create all database tables"""
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
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
    except Exception as e:
        print(f"Error creating database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_database()