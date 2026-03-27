#!/usr/bin/env python3
"""
QA Validation Script for TWOM Translations
Validates translation quality and identifies issues
"""
import sqlite3
import argparse
import re
import random
from datetime import datetime

DB_FILE = 'twom_data.db'

class TranslationQA:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def check_references(self, original, translated, row_number):
        """Check that all #NUMBER references are preserved"""
        original_refs = set(re.findall(r'#\d+', original))
        translated_refs = set(re.findall(r'#\d+', translated))

        if original_refs != translated_refs:
            missing = original_refs - translated_refs
            extra = translated_refs - original_refs

            if missing:
                self.errors.append({
                    'row': row_number,
                    'type': 'missing_references',
                    'detail': f"Missing: {missing}"
                })

            if extra:
                self.errors.append({
                    'row': row_number,
                    'type': 'extra_references',
                    'detail': f"Extra: {extra}"
                })

    def check_back_to_game(self, original, translated, row_number):
        """Check #BACK TO GAME is not translated"""
        if '#BACK TO GAME' in original:
            if '#BACK TO GAME' not in translated:
                self.errors.append({
                    'row': row_number,
                    'type': 'back_to_game_translated',
                    'detail': '#BACK TO GAME was translated'
                })

    def check_option_markers(self, original, translated, row_number):
        """Check that > option markers are preserved"""
        original_lines = original.split('\n')
        translated_lines = translated.split('\n')

        original_options = [i for i, line in enumerate(original_lines) if line.strip().startswith('>')]
        translated_options = [i for i, line in enumerate(translated_lines) if line.strip().startswith('>')]

        if len(original_options) != len(translated_options):
            self.warnings.append({
                'row': row_number,
                'type': 'option_count_mismatch',
                'detail': f"Original has {len(original_options)} options, translated has {len(translated_options)}"
            })

    def check_formatting(self, original, translated, row_number):
        """Check that formatting is preserved"""
        # Check markdown bold markers
        original_bold = len(re.findall(r'\*[^*]+\*', original))
        translated_bold = len(re.findall(r'\*[^*]+\*', translated))

        if abs(original_bold - translated_bold) > 2:
            self.warnings.append({
                'row': row_number,
                'type': 'formatting_mismatch',
                'detail': f"Bold formatting differs: {original_bold} vs {translated_bold}"
            })

        # Check line breaks
        original_lines = len(original.split('\n'))
        translated_lines = len(translated.split('\n'))

        if abs(original_lines - translated_lines) > original_lines * 0.2:
            self.warnings.append({
                'row': row_number,
                'type': 'line_count_differs',
                'detail': f"Line count: {original_lines} vs {translated_lines}"
            })

    def check_empty_translation(self, translated, row_number):
        """Check for empty or missing translations"""
        if not translated or translated.strip() == '':
            self.errors.append({
                'row': row_number,
                'type': 'empty_translation',
                'detail': 'Translation is empty'
            })

    def validate_entry(self, row_number, original, translated):
        """Run all validation checks on an entry"""
        if not translated:
            self.check_empty_translation(translated, row_number)
            return

        self.check_references(original, translated, row_number)
        self.check_back_to_game(original, translated, row_number)
        self.check_option_markers(original, translated, row_number)
        self.check_formatting(original, translated, row_number)

