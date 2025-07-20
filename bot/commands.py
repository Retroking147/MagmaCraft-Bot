"""
Discord Bot Slash Commands
"""
import logging
import discord
from discord import app_commands
from discord.ext import commands
from .utils import MessageUtils
from .voice_bridge import VoiceBridge

logger = logging.getLogger(__name__)

async def setup_commands(bot):
    """Set up all slash commands for the bot"""
    
    @bot.tree.command(name="ping", description="Check bot latency")
    async def ping(interaction: discord.Interaction):
        """Ping command to check bot latency"""
        try:
            latency = round(bot.latency * 1000)
            embed = MessageUtils.create_info_embed(
                title="🏓 Pong!",
                description=f"Bot latency: `{latency}ms`"
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"Ping command used by {interaction.user} - Latency: {latency}ms")
        except Exception as e:
            logger.error(f"Error in ping command: {e}")
            await interaction.response.send_message("❌ An error occurred while checking latency.", ephemeral=True)
    
    @bot.tree.command(name="hello", description="Get a friendly greeting")
    async def hello(interaction: discord.Interaction):
        """Hello command for friendly greeting"""
        try:
            user = interaction.user
            embed = MessageUtils.create_success_embed(
                title="👋 Hello!",
                description=f"Hello {user.mention}! Nice to meet you!"
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            logger.info(f"Hello command used by {user}")
        except Exception as e:
            logger.error(f"Error in hello command: {e}")
            await interaction.response.send_message("❌ An error occurred while saying hello.", ephemeral=True)
    
    @bot.tree.command(name="info", description="Get information about the bot")
    async def info(interaction: discord.Interaction):
        """Info command to display bot information"""
        try:
            embed = MessageUtils.create_info_embed(
                title="🤖 Bot Information",
                description="A Discord bot with message sending capabilities and custom slash commands"
            )
            
            # Add bot statistics
            embed.add_field(
                name="📊 Statistics",
                value=f"• Guilds: `{len(bot.guilds)}`\n• Users: `{len(bot.users)}`\n• Latency: `{round(bot.latency * 1000)}ms`",
                inline=True
            )
            
            # Add bot details
            embed.add_field(
                name="ℹ️ Details",
                value=f"• Created: <t:{int(bot.user.created_at.timestamp())}:D>\n• Library: `discord.py`\n• Python: `3.x`",
                inline=True
            )
            
            # Add commands info
            commands_count = len(bot.tree.get_commands())
            embed.add_field(
                name="⚡ Commands",
                value=f"• Slash Commands: `{commands_count}`\n• Prefix: `{bot.command_prefix}`",
                inline=True
            )
            
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            embed.set_footer(text=f"Bot ID: {bot.user.id}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Info command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in info command: {e}")
            await interaction.response.send_message("❌ An error occurred while fetching bot information.", ephemeral=True)
    
    @bot.tree.command(name="say", description="Make the bot say something")
    @app_commands.describe(
        message="The message you want the bot to say",
        channel="The channel to send the message to (optional)"
    )
    async def say(interaction: discord.Interaction, message: str, channel: discord.TextChannel = None):
        """Say command to make bot send messages"""
        try:
            # Use current channel if no channel specified
            target_channel = channel or interaction.channel
            
            # Check permissions
            if not target_channel.permissions_for(interaction.guild.me).send_messages:
                await interaction.response.send_message(
                    f"❌ I don't have permission to send messages in {target_channel.mention}",
                    ephemeral=True
                )
                return
            
            # Send the message
            await target_channel.send(message)
            
            # Confirm to user
            if channel and channel != interaction.channel:
                await interaction.response.send_message(
                    f"✅ Message sent to {target_channel.mention}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message("✅ Message sent!", ephemeral=True)
            
            logger.info(f"Say command used by {interaction.user} in #{target_channel.name}: {message[:50]}...")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to send messages in that channel.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in say command: {e}")
            await interaction.response.send_message("❌ An error occurred while sending the message.", ephemeral=True)
    
    @bot.tree.command(name="embed", description="Send a message as an embed")
    @app_commands.describe(
        title="The title of the embed",
        description="The description/content of the embed",
        color="Hex color code (e.g., #ff0000 for red)"
    )
    async def embed(interaction: discord.Interaction, title: str, description: str, color: str = None):
        """Embed command to send formatted embeds"""
        try:
            # Parse color
            embed_color = discord.Color.blue()  # Default color
            if color:
                try:
                    # Remove # if present and convert to int
                    color_hex = color.lstrip('#')
                    embed_color = discord.Color(int(color_hex, 16))
                except ValueError:
                    await interaction.response.send_message(
                        "❌ Invalid color format. Use hex format like `#ff0000`",
                        ephemeral=True
                    )
                    return
            
            # Create embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=embed_color
            )
            embed.set_footer(text=f"Sent by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Embed command used by {interaction.user}: {title}")
            
        except Exception as e:
            logger.error(f"Error in embed command: {e}")
            await interaction.response.send_message("❌ An error occurred while creating the embed.", ephemeral=True)
    
    @bot.tree.command(name="minecraft-counter", description="Create channels that show Minecraft server status and player count")
    @app_commands.describe(
        server_ip="Your Minecraft server IP address",
        server_port="Server port (default: 25565)",
        status_channel_name="Name format for status channel (use {status} for online/offline)",
        count_channel_name="Name format for player count channel (use {count} for player count)"
    )
    async def minecraft_counter(
        interaction: discord.Interaction, 
        server_ip: str, 
        server_port: int = 25565,
        status_channel_name: str = "{status}",
        count_channel_name: str = "👤 {count} Players"
    ):
        """Create a voice channel that displays Minecraft server player count"""
        try:
            # Check if user has manage channels permission
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    "❌ You need 'Manage Channels' permission to use this command.",
                    ephemeral=True
                )
                return
            
            # Check if bot has manage channels permission
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    "❌ I need 'Manage Channels' permission to create channels.",
                    ephemeral=True
                )
                return
            
            await interaction.response.defer()
            
            # Import minecraft server status checker
            from .minecraft_utils import check_minecraft_server
            
            # Check if server is reachable
            player_count, max_players, is_online = await check_minecraft_server(server_ip, server_port)
            
            if not is_online:
                await interaction.followup.send(
                    f"❌ Could not connect to Minecraft server `{server_ip}:{server_port}`. "
                    "Please check the IP address and port.",
                    ephemeral=True
                )
                return
            
            # Format channel names
            status_indicator = "🟢" if is_online else "🔴"
            status_text = "Online" if is_online else "Offline"
            status_formatted_name = status_channel_name.format(status=f"{status_indicator} {status_text}")
            count_formatted_name = count_channel_name.format(count=f"{player_count}/{max_players}")
            
            # Create status voice channel
            status_channel = await interaction.guild.create_voice_channel(
                name=status_formatted_name,
                reason=f"Minecraft status counter created by {interaction.user}"
            )
            
            # Create player count voice channel
            count_channel = await interaction.guild.create_voice_channel(
                name=count_formatted_name,
                reason=f"Minecraft player counter created by {interaction.user}"
            )
            
            # Store server info in bot's memory for updates
            if not hasattr(bot, 'minecraft_counters'):
                bot.minecraft_counters = {}
            
            # Store both channels with their templates
            bot.minecraft_counters[status_channel.id] = {
                'server_ip': server_ip,
                'server_port': server_port,
                'channel_type': 'status',
                'channel_name_template': status_channel_name,
                'guild_id': interaction.guild.id
            }
            
            bot.minecraft_counters[count_channel.id] = {
                'server_ip': server_ip,
                'server_port': server_port,
                'channel_type': 'count',
                'channel_name_template': count_channel_name,
                'guild_id': interaction.guild.id
            }
            
            # Create success embed
            embed = MessageUtils.create_success_embed(
                title="🎮 Minecraft Counters Created!",
                description=f"Created two channels for your server monitoring"
            )
            embed.add_field(
                name="📊 Status Channel",
                value=f"**{status_formatted_name}**\nShows online/offline status",
                inline=True
            )
            embed.add_field(
                name="👤 Player Count Channel", 
                value=f"**{count_formatted_name}**\nShows current player count",
                inline=True
            )
            embed.add_field(
                name="🔄 Smart Updates",
                value="• **Players online**: 15-second intervals\n• **Server empty**: Maintains 15-second intervals for 2 minutes\n• **After grace period**: Switches to 30-second intervals",
                inline=False
            )
            embed.add_field(
                name="🖥️ Server Info",
                value=f"Server: `{server_ip}:{server_port}`\nCurrent Status: `{status_text}`\nPlayers: `{player_count}/{max_players}`",
                inline=False
            )
            embed.set_footer(text=f"Status ID: {status_channel.id} | Count ID: {count_channel.id}")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Minecraft counter created by {interaction.user} for server {server_ip}:{server_port}")
            
        except ImportError:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ Minecraft server checking functionality is being set up. Please try again in a moment.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Minecraft server checking functionality is being set up. Please try again in a moment.",
                        ephemeral=True
                    )
            except:
                pass
        except Exception as e:
            logger.error(f"Error in minecraft-counter command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred while creating the Minecraft counter.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ An error occurred while creating the Minecraft counter.",
                        ephemeral=True
                    )
            except:
                pass
    
    @bot.tree.command(name="commands", description="List all available bot commands")
    async def commands_list(interaction: discord.Interaction):
        """List all available commands"""
        try:
            commands = bot.tree.get_commands()
            
            embed = MessageUtils.create_info_embed(
                title="🤖 Available Commands",
                description=f"Here are all {len(commands)} available slash commands:"
            )
            
            command_list = []
            for cmd in commands:
                command_list.append(f"• `/{cmd.name}` - {cmd.description}")
            
            embed.add_field(
                name="Commands",
                value="\n".join(command_list),
                inline=False
            )
            
            embed.set_footer(text="Use / followed by the command name to use them")
            await interaction.response.send_message(embed=embed)
            logger.info(f"Commands list requested by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in commands command: {e}")
            await interaction.response.send_message("❌ An error occurred while listing commands.", ephemeral=True)
    
    # Voice Bridge Commands
    @bot.tree.command(name="voice-link", description="Link your Discord account to your Minecraft username for voice bridge")
    @app_commands.describe(minecraft_username="Your exact Minecraft username (case-sensitive)")
    async def voice_link(interaction: discord.Interaction, minecraft_username: str):
        """Link Discord user to Minecraft username for voice bridge"""
        try:
            if not hasattr(bot, 'voice_bridge'):
                bot.voice_bridge = VoiceBridge(bot)
            
            # Set up voice channel if it doesn't exist
            await bot.voice_bridge.setup_voice_channel(interaction.guild)
            
            # Link the user
            success = bot.voice_bridge.link_user(interaction.user.id, minecraft_username)
            
            if success:
                embed = MessageUtils.create_success_embed(
                    title="🔗 Voice Link Created!",
                    description=f"Your Discord account is now linked to Minecraft username: **{minecraft_username}**"
                )
                embed.add_field(
                    name="🎮 How it works",
                    value="• When you join the Minecraft server, you'll be moved to the voice bridge channel\n• When you leave Minecraft, you'll be removed from the voice bridge\n• This allows cross-platform voice chat with Bedrock players",
                    inline=False
                )
                embed.add_field(
                    name="🎤 Voice Channel",
                    value=f"Voice bridge: **{bot.voice_bridge.minecraft_voice_channel.mention}**",
                    inline=False
                )
            else:
                embed = MessageUtils.create_error_embed(
                    title="❌ Link Failed",
                    description="Failed to create voice link. Please try again."
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Voice link command by {interaction.user}: {minecraft_username}")
            
        except Exception as e:
            logger.error(f"Error in voice-link command: {e}")
            await interaction.response.send_message("❌ An error occurred while creating voice link.", ephemeral=True)
    
    @bot.tree.command(name="voice-unlink", description="Remove your Minecraft voice bridge link")
    async def voice_unlink(interaction: discord.Interaction):
        """Unlink Discord user from Minecraft voice bridge"""
        try:
            if not hasattr(bot, 'voice_bridge'):
                bot.voice_bridge = VoiceBridge(bot)
            
            success = bot.voice_bridge.unlink_user(interaction.user.id)
            
            if success:
                embed = MessageUtils.create_success_embed(
                    title="🔗 Voice Link Removed",
                    description="Your Discord account has been unlinked from the Minecraft voice bridge."
                )
            else:
                embed = MessageUtils.create_error_embed(
                    title="❌ No Link Found",
                    description="You don't have an active voice bridge link to remove."
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Voice unlink command by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in voice-unlink command: {e}")
            await interaction.response.send_message("❌ An error occurred while removing voice link.", ephemeral=True)
    
    @bot.tree.command(name="voice-status", description="Check your voice bridge link status")
    async def voice_status(interaction: discord.Interaction):
        """Check voice bridge link status"""
        try:
            if not hasattr(bot, 'voice_bridge'):
                bot.voice_bridge = VoiceBridge(bot)
            
            minecraft_username = bot.voice_bridge.get_minecraft_username(interaction.user.id)
            stats = bot.voice_bridge.get_stats()
            
            if minecraft_username:
                embed = MessageUtils.create_info_embed(
                    title="🎤 Voice Bridge Status",
                    description=f"Your Discord account is linked to: **{minecraft_username}**"
                )
                embed.add_field(
                    name="🔗 Link Status",
                    value="✅ Active voice bridge link",
                    inline=True
                )
            else:
                embed = MessageUtils.create_info_embed(
                    title="🎤 Voice Bridge Status",
                    description="Your Discord account is not linked to any Minecraft username."
                )
                embed.add_field(
                    name="🔗 Link Status",
                    value="❌ No active voice bridge link\nUse `/voice-link` to create one",
                    inline=True
                )
            
            embed.add_field(
                name="📊 Bridge Statistics",
                value=f"Total linked users: **{stats['total_links']}**\nVoice channel: **{'✅ Active' if stats['voice_channel_exists'] else '❌ Not set up'}**",
                inline=False
            )
            
            if stats['voice_channel_exists']:
                channel = bot.voice_bridge.minecraft_voice_channel
                embed.add_field(
                    name="🎮 Voice Channel",
                    value=f"{channel.mention} ({len(channel.members)} members connected)",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Voice status command by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in voice-status command: {e}")
            await interaction.response.send_message("❌ An error occurred while checking voice status.", ephemeral=True)
    
    logger.info("All slash commands have been set up")
    logger.info("Commands registered: ping, hello, info, say, embed, minecraft-counter, commands, voice-link, voice-unlink, voice-status")
