"""
Combined Discord Bot and Web Dashboard Application
"""
import os
import asyncio
import logging
from threading import Thread
from datetime import datetime, timezone
from dotenv import load_dotenv

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

def run_web_app():
    """Run the Flask web dashboard"""
    try:
        from web_app import create_app
        app = create_app()
        logger.info("Starting Flask web server on port 5000...")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start web app: {e}")
        import traceback
        traceback.print_exc()

async def run_discord_bot():
    """Run the Discord bot"""
    try:
        from bot.client import DiscordBot
        
        # Get bot token from environment variables
        token = os.getenv('DISCORD_BOT_TOKEN')
        
        if not token:
            logger.error("DISCORD_BOT_TOKEN not found in environment variables!")
            logger.error("Web dashboard will still be available at http://localhost:5000")
            logger.error("Add your Discord bot token to run the full application.")
            return
        
        # Initialize bot
        bot = DiscordBot()
        
        try:
            logger.info("Starting Discord bot...")
            
            # Track bot startup
            if bot.stats_tracker:
                bot.stats_tracker.track_bot_start()
            
            await bot.start(token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
        finally:
            if not bot.is_closed():
                # Track bot shutdown
                if bot.stats_tracker:
                    bot.stats_tracker.track_bot_shutdown()
                await bot.close()
                
    except Exception as e:
        logger.error(f"Error in Discord bot setup: {e}")

async def main():
    """Main application entry point"""
    logger.info("Starting Discord Bot Dashboard Application...")
    
    # Start web dashboard in a separate thread
    web_thread = Thread(target=run_web_app, daemon=True)
    web_thread.start()
    logger.info("Web dashboard started at http://localhost:5000")
    
    # Start Discord bot
    await run_discord_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")