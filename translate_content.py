#!/usr/bin/env python3
"""
Translation Automation Script for TWOM Content
Translates game content to Traditional Chinese (zh-HK) using AI
"""
import sqlite3
import argparse
import sys
import time
from datetime import datetime
import re

# This script requires either:
# - Anthropic API (Claude): pip install anthropic
# - OpenAI API (GPT-4): pip install openai

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

DB_FILE = 'twom_data.db'

# Game terminology glossary for consistent translations
GLOSSARY = {
    "Shelter": "庇護所",
    "Scavenging": "搜刮",
    "Character": "角色",
    "Fatigue": "疲勞",
    "Waste bag": "廢棄袋",
    "Save bag": "保存袋",
    "Resource": "資源",
    "Water": "水",
    "Wood": "木材",
    "Components": "零件",
    "Food": "食物",
    "Canned Food": "罐頭食品",
    "Raw Food": "生食",
    "Vegetable": "蔬菜",
    "Meds": "藥品",
    "Bandages": "繃帶",
    "Weapon": "武器",
    "Assault Rifle": "突擊步槍",
    "Shotgun": "霰彈槍",
    "Pistol": "手槍",
    "Knife": "刀",
    "Hatchet": "斧頭",
    "Ammo": "彈藥",
    "Shell": "彈殼",
    "Fittings": "裝置",
    "Workshop": "工作坊",
    "Moonshine": "私酒",
    "Cigarette": "香煙",
    "Coffee": "咖啡",
    "Sugar": "糖",
    "Lockpick": "開鎖工具",
    "Shovel": "鏟子",
    "Sawblade": "鋸片",
    "Guitar": "吉他",
    "Book": "書",
    "Filter": "濾網",
    "Jewelry": "珠寶",
    "Alcohol": "酒精",
    "Herbal Meds": "草藥",
    "Herb": "藥草",
    "Chems": "化學品"
}

TRANSLATION_PROMPT_TEMPLATE = """You are translating content from the board game "This War of Mine" to Traditional Chinese (Hong Kong variant, zh-HK).

CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:
1. Preserve ALL cross-references like #123 or #1819 EXACTLY as they appear
2. Keep option markers ">" at the start of lines EXACTLY as they are
3. DO NOT translate "#BACK TO GAME" - keep it in English
4. Maintain all line breaks and paragraph structure
5. Preserve markdown formatting like *bold* and bullet points (•)
6. Use Hong Kong Traditional Chinese characters
7. Use the provided glossary for game terms

GLOSSARY:
{glossary}

CONTENT TO TRANSLATE:
{content}

Translate to Traditional Chinese (zh-HK), following all rules above. Return ONLY the translated text, no explanations."""

class TWOMTranslator:
    def __init__(self, api_key=None, provider='anthropic'):
        """
        Initialize translator
        provider: 'anthropic' (Claude) or 'openai' (GPT-4)
        """
        self.provider = provider
        self.api_key = api_key

        if provider == 'anthropic':
            if not HAS_ANTHROPIC:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            self.client = anthropic.Anthropic(api_key=api_key)
        elif provider == 'openai':
            if not HAS_OPENAI:
                raise ImportError("openai package not installed. Run: pip install openai")
            openai.api_key = api_key
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def translate_text(self, text):
        """Translate a single text entry"""
        # Build glossary string
        glossary_str = "\n".join([f"- {en}: {zh}" for en, zh in GLOSSARY.items()])

        # Build prompt
        prompt = TRANSLATION_PROMPT_TEMPLATE.format(
            glossary=glossary_str,
            content=text
        )

        if self.provider == 'anthropic':
            return self._translate_with_claude(prompt)
        else:
            return self._translate_with_gpt4(prompt)

    def _translate_with_claude(self, prompt):
        """Translate using Claude API"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise

    def _translate_with_gpt4(self, prompt):
        """Translate using GPT-4 API"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in Traditional Chinese (Hong Kong)."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling GPT-4 API: {e}")
            raise

    def validate_translation(self, original, translated):
        """Validate that critical elements are preserved"""
        errors = []

        # Check that all #NUMBER references are preserved
        original_refs = set(re.findall(r'#\d+', original))
        translated_refs = set(re.findall(r'#\d+', translated))

        if original_refs != translated_refs:
            missing = original_refs - translated_refs
            extra = translated_refs - original_refs
            if missing:
                errors.append(f"Missing references: {missing}")
            if extra:
                errors.append(f"Extra references: {extra}")

        # Check #BACK TO GAME is preserved
        if '#BACK TO GAME' in original and '#BACK TO GAME' not in translated:
            errors.append("#BACK TO GAME was translated but should not be")

        # Check line count is similar (allow 10% difference)
        original_lines = len(original.split('\n'))
        translated_lines = len(translated.split('\n'))
        if abs(original_lines - translated_lines) > original_lines * 0.1:
            errors.append(f"Line count differs significantly: {original_lines} vs {translated_lines}")

        return errors

