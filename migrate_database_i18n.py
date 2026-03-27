#!/usr/bin/env python3
"""
Database Migration Script for i18n Support
Migrates TWOM database to support Traditional Chinese (zh-HK) alongside English
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
import argparse

DB_FILE = 'twom_data.db'
BACKUP_SUFFIX = '.backup'

# UI labels to be translated
UI_LABELS = {
    'title': {
        'en': 'War Journal',
        'context': 'Main page title'
    },
    'subtitle': {
        'en': 'This War of Mine',
        'context': 'Game name subtitle'
    },
    'search_label': {
        'en': 'Search Entry',
        'context': 'Search section header'
    },
    'script_number_label': {
        'en': 'Script Number (1-1950)',
        'context': 'Script input label'
    },
    'script_number_placeholder': {
        'en': 'Enter script #',
        'context': 'Script input placeholder'
    },
    'reward_number_label': {
        'en': 'Reward Number (1-31)',
        'context': 'Reward input label'
    },
    'reward_number_placeholder': {
        'en': 'Enter reward #',
        'context': 'Reward input placeholder'
    },
    'load_script_button': {
        'en': 'Load Script',
        'context': 'Button to load script entry'
    },
    'load_reward_button': {
        'en': 'Load Reward',
        'context': 'Button to load reward entry'
    },
    'script_entry_type': {
        'en': 'Script Entry',
        'context': 'Entry type badge for scripts'
    },
    'reward_entry_type': {
        'en': 'Reward Entry',
        'context': 'Entry type badge for rewards'
    },
    'loading_text': {
        'en': 'Loading entry...',
        'context': 'Loading indicator text'
    },
    'error_title': {
        'en': 'Error',
        'context': 'Error message title'
    },
    'breadcrumb_home': {
        'en': 'Home',
        'context': 'Breadcrumb home link'
    }
}

def backup_database(db_path):
    """Create a backup of the database"""
    backup_path = f"{db_path}{BACKUP_SUFFIX}"
    print(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup created successfully")
    return backup_path

def migrate_table(conn, table_name):
    """Migrate a table to support multiple languages"""
    cursor = conn.cursor()

    print(f"\nMigrating table: {table_name}")

    # Check if already migrated
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]

    if 'content_en' in columns:
        print(f"  ⚠ Table {table_name} already migrated, skipping...")
        return

    # Rename content to content_en
    print(f"  Renaming 'content' to 'content_en'...")
    cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN content TO content_en")

    # Add new columns
    print(f"  Adding 'content_zh_hk' column...")
    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN content_zh_hk TEXT")

    print(f"  Adding 'last_updated_en' column...")
    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN last_updated_en DATETIME")

    print(f"  Adding 'last_updated_zh_hk' column...")
    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN last_updated_zh_hk DATETIME")

    # Set initial timestamp for last_updated_en for all existing rows
    print(f"  Setting initial timestamps...")
    cursor.execute(f"UPDATE {table_name} SET last_updated_en = CURRENT_TIMESTAMP WHERE content_en IS NOT NULL")

    conn.commit()
    print(f"  ✓ Table {table_name} migrated successfully")

def create_ui_labels_table(conn):
    """Create the ui_labels table and populate with English labels"""
    cursor = conn.cursor()

    print("\nCreating ui_labels table...")

    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS ui_labels")

    # Create table
    cursor.execute('''
        CREATE TABLE ui_labels (
            key TEXT PRIMARY KEY,
            label_en TEXT NOT NULL,
            label_zh_hk TEXT,
            context TEXT
        )
    ''')

    # Insert UI labels
    print("  Inserting UI labels...")
    for key, data in UI_LABELS.items():
        cursor.execute('''
            INSERT INTO ui_labels (key, label_en, context)
            VALUES (?, ?, ?)
        ''', (key, data['en'], data['context']))

    conn.commit()
    print(f"  ✓ Created ui_labels table with {len(UI_LABELS)} labels")

def verify_migration(conn):
    """Verify the migration was successful"""
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    # Check each table
    for table_name in ['scripts', 'rewards']:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        print(f"\n{table_name} table columns:")
        for col in columns:
            print(f"  - {col}")

        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Total rows: {count}")

        # Check if content was preserved
        if table_name in ['scripts', 'rewards']:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE content_en IS NOT NULL")
            en_count = cursor.fetchone()[0]
            print(f"  Rows with English content: {en_count}")

            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE content_zh_hk IS NOT NULL")
            zh_count = cursor.fetchone()[0]
            print(f"  Rows with Chinese content: {zh_count}")

    # Check ui_labels table
    cursor.execute("SELECT COUNT(*) FROM ui_labels")
    count = cursor.fetchone()[0]
    print(f"\nui_labels table:")
    print(f"  Total labels: {count}")

    cursor.execute("SELECT key, label_en, label_zh_hk FROM ui_labels LIMIT 5")
    print(f"  Sample labels:")
    for row in cursor.fetchall():
        zh_status = "✓" if row[2] else "✗"
        print(f"    {row[0]}: {row[1]} [{zh_status} Chinese]")

    print("\n" + "="*80)

def main():
    """Main migration process"""
    parser = argparse.ArgumentParser(description='Migrate TWOM database for i18n support')
    parser.add_argument('--db', default=DB_FILE, help='Database file path')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    args = parser.parse_args()

    db_path = args.db

    if not Path(db_path).exists():
        print(f"Error: Database file '{db_path}' not found!")
        return 1

    print("="*80)
    print("TWOM Database i18n Migration")
    print("="*80)
    print(f"Database: {Path(db_path).absolute()}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Create backup
    if not args.no_backup:
        try:
            backup_database(db_path)
        except Exception as e:
            print(f"Error creating backup: {e}")
            return 1
    else:
        print("\n⚠ Skipping backup (--no-backup flag)")

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        print(f"\n✓ Connected to database")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return 1

    try:
        # Migrate tables (only scripts and rewards have content columns)
        migrate_table(conn, 'scripts')
        migrate_table(conn, 'rewards')

        # Create ui_labels table
        create_ui_labels_table(conn)

        # Verify migration
        verify_migration(conn)

        print("\n✓ Migration completed successfully!")
        print(f"\nNext steps:")
        print(f"  1. Run API server to verify endpoints work")
        print(f"  2. Translate UI labels in ui_labels table")
        print(f"  3. Run translate_content.py to translate content entries")

        return 0

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()

        print(f"\nRestoring from backup...")
        if not args.no_backup and Path(f"{db_path}{BACKUP_SUFFIX}").exists():
            shutil.copy2(f"{db_path}{BACKUP_SUFFIX}", db_path)
            print(f"✓ Database restored from backup")

        return 1

    finally:
        conn.close()

if __name__ == '__main__':
    exit(main())
