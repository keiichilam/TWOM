#!/usr/bin/env python3
"""
Analyze the TMOM.xls Excel file structure
"""
import pandas as pd
import sys

# Read the Excel file
excel_file = 'TMOM.xls'

try:
    # Try to read with openpyxl engine (works for both .xls and .xlsx)
    xls = pd.ExcelFile(excel_file, engine='openpyxl')

    print(f"Excel file: {excel_file}")
    print(f"Number of sheets: {len(xls.sheet_names)}")
    print(f"Sheet names: {xls.sheet_names}")
    print("\n" + "="*80 + "\n")

    # Analyze each sheet
    for sheet_name in xls.sheet_names:
        print(f"Sheet: {sheet_name}")
        print("-" * 80)

        # Read the sheet
        df = pd.read_excel(xls, sheet_name=sheet_name)

        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"\nColumn names:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")

        print(f"\nFirst 5 rows:")
        print(df.head())

        print(f"\nData types:")
        print(df.dtypes)

        print(f"\nBasic statistics:")
        print(df.describe(include='all'))

        print("\n" + "="*80 + "\n")

except Exception as e:
    print(f"Error reading Excel file: {e}")
    sys.exit(1)
