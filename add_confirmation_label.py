#!/usr/bin/env python3
"""
Add confirmation message label for history clearing
"""
import sqlite3

DB_FILE = 'twom_data.db'

def main():
    """Add confirmation message label to ui_labels table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Adding confirmation message label...")
    print("=" * 80)

    # Confirmation message
    key = 'confirm_clear_history'
    label_en = 'Clear navigation history and return to search?'
    label_zh = '清除導航歷史記錄並返回搜尋？'

    # Check if exists
    cursor.execute('SELECT key FROM ui_labels WHERE key = ?', (key,))
    exists = cursor.fetchone()

    if exists:
        # Update
        cursor.execute('''
            UPDATE ui_labels
            SET label_en = ?, label_zh_hk = ?
            WHERE key = ?
        ''', (label_en, label_zh, key))
        print(f"  ✓ Updated {key}")
    else:
        # Insert
        cursor.execute('''
            INSERT INTO ui_labels (key, label_en, label_zh_hk, context)
            VALUES (?, ?, ?, ?)
        ''', (key, label_en, label_zh, 'Confirmation dialog'))
        print(f"  ✓ Added {key}")

    conn.commit()

    # Verify
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    cursor.execute('SELECT key, label_en, label_zh_hk FROM ui_labels WHERE key = ?', (key,))
    row = cursor.fetchone()
    print(f"\n{row[0]}:")
    print(f"  EN: {row[1]}")
    print(f"  ZH: {row[2]}")

    conn.close()
    print("\n✓ Confirmation label added successfully!")

if __name__ == '__main__':
    main()
