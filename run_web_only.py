"""
Run only the web dashboard (without Discord bot)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set environment based on deployment context
if not os.environ.get('FLASK_ENV'):
    # Default to development for local testing
    os.environ['FLASK_ENV'] = 'development'

def create_application():
    try:
        from web_app import create_app
        return create_app()
    except Exception as e:
        print(f"Failed to load main app: {e}")
        print("Loading simple health check version...")
        from simple_web import create_app
        return create_app()

app = create_application()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Discord Bot Dashboard at port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)