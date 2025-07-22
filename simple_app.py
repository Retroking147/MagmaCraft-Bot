"""
Simple production entry point for Render deployment
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set production environment for Render
os.environ['FLASK_ENV'] = 'production'

def create_app():
    """Create Flask application with better error handling"""
    try:
        print("Attempting to load full Discord Bot Dashboard...")
        from web_app import create_app as create_main_app
        app = create_main_app()
        
        # Test database connection
        with app.app_context():
            from models import db
            db.create_all()
            print("✅ Database connected successfully!")
            
        print("✅ Full application loaded successfully!")
        return app
        
    except Exception as error:
        print(f"❌ Main application failed: {error}")
        print("🔄 Loading fallback diagnostic page...")
        
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-key-12345")
        
        @app.route('/')
        def diagnostic():
            env_status = {
                "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
                "FLASK_SECRET_KEY": bool(os.environ.get('FLASK_SECRET_KEY')),
                "DISCORD_CLIENT_ID": bool(os.environ.get('DISCORD_CLIENT_ID')),
                "DISCORD_CLIENT_SECRET": bool(os.environ.get('DISCORD_CLIENT_SECRET')),
                "DISCORD_BOT_TOKEN": bool(os.environ.get('DISCORD_BOT_TOKEN'))
            }
            
            missing_vars = [k for k, v in env_status.items() if not v]
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Discord Bot Dashboard - Setup Required</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #2c2f33; color: white; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .error {{ background: #f04747; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .success {{ background: #43b581; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .warning {{ background: #faa61a; color: black; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .code {{ background: #23272a; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-line; }}
                    ul {{ text-align: left; }}
                    li {{ margin: 5px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Discord Bot Dashboard</h1>
                    
                    <div class="error">
                        <h3>⚙️ Configuration Required</h3>
                        <p><strong>Error:</strong> {str(error)}</p>
                    </div>
                    
                    <div class="{'success' if not missing_vars else 'warning'}">
                        <h3>📋 Environment Variable Status</h3>
                        <ul>
                            {''.join(f"<li>{'✅' if v else '❌'} {k}</li>" for k, v in env_status.items())}
                        </ul>
                        {f'<p><strong>Missing:</strong> {", ".join(missing_vars)}</p>' if missing_vars else '<p><strong>All variables configured!</strong></p>'}
                    </div>
                    
                    <div class="success">
                        <h3>🔧 Fix Steps for Render</h3>
                        <p>1. Go to your Render Dashboard → Environment tab</p>
                        <p>2. Add these environment variables:</p>
                        <div class="code">FLASK_SECRET_KEY=your_random_secret_key_here
DISCORD_CLIENT_ID=your_discord_app_client_id
DISCORD_CLIENT_SECRET=your_discord_app_client_secret
DISCORD_BOT_TOKEN=your_discord_bot_token</div>
                        <p>3. Click "Deploy latest commit" in the Deploys tab</p>
                    </div>
                    
                    <p><a href="/health" style="color: #7289da;">Check Health Status</a></p>
                </div>
            </body>
            </html>
            """
            return html
        
        @app.route('/health')
        def health():
            return jsonify({
                "status": "configuration_required",
                "error": str(error),
                "environment_variables": {
                    "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
                    "FLASK_SECRET_KEY": bool(os.environ.get('FLASK_SECRET_KEY')),
                    "DISCORD_CLIENT_ID": bool(os.environ.get('DISCORD_CLIENT_ID')),
                    "DISCORD_CLIENT_SECRET": bool(os.environ.get('DISCORD_CLIENT_SECRET')),
                    "DISCORD_BOT_TOKEN": bool(os.environ.get('DISCORD_BOT_TOKEN'))
                }
            })
        
        return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)