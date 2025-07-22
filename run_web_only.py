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
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Discord Bot Dashboard at port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)