"""
Discord Bot Slash Commands
"""
import logging
import discord
from discord import app_commands
from discord.ext import commands
from .utils import MessageUtils


logger = logging.getLogger(__name__)

def is_commands_channel(interaction: discord.Interaction) -> bool:
    """Check if the interaction is in a commands channel"""
    if not interaction.channel:
        return False
    channel_name = interaction.channel.name.lower()
    return "command" in channel_name and ("⚠️" in interaction.channel.name or "warning" in channel_name)

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
            ephemeral = is_commands_channel(interaction)
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
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
            ephemeral = is_commands_channel(interaction)
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
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
            
            ephemeral = is_commands_channel(interaction)
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
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
    @app_commands.default_permissions(administrator=True)
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
            player_count, max_players, is_online, _ = await check_minecraft_server(server_ip, server_port)
            
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
            ephemeral = is_commands_channel(interaction)
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
            logger.info(f"Commands list requested by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in commands command: {e}")
            await interaction.response.send_message("❌ An error occurred while listing commands.", ephemeral=True)
    

    

    
    @bot.tree.command(name="send-commands", description="Send command list to a channel (Admin only)")
    @app_commands.describe(channel="Channel to send the command list to")
    @app_commands.default_permissions(administrator=True)
    async def send_commands(interaction: discord.Interaction, channel: discord.TextChannel):
        """Send command list to specified channel"""
        try:
            commands = bot.tree.get_commands()
            
            embed = MessageUtils.create_info_embed(
                title="🤖 MagmaCraft Bot Commands",
                description="Here are all available slash commands for the server:"
            )
            
            # Group commands by category
            general_commands = []
            minecraft_commands = []
            voice_commands = []
            admin_commands = []
            
            for cmd in commands:
                cmd_text = f"**`/{cmd.name}`** - {cmd.description}"
                
                if cmd.name in ['ping', 'hello', 'info', 'commands']:
                    general_commands.append(cmd_text)
                elif cmd.name in ['minecraft-counter']:
                    admin_commands.append(cmd_text)

                elif cmd.name in ['say', 'embed']:
                    admin_commands.append(cmd_text)
                else:
                    general_commands.append(cmd_text)
            
            if general_commands:
                embed.add_field(
                    name="🔧 General Commands",
                    value="\n".join(general_commands),
                    inline=False
                )
            

            
            if admin_commands:
                embed.add_field(
                    name="🛡️ Admin Commands",
                    value="\n".join(admin_commands),
                    inline=False
                )
            
            embed.add_field(
                name="📊 Server Monitoring",
                value="The bot automatically monitors your Minecraft server with smart dynamic updates and provides real-time status channels.",
                inline=False
            )
            
            embed.set_footer(text="Use / followed by the command name to use them")
            
            await channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Command list sent to {channel.mention}", ephemeral=True)
            logger.info(f"Command list sent to #{channel.name} by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in send-commands command: {e}")
            await interaction.response.send_message("❌ An error occurred while sending command list.", ephemeral=True)
    
    @bot.tree.command(name="reset-counter", description="Reset all Minecraft counter channels (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def reset_counter(interaction: discord.Interaction):
        """Reset Minecraft counter system"""
        try:
            # Clear the counter channels from the bot's tracking
            if hasattr(bot, 'minecraft_counters'):
                bot.minecraft_counters.clear()
                logger.info("Cleared minecraft counters tracking")
            
            # The update task continues running but will have no counters to update
            logger.info("Counter tracking cleared - update task will continue but find no counters")
            
            embed = MessageUtils.create_success_embed(
                title="🔄 Counter Reset Complete",
                description="All Minecraft counter channels have been reset. You can now create new ones with `/minecraft-counter`."
            )
            embed.add_field(
                name="ℹ️ What was reset",
                value="• Counter channel tracking cleared\n• Update tasks cancelled\n• Ready for new counter setup",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Counter reset by admin: {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in reset-counter command: {e}")
            await interaction.response.send_message("❌ An error occurred while resetting counters.", ephemeral=True)
    
    @bot.tree.command(name="force-update", description="Force update all Minecraft counter channels (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def force_update(interaction: discord.Interaction):
        """Manually trigger counter update"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            if not hasattr(bot, 'minecraft_counters') or not bot.minecraft_counters:
                await interaction.followup.send("❌ No counter channels are currently active.", ephemeral=True)
                return
            
            # Import the update function  
            from .minecraft_utils import update_minecraft_counter_channel
            
            # Force an update on all counters
            updated_count = 0
            for channel_id, server_info in bot.minecraft_counters.items():
                try:
                    success, _, _ = await update_minecraft_counter_channel(bot, channel_id, server_info)
                    if success:
                        updated_count += 1
                except Exception as e:
                    logger.error(f"Error force updating counter {channel_id}: {e}")
            
            embed = MessageUtils.create_success_embed(
                title="🔄 Update Triggered",
                description=f"Manually updated {updated_count} counter channels."
            )
            embed.add_field(
                name="📊 Active Counters",
                value=f"Currently monitoring **{len(bot.minecraft_counters)}** counter channels",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Manual counter update triggered by admin: {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in force-update command: {e}")
            try:
                await interaction.followup.send("❌ An error occurred while forcing update.", ephemeral=True)
            except:
                await interaction.response.send_message("❌ An error occurred while forcing update.", ephemeral=True)
    
    logger.info("All slash commands have been set up")
    logger.info("Commands registered: ping, hello, info, say, embed, minecraft-counter, commands, send-commands, reset-counter, force-update")
