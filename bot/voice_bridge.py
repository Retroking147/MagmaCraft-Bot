"""
Minecraft Voice Bridge System
Manages Discord voice channels for cross-platform communication
"""
import logging
import json
import os
from typing import Dict, Optional, Set
import discord

logger = logging.getLogger(__name__)

class VoiceBridge:
    """Manages voice bridge functionality for Minecraft cross-platform communication"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_links = {}  # Discord user ID -> Minecraft username
        self.minecraft_voice_channel = None
        self.data_file = "voice_links.json"
        self.load_voice_links()
    
    def load_voice_links(self):
        """Load voice link data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.voice_links = {int(k): v for k, v in data.items()}
                logger.info(f"Loaded {len(self.voice_links)} voice links")
            else:
                self.voice_links = {}
        except Exception as e:
            logger.error(f"Error loading voice links: {e}")
            self.voice_links = {}
    
    def save_voice_links(self):
        """Save voice link data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.voice_links, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving voice links: {e}")
    
    async def setup_voice_channel(self, guild: discord.Guild) -> Optional[discord.VoiceChannel]:
        """Create or find the Minecraft voice bridge channel"""
        try:
            # Look for existing channel
            for channel in guild.voice_channels:
                if channel.name == "🎮 Minecraft Voice Bridge":
                    self.minecraft_voice_channel = channel
                    logger.info(f"Found existing voice bridge channel: {channel.name}")
                    return channel
            
            # Create new channel
            channel = await guild.create_voice_channel(
                "🎮 Minecraft Voice Bridge",
                reason="Minecraft cross-platform voice communication"
            )
            self.minecraft_voice_channel = channel
            logger.info(f"Created voice bridge channel: {channel.name}")
            return channel
            
        except Exception as e:
            logger.error(f"Error setting up voice channel: {e}")
            return None
    
    def link_user(self, discord_user_id: int, minecraft_username: str) -> bool:
        """Link a Discord user to a Minecraft username"""
        try:
            self.voice_links[discord_user_id] = minecraft_username.lower()
            self.save_voice_links()
            logger.info(f"Linked Discord user {discord_user_id} to Minecraft user {minecraft_username}")
            return True
        except Exception as e:
            logger.error(f"Error linking user: {e}")
            return False
    
    def unlink_user(self, discord_user_id: int) -> bool:
        """Unlink a Discord user from their Minecraft account"""
        try:
            if discord_user_id in self.voice_links:
                minecraft_username = self.voice_links.pop(discord_user_id)
                self.save_voice_links()
                logger.info(f"Unlinked Discord user {discord_user_id} from Minecraft user {minecraft_username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error unlinking user: {e}")
            return False
    
    def get_minecraft_username(self, discord_user_id: int) -> Optional[str]:
        """Get the Minecraft username for a Discord user"""
        return self.voice_links.get(discord_user_id)
    
    def get_discord_user_id(self, minecraft_username: str) -> Optional[int]:
        """Get the Discord user ID for a Minecraft username"""
        minecraft_username = minecraft_username.lower()
        for discord_id, mc_username in self.voice_links.items():
            if mc_username == minecraft_username:
                return discord_id
        return None
    
    def get_all_links(self) -> Dict[int, str]:
        """Get all voice links"""
        return self.voice_links.copy()
    
    async def move_user_to_voice(self, guild: discord.Guild, discord_user_id: int, should_be_in_voice: bool):
        """Move a Discord user in or out of the voice bridge channel"""
        try:
            if not self.minecraft_voice_channel:
                await self.setup_voice_channel(guild)
            
            member = guild.get_member(discord_user_id)
            if not member:
                return
            
            if should_be_in_voice:
                # User should be in voice channel
                if member.voice and member.voice.channel != self.minecraft_voice_channel:
                    # User is in a different voice channel - move them to the bridge
                    await member.move_to(self.minecraft_voice_channel)
                    logger.info(f"Automatically moved {member.display_name} to Minecraft voice bridge (was in {member.voice.channel.name})")
                elif not member.voice:
                    # User not in any voice channel - send them a notification
                    try:
                        embed = discord.Embed(
                            title="🎮 Minecraft Voice Bridge",
                            description=f"You joined the Minecraft server! Join the voice channel to chat with other players.",
                            color=0x00FF00
                        )
                        embed.add_field(
                            name="Voice Channel",
                            value=f"{self.minecraft_voice_channel.mention}",
                            inline=False
                        )
                        await member.send(embed=embed)
                        logger.info(f"Sent voice bridge notification to {member.display_name}")
                    except discord.Forbidden:
                        logger.debug(f"Could not DM {member.display_name} about voice bridge")
                else:
                    # User already in correct channel
                    logger.debug(f"{member.display_name} already in voice bridge")
            else:
                # User should not be in voice channel (they left Minecraft)
                if member.voice and member.voice.channel == self.minecraft_voice_channel:
                    # Check if there are other players still in Minecraft before disconnecting
                    should_disconnect = True
                    
                    # If the user wants to stay connected for other reasons, we can add logic here
                    # For now, we'll automatically disconnect them when they leave Minecraft
                    
                    if should_disconnect:
                        await member.move_to(None)
                        logger.info(f"Automatically disconnected {member.display_name} from voice bridge (left Minecraft)")
                        
                        # Send them a notification
                        try:
                            embed = discord.Embed(
                                title="👋 Left Minecraft",
                                description="You left the Minecraft server, so you were disconnected from the voice bridge.",
                                color=0xFF6B00
                            )
                            await member.send(embed=embed)
                        except discord.Forbidden:
                            logger.debug(f"Could not DM {member.display_name} about voice bridge disconnect")
                    
        except Exception as e:
            logger.error(f"Error managing voice for user {discord_user_id}: {e}")
    
    async def handle_minecraft_player_join(self, guild: discord.Guild, minecraft_username: str):
        """Handle when a Minecraft player joins the server"""
        discord_user_id = self.get_discord_user_id(minecraft_username)
        if discord_user_id:
            await self.move_user_to_voice(guild, discord_user_id, True)
            logger.info(f"Minecraft player {minecraft_username} joined - managing Discord voice")
    
    async def handle_minecraft_player_leave(self, guild: discord.Guild, minecraft_username: str):
        """Handle when a Minecraft player leaves the server"""
        discord_user_id = self.get_discord_user_id(minecraft_username)
        if discord_user_id:
            await self.move_user_to_voice(guild, discord_user_id, False)
            logger.info(f"Minecraft player {minecraft_username} left - managing Discord voice")
    
    def get_stats(self) -> dict:
        """Get voice bridge statistics"""
        return {
            "total_links": len(self.voice_links),
            "voice_channel_exists": self.minecraft_voice_channel is not None,
            "voice_channel_name": self.minecraft_voice_channel.name if self.minecraft_voice_channel else None
        }