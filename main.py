"""
Discord Bot Main Entry Point
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from bot.client import DiscordBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the Discord bot"""
    # Get bot token from environment variables
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables!")
        logger.error("Please set your bot token in the .env file or environment variables.")
        return
    
    # Initialize bot
    bot = DiscordBot()
    
    try:
        logger.info("Starting Discord bot...")
        await bot.start(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
