#!/usr/bin/env python3
"""
REST API for TWOM Database
Provides endpoints to retrieve data by row number
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import sqlite3
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for web application access

DB_FILE = 'twom_data.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.route('/')
def index():
    """Serve the journal UI"""
    return send_file('journal.html')

@app.route('/journal.html')
def journal():
    """Serve the journal UI"""
    return send_file('journal.html')

@app.route('/api')
def api_docs():
    """API documentation"""
    return jsonify({
        'name': 'TWOM Data API',
        'version': '1.0',
        'endpoints': {
            '/api/lookup': 'Get all lookup data',
            '/api/lookup/<row_number>': 'Get lookup by row number',
            '/api/rewards': 'Get all rewards (with pagination)',
            '/api/rewards/<row_number>': 'Get reward by row number',
            '/api/scripts': 'Get all scripts (with pagination)',
            '/api/scripts/<row_number>': 'Get script by row number',
            '/api/search/scripts?q=<query>': 'Search scripts by text',
            '/api/search/rewards?q=<query>': 'Search rewards by text',
            '/api/stats': 'Get database statistics'
        }
    })

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    # Count records in each table
    cursor.execute('SELECT COUNT(*) FROM lookup')
    stats['lookup_count'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM rewards')
    stats['rewards_count'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM scripts')
    stats['scripts_count'] = cursor.fetchone()[0]

    conn.close()

    return jsonify(stats)

# LOOKUP ENDPOINTS
@app.route('/api/lookup')
def get_all_lookup():
    """Get all lookup data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM lookup ORDER BY row_number')
    rows = cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])

@app.route('/api/lookup/<int:row_number>')
def get_lookup_by_row(row_number):
    """Get lookup by row number"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM lookup WHERE row_number = ?', (row_number,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return jsonify(dict(row))
    else:
        return jsonify({'error': 'Row not found'}), 404

# REWARDS ENDPOINTS
@app.route('/api/rewards')
def get_all_rewards():
    """Get all rewards with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM rewards')
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT * FROM rewards
        ORDER BY row_number
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    rows = cursor.fetchall()

    conn.close()

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'data': [dict(row) for row in rows]
    })

@app.route('/api/rewards/<int:row_number>')
def get_reward_by_row(row_number):
    """Get reward by row number"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM rewards WHERE row_number = ?', (row_number,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return jsonify(dict(row))
    else:
        return jsonify({'error': 'Row not found'}), 404

# SCRIPTS ENDPOINTS
@app.route('/api/scripts')
def get_all_scripts():
    """Get all scripts with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM scripts')
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT * FROM scripts
        ORDER BY row_number
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    rows = cursor.fetchall()

    conn.close()

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'data': [dict(row) for row in rows]
    })

@app.route('/api/scripts/<int:row_number>')
def get_script_by_row(row_number):
    """Get script by row number"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM scripts WHERE row_number = ?', (row_number,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return jsonify(dict(row))
    else:
        return jsonify({'error': 'Row not found'}), 404

# SEARCH ENDPOINTS
@app.route('/api/search/scripts')
def search_scripts():
    """Search scripts by text"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    search_pattern = f'%{query}%'

    cursor.execute('''
        SELECT COUNT(*) FROM scripts
        WHERE content LIKE ?
    ''', (search_pattern,))
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT * FROM scripts
        WHERE content LIKE ?
        ORDER BY row_number
        LIMIT ? OFFSET ?
    ''', (search_pattern, per_page, offset))
    rows = cursor.fetchall()

    conn.close()

    return jsonify({
        'query': query,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'data': [dict(row) for row in rows]
    })

@app.route('/api/search/rewards')
def search_rewards():
    """Search rewards by text"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    search_pattern = f'%{query}%'

    cursor.execute('''
        SELECT COUNT(*) FROM rewards
        WHERE content LIKE ?
    ''', (search_pattern,))
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT * FROM rewards
        WHERE content LIKE ?
        ORDER BY row_number
        LIMIT ? OFFSET ?
    ''', (search_pattern, per_page, offset))
    rows = cursor.fetchall()

    conn.close()

    return jsonify({
        'query': query,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'data': [dict(row) for row in rows]
    })

if __name__ == '__main__':
    # Check if database exists
    if not Path(DB_FILE).exists():
        print(f"Error: Database file '{DB_FILE}' not found!")
        print("Please run import_to_database.py first.")
        exit(1)

    print("="*80)
    print("TWOM Data API Server")
    print("="*80)
    print(f"Database: {Path(DB_FILE).absolute()}")
    print("\nAPI Endpoints:")
    print("  http://localhost:5000/                    - API documentation")
    print("  http://localhost:5000/api/stats           - Database statistics")
    print("  http://localhost:5000/api/rewards/<row>   - Get reward by row number")
    print("  http://localhost:5000/api/scripts/<row>   - Get script by row number")
    print("  http://localhost:5000/api/lookup/<row>    - Get lookup by row number")
    print("\nStarting server...")
    print("="*80)

    app.run(debug=True, host='0.0.0.0', port=5000)
