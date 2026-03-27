#!/usr/bin/env python3
"""
REST API for TWOM Database - SECURE VERSION
Provides endpoints with security hardening
"""
from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import sqlite3
from pathlib import Path
import re
import logging
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/twom_api_secure.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024  # 16KB max request size
app.config['JSON_SORT_KEYS'] = False

# CORS Configuration - restrict to specific origins in production
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Change to specific domains in production
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

# Rate Limiting - prevent DoS attacks
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Security Headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

DB_FILE = 'twom_data.db'

def get_language_param():
    """Get language from query param, default to English"""
    lang = request.args.get('lang', 'en').lower()
    if lang not in ['en', 'zh-hk']:
        lang = 'en'
    return lang

def get_content_with_language(row, lang='en'):
    """
    Returns content in requested language with fallback to English
    Returns: (content, actual_lang, available_langs)
    """
    # Get available languages
    available_langs = ['en']
    if row.get('content_zh_hk'):
        available_langs.append('zh-hk')

    # Return requested language or fallback
    if lang == 'zh-hk' and row.get('content_zh_hk'):
        return (row['content_zh_hk'], 'zh-hk', available_langs)
    return (row['content_en'], 'en', available_langs)

def get_db_connection():
    """Create a database connection with security settings"""
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys and other security features
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('PRAGMA query_only = ON')  # Read-only mode
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        abort(500, description="Database connection failed")

def validate_integer(value, min_val=None, max_val=None):
    """Validate and sanitize integer input"""
    try:
        num = int(value)
        if min_val is not None and num < min_val:
            raise ValueError(f"Value must be at least {min_val}")
        if max_val is not None and num > max_val:
            raise ValueError(f"Value must be at most {max_val}")
        return num
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid integer input: {value} - {e}")
        abort(400, description=f"Invalid input: {str(e)}")

def validate_string(value, max_length=100):
    """Validate and sanitize string input"""
    if not isinstance(value, str):
        abort(400, description="Invalid string input")

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[^\w\s\-\.]', '', value)

    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized

def log_request():
    """Log incoming requests for security monitoring"""
    logger.info(f"Request: {request.method} {request.path} from {get_remote_address()}")

def error_response(message, status_code=400):
    """Standardized error response"""
    logger.warning(f"Error response: {status_code} - {message}")
    return jsonify({'error': message}), status_code

# Routes
@app.route('/')
@limiter.limit("30 per minute")
def index():
    """Serve the journal UI"""
    log_request()
    try:
        return send_file('journal.html')
    except FileNotFoundError:
        return error_response("Journal not found", 404)

@app.route('/journal.html')
@limiter.limit("30 per minute")
def journal():
    """Serve the journal UI"""
    log_request()
    try:
        return send_file('journal.html')
    except FileNotFoundError:
        return error_response("Journal not found", 404)

@app.route('/static/<path:filename>')
@limiter.limit("100 per hour")
def serve_static(filename):
    """Serve static files (JS, CSS, etc.)"""
    log_request()
    try:
        return send_file(f'static/{filename}')
    except FileNotFoundError:
        return error_response("File not found", 404)

@app.route('/api')
@limiter.limit("100 per hour")
def api_docs():
    """API documentation"""
    log_request()
    return jsonify({
        'name': 'TWOM Data API (Secured)',
        'version': '3.0',
        'security': 'Rate limited, input validated, read-only access',
        'features': ['Multi-language support (en, zh-hk)', 'Content fallback', 'UI translations'],
        'endpoints': {
            '/api/lookup': 'Get all lookup data',
            '/api/lookup/<row_number>': 'Get lookup by row number',
            '/api/rewards': 'Get all rewards (with pagination, ?lang=en|zh-hk)',
            '/api/rewards/<row_number>': 'Get reward by row number (supports ?lang parameter)',
            '/api/scripts': 'Get all scripts (with pagination, ?lang=en|zh-hk)',
            '/api/scripts/<row_number>': 'Get script by row number (supports ?lang parameter)',
            '/api/search/scripts?q=<query>': 'Search scripts by text (supports ?lang parameter)',
            '/api/search/rewards?q=<query>': 'Search rewards by text (supports ?lang parameter)',
            '/api/ui-labels': 'Get UI labels for all languages (?lang=en|zh-hk)',
            '/api/languages': 'Get available languages',
            '/api/stats': 'Get database statistics'
        }
    })

