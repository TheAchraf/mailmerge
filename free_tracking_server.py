# Free Email Tracking Server
# Optimized for free hosting services (Render, Railway, Heroku)

import os
from flask import Flask, request, jsonify, make_response
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)

# Database setup - use in-memory SQLite for free hosting
def init_db():
    """Initialize database - use in-memory for free hosting"""
    conn = sqlite3.connect(':memory:')  # In-memory database
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tracking_events
                 (id TEXT PRIMARY KEY, email TEXT, sent_time TEXT, 
                  opened BOOLEAN, open_time TEXT, ip_address TEXT, user_agent TEXT)''')
    conn.commit()
    return conn

# Global database connection
db_conn = init_db()

@app.route('/')
def home():
    """Home page with tracking info"""
    return '''
    <html>
    <head><title>Email Tracking Server</title></head>
    <body>
        <h1>📧 Email Tracking Server</h1>
        <p>This server tracks email opens using tracking pixels.</p>
        <h2>Endpoints:</h2>
        <ul>
            <li><strong>Tracking Pixel:</strong> /track/&lt;tracking_id&gt;</li>
            <li><strong>API Status:</strong> /api/tracking/&lt;tracking_id&gt;</li>
            <li><strong>All Data:</strong> /api/tracking</li>
        </ul>
        <h2>Usage in Merge Mail App:</h2>
        <p>Replace the tracking pixel URL in your emails with:</p>
        <code>https://your-app-name.onrender.com/track/{tracking_id}</code>
    </body>
    </html>
    '''

@app.route('/track/<tracking_id>')
def track_pixel(tracking_id):
    """Serve tracking pixel and record email open"""
    try:
        # Record the open event
        c = db_conn.cursor()
        c.execute('''UPDATE tracking_events 
                     SET opened = ?, open_time = ?, ip_address = ?, user_agent = ?
                     WHERE id = ?''', 
                  (True, datetime.now().isoformat(), 
                   request.remote_addr, request.headers.get('User-Agent'), tracking_id))
        
        # If no rows updated, create new entry
        if c.rowcount == 0:
            c.execute('''INSERT INTO tracking_events 
                         (id, email, sent_time, opened, open_time, ip_address, user_agent)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (tracking_id, 'unknown@example.com', datetime.now().isoformat(),
                       True, datetime.now().isoformat(), request.remote_addr, 
                       request.headers.get('User-Agent')))
        
        db_conn.commit()
        
        print(f"📧 Email opened: {tracking_id} from {request.remote_addr}")
        
    except Exception as e:
        print(f"Error tracking email: {e}")
    
    # Return 1x1 transparent GIF pixel
    pixel_data = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    
    response = make_response(pixel_data)
    response.headers['Content-Type'] = 'image/gif'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/api/tracking/<tracking_id>')
def get_tracking_status(tracking_id):
    """Get tracking status for a specific email"""
    try:
        c = db_conn.cursor()
        c.execute('SELECT * FROM tracking_events WHERE id = ?', (tracking_id,))
        result = c.fetchone()
        
        if result:
            return jsonify({
                'id': result[0],
                'email': result[1],
                'sent_time': result[2],
                'opened': result[3],
                'open_time': result[4],
                'ip_address': result[5],
                'user_agent': result[6]
            })
        else:
            return jsonify({'error': 'Tracking ID not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tracking')
def get_all_tracking():
    """Get all tracking data"""
    try:
        c = db_conn.cursor()
        c.execute('SELECT * FROM tracking_events ORDER BY sent_time DESC')
        results = c.fetchall()
        
        tracking_data = []
        for result in results:
            tracking_data.append({
                'id': result[0],
                'email': result[1],
                'sent_time': result[2],
                'opened': result[3],
                'open_time': result[4],
                'ip_address': result[5],
                'user_agent': result[6]
            })
        
        return jsonify(tracking_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for hosting services"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Email Tracking Server on port {port}")
    print("📧 Tracking pixel endpoint: /track/<tracking_id>")
    print("🔍 API endpoint: /api/tracking")
    print("🏠 Home page: /")
    app.run(host='0.0.0.0', port=port, debug=False)
