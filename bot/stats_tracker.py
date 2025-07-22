"""
Statistics tracking utilities for Discord bot
"""
import os
import logging
from datetime import datetime, timezone
import asyncio
from typing import Optional
import time

logger = logging.getLogger(__name__)

class StatsTracker:
    """Track bot statistics and store in database"""
    
    def __init__(self):
        self.db_connected = False
        self.db = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database connection"""
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from models import db, BotStats, MinecraftServerStats, CommandUsage, BotUptime
            
            # Configure Flask app for database operations
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
                db.create_all()
                self.db_connected = True
                self.db = db
                self.app = app
                self.BotStats = BotStats
                self.MinecraftServerStats = MinecraftServerStats
                self.CommandUsage = CommandUsage
                self.BotUptime = BotUptime
                logger.info("Database connection established for statistics tracking")
                
        except Exception as e:
            logger.error(f"Failed to initialize database for stats tracking: {e}")
            self.db_connected = False
    
    def track_minecraft_counter_update(self, server_ip: str, server_port: int, 
                                     player_count: int, max_players: int, 
                                     is_online: bool, response_time_ms: int = 0,
                                     players_list: list = None):
        """Track a Minecraft server counter update"""
        if not self.db_connected:
            return
            
        try:
            with self.app.app_context():
                # Increment global counter
                self.BotStats.increment_stat('minecraft_counter_updates')
                
                # Store detailed server stats
                server_stat = self.MinecraftServerStats(
                    server_ip=server_ip,
                    server_port=server_port,
                    is_online=is_online,
                    player_count=player_count,
                    max_players=max_players,
                    response_time_ms=response_time_ms,
                    timestamp=datetime.now(timezone.utc)
                )
                
                if players_list:
                    server_stat.players = players_list
                
                self.db.session.add(server_stat)
                self.db.session.commit()
                
        except Exception as e:
            logger.error(f"Failed to track Minecraft counter update: {e}")
    
    def track_command_usage(self, command_name: str, user_id: str, 
                          guild_id: Optional[str] = None, success: bool = True):
        """Track Discord command usage"""
        if not self.db_connected:
            return
            
        try:
            with self.app.app_context():
                # Increment global command counter
                self.BotStats.increment_stat('total_commands_used')
                
                # Store command usage details
                command_usage = self.CommandUsage(
                    command_name=command_name,
                    user_id=str(user_id),
                    guild_id=str(guild_id) if guild_id else None,
                    success=success,
                    timestamp=datetime.now(timezone.utc)
                )
                
                self.db.session.add(command_usage)
                self.db.session.commit()
                
        except Exception as e:
            logger.error(f"Failed to track command usage: {e}")
    
    def track_bot_start(self):
        """Track bot startup"""
        if not self.db_connected:
            return
            
        try:
            with self.app.app_context():
                # Increment restart counter
                self.BotStats.increment_stat('bot_restarts')
                
                # End any previous active sessions
                current_session = self.BotUptime.get_current_session()
                if current_session:
                    current_session.end_session()
                
                # Start new uptime session
                new_session = self.BotUptime(
                    session_start=datetime.now(timezone.utc)
                )
                self.db.session.add(new_session)
                self.db.session.commit()
                
                logger.info("Bot startup tracked in database")
                
        except Exception as e:
            logger.error(f"Failed to track bot startup: {e}")
    
    def track_bot_shutdown(self):
        """Track bot shutdown"""
        if not self.db_connected:
            return
            
        try:
            with self.app.app_context():
                # End current session
                current_session = self.BotUptime.get_current_session()
                if current_session:
                    current_session.end_session()
                    logger.info("Bot shutdown tracked in database")
                
        except Exception as e:
            logger.error(f"Failed to track bot shutdown: {e}")
    
    def track_guild_join(self):
        """Track when bot joins a guild"""
        if not self.db_connected:
            return
            
        try:
            with self.app.app_context():
                self.BotStats.increment_stat('guilds_joined')
                
        except Exception as e:
            logger.error(f"Failed to track guild join: {e}")
    
    def update_heartbeat(self):
        """Update bot heartbeat to show it's alive"""
        if not self.db_connected:
            return
            
        try:
            with self.app.app_context():
                self.BotStats.set_stat('last_heartbeat', int(time.time()))
                
        except Exception as e:
            logger.error(f"Failed to update heartbeat: {e}")

# Global stats tracker instance
stats_tracker = StatsTracker()