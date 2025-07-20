"""
Discord Bot Event Handlers
"""
import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

def setup_events(bot):
    """Set up all event handlers for the bot"""
    
    @bot.event
    async def on_guild_join(guild):
        """Called when the bot joins a new guild"""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id}) with {guild.member_count} members")
        
        # Try to send a welcome message to the first available channel
        try:
            # Find a suitable channel to send welcome message
            channel = None
            
            # Try to find general channel
            for ch in guild.text_channels:
                if ch.name.lower() in ['general', 'welcome', 'main']:
                    channel = ch
                    break
            
            # If no specific channel found, use the first available channel
            if not channel:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            if channel:
                embed = discord.Embed(
                    title="👋 Hello!",
                    description="Thank you for adding me to your server!\n\nI'm a Discord bot with message sending capabilities and custom slash commands.",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="🚀 Getting Started",
                    value="Use `/ping` to test if I'm working\nUse `/info` to learn more about me\nUse `/hello` for a friendly greeting",
                    inline=False
                )
                embed.add_field(
                    name="💡 Commands",
                    value="All my commands are slash commands! Just type `/` and you'll see them.",
                    inline=False
                )
                embed.set_footer(text="Thanks for using our bot!")
                
                await channel.send(embed=embed)
                logger.info(f"Sent welcome message to #{channel.name} in {guild.name}")
                
        except Exception as e:
            logger.error(f"Failed to send welcome message in {guild.name}: {e}")
    
    @bot.event
    async def on_guild_remove(guild):
        """Called when the bot is removed from a guild"""
        logger.info(f"Removed from guild: {guild.name} (ID: {guild.id})")
    
    @bot.event
    async def on_command_error(ctx, error):
        """Handle command errors (for text commands)"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        logger.error(f"Command error in {ctx.command}: {error}")
        
        try:
            await ctx.send("❌ An error occurred while executing the command.", delete_after=10)
        except discord.Forbidden:
            pass  # Can't send message
    
    @bot.event
    async def on_app_command_error(interaction, error):
        """Handle slash command errors"""
        logger.error(f"Slash command error in {interaction.command}: {error}")
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while executing the command.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ An error occurred while executing the command.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    @bot.event
    async def on_message(message):
        """Handle message events"""
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Log messages mentioning the bot
        if bot.user.mentioned_in(message):
            logger.info(f"Bot mentioned by {message.author} in #{message.channel.name}: {message.content}")
        
        # Process commands (for text commands)
        await bot.process_commands(message)
    
    @bot.event
    async def on_member_join(member):
        """Called when a member joins a guild"""
        logger.info(f"New member joined {member.guild.name}: {member} (ID: {member.id})")
    
    @bot.event
    async def on_member_remove(member):
        """Called when a member leaves a guild"""
        logger.info(f"Member left {member.guild.name}: {member} (ID: {member.id})")
    
    logger.info("All event handlers have been set up")
