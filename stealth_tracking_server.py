# Stealth Email Tracking Server
# Designed to avoid spam filters and tracking detection

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
    """Home page - looks like a legitimate website"""
    return '''
    <html>
    <head>
        <title>Welcome to Our Services</title>
        <meta name="description" content="Professional business solutions and consulting services">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .service { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Our Business Services</h1>
            <p>We provide professional consulting and business solutions to help your company grow.</p>
            
            <div class="service">
                <h3>Business Strategy</h3>
                <p>Comprehensive business planning and strategic consulting services.</p>
            </div>
            
            <div class="service">
                <h3>Digital Marketing</h3>
                <p>Modern marketing solutions to increase your online presence.</p>
            </div>
            
            <div class="service">
                <h3>Technology Consulting</h3>
                <p>Expert advice on technology implementation and optimization.</p>
            </div>
            
            <p><strong>Contact us:</strong> info@businessservices.com</p>
        </div>
    </body>
    </html>
    '''

@app.route('/analytics/<tracking_id>')
def track_analytics(tracking_id):
    """Stealth tracking endpoint - looks like analytics"""
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
    
    # Return a legitimate-looking analytics response (JSON)
    response_data = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "message": "Analytics data recorded successfully"
    }
    
    response = make_response(json.dumps(response_data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/pixel/<tracking_id>')
def track_pixel(tracking_id):
    """Alternative tracking endpoint - returns a legitimate image"""
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
    
    # Return a legitimate 1x1 transparent PNG (less suspicious than GIF)
    pixel_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x00\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82'
    
    response = make_response(pixel_data)
    response.headers['Content-Type'] = 'image/png'
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
    print(f"🚀 Starting Stealth Email Tracking Server on port {port}")
    print("📧 Analytics endpoint: /analytics/<tracking_id>")
    print("🖼️  Pixel endpoint: /pixel/<tracking_id>")
    print("🔍 API endpoint: /api/tracking")
    print("🏠 Home page: /")
    app.run(host='0.0.0.0', port=port, debug=False)
