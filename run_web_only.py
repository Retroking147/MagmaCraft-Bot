"""
Run only the web dashboard (without Discord bot)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    from web_app import create_app
    app = create_app()
    print("Starting Discord Bot Dashboard at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)