def translate_batch(table_name, start_row, end_row, translator, dry_run=False):
    """Translate a batch of entries"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print(f"Translating {table_name} rows {start_row} to {end_row}")
    print(f"{'='*80}\n")

    # Fetch rows
    cursor.execute(f'''
        SELECT row_number, content_en
        FROM {table_name}
        WHERE row_number >= ? AND row_number <= ?
        ORDER BY row_number
    ''', (start_row, end_row))

    rows = cursor.fetchall()
    total = len(rows)

    if total == 0:
        print("No rows to translate")
        conn.close()
        return

    print(f"Found {total} rows to translate\n")

    success_count = 0
    error_count = 0

    for i, (row_number, content_en) in enumerate(rows, 1):
        print(f"[{i}/{total}] Row {row_number}...", end=' ', flush=True)

        try:
            # Translate
            translated = translator.translate_text(content_en)

            # Validate
            validation_errors = translator.validate_translation(content_en, translated)

            if validation_errors:
                print(f"❌ VALIDATION FAILED")
                for error in validation_errors:
                    print(f"  - {error}")
                error_count += 1
                continue

            if dry_run:
                print(f"✓ (dry run - not saved)")
                print(f"  Preview: {translated[:100]}...")
            else:
                # Save to database
                cursor.execute(f'''
                    UPDATE {table_name}
                    SET content_zh_hk = ?, last_updated_zh_hk = CURRENT_TIMESTAMP
                    WHERE row_number = ?
                ''', (translated, row_number))
                conn.commit()
                print(f"✓")

            success_count += 1

            # Rate limiting - be nice to the API
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            error_count += 1

    conn.close()

    print(f"\n{'='*80}")
    print(f"Translation complete:")
    print(f"  Success: {success_count}/{total}")
    print(f"  Errors: {error_count}/{total}")
    print(f"{'='*80}\n")

def main():
    parser = argparse.ArgumentParser(description='Translate TWOM content to Traditional Chinese')
    parser.add_argument('--table', choices=['scripts', 'rewards', 'ui_labels'], required=True,
                        help='Table to translate')
    parser.add_argument('--start', type=int, help='Start row number')
    parser.add_argument('--end', type=int, help='End row number')
    parser.add_argument('--provider', choices=['anthropic', 'openai'], default='anthropic',
                        help='AI provider to use')
    parser.add_argument('--api-key', help='API key (or set ANTHROPIC_API_KEY / OPENAI_API_KEY env var)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Test translation without saving to database')

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key
    if not api_key:
        import os
        if args.provider == 'anthropic':
            api_key = os.environ.get('ANTHROPIC_API_KEY')
        else:
            api_key = os.environ.get('OPENAI_API_KEY')

    if not api_key:
        print(f"Error: API key not provided. Set {args.provider.upper()}_API_KEY environment variable or use --api-key")
        return 1

    # Initialize translator
    try:
        translator = TWOMTranslator(api_key=api_key, provider=args.provider)
    except Exception as e:
        print(f"Error initializing translator: {e}")
        return 1

    # Translate
    if args.table == 'ui_labels':
        print("UI labels translation not yet implemented - please translate manually")
        return 1
    else:
        if not args.start or not args.end:
            print("Error: --start and --end required for scripts/rewards tables")
            return 1

        translate_batch(args.table, args.start, args.end, translator, args.dry_run)

    return 0

if __name__ == '__main__':
    exit(main())