def validate_table(table_name, sample_size=None):
    """Validate translations in a table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print(f"QA Validation: {table_name}")
    print(f"{'='*80}\n")

    # Get all rows with translations
    cursor.execute(f'''
        SELECT row_number, content_en, content_zh_hk
        FROM {table_name}
        WHERE content_zh_hk IS NOT NULL AND content_zh_hk != ''
        ORDER BY row_number
    ''')

    rows = cursor.fetchall()
    conn.close()

    total = len(rows)
    print(f"Found {total} translated rows\n")

    if total == 0:
        print("No translations to validate")
        return

    # Sample if requested
    if sample_size and sample_size < total:
        rows = random.sample(rows, sample_size)
        print(f"Sampling {sample_size} rows for validation\n")

    qa = TranslationQA()

    for row_number, content_en, content_zh_hk in rows:
        qa.validate_entry(row_number, content_en, content_zh_hk)

    # Print results
    print(f"{'='*80}")
    print(f"Validation Results")
    print(f"{'='*80}\n")

    if len(qa.errors) == 0 and len(qa.warnings) == 0:
        print("✓ All validations passed!")
    else:
        if qa.errors:
            print(f"ERRORS ({len(qa.errors)}):")
            for error in qa.errors[:20]:  # Show first 20
                print(f"  Row {error['row']}: [{error['type']}] {error['detail']}")
            if len(qa.errors) > 20:
                print(f"  ... and {len(qa.errors) - 20} more errors")
            print()

        if qa.warnings:
            print(f"WARNINGS ({len(qa.warnings)}):")
            for warning in qa.warnings[:20]:  # Show first 20
                print(f"  Row {warning['row']}: [{warning['type']}] {warning['detail']}")
            if len(qa.warnings) > 20:
                print(f"  ... and {len(qa.warnings) - 20} more warnings")
            print()

    print(f"Summary:")
    print(f"  Total validated: {len(rows)}")
    print(f"  Errors: {len(qa.errors)}")
    print(f"  Warnings: {len(qa.warnings)}")
    print(f"  Pass rate: {((len(rows) - len(qa.errors)) / len(rows) * 100):.1f}%")
    print(f"{'='*80}\n")

def generate_review_samples(table_name, count=50, output_file=None):
    """Generate sample entries for manual review"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print(f"Generating Review Samples: {table_name}")
    print(f"{'='*80}\n")

    # Get all rows with translations
    cursor.execute(f'''
        SELECT row_number, content_en, content_zh_hk
        FROM {table_name}
        WHERE content_zh_hk IS NOT NULL AND content_zh_hk != ''
        ORDER BY row_number
    ''')

    rows = cursor.fetchall()
    conn.close()

    total = len(rows)

    if total == 0:
        print("No translations found")
        return

    # Sample
    sample_count = min(count, total)
    samples = random.sample(rows, sample_count)

    # Generate output
    if not output_file:
        output_file = f"qa_review_samples_{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(f"QA Review Samples: {table_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Sample size: {sample_count} of {total}\n")
        f.write("="*80 + "\n\n")

        for i, (row_number, content_en, content_zh_hk) in enumerate(samples, 1):
            f.write(f"--- Sample {i}/{sample_count} - Row {row_number} ---\n\n")
            f.write("ENGLISH:\n")
            f.write(content_en + "\n\n")
            f.write("CHINESE:\n")
            f.write(content_zh_hk + "\n\n")
            f.write("REVIEW NOTES:\n")
            f.write("  [ ] Translation accurate\n")
            f.write("  [ ] Terminology consistent\n")
            f.write("  [ ] Formatting preserved\n")
            f.write("  [ ] References intact\n\n")
            f.write("="*80 + "\n\n")

    print(f"✓ Generated {sample_count} review samples")
    print(f"  Output: {output_file}")
    print(f"  Total translations: {total}")
    print(f"  Sample rate: {(sample_count/total*100):.1f}%")
    print()

def get_translation_stats():
    """Get statistics about translation progress"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print(f"Translation Statistics")
    print(f"{'='*80}\n")

    for table in ['scripts', 'rewards']:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        total = cursor.fetchone()[0]

        cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE content_zh_hk IS NOT NULL AND content_zh_hk != ""')
        translated = cursor.fetchone()[0]

        percentage = (translated / total * 100) if total > 0 else 0

        print(f"{table.capitalize()}:")
        print(f"  Total: {total}")
        print(f"  Translated: {translated}")
        print(f"  Remaining: {total - translated}")
        print(f"  Progress: {percentage:.1f}%")
        print()

    # UI labels
    cursor.execute('SELECT COUNT(*) FROM ui_labels')
    total_labels = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM ui_labels WHERE label_zh_hk IS NOT NULL AND label_zh_hk != ""')
    translated_labels = cursor.fetchone()[0]

    percentage = (translated_labels / total_labels * 100) if total_labels > 0 else 0

    print(f"UI Labels:")
    print(f"  Total: {total_labels}")
    print(f"  Translated: {translated_labels}")
    print(f"  Remaining: {total_labels - translated_labels}")
    print(f"  Progress: {percentage:.1f}%")
    print()

    conn.close()

    print(f"{'='*80}\n")

def main():
    parser = argparse.ArgumentParser(description='QA validation for TWOM translations')
    parser.add_argument('--table', choices=['scripts', 'rewards', 'all'],
                        help='Table to validate')
    parser.add_argument('--sample', type=int,
                        help='Sample size for validation (default: all)')
    parser.add_argument('--generate-samples', action='store_true',
                        help='Generate review samples for manual QA')
    parser.add_argument('--count', type=int, default=50,
                        help='Number of samples to generate (default: 50)')
    parser.add_argument('--stats', action='store_true',
                        help='Show translation statistics')

    args = parser.parse_args()

    if args.stats:
        get_translation_stats()
        return 0

    if args.generate_samples:
        if not args.table or args.table == 'all':
            generate_review_samples('scripts', args.count)
            generate_review_samples('rewards', args.count)
        else:
            generate_review_samples(args.table, args.count)
        return 0

    if not args.table:
        parser.print_help()
        return 1

    if args.table == 'all':
        validate_table('scripts', args.sample)
        validate_table('rewards', args.sample)
    else:
        validate_table(args.table, args.sample)

    return 0

if __name__ == '__main__':
    exit(main())