@app.route('/api/stats')
@limiter.limit("100 per hour")
def get_stats():
    """Get database statistics"""
    log_request()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        stats = {}
        cursor.execute('SELECT COUNT(*) FROM lookup')
        stats['lookup_count'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM rewards')
        stats['rewards_count'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM scripts')
        stats['scripts_count'] = cursor.fetchone()[0]

        # Translation statistics
        cursor.execute('SELECT COUNT(*) FROM scripts WHERE content_zh_hk IS NOT NULL')
        stats['scripts_translated'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM rewards WHERE content_zh_hk IS NOT NULL')
        stats['rewards_translated'] = cursor.fetchone()[0]

        conn.close()
        return jsonify(stats)
    except sqlite3.Error as e:
        logger.error(f"Database error in get_stats: {e}")
        conn.close()
        return error_response("Database query failed", 500)

@app.route('/api/languages')
@limiter.limit("100 per hour")
def get_languages():
    """Get available languages"""
    log_request()
    return jsonify({
        'languages': ['en', 'zh-hk'],
        'default': 'en',
        'names': {
            'en': 'English',
            'zh-hk': '繁體中文 (香港)'
        }
    })

@app.route('/api/ui-labels')
@limiter.limit("100 per hour")
def get_ui_labels():
    """Get UI labels for translation"""
    log_request()
    lang = get_language_param()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT key, label_en, label_zh_hk FROM ui_labels')
        rows = cursor.fetchall()
        conn.close()

        labels = {}
        for row in rows:
            key = row[0]
            if lang == 'zh-hk' and row[2]:
                labels[key] = row[2]
            else:
                labels[key] = row[1]

        return jsonify({
            'lang': lang,
            'labels': labels
        })
    except sqlite3.Error as e:
        logger.error(f"Database error in get_ui_labels: {e}")
        conn.close()
        return error_response("Database query failed", 500)

# LOOKUP ENDPOINTS
@app.route('/api/lookup')
@limiter.limit("50 per hour")
def get_all_lookup():
    """Get all lookup data"""
    log_request()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM lookup ORDER BY row_number LIMIT 100')
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    except sqlite3.Error as e:
        logger.error(f"Database error in get_all_lookup: {e}")
        conn.close()
        return error_response("Database query failed", 500)

@app.route('/api/lookup/<row_number>')
@limiter.limit("100 per hour")
def get_lookup_by_row(row_number):
    """Get lookup by row number"""
    log_request()
    row_num = validate_integer(row_number, min_val=1, max_val=10000)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM lookup WHERE row_number = ? LIMIT 1', (row_num,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return jsonify(dict(row))
        else:
            return error_response('Row not found', 404)
    except sqlite3.Error as e:
        logger.error(f"Database error in get_lookup_by_row: {e}")
        conn.close()
        return error_response("Database query failed", 500)

# REWARDS ENDPOINTS
@app.route('/api/rewards')
@limiter.limit("50 per hour")
def get_all_rewards():
    """Get all rewards with pagination and language support"""
    log_request()
    page = validate_integer(request.args.get('page', 1), min_val=1, max_val=100)
    per_page = validate_integer(request.args.get('per_page', 20), min_val=1, max_val=50)
    lang = get_language_param()

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT COUNT(*) FROM rewards')
        total = cursor.fetchone()[0]

        cursor.execute('''
            SELECT row_number, content_en, content_zh_hk, last_updated_en, last_updated_zh_hk
            FROM rewards
            ORDER BY row_number
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        rows = cursor.fetchall()

        conn.close()

        # Process each row to include language-specific content
        data = []
        for row in rows:
            row_dict = dict(row)
            content, actual_lang, available_langs = get_content_with_language(row_dict, lang)
            data.append({
                'row_number': row_dict['row_number'],
                'content': content,
                'lang': actual_lang,
                'available_langs': available_langs
            })

        return jsonify({
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'lang': lang,
            'data': data
        })
    except sqlite3.Error as e:
        logger.error(f"Database error in get_all_rewards: {e}")
        conn.close()
        return error_response("Database query failed", 500)

@app.route('/api/rewards/<row_number>')
@limiter.limit("100 per hour")
def get_reward_by_row(row_number):
    """Get reward by row number with language support"""
    log_request()
    row_num = validate_integer(row_number, min_val=1, max_val=31)
    lang = get_language_param()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT row_number, content_en, content_zh_hk, last_updated_en, last_updated_zh_hk
            FROM rewards WHERE row_number = ? LIMIT 1
        ''', (row_num,))
        row = cursor.fetchone()
        conn.close()

        if row:
            row_dict = dict(row)
            content, actual_lang, available_langs = get_content_with_language(row_dict, lang)

            return jsonify({
                'row_number': row_dict['row_number'],
                'content': content,
                'lang': actual_lang,
                'available_langs': available_langs
            })
        else:
            return error_response('Row not found', 404)
    except sqlite3.Error as e:
        logger.error(f"Database error in get_reward_by_row: {e}")
        conn.close()
        return error_response("Database query failed", 500)

# SCRIPTS ENDPOINTS
@app.route('/api/scripts')
@limiter.limit("50 per hour")
def get_all_scripts():
    """Get all scripts with pagination and language support"""
    log_request()
    page = validate_integer(request.args.get('page', 1), min_val=1, max_val=100)
    per_page = validate_integer(request.args.get('per_page', 20), min_val=1, max_val=50)
    lang = get_language_param()

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT COUNT(*) FROM scripts')
        total = cursor.fetchone()[0]

        cursor.execute('''
            SELECT row_number, content_en, content_zh_hk, last_updated_en, last_updated_zh_hk
            FROM scripts
            ORDER BY row_number
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        rows = cursor.fetchall()

        conn.close()

        # Process each row to include language-specific content
        data = []
        for row in rows:
            row_dict = dict(row)
            content, actual_lang, available_langs = get_content_with_language(row_dict, lang)
            data.append({
                'row_number': row_dict['row_number'],
                'content': content,
                'lang': actual_lang,
                'available_langs': available_langs
            })

        return jsonify({
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'lang': lang,
            'data': data
        })
    except sqlite3.Error as e:
        logger.error(f"Database error in get_all_scripts: {e}")
        conn.close()
        return error_response("Database query failed", 500)

@app.route('/api/scripts/<row_number>')
@limiter.limit("100 per hour")
def get_script_by_row(row_number):
    """Get script by row number with language support"""
    log_request()
    row_num = validate_integer(row_number, min_val=1, max_val=1950)
    lang = get_language_param()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT row_number, content_en, content_zh_hk, last_updated_en, last_updated_zh_hk
            FROM scripts WHERE row_number = ? LIMIT 1
        ''', (row_num,))
        row = cursor.fetchone()
        conn.close()

        if row:
            row_dict = dict(row)
            content, actual_lang, available_langs = get_content_with_language(row_dict, lang)

            return jsonify({
                'row_number': row_dict['row_number'],
                'content': content,
                'lang': actual_lang,
                'available_langs': available_langs
            })
        else:
            return error_response('Row not found', 404)
    except sqlite3.Error as e:
        logger.error(f"Database error in get_script_by_row: {e}")
        conn.close()
        return error_response("Database query failed", 500)

# SEARCH ENDPOINTS
@app.route('/api/search/scripts')
@limiter.limit("20 per hour")
def search_scripts():
    """Search scripts by text with language support"""
    log_request()
    query = request.args.get('q', '')

    if not query:
        return error_response('Query parameter "q" is required', 400)

    # Sanitize search query
    query = validate_string(query, max_length=50)

    page = validate_integer(request.args.get('page', 1), min_val=1, max_val=20)
    per_page = validate_integer(request.args.get('per_page', 20), min_val=1, max_val=20)
    lang = get_language_param()

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        search_pattern = f'%{query}%'

        # Search in both language columns
        cursor.execute('''
            SELECT COUNT(*) FROM scripts
            WHERE content_en LIKE ? OR content_zh_hk LIKE ?
        ''', (search_pattern, search_pattern))
        total = cursor.fetchone()[0]

        # Limit total results to prevent abuse
        if total > 200:
            total = 200

        cursor.execute('''
            SELECT row_number, content_en, content_zh_hk, last_updated_en, last_updated_zh_hk
            FROM scripts
            WHERE content_en LIKE ? OR content_zh_hk LIKE ?
            ORDER BY row_number
            LIMIT ? OFFSET ?
        ''', (search_pattern, search_pattern, per_page, offset))
        rows = cursor.fetchall()

        conn.close()

        # Process each row to include language-specific content
        data = []
        for row in rows:
            row_dict = dict(row)
            content, actual_lang, available_langs = get_content_with_language(row_dict, lang)
            data.append({
                'row_number': row_dict['row_number'],
                'content': content,
                'lang': actual_lang,
                'available_langs': available_langs
            })

        return jsonify({
            'query': query,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'lang': lang,
            'data': data
        })
    except sqlite3.Error as e:
        logger.error(f"Database error in search_scripts: {e}")
        conn.close()
        return error_response("Database query failed", 500)

@app.route('/api/search/rewards')
@limiter.limit("20 per hour")
def search_rewards():
    """Search rewards by text with language support"""
    log_request()
    query = request.args.get('q', '')

    if not query:
        return error_response('Query parameter "q" is required', 400)

    # Sanitize search query
    query = validate_string(query, max_length=50)

    page = validate_integer(request.args.get('page', 1), min_val=1, max_val=10)
    per_page = validate_integer(request.args.get('per_page', 20), min_val=1, max_val=20)
    lang = get_language_param()

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        search_pattern = f'%{query}%'

        # Search in both language columns
        cursor.execute('''
            SELECT COUNT(*) FROM rewards
            WHERE content_en LIKE ? OR content_zh_hk LIKE ?
        ''', (search_pattern, search_pattern))
        total = cursor.fetchone()[0]

        cursor.execute('''
            SELECT row_number, content_en, content_zh_hk, last_updated_en, last_updated_zh_hk
            FROM rewards
            WHERE content_en LIKE ? OR content_zh_hk LIKE ?
            ORDER BY row_number
            LIMIT ? OFFSET ?
        ''', (search_pattern, search_pattern, per_page, offset))
        rows = cursor.fetchall()

        conn.close()

        # Process each row to include language-specific content
        data = []
        for row in rows:
            row_dict = dict(row)
            content, actual_lang, available_langs = get_content_with_language(row_dict, lang)
            data.append({
                'row_number': row_dict['row_number'],
                'content': content,
                'lang': actual_lang,
                'available_langs': available_langs
            })

        return jsonify({
            'query': query,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'lang': lang,
            'data': data
        })
    except sqlite3.Error as e:
        logger.error(f"Database error in search_rewards: {e}")
        conn.close()
        return error_response("Database query failed", 500)

# Error handlers
@app.errorhandler(400)
def bad_request(e):
    return error_response(str(e.description), 400)

@app.errorhandler(404)
def not_found(e):
    return error_response("Resource not found", 404)

@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning(f"Rate limit exceeded from {get_remote_address()}")
    return error_response("Rate limit exceeded. Please try again later.", 429)

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return error_response("Internal server error", 500)

if __name__ == '__main__':
    # Check if database exists
    if not Path(DB_FILE).exists():
        print(f"Error: Database file '{DB_FILE}' not found!")
        print("Please run import_to_database.py first.")
        exit(1)

    print("="*80)
    print("TWOM Data API Server - SECURE VERSION")
    print("="*80)
    print(f"Database: {Path(DB_FILE).absolute()}")
    print("\nSecurity Features:")
    print("  ✓ Rate limiting enabled")
    print("  ✓ Input validation and sanitization")
    print("  ✓ SQL injection prevention")
    print("  ✓ Security headers configured")
    print("  ✓ Request logging enabled")
    print("  ✓ Read-only database access")
    print("  ✓ XSS protection")
    print("  ✓ CORS configured")
    print("\nAPI Endpoints:")
    print("  http://localhost:5000/                    - Journal UI")
    print("  http://localhost:5000/api/stats           - Database statistics")
    print("  http://localhost:5000/api/rewards/<row>   - Get reward by row number")
    print("  http://localhost:5000/api/scripts/<row>   - Get script by row number")
    print("\nStarting secure server...")
    print("="*80)

    # Run in production mode (debug=False)
    app.run(debug=False, host='0.0.0.0', port=5000)
