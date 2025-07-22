"""
Moderation module for Discord bot with advanced features
"""
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import re
import logging
from typing import Optional

class ModerationSystem:
    def __init__(self, bot):
        self.bot = bot
        self.auto_mod_settings = {}
        self.warn_counts = {}
        self.temp_bans = {}
        
        # Auto-moderation patterns
        self.spam_patterns = [
            r'(.)\1{4,}',  # Repeated characters
            r'(.+?)\1{3,}',  # Repeated phrases
        ]
        
        self.bad_words = [
            # Add actual bad words here based on server needs
            'spam', 'scam', 'hack'  # Placeholder examples
        ]

    def get_guild_settings(self, guild_id):
        """Get auto-moderation settings for guild"""
        return self.auto_mod_settings.get(guild_id, {
            'anti_spam': False,
            'anti_raid': False,
            'bad_word_filter': False,
            'anti_link': False,
            'max_mentions': 5,
            'max_messages_per_minute': 10
        })

    def set_guild_settings(self, guild_id, settings):
        """Set auto-moderation settings for guild"""
        self.auto_mod_settings[guild_id] = settings

    async def check_spam(self, message):
        """Check if message is spam"""
        for pattern in self.spam_patterns:
            if re.search(pattern, message.content, re.IGNORECASE):
                return True
        return False

    async def check_bad_words(self, message):
        """Check for inappropriate content"""
        content_lower = message.content.lower()
        for word in self.bad_words:
            if word in content_lower:
                return True
        return False

    async def check_excessive_mentions(self, message):
        """Check for excessive mentions"""
        settings = self.get_guild_settings(message.guild.id)
        max_mentions = settings.get('max_mentions', 5)
        
        total_mentions = len(message.mentions) + len(message.role_mentions)
        return total_mentions > max_mentions

    async def check_links(self, message):
        """Check for unauthorized links"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return bool(re.search(url_pattern, message.content))

    async def add_warning(self, guild_id, user_id, reason, moderator_id):
        """Add warning to user"""
        if guild_id not in self.warn_counts:
            self.warn_counts[guild_id] = {}
        
        if user_id not in self.warn_counts[guild_id]:
            self.warn_counts[guild_id][user_id] = []
        
        warning = {
            'reason': reason,
            'moderator': moderator_id,
            'timestamp': datetime.now(),
            'id': len(self.warn_counts[guild_id][user_id]) + 1
        }
        
        self.warn_counts[guild_id][user_id].append(warning)
        return warning

    def get_warnings(self, guild_id, user_id):
        """Get user warnings"""
        if guild_id not in self.warn_counts:
            return []
        return self.warn_counts[guild_id].get(user_id, [])

    async def auto_moderate_message(self, message):
        """Automatically moderate message based on settings"""
        if message.author.bot:
            return
        
        settings = self.get_guild_settings(message.guild.id)
        actions_taken = []

        # Check spam
        if settings.get('anti_spam') and await self.check_spam(message):
            await message.delete()
            actions_taken.append('Deleted spam message')
            
            # Add warning
            await self.add_warning(
                message.guild.id, 
                message.author.id, 
                'Automatic: Spam detection', 
                self.bot.user.id
            )

        # Check bad words
        if settings.get('bad_word_filter') and await self.check_bad_words(message):
            await message.delete()
            actions_taken.append('Deleted inappropriate content')
            
            await self.add_warning(
                message.guild.id,
                message.author.id,
                'Automatic: Inappropriate language',
                self.bot.user.id
            )

        # Check excessive mentions
        if await self.check_excessive_mentions(message):
            await message.delete()
            actions_taken.append('Deleted message with excessive mentions')

        # Check unauthorized links
        if settings.get('anti_link') and await self.check_links(message):
            await message.delete()
            actions_taken.append('Deleted unauthorized link')

        return actions_taken


class ModerationCommands(commands.Cog):
    """Moderation commands for Discord bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.moderation = ModerationSystem(bot)

    @commands.slash_command(name="kick", description="Kick a user from the server")
    @commands.default_permissions(kick_members=True)
    async def kick_command(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        """Kick a user"""
        if user.top_role >= ctx.author.top_role:
            await ctx.respond("❌ You cannot kick this user!", ephemeral=True)
            return
            
        try:
            await user.kick(reason=f"Kicked by {ctx.author}: {reason}")
            
            embed = discord.Embed(title="👢 User Kicked", color=0xff9900)
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.timestamp = datetime.now()
            
            await ctx.respond(embed=embed)
            
        except discord.Forbidden:
            await ctx.respond("❌ I don't have permission to kick this user!", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Error kicking user: {str(e)}", ephemeral=True)

    @commands.slash_command(name="ban", description="Ban a user from the server")
    @commands.default_permissions(ban_members=True)
    async def ban_command(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        """Ban a user"""
        if user.top_role >= ctx.author.top_role:
            await ctx.respond("❌ You cannot ban this user!", ephemeral=True)
            return
            
        try:
            await user.ban(reason=f"Banned by {ctx.author}: {reason}")
            
            embed = discord.Embed(title="🔨 User Banned", color=0xff0000)
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.timestamp = datetime.now()
            
            await ctx.respond(embed=embed)
            
        except discord.Forbidden:
            await ctx.respond("❌ I don't have permission to ban this user!", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Error banning user: {str(e)}", ephemeral=True)

    @commands.slash_command(name="timeout", description="Timeout a user")
    @commands.default_permissions(moderate_members=True)
    async def timeout_command(self, ctx, user: discord.Member, duration: int, *, reason: str = "No reason provided"):
        """Timeout a user for specified minutes"""
        if user.top_role >= ctx.author.top_role:
            await ctx.respond("❌ You cannot timeout this user!", ephemeral=True)
            return
            
        try:
            timeout_until = datetime.now() + timedelta(minutes=duration)
            await user.timeout(timeout_until, reason=f"Timed out by {ctx.author}: {reason}")
            
            embed = discord.Embed(title="⏰ User Timed Out", color=0xffaa00)
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.timestamp = datetime.now()
            
            await ctx.respond(embed=embed)
            
        except discord.Forbidden:
            await ctx.respond("❌ I don't have permission to timeout this user!", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Error timing out user: {str(e)}", ephemeral=True)

    @commands.slash_command(name="warn", description="Warn a user")
    @commands.default_permissions(kick_members=True)
    async def warn_command(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        """Warn a user"""
        warning = await self.moderation.add_warning(
            ctx.guild.id, user.id, reason, ctx.author.id
        )
        
        embed = discord.Embed(title="⚠️ User Warned", color=0xffdd00)
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Warning #", value=str(warning['id']), inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.timestamp = datetime.now()
        
        await ctx.respond(embed=embed)
        
        # Send DM to user
        try:
            dm_embed = discord.Embed(title="⚠️ Warning Received", color=0xffdd00)
            dm_embed.add_field(name="Server", value=ctx.guild.name, inline=False)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Warning Count", value=str(len(self.moderation.get_warnings(ctx.guild.id, user.id))), inline=False)
            
            await user.send(embed=dm_embed)
        except:
            pass  # User has DMs disabled

    @commands.slash_command(name="warnings", description="Check user warnings")
    @commands.default_permissions(kick_members=True)
    async def warnings_command(self, ctx, user: discord.Member):
        """Check warnings for a user"""
        warnings = self.moderation.get_warnings(ctx.guild.id, user.id)
        
        embed = discord.Embed(title=f"⚠️ Warnings for {user}", color=0xffdd00)
        
        if warnings:
            for warning in warnings[-10:]:  # Show last 10 warnings
                timestamp = warning['timestamp'].strftime("%Y-%m-%d %H:%M")
                moderator = ctx.guild.get_member(warning['moderator'])
                mod_name = moderator.display_name if moderator else "Unknown"
                
                embed.add_field(
                    name=f"Warning #{warning['id']} - {timestamp}",
                    value=f"**Reason:** {warning['reason']}\n**Moderator:** {mod_name}",
                    inline=False
                )
        else:
            embed.description = "No warnings found."
        
        embed.set_footer(text=f"Total warnings: {len(warnings)}")
        await ctx.respond(embed=embed)

    @commands.slash_command(name="clear", description="Clear messages from channel")
    @commands.default_permissions(manage_messages=True)
    async def clear_command(self, ctx, amount: int):
        """Clear messages from channel"""
        if amount > 100:
            await ctx.respond("❌ Cannot delete more than 100 messages at once!", ephemeral=True)
            return
            
        await ctx.defer()
        
        try:
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.followup.send(f"✅ Deleted {len(deleted)} messages!", ephemeral=True)
            
        except discord.Forbidden:
            await ctx.followup.send("❌ I don't have permission to delete messages!", ephemeral=True)
        except Exception as e:
            await ctx.followup.send(f"❌ Error deleting messages: {str(e)}", ephemeral=True)

    @commands.slash_command(name="automod", description="Configure auto-moderation settings")
    @commands.default_permissions(administrator=True)
    async def automod_command(self, ctx, 
                            anti_spam: bool = False, 
                            anti_raid: bool = False, 
                            bad_word_filter: bool = False, 
                            anti_link: bool = False):
        """Configure auto-moderation settings"""
        settings = {
            'anti_spam': anti_spam,
            'anti_raid': anti_raid,
            'bad_word_filter': bad_word_filter,
            'anti_link': anti_link
        }
        
        self.moderation.set_guild_settings(ctx.guild.id, settings)
        
        embed = discord.Embed(title="⚙️ Auto-Moderation Settings", color=0x5865f2)
        embed.add_field(name="Anti-Spam", value="✅" if anti_spam else "❌", inline=True)
        embed.add_field(name="Anti-Raid", value="✅" if anti_raid else "❌", inline=True)
        embed.add_field(name="Bad Word Filter", value="✅" if bad_word_filter else "❌", inline=True)
        embed.add_field(name="Anti-Link", value="✅" if anti_link else "❌", inline=True)
        
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Auto-moderate messages"""
        if message.guild:
            await self.moderation.auto_moderate_message(message)

def setup(bot):
    bot.add_cog(ModerationCommands(bot))