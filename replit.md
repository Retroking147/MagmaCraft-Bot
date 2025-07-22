# Discord Bot - Replit Guide

## Overview

This is a Python-based Discord bot built using the discord.py library. The bot features slash commands, message sending capabilities, and a modular architecture for easy expansion. It's designed to be simple to set up and extend with additional functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Language**: Python 3.x
- **Framework**: discord.py library for Discord API interaction
- **Architecture Pattern**: Modular command-based structure
- **Configuration**: Environment variables via python-dotenv
- **Logging**: Built-in Python logging with file and console output

### Project Structure
```
/
├── main.py              # Entry point and bot initialization
├── bot/                 # Main bot package
│   ├── __init__.py     # Package initialization
│   ├── client.py       # Custom Discord bot client
│   ├── commands.py     # Slash command definitions
│   ├── events.py       # Event handlers
│   └── utils.py        # Utility functions and embed helpers
├── .env.example        # Environment variables template
└── README.md          # Documentation
```

## Key Components

### 1. Bot Client (`bot/client.py`)
- **Purpose**: Custom Discord bot class extending commands.Bot
- **Features**: 
  - Configures Discord intents for message content and guild access
  - Handles command synchronization (guild-specific or global)
  - Sets up slash commands and events during initialization
- **Design Decision**: Uses slash commands as primary interface for modern Discord interaction

### 2. Command System (`bot/commands.py`)
- **Purpose**: Defines all slash commands available to users
- **Current Commands**:
  - `/ping` - Latency checker
  - `/hello` - Friendly greeting with user mention
  - `/info` - Bot information display
- **Design Decision**: Uses Discord's app_commands tree for slash commands rather than traditional text commands

### 3. Event Handling (`bot/events.py`)
- **Purpose**: Manages Discord events like guild joins, ready state, errors
- **Features**: 
  - Welcome messages for new servers
  - Automatic channel detection for welcome messages
  - Comprehensive error handling and logging
- **Design Decision**: Separates event logic from command logic for better organization

### 4. Utilities (`bot/utils.py`)
- **Purpose**: Provides helper functions for common operations
- **Key Features**:
  - Embed creation utilities with consistent styling
  - Success, error, and info embed templates
  - Timestamp management
- **Design Decision**: Centralizes embed creation to ensure consistent visual branding

## Data Flow

### Bot Startup Process
1. Load environment variables from `.env` file
2. Initialize logging system (file + console output)
3. Create DiscordBot instance with proper intents
4. Set up commands and events during `setup_hook()`
5. Sync slash commands (guild-specific or global)
6. Connect to Discord and maintain connection

### Command Execution Flow
1. User invokes slash command in Discord
2. Discord sends interaction to bot
3. Bot routes to appropriate command handler
4. Command executes business logic
5. Response sent back via interaction response
6. Action logged for monitoring

### Event Processing Flow
1. Discord sends event to bot (e.g., guild join, message)
2. Bot routes to appropriate event handler
3. Event handler processes the event
4. Any responses sent to appropriate channels
5. Event logged for debugging

## External Dependencies

### Core Dependencies
- **discord.py**: Primary Discord API library for bot functionality
- **python-dotenv**: Environment variable management for configuration
- **asyncio**: Built-in Python library for asynchronous operations

### Discord API Integration
- **Authentication**: Bot token-based authentication
- **Permissions**: Configurable via Discord Developer Portal
- **Rate Limiting**: Built-in awareness to avoid API limits
- **Intents**: Configured for message content and guild access

## Deployment Strategy

### Environment Configuration
- **Bot Token**: Stored in `DISCORD_BOT_TOKEN` environment variable
- **Guild ID**: Optional `GUILD_ID` for faster command sync during development
- **Logging**: Outputs to both `bot.log` file and console

### Error Handling Strategy
- **Command Errors**: Graceful error responses to users with ephemeral messages
- **API Errors**: Comprehensive logging with fallback behaviors
- **Connection Issues**: Automatic reconnection handled by discord.py
- **Missing Permissions**: Proper error handling for insufficient bot permissions

