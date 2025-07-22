"""
Run only the web dashboard (without Discord bot)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_application():
    from web_app import create_app
    return create_app()

app = create_application()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Discord Bot Dashboard at port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)