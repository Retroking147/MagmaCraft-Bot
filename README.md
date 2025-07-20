# Discord Bot

A Python Discord bot with message sending capabilities and custom slash commands using discord.py.

## Features

- ✅ Connect to Discord and stay online
- ✅ Send messages to specified channels
- ✅ Respond to custom slash commands
- ✅ Basic command examples (ping, hello, info, say, embed)
- ✅ Send messages programmatically through code
- ✅ Error handling for common Discord API issues
- ✅ Modular command structure for easy expansion
- ✅ Logging for debugging and monitoring
- ✅ Rate limiting awareness to avoid API limits

## Setup Instructions

### 1. Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token

### 2. Set Up Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your bot token:
   ```env
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```

3. (Optional) Add your guild ID for faster command sync during development:
   ```env
   GUILD_ID=your_guild_id_here
   ```

### 3. Install Dependencies

Install required Python packages:
```bash
pip install discord.py python-dotenv
