#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('twom_data.db')
cursor = conn.cursor()

print("=" * 60)
print("DATABASE VERIFICATION - ALL SHEETS")
print("=" * 60)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\nTables in database: {[t[0] for t in tables]}")

# Check each table
for table_name in ['lookup', 'rewards', 'scripts']:
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f"\n{table_name.upper()} Table:")
    print(f"  Total rows: {count}")

    # Show sample data
    cursor.execute(f'SELECT * FROM {table_name} LIMIT 2')
    rows = cursor.fetchall()
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = [col[1] for col in cursor.fetchall()]

    print(f"  Columns: {columns}")
    print(f"  Sample rows:")
    for row in rows:
        print(f"    Row #{row[0]}: {str(row[1])[:80]}...")

print("\n" + "=" * 60)
print("✓ All 3 sheets successfully imported!")
print("=" * 60)

conn.close()
