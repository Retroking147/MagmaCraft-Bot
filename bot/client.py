"""
Discord Bot Client
"""
import logging
import os
import discord
from discord.ext import commands
from .commands import setup_commands
from .events import setup_events

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Custom Discord Bot class with enhanced functionality"""
    
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        # Initialize bot with command prefix and intents
        super().__init__(
            command_prefix='!',  # Fallback prefix for text commands
            intents=intents,
            help_command=None  # Disable default help command
        )
        
        # Bot configuration
        self.initial_extensions = []
        self.guild_id = os.getenv('GUILD_ID')
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up bot...")
        
        # Set up commands and events
        await setup_commands(self)
        setup_events(self)
        
        # Sync slash commands
        try:
            if self.guild_id:
                # Sync to specific guild for faster testing
                guild = discord.Object(id=int(self.guild_id))
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} commands to guild {self.guild_id}")
            else:
                # Sync globally (takes up to 1 hour to propagate)
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} commands globally")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set bot activity
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for slash commands"
        )
        await self.change_presence(activity=activity)
    
    async def on_error(self, event, *args, **kwargs):
        """Global error handler"""
        logger.error(f"Error in event {event}", exc_info=True)
    
    async def send_message(self, channel_id: int, content: str = None, embed: discord.Embed = None):
        """
        Send a message to a specific channel
        
        Args:
            channel_id (int): The ID of the channel to send to
            content (str): The message content
            embed (discord.Embed): Optional embed to send
            
        Returns:
            discord.Message: The sent message, or None if failed
        """
        try:
            channel = self.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel with ID {channel_id} not found")
                return None
            
            message = await channel.send(content=content, embed=embed)
            logger.info(f"Message sent to #{channel.name}: {content[:50]}...")
            return message
            
        except discord.Forbidden:
            logger.error(f"No permission to send message to channel {channel_id}")
        except discord.HTTPException as e:
            logger.error(f"HTTP error sending message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
        
        return None
    
    async def send_dm(self, user_id: int, content: str = None, embed: discord.Embed = None):
        """
        Send a direct message to a user
        
        Args:
            user_id (int): The ID of the user to send to
            content (str): The message content
            embed (discord.Embed): Optional embed to send
            
        Returns:
            discord.Message: The sent message, or None if failed
        """
        try:
            user = self.get_user(user_id) or await self.fetch_user(user_id)
            if not user:
                logger.error(f"User with ID {user_id} not found")
                return None
            
            message = await user.send(content=content, embed=embed)
            logger.info(f"DM sent to {user.name}: {content[:50]}...")
            return message
            
        except discord.Forbidden:
            logger.error(f"Cannot send DM to user {user_id} (DMs may be disabled)")
        except discord.HTTPException as e:
            logger.error(f"HTTP error sending DM: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending DM: {e}")
        
        return None
