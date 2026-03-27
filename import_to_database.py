#!/usr/bin/env python3
"""
Import TMOM.xls Excel file into SQLite database with row number preservation
"""
import pandas as pd
import sqlite3
from pathlib import Path

# Configuration
EXCEL_FILE = 'TWOM.xlsx'  # Updated to use .xlsx file with Chinese translations
DB_FILE = 'twom_data.db'

def create_database():
    """Create SQLite database and tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute('DROP TABLE IF EXISTS lookup')
    cursor.execute('DROP TABLE IF EXISTS rewards')
    cursor.execute('DROP TABLE IF EXISTS scripts')

    # Create Lookup table
    cursor.execute('''
        CREATE TABLE lookup (
            row_number INTEGER PRIMARY KEY,
            reward_num INTEGER,
            reward_result TEXT,
            script_num INTEGER,
            script_result TEXT
        )
    ''')

    # Create Rewards table
    cursor.execute('''
        CREATE TABLE rewards (
            row_number INTEGER PRIMARY KEY,
            content_en TEXT NOT NULL,
            content_zh_hk TEXT,
            last_updated_en DATETIME,
            last_updated_zh_hk DATETIME
        )
    ''')

    # Create Scripts table
    cursor.execute('''
        CREATE TABLE scripts (
            row_number INTEGER PRIMARY KEY,
            content_en TEXT NOT NULL,
            content_zh_hk TEXT,
            last_updated_en DATETIME,
            last_updated_zh_hk DATETIME
        )
    ''')

    conn.commit()
    return conn

def import_lookup_sheet(conn, xls):
    """Import Lookup sheet"""
    df = pd.read_excel(xls, sheet_name='Lookup', header=None)

    cursor = conn.cursor()
    for idx, row in df.iterrows():
        row_number = idx + 1  # 1-based row numbering
        if len(row) >= 4:
            cursor.execute('''
                INSERT INTO lookup (row_number, reward_num, reward_result, script_num, script_result)
                VALUES (?, ?, ?, ?, ?)
            ''', (row_number, row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3]))

    conn.commit()
    print(f"Imported {len(df)} rows into lookup table")

def import_rewards_sheet(conn, xls):
    """Import Rewards sheet with English and Chinese content"""
    df = pd.read_excel(xls, sheet_name='Rewards', header=None)

    cursor = conn.cursor()
    for idx, row in df.iterrows():
        row_number = idx + 1  # 1-based row numbering
        content_en = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
        content_zh_hk = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else None

        if content_zh_hk:
            cursor.execute('''
                INSERT INTO rewards (row_number, content_en, content_zh_hk, last_updated_en, last_updated_zh_hk)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (row_number, content_en, content_zh_hk))
        else:
            cursor.execute('''
                INSERT INTO rewards (row_number, content_en, last_updated_en)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (row_number, content_en))

    conn.commit()
    print(f"Imported {len(df)} rows into rewards table")

def import_scripts_sheet(conn, xls):
    """Import Scripts sheet with English and Chinese content"""
    df = pd.read_excel(xls, sheet_name='Scripts', header=None)

    cursor = conn.cursor()
    for idx, row in df.iterrows():
        row_number = idx + 1  # 1-based row numbering
        content_en = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
        content_zh_hk = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else None

        if content_zh_hk:
            cursor.execute('''
                INSERT INTO scripts (row_number, content_en, content_zh_hk, last_updated_en, last_updated_zh_hk)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (row_number, content_en, content_zh_hk))
        else:
            cursor.execute('''
                INSERT INTO scripts (row_number, content_en, last_updated_en)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (row_number, content_en))

    conn.commit()
    print(f"Imported {len(df)} rows into scripts table")

def create_indexes(conn):
    """Create indexes for better query performance"""
    cursor = conn.cursor()

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lookup_reward_num ON lookup(reward_num)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lookup_script_num ON lookup(script_num)')

    conn.commit()
    print("Created indexes")

def verify_import(conn):
    """Verify the import by running sample queries"""
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    # Check lookup table
    cursor.execute('SELECT COUNT(*) FROM lookup')
    count = cursor.fetchone()[0]
    print(f"\nLookup table: {count} rows")
    cursor.execute('SELECT * FROM lookup LIMIT 2')
    for row in cursor.fetchall():
        print(f"  Row {row[0]}: Reward #{row[1]}, Script #{row[3]}")

    # Check rewards table
    cursor.execute('SELECT COUNT(*) FROM rewards')
    count = cursor.fetchone()[0]
    print(f"\nRewards table: {count} rows")

    cursor.execute('SELECT COUNT(*) FROM rewards WHERE content_zh_hk IS NOT NULL')
    zh_count = cursor.fetchone()[0]
    print(f"  Rows with Chinese translation: {zh_count}")

    cursor.execute('SELECT row_number, SUBSTR(content_en, 1, 50), SUBSTR(content_zh_hk, 1, 30) FROM rewards WHERE content_zh_hk IS NOT NULL LIMIT 2')
    for row in cursor.fetchall():
        print(f"  Row {row[0]}:")
        print(f"    EN: {row[1]}...")
        print(f"    ZH: {row[2]}...")

    # Check scripts table
    cursor.execute('SELECT COUNT(*) FROM scripts')
    count = cursor.fetchone()[0]
    print(f"\nScripts table: {count} rows")

    cursor.execute('SELECT COUNT(*) FROM scripts WHERE content_zh_hk IS NOT NULL')
    zh_count = cursor.fetchone()[0]
    print(f"  Rows with Chinese translation: {zh_count}")

    cursor.execute('SELECT row_number, SUBSTR(content_en, 1, 50), SUBSTR(content_zh_hk, 1, 30) FROM scripts WHERE content_zh_hk IS NOT NULL LIMIT 2')
    for row in cursor.fetchall():
        print(f"  Row {row[0]}:")
        print(f"    EN: {row[1]}...")
        print(f"    ZH: {row[2]}...")

    print("\n" + "="*80)

def main():
    """Main import process"""
    print(f"Starting import from {EXCEL_FILE} to {DB_FILE}")
    print("="*80)

    # Read Excel file
    xls = pd.ExcelFile(EXCEL_FILE, engine='openpyxl')
    print(f"Found sheets: {xls.sheet_names}")

    # Create database
    conn = create_database()
    print("Database created")

    # Import each sheet
    import_lookup_sheet(conn, xls)
    import_rewards_sheet(conn, xls)
    import_scripts_sheet(conn, xls)

    # Create indexes
    create_indexes(conn)

    # Verify import
    verify_import(conn)

    # Close connection
    conn.close()

    print(f"\n✓ Import completed successfully!")
    print(f"Database file: {Path(DB_FILE).absolute()}")

if __name__ == '__main__':
    main()
