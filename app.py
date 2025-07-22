"""
Ultra-simple Flask app for Render - No dependencies issues
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

@app.route('/')
def home():
    """Main page"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', 
                         user=session.get('user_info', {'username': 'User'}),
                         stats={'servers': 1, 'users': 50, 'commands_used': 125, 'uptime_hours': 72})

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/dev-login')
def dev_login():
    """Development login bypass"""
    session['user_id'] = '123456789'
    session['user_info'] = {
        'username': 'Developer',
        'discriminator': '0001',
        'avatar': None,
        'id': '123456789'
    }
    return redirect(url_for('home'))

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'discord_configured': bool(os.environ.get('DISCORD_CLIENT_ID')),
        'version': 'simplified'
    })

# Simple API endpoints
@app.route('/api/music/play', methods=['POST'])
def music_play():
    return jsonify({'status': 'Music play command sent'})

@app.route('/api/music/pause', methods=['POST'])
def music_pause():
    return jsonify({'status': 'Music paused'})

@app.route('/api/moderation/kick', methods=['POST'])
def kick_user():
    return jsonify({'status': 'User kick command sent'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)