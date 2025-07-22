"""
Database models for Discord bot statistics tracking
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timezone
import json

db = SQLAlchemy()

class BotStats(db.Model):
    """General bot statistics"""
    __tablename__ = 'bot_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    stat_name = db.Column(db.String(100), unique=True, nullable=False)
    stat_value = db.Column(db.BigInteger, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    @staticmethod
    def increment_stat(stat_name: str, increment: int = 1):
        """Increment a statistic by a given amount"""
        stat = BotStats.query.filter_by(stat_name=stat_name).first()
        if stat:
            stat.stat_value += increment
            stat.last_updated = datetime.now(timezone.utc)
        else:
            stat = BotStats(
                stat_name=stat_name,
                stat_value=increment,
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(stat)
        db.session.commit()
        return stat
    
    @staticmethod
    def get_stat(stat_name: str, default: int = 0):
        """Get a statistic value"""
        stat = BotStats.query.filter_by(stat_name=stat_name).first()
        return stat.stat_value if stat else default
    
    @staticmethod
    def set_stat(stat_name: str, value: int):
        """Set a statistic to a specific value"""
        stat = BotStats.query.filter_by(stat_name=stat_name).first()
        if stat:
            stat.stat_value = value
            stat.last_updated = datetime.now(timezone.utc)
        else:
            stat = BotStats(
                stat_name=stat_name,
                stat_value=value,
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(stat)
        db.session.commit()
        return stat

class MinecraftServerStats(db.Model):
    """Minecraft server monitoring statistics"""
    __tablename__ = 'minecraft_server_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    server_ip = db.Column(db.String(255), nullable=False)
    server_port = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Server status
    is_online = db.Column(db.Boolean, nullable=False)
    player_count = db.Column(db.Integer, default=0)
    max_players = db.Column(db.Integer, default=0)
    
    # Response metrics
    response_time_ms = db.Column(db.Integer, default=0)  # Response time in milliseconds
    
    # Players list (JSON stored as text)
    players_list = db.Column(db.Text)  # JSON array of player names
    
    def __repr__(self):
        return f'<MinecraftServerStats {self.server_ip}:{self.server_port} - {self.player_count}/{self.max_players}>'
    
    @property
    def players(self):
        """Get players list as Python list"""
        if self.players_list:
            try:
                return json.loads(self.players_list)
            except:
                return []
        return []
    
    @players.setter
    def players(self, player_list):
        """Set players list from Python list"""
        self.players_list = json.dumps(player_list) if player_list else None

class CommandUsage(db.Model):
    """Track Discord command usage"""
    __tablename__ = 'command_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    command_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(20), nullable=False)
    guild_id = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    success = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<CommandUsage {self.command_name} by {self.user_id}>'

class BotUptime(db.Model):
    """Track bot uptime sessions"""
    __tablename__ = 'bot_uptime'
    
    id = db.Column(db.Integer, primary_key=True)
    session_start = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    session_end = db.Column(db.DateTime)
    uptime_seconds = db.Column(db.Integer, default=0)
    
    def end_session(self):
        """Mark session as ended and calculate uptime"""
        self.session_end = datetime.now(timezone.utc)
        if self.session_start:
            self.uptime_seconds = int((self.session_end - self.session_start).total_seconds())
        db.session.commit()
    
    @staticmethod
    def get_total_uptime():
        """Get total uptime across all sessions in seconds"""
        result = db.session.query(func.sum(BotUptime.uptime_seconds)).scalar()
        return result or 0
    
    @staticmethod
    def get_current_session():
        """Get the current active session (session_end is None)"""
        return BotUptime.query.filter_by(session_end=None).first()