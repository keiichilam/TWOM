#!/usr/bin/env python3
"""
Add error message labels for localization
"""
import sqlite3

DB_FILE = 'twom_data.db'

# Error message translations
ERROR_TRANSLATIONS = {
    'error_required': {
        'en': 'Please enter a {field}',
        'zh': '請輸入{field}'
    },
    'error_must_be_number': {
        'en': '{field} must be a number',
        'zh': '{field}必須是數字'
    },
    'error_out_of_range': {
        'en': '{field} must be between {min} and {max}',
        'zh': '{field}必須介於 {min} 和 {max} 之間'
    },
    'error_timeout': {
        'en': 'Request timed out. Please check your connection and try again.',
        'zh': '請求逾時。請檢查您的連線並重試。'
    },
    'error_no_internet': {
        'en': 'No internet connection. Please check your network.',
        'zh': '沒有網路連線。請檢查您的網路。'
    },
    'error_load_failed': {
        'en': 'Failed to load entry: {error}',
        'zh': '無法載入條目：{error}'
    },
    'error_entry_not_found': {
        'en': 'Entry #{number} not found',
        'zh': '找不到條目 #{number}'
    },
    'error_invalid_response': {
        'en': 'Invalid server response',
        'zh': '伺服器回應無效'
    }
}

def main():
    """Add error message labels to ui_labels table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Adding error message labels...")
    print("=" * 80)

    for key, translations in ERROR_TRANSLATIONS.items():
        # Check if exists
        cursor.execute('SELECT key FROM ui_labels WHERE key = ?', (key,))
        exists = cursor.fetchone()

        if exists:
            # Update
            cursor.execute('''
                UPDATE ui_labels
                SET label_en = ?, label_zh_hk = ?
                WHERE key = ?
            ''', (translations['en'], translations['zh'], key))
            print(f"  ✓ Updated {key}")
        else:
            # Insert
            cursor.execute('''
                INSERT INTO ui_labels (key, label_en, label_zh_hk, context)
                VALUES (?, ?, ?, ?)
            ''', (key, translations['en'], translations['zh'], 'Error message'))
            print(f"  ✓ Added {key}")

    conn.commit()

    # Verify
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    cursor.execute('SELECT COUNT(*) FROM ui_labels WHERE key LIKE "error_%"')
    count = cursor.fetchone()[0]

    print(f"\nError message labels: {count}")

    cursor.execute('SELECT key, label_en, label_zh_hk FROM ui_labels WHERE key LIKE "error_%" LIMIT 3')
    print("\nSample labels:")
    for row in cursor.fetchall():
        print(f"  {row[0]}:")
        print(f"    EN: {row[1]}")
        print(f"    ZH: {row[2]}")

    conn.close()
    print("\n✓ Error message labels added successfully!")

if __name__ == '__main__':
    main()
