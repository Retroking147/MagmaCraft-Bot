"""
Production entry point for Discord Bot Dashboard
This ensures the application works on Render with proper configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Force production environment for Render
if 'RENDER' in os.environ or 'render.com' in os.environ.get('RENDER_EXTERNAL_URL', ''):
    os.environ['FLASK_ENV'] = 'production'

def create_app():
    """Create the Flask application"""
    try:
        # Try to import the full web application
        from web_app import create_app as create_main_app
        print("Loading full Discord Bot Dashboard...")
        app = create_main_app()
        
        # Test database connection
        with app.app_context():
            from models import db
            db.create_all()
            
        print("✅ Full application loaded successfully!")
        return app
        
    except Exception as e:
        print(f"❌ Failed to load main application: {e}")
        print("🔄 Loading simplified version for debugging...")
        
        # Fallback to simple version with better error reporting
        from flask import Flask, jsonify, render_template_string
        
        app = Flask(__name__)
        app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret-key")
        
        @app.route('/')
        def index():
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Discord Bot Dashboard - Configuration Required</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #2c2f33; color: white; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .error { background: #f04747; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .fix { background: #43b581; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .code { background: #23272a; padding: 10px; border-radius: 4px; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Discord Bot Dashboard</h1>
                    
                    <div class="error">
                        <h3>❌ Configuration Error</h3>
                        <p>The dashboard couldn't start because of missing configuration.</p>
                        <p><strong>Error:</strong> {{ error_details }}</p>
                    </div>
                    
                    <div class="fix">
                        <h3>🔧 How to Fix This</h3>
                        <p>In your Render dashboard, add these environment variables:</p>
                        <div class="code">
                            DATABASE_URL=postgresql://... (auto-provided by Render)<br>
                            FLASK_SECRET_KEY=your_secret_key<br>
                            DISCORD_CLIENT_ID=your_discord_app_id<br>
                            DISCORD_CLIENT_SECRET=your_discord_secret<br>
                            DISCORD_BOT_TOKEN=your_bot_token
                        </div>
                        <p>After adding these, redeploy your service in Render.</p>
                    </div>
                    
                    <div class="fix">
                        <h3>📋 Current Environment Status</h3>
                        <ul>
                            <li>DATABASE_URL: {{ 'SET' if database_url else 'MISSING' }}</li>
                            <li>FLASK_SECRET_KEY: {{ 'SET' if flask_secret else 'MISSING' }}</li>
                            <li>DISCORD_CLIENT_ID: {{ 'SET' if discord_id else 'MISSING' }}</li>
                            <li>DISCORD_CLIENT_SECRET: {{ 'SET' if discord_secret else 'MISSING' }}</li>
                            <li>DISCORD_BOT_TOKEN: {{ 'SET' if bot_token else 'MISSING' }}</li>
                        </ul>
                    </div>
                    
                    <p><a href="/api/health" style="color: #7289da;">Check API Health</a></p>
                </div>
            </body>
            </html>
            """, 
                error_details=str(e),
                database_url=bool(os.environ.get('DATABASE_URL')),
                flask_secret=bool(os.environ.get('FLASK_SECRET_KEY')),
                discord_id=bool(os.environ.get('DISCORD_CLIENT_ID')),
                discord_secret=bool(os.environ.get('DISCORD_CLIENT_SECRET')),
                bot_token=bool(os.environ.get('DISCORD_BOT_TOKEN'))
            )
        
        @app.route('/api/health')
        def health():
            return jsonify({
                "status": "partial",
                "message": "Fallback mode - configuration required",
                "error": str(e),
                "required_env_vars": {
                    "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
                    "FLASK_SECRET_KEY": bool(os.environ.get('FLASK_SECRET_KEY')),
                    "DISCORD_CLIENT_ID": bool(os.environ.get('DISCORD_CLIENT_ID')),
                    "DISCORD_CLIENT_SECRET": bool(os.environ.get('DISCORD_CLIENT_SECRET')),
                    "DISCORD_BOT_TOKEN": bool(os.environ.get('DISCORD_BOT_TOKEN'))
                }
            })
        
        return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Discord Bot Dashboard on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)