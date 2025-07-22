"""
Music player module for Discord bot with YouTube support
"""
import asyncio
import discord
from discord.ext import commands
import yt_dlp
import logging

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queues = {}
        self.current_track = {}
        self.is_playing = {}
        
        # YT-DLP options
        self.ytdl_options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'extract_flat': False
        }
        
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

    async def join_voice_channel(self, channel):
        """Join a voice channel"""
        try:
            voice_client = await channel.connect()
            self.voice_clients[channel.guild.id] = voice_client
            return voice_client
        except Exception as e:
            logging.error(f"Error joining voice channel: {e}")
            return None

    async def leave_voice_channel(self, guild_id):
        """Leave voice channel"""
        if guild_id in self.voice_clients:
            await self.voice_clients[guild_id].disconnect()
            del self.voice_clients[guild_id]
            if guild_id in self.queues:
                self.queues[guild_id].clear()

    def get_voice_client(self, guild_id):
        """Get voice client for guild"""
        return self.voice_clients.get(guild_id)

    async def search_youtube(self, query):
        """Search YouTube for a track"""
        try:
            with yt_dlp.YoutubeDL(self.ytdl_options) as ytdl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=False)
                )
                
                if 'entries' in info and len(info['entries']) > 0:
                    return info['entries'][0]
                return None
        except Exception as e:
            logging.error(f"Error searching YouTube: {e}")
            return None

    async def get_audio_source(self, url):
        """Get audio source from URL"""
        try:
            with yt_dlp.YoutubeDL(self.ytdl_options) as ytdl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ytdl.extract_info(url, download=False)
                )
                
                url = info.get('url')
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                return {
                    'source': discord.FFmpegPCMAudio(url, **self.ffmpeg_options),
                    'title': title,
                    'duration': duration,
                    'url': info.get('webpage_url', url)
                }
        except Exception as e:
            logging.error(f"Error getting audio source: {e}")
            return None

    def add_to_queue(self, guild_id, track_info):
        """Add track to guild queue"""
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        self.queues[guild_id].append(track_info)

    def get_queue(self, guild_id):
        """Get guild queue"""
        return self.queues.get(guild_id, [])

    def clear_queue(self, guild_id):
        """Clear guild queue"""
        if guild_id in self.queues:
            self.queues[guild_id].clear()

    async def play_next(self, guild_id):
        """Play next track in queue"""
        voice_client = self.get_voice_client(guild_id)
        if not voice_client:
            return False

        queue = self.get_queue(guild_id)
        if not queue:
            self.is_playing[guild_id] = False
            return False

        track_info = queue.pop(0)
        audio_source = await self.get_audio_source(track_info['url'])
        
        if audio_source:
            self.current_track[guild_id] = {
                'title': audio_source['title'],
                'duration': audio_source['duration'],
                'url': audio_source['url']
            }
            
            def after_playing(error):
                if error:
                    logging.error(f"Audio playback error: {error}")
                asyncio.run_coroutine_threadsafe(
                    self.play_next(guild_id), self.bot.loop
                )

            voice_client.play(audio_source['source'], after=after_playing)
            self.is_playing[guild_id] = True
            return True
        
        return False

    def pause(self, guild_id):
        """Pause playback"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            return True
        return False

    def resume(self, guild_id):
        """Resume playback"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            return True
        return False

    def stop(self, guild_id):
        """Stop playback"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            self.is_playing[guild_id] = False
            return True
        return False

    def skip(self, guild_id):
        """Skip current track"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # This will trigger play_next via the after callback
            return True
        return False

    def get_current_track(self, guild_id):
        """Get currently playing track"""
        return self.current_track.get(guild_id)

    def is_connected(self, guild_id):
        """Check if bot is connected to voice channel"""
        voice_client = self.get_voice_client(guild_id)
        return voice_client and voice_client.is_connected()

    def is_track_playing(self, guild_id):
        """Check if a track is currently playing"""
        voice_client = self.get_voice_client(guild_id)
        return voice_client and voice_client.is_playing()


class MusicCommands(commands.Cog):
    """Music commands for the Discord bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_player = MusicPlayer(bot)

    @commands.slash_command(name="join", description="Join your voice channel")
    async def join_command(self, ctx):
        """Join the user's voice channel"""
        if not ctx.author.voice:
            await ctx.respond("❌ You need to be in a voice channel!", ephemeral=True)
            return

        channel = ctx.author.voice.channel
        voice_client = await self.music_player.join_voice_channel(channel)
        
        if voice_client:
            await ctx.respond(f"✅ Joined {channel.name}!")
        else:
            await ctx.respond("❌ Failed to join voice channel!", ephemeral=True)

    @commands.slash_command(name="leave", description="Leave voice channel")
    async def leave_command(self, ctx):
        """Leave the voice channel"""
        await self.music_player.leave_voice_channel(ctx.guild.id)
        await ctx.respond("👋 Left voice channel!")

    @commands.slash_command(name="play", description="Play music from YouTube")
    async def play_command(self, ctx, *, query: str):
        """Play music from YouTube search or URL"""
        await ctx.defer()

        # Join voice channel if not already connected
        if not self.music_player.is_connected(ctx.guild.id):
            if not ctx.author.voice:
                await ctx.followup.send("❌ You need to be in a voice channel!")
                return
            
            channel = ctx.author.voice.channel
            voice_client = await self.music_player.join_voice_channel(channel)
            if not voice_client:
                await ctx.followup.send("❌ Failed to join voice channel!")
                return

        # Search for track
        if query.startswith('http'):
            track_info = {'url': query, 'title': 'Unknown Track'}
        else:
            search_result = await self.music_player.search_youtube(query)
            if not search_result:
                await ctx.followup.send("❌ No results found!")
                return
            
            track_info = {
                'url': search_result['webpage_url'],
                'title': search_result['title']
            }

        # Add to queue
        self.music_player.add_to_queue(ctx.guild.id, track_info)
        
        # If nothing is playing, start playing
        if not self.music_player.is_track_playing(ctx.guild.id):
            success = await self.music_player.play_next(ctx.guild.id)
            if success:
                await ctx.followup.send(f"🎵 Now playing: **{track_info['title']}**")
            else:
                await ctx.followup.send("❌ Failed to play track!")
        else:
            await ctx.followup.send(f"📝 Added to queue: **{track_info['title']}**")

    @commands.slash_command(name="pause", description="Pause music playback")
    async def pause_command(self, ctx):
        """Pause the current track"""
        if self.music_player.pause(ctx.guild.id):
            await ctx.respond("⏸️ Paused playback")
        else:
            await ctx.respond("❌ Nothing to pause!", ephemeral=True)

    @commands.slash_command(name="resume", description="Resume music playback")
    async def resume_command(self, ctx):
        """Resume the current track"""
        if self.music_player.resume(ctx.guild.id):
            await ctx.respond("▶️ Resumed playback")
        else:
            await ctx.respond("❌ Nothing to resume!", ephemeral=True)

    @commands.slash_command(name="skip", description="Skip current track")
    async def skip_command(self, ctx):
        """Skip the current track"""
        if self.music_player.skip(ctx.guild.id):
            await ctx.respond("⏭️ Skipped track")
        else:
            await ctx.respond("❌ Nothing to skip!", ephemeral=True)

    @commands.slash_command(name="stop", description="Stop music and clear queue")
    async def stop_command(self, ctx):
        """Stop music and clear the queue"""
        self.music_player.stop(ctx.guild.id)
        self.music_player.clear_queue(ctx.guild.id)
        await ctx.respond("⏹️ Stopped music and cleared queue")

    @commands.slash_command(name="queue", description="Show music queue")
    async def queue_command(self, ctx):
        """Display the current music queue"""
        queue = self.music_player.get_queue(ctx.guild.id)
        current = self.music_player.get_current_track(ctx.guild.id)
        
        embed = discord.Embed(title="🎵 Music Queue", color=0x5865f2)
        
        if current:
            embed.add_field(
                name="Currently Playing",
                value=f"🎶 {current['title']}",
                inline=False
            )
        
        if queue:
            queue_text = "\n".join([f"{i+1}. {track['title']}" for i, track in enumerate(queue[:10])])
            if len(queue) > 10:
                queue_text += f"\n... and {len(queue) - 10} more"
            embed.add_field(name="Up Next", value=queue_text, inline=False)
        else:
            embed.add_field(name="Queue", value="Empty", inline=False)
        
        embed.set_footer(text=f"Total songs in queue: {len(queue)}")
        await ctx.respond(embed=embed)

    @commands.slash_command(name="nowplaying", description="Show current track info")
    async def nowplaying_command(self, ctx):
        """Display information about the currently playing track"""
        current = self.music_player.get_current_track(ctx.guild.id)
        
        if current:
            embed = discord.Embed(title="🎵 Now Playing", color=0x5865f2)
            embed.add_field(name="Track", value=current['title'], inline=False)
            
            if current.get('duration'):
                duration = f"{current['duration']//60}:{current['duration']%60:02d}"
                embed.add_field(name="Duration", value=duration, inline=True)
            
            if current.get('url'):
                embed.add_field(name="URL", value=f"[Click here]({current['url']})", inline=True)
            
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("❌ Nothing is currently playing!", ephemeral=True)

def setup(bot):
    bot.add_cog(MusicCommands(bot))