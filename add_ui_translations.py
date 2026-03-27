#!/usr/bin/env python3
"""
Add Chinese translations to UI labels
"""
import sqlite3

DB_FILE = 'twom_data.db'

# Chinese translations for UI labels
UI_TRANSLATIONS = {
    'title': '戰爭日記',
    'subtitle': '這是我的戰爭',
    'search_label': '搜尋條目',
    'script_number_label': '劇本編號 (1-1950)',
    'script_number_placeholder': '輸入劇本編號',
    'reward_number_label': '獎勵編號 (1-31)',
    'reward_number_placeholder': '輸入獎勵編號',
    'load_script_button': '載入劇本',
    'load_reward_button': '載入獎勵',
    'script_entry_type': '劇本條目',
    'reward_entry_type': '獎勵條目',
    'loading_text': '載入中...',
    'error_title': '錯誤',
    'breadcrumb_home': '主頁'
}

def main():
    """Add Chinese translations to ui_labels table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Adding Chinese translations to UI labels...")
    print("=" * 80)

    for key, zh_text in UI_TRANSLATIONS.items():
        cursor.execute('''
            UPDATE ui_labels
            SET label_zh_hk = ?
            WHERE key = ?
        ''', (zh_text, key))
        print(f"  ✓ {key}: {zh_text}")

    conn.commit()

    # Verify
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    cursor.execute('SELECT COUNT(*) FROM ui_labels WHERE label_zh_hk IS NOT NULL')
    translated = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM ui_labels')
    total = cursor.fetchone()[0]

    print(f"\nUI Labels: {translated}/{total} translated")

    cursor.execute('SELECT key, label_en, label_zh_hk FROM ui_labels LIMIT 5')
    print("\nSample labels:")
    for row in cursor.fetchall():
        print(f"  {row[0]}:")
        print(f"    EN: {row[1]}")
        print(f"    ZH: {row[2]}")

    conn.close()
    print("\n✓ Chinese UI translations added successfully!")

if __name__ == '__main__':
    main()
