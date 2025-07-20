"""
Discord Bot Utilities
"""
import logging
import discord
from typing import Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageUtils:
    """Utility class for message-related operations"""
    
    @staticmethod
    def create_embed(
        title: str = None,
        description: str = None,
        color: discord.Color = discord.Color.blue(),
        timestamp: bool = True
    ) -> discord.Embed:
        """
        Create a basic embed with common settings
        
        Args:
            title (str): Embed title
            description (str): Embed description
            color (discord.Color): Embed color
            timestamp (bool): Whether to add timestamp
            
        Returns:
            discord.Embed: The created embed
        """
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        if timestamp:
            embed.timestamp = datetime.utcnow()
        
        return embed
    
    @staticmethod
    def create_success_embed(
        title: str = None,
        description: str = None,
        timestamp: bool = True
    ) -> discord.Embed:
        """Create a success-themed embed (green color)"""
        return MessageUtils.create_embed(
            title=title,
            description=description,
            color=discord.Color.green(),
            timestamp=timestamp
        )
    
    @staticmethod
    def create_error_embed(
        title: str = None,
        description: str = None,
        timestamp: bool = True
    ) -> discord.Embed:
        """Create an error-themed embed (red color)"""
        return MessageUtils.create_embed(
            title=title,
            description=description,
            color=discord.Color.red(),
            timestamp=timestamp
        )
    
    @staticmethod
    def create_warning_embed(
        title: str = None,
        description: str = None,
        timestamp: bool = True
    ) -> discord.Embed:
        """Create a warning-themed embed (orange color)"""
        return MessageUtils.create_embed(
            title=title,
            description=description,
            color=discord.Color.orange(),
            timestamp=timestamp
        )
    
    @staticmethod
    def create_info_embed(
        title: str = None,
        description: str = None,
        timestamp: bool = True
    ) -> discord.Embed:
        """Create an info-themed embed (blue color)"""
        return MessageUtils.create_embed(
            title=title,
            description=description,
            color=discord.Color.blue(),
            timestamp=timestamp
        )
    
    @staticmethod
    def format_user_info(user: Union[discord.User, discord.Member]) -> discord.Embed:
        """
        Create an embed with user information
        
        Args:
            user: Discord user or member object
            
        Returns:
            discord.Embed: Formatted user info embed
        """
        embed = MessageUtils.create_info_embed(
            title=f"👤 {user.display_name}",
            description=f"Information about {user.mention}"
        )
        
        embed.add_field(name="Username", value=f"`{user}`", inline=True)
        embed.add_field(name="ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        
        if isinstance(user, discord.Member):
            embed.add_field(name="Joined", value=f"<t:{int(user.joined_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Roles", value=f"`{len(user.roles) - 1}`", inline=True)  # -1 to exclude @everyone
            
            if user.premium_since:
                embed.add_field(name="Boosting Since", value=f"<t:{int(user.premium_since.timestamp())}:R>", inline=True)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        return embed
    
    @staticmethod
    def format_guild_info(guild: discord.Guild) -> discord.Embed:
        """
        Create an embed with guild information
        
        Args:
            guild: Discord guild object
            
        Returns:
            discord.Embed: Formatted guild info embed
        """
        embed = MessageUtils.create_info_embed(
            title=f"🏠 {guild.name}",
            description=guild.description or "No description available"
        )
        
        embed.add_field(name="ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        
        embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="Channels", value=f"`{len(guild.channels)}`", inline=True)
        embed.add_field(name="Roles", value=f"`{len(guild.roles)}`", inline=True)
        
        if guild.premium_subscription_count:
            embed.add_field(name="Boosts", value=f"`{guild.premium_subscription_count}`", inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        return embed
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 2000) -> str:
        """
        Truncate text to fit Discord's character limits
        
        Args:
            text (str): Text to truncate
            max_length (int): Maximum length (default: 2000 for message content)
            
        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def format_code_block(content: str, language: str = "") -> str:
        """
        Format text as a code block
        
        Args:
            content (str): Content to format
            language (str): Programming language for syntax highlighting
            
        Returns:
            str: Formatted code block
        """
        return f"```{language}\n{content}\n```"
    
    @staticmethod
    def format_inline_code(content: str) -> str:
        """
        Format text as inline code
        
        Args:
            content (str): Content to format
            
        Returns:
            str: Formatted inline code
        """
        return f"`{content}`"

class RateLimitUtils:
    """Utility class for rate limiting awareness"""
    
    @staticmethod
    def calculate_send_delay(message_count: int) -> float:
        """
        Calculate appropriate delay between messages to avoid rate limits
        
        Args:
            message_count (int): Number of messages to send
            
        Returns:
            float: Delay in seconds
        """
        # Discord allows 5 messages per 5 seconds per channel
        if message_count <= 5:
            return 0.0
        
        # Add 1 second delay for every 5 messages beyond the first 5
        return ((message_count - 1) // 5) * 1.0
    
    @staticmethod
    def is_rate_limited_error(error: Exception) -> bool:
        """
        Check if an error is rate limit related
        
        Args:
            error (Exception): The error to check
            
        Returns:
            bool: True if rate limit error
        """
        return isinstance(error, discord.HTTPException) and error.status == 429

class PermissionUtils:
    """Utility class for permission checking"""
    
    @staticmethod
    def can_send_messages(channel: discord.TextChannel, member: discord.Member) -> bool:
        """
        Check if a member can send messages in a channel
        
        Args:
            channel: The text channel
            member: The member to check
            
        Returns:
            bool: True if can send messages
        """
        return channel.permissions_for(member).send_messages
    
    @staticmethod
    def can_manage_messages(channel: discord.TextChannel, member: discord.Member) -> bool:
        """
        Check if a member can manage messages in a channel
        
        Args:
            channel: The text channel
            member: The member to check
            
        Returns:
            bool: True if can manage messages
        """
        return channel.permissions_for(member).manage_messages
    
    @staticmethod
    def can_embed_links(channel: discord.TextChannel, member: discord.Member) -> bool:
        """
        Check if a member can embed links in a channel
        
        Args:
            channel: The text channel
            member: The member to check
            
        Returns:
            bool: True if can embed links
        """
        return channel.permissions_for(member).embed_links