### Scalability Considerations
- **Modular Design**: Easy to add new commands by extending commands.py
- **Separate Concerns**: Commands, events, and utilities in separate modules
- **Logging**: Comprehensive logging for debugging and monitoring
- **Configuration**: Environment-based configuration for different deployment environments

### Development vs Production
- **Guild Sync**: Use GUILD_ID for faster testing in development
- **Global Sync**: Remove GUILD_ID for production deployment (slower but reaches all servers)
- **Logging Level**: Configurable logging levels for different environments
- **Error Handling**: More verbose error messages in development mode

The architecture prioritizes simplicity and modularity, making it easy to extend the bot with additional commands and features while maintaining clean separation of concerns.

## Recent Changes: Latest modifications with dates

### July 22, 2025
- **Complete Web Dashboard Overhaul**: Transformed simple dashboard into comprehensive Discord-styled control panel
- **Navigation Menu System**: Added tabbed interface with Dashboard, Music, Moderation, Minecraft, and Settings sections
- **ProBot-Style Features**: Integrated advanced Discord bot management capabilities matching professional bot dashboards
- **Music Player Module**: Full YouTube music integration with play/pause/skip controls, queue management, and voice channel support
- **Advanced Moderation System**: Auto-moderation with spam detection, bad word filtering, user management (kick/ban/timeout/warn), and configurable settings
- **Expanded API Endpoints**: 15+ new REST API endpoints for music control, moderation actions, server management, and bot settings
- **Enhanced Bot Architecture**: Modular cog system with separate music_player.py and moderation.py modules
- **Real-time Controls**: Dashboard buttons for music playback, moderation actions, server management, and bot configuration
- **Security Features**: Token management interface with encrypted storage for Discord, YouTube, and Spotify API keys
- **System Management**: Bot restart, log export, cache clearing, and comprehensive settings management
- **UptimeRobot Integration**: Health check endpoint for external monitoring services
- **Database Expansion**: Enhanced models for storing bot statistics, command usage, and system monitoring data
- **Public Deployment Success**: Successfully deployed Discord dashboard to Render.com at magmacraft-bot.onrender.com
- **Discord OAuth Integration**: Implemented complete Discord OAuth login system with professional authentication flow
- **Public Access System**: Created public dashboard accessible via URL with Discord login for server administrators
- **Fallback Architecture**: Built robust error handling with health check fallback to ensure 100% uptime
- **Production Configuration**: Configured PostgreSQL database, environment variables, and Gunicorn for production deployment

### July 20, 2025
- **Added Minecraft Server Counter Feature**: Bot can now create and manage channels that display real-time Minecraft server status
- **Separate Channel System**: Creates two channels - status (🟢 Online/🔴 Offline) and player count (👤 X/Y Players)  
- **Smart Dynamic Updates with Grace Period**: 15-second updates when players are online, maintains 15-second updates for 120 seconds after server becomes empty to catch quick rejoins, then switches to 30-second updates
- **Clean Category-Friendly Names**: Status shows just "🟢 Online" without extra text for category organization
- **New Command**: `/minecraft-counter` with customizable channel naming and automatic server monitoring
- **Stability Enhancement**: Added 2-minute buffer period before switching back to slow updates to handle brief disconnections
- **Admin Restrictions**: Made `/minecraft-counter` command admin-only using `@app_commands.default_permissions(administrator=True)`
- **Command List Feature**: Added `/send-commands` admin command to send organized command lists to channels
- **Ephemeral Responses**: Commands used in channels with "command" + warning symbols now show responses only to user and admins
- **Counter Management**: Added `/reset-counter` and `/force-update` admin commands for counter troubleshooting and manual control
- **Bug Fixes**: Fixed minecraft-counter command to handle 4-value server status returns correctly
- **Voice System Removal**: Completely removed automatic voice bridge system due to functionality issues - bot now focuses on core counter and command features