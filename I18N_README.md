# Traditional Chinese (zh-HK) Support - Implementation Guide

## Overview

This implementation adds full Traditional Chinese (Hong Kong) language support to the TWOM War Journal application with:
- ✅ Database schema migration for multi-language content
- ✅ Language-aware REST API with fallback
- ✅ Frontend language switcher (English | 繁體中文)
- ✅ Translation automation tools
- ✅ QA validation scripts

## System Architecture

### Database Schema

**Tables Modified:**
- `scripts` - 1,950 game script entries
- `rewards` - 31 reward entries
- `ui_labels` - 14 UI label translations (NEW)

**Schema Changes:**
```sql
-- Before: scripts/rewards
row_number INTEGER PRIMARY KEY
content TEXT NOT NULL

-- After: scripts/rewards
row_number INTEGER PRIMARY KEY
content_en TEXT NOT NULL
content_zh_hk TEXT
last_updated_en DATETIME
last_updated_zh_hk DATETIME
```

### API Endpoints

**New/Updated Endpoints:**
```
GET /api/scripts/<row>?lang=en|zh-hk      - Get script with language support
GET /api/rewards/<row>?lang=en|zh-hk      - Get reward with language support
GET /api/ui-labels?lang=en|zh-hk          - Get UI translations
GET /api/languages                         - Get available languages
GET /api/stats                             - Shows translation progress
```

**Response Format:**
```json
{
  "row_number": 100,
  "content": "您在廢棄建築物的走廊...",
  "lang": "zh-hk",
  "available_langs": ["en", "zh-hk"]
}
```

### Frontend Features

**Language Switcher:**
- Fixed position (top-right)
- Persists preference in localStorage
- Automatically reloads current entry on switch

**Internationalization:**
- All UI elements tagged with `data-i18n` attributes
- Dynamic label updates on language change
- Chinese font support (Noto Sans TC)

## Implementation Status

### ✅ Phase 1: Database Layer (COMPLETED)
- Database migrated successfully
- Backup created: `twom_data.db.backup`
- UI labels table created with 14 English labels

### ✅ Phase 2: API Layer (COMPLETED)
- All endpoints support `?lang=` parameter
- Fallback to English if Chinese unavailable
- Backward compatible (default to English)

### ✅ Phase 3: Translation Tools (COMPLETED)
- Translation automation script created
- QA validation script created
- Ready for AI-powered translation

### ✅ Phase 4: Frontend Implementation (COMPLETED)
- Language switcher UI added
- i18n.js module created
- All UI elements internationalized

### ⏳ Phase 5: Content Translation (TODO)
- 0/1,950 scripts translated (0.0%)
- 0/31 rewards translated (0.0%)
- 0/14 UI labels translated (0.0%)

## Usage Instructions

### 1. Check Translation Status

```bash
python3 qa_translations.py --stats
```

### 2. Translate UI Labels (Manual - Recommended First)

Edit the database directly to add Chinese UI labels:

```sql
UPDATE ui_labels SET label_zh_hk = '戰爭日記' WHERE key = 'title';
UPDATE ui_labels SET label_zh_hk = '這是我的戰爭' WHERE key = 'subtitle';
UPDATE ui_labels SET label_zh_hk = '搜尋條目' WHERE key = 'search_label';
UPDATE ui_labels SET label_zh_hk = '腳本編號 (1-1950)' WHERE key = 'script_number_label';
UPDATE ui_labels SET label_zh_hk = '輸入腳本編號' WHERE key = 'script_number_placeholder';
UPDATE ui_labels SET label_zh_hk = '獎勵編號 (1-31)' WHERE key = 'reward_number_label';
UPDATE ui_labels SET label_zh_hk = '輸入獎勵編號' WHERE key = 'reward_number_placeholder';
UPDATE ui_labels SET label_zh_hk = '載入腳本' WHERE key = 'load_script_button';
UPDATE ui_labels SET label_zh_hk = '載入獎勵' WHERE key = 'load_reward_button';
UPDATE ui_labels SET label_zh_hk = '腳本條目' WHERE key = 'script_entry_type';
UPDATE ui_labels SET label_zh_hk = '獎勵條目' WHERE key = 'reward_entry_type';
UPDATE ui_labels SET label_zh_hk = '載入中...' WHERE key = 'loading_text';
UPDATE ui_labels SET label_zh_hk = '錯誤' WHERE key = 'error_title';
UPDATE ui_labels SET label_zh_hk = '主頁' WHERE key = 'breadcrumb_home';
```

Or use Python:

```python
import sqlite3
conn = sqlite3.connect('twom_data.db')
cursor = conn.cursor()

ui_translations = {
    'title': '戰爭日記',
    'subtitle': '這是我的戰爭',
    'search_label': '搜尋條目',
    'script_number_label': '腳本編號 (1-1950)',
    'script_number_placeholder': '輸入腳本編號',
    'reward_number_label': '獎勵編號 (1-31)',
    'reward_number_placeholder': '輸入獎勵編號',
    'load_script_button': '載入腳本',
    'load_reward_button': '載入獎勵',
    'script_entry_type': '腳本條目',
    'reward_entry_type': '獎勵條目',
    'loading_text': '載入中...',
    'error_title': '錯誤',
    'breadcrumb_home': '主頁'
}

for key, label_zh in ui_translations.items():
    cursor.execute('UPDATE ui_labels SET label_zh_hk = ? WHERE key = ?', (label_zh, key))

conn.commit()
conn.close()
```

### 3. Translate Content with AI

**Requirements:**
```bash
# Install Anthropic SDK (for Claude)
pip install anthropic

# Or install OpenAI SDK (for GPT-4)
pip install openai
```

**Set API Key:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
# or
export OPENAI_API_KEY="your-api-key-here"
```

**Translate Rewards (31 entries - small batch):**
```bash
python3 translate_content.py \
  --table rewards \
  --start 1 \
  --end 31 \
  --provider anthropic
```

**Translate Scripts (1,950 entries - in batches of 100):**
```bash
# Batch 1
python3 translate_content.py \
  --table scripts \
  --start 1 \
  --end 100 \
  --provider anthropic

# Batch 2
python3 translate_content.py \
  --table scripts \
  --start 101 \
  --end 200 \
  --provider anthropic

# Continue for all batches...
```

**Dry Run (test without saving):**
```bash
python3 translate_content.py \
  --table scripts \
  --start 1 \
  --end 10 \
  --dry-run
```

### 4. Validate Translations

**Run QA Checks:**
```bash
# Validate all scripts
python3 qa_translations.py --table scripts

# Validate all rewards
python3 qa_translations.py --table rewards

# Validate both
python3 qa_translations.py --table all

# Sample validation (faster)
python3 qa_translations.py --table scripts --sample 100
```

**Generate Review Samples:**
```bash
# Generate 50 random samples for manual review
python3 qa_translations.py --generate-samples --table scripts --count 50

# Generate samples for both tables
python3 qa_translations.py --generate-samples --table all --count 100
```

### 5. Test the Application

**Access the Journal:**
```
http://192.168.4.232:5000/
```

**Test Language Switching:**
1. Click "繁體中文" button (top-right)
2. UI should update to Chinese
3. Load a script entry
4. Content should display in Chinese (if translated)
5. Click "English" to switch back

**Test API Directly:**
```bash
# Get script in English
curl "http://localhost:5000/api/scripts/100?lang=en"

# Get script in Chinese (will fallback to English if not translated)
curl "http://localhost:5000/api/scripts/100?lang=zh-hk"

# Get UI labels in Chinese
curl "http://localhost:5000/api/ui-labels?lang=zh-hk"
```

## Translation Guidelines

### Critical Rules

**MUST PRESERVE:**
1. ✅ All `#NUMBER` cross-references (e.g., #100, #1819)
2. ✅ Option markers `>` at start of lines
3. ✅ `#BACK TO GAME` command (keep in English)
4. ✅ Line breaks and paragraph structure
5. ✅ Markdown formatting (`*bold*`, bullet points)

**TRANSLATION QUALITY:**
- Use Hong Kong Traditional Chinese variant (zh-HK)
- Use game terminology glossary (see translate_content.py)
- Maintain consistent terminology throughout
- Preserve game mechanics context

### Example

**English:**
```
You are in an abandoned building.

>Go left #123
>Go right #456

#BACK TO GAME
```

**Chinese (Correct):**
```
您在一座廢棄的建築物內。

>向左走 #123
>向右走 #456

#BACK TO GAME
```

## Cost Estimation

**AI Translation Costs:**
- Claude Sonnet 4.5: ~$3-5 per 1,000,000 tokens
- Estimated total: 1,983 entries × ~500 tokens = ~1,000,000 tokens
- **Total cost: $50-100** (one-time)

**Time Estimation:**
- Rewards (31 entries): 15-30 minutes
- Scripts (1,950 entries): 16-20 hours (with batching)
- Manual QA (5% sample): 2-4 hours
- **Total: 20-25 hours** (mostly automated)

## Troubleshooting

### API Returns English Instead of Chinese

**Cause:** Translation not yet saved to database
**Solution:** Check translation status with `qa_translations.py --stats`

### Language Switcher Not Appearing

**Cause:** Static file not served properly
**Solution:** Check browser console, verify `/static/i18n.js` loads correctly

### Translation Script Fails

**Common Issues:**
1. Missing API key → Set ANTHROPIC_API_KEY or OPENAI_API_KEY
2. Package not installed → Run `pip install anthropic` or `pip install openai`
3. Rate limiting → Add delay between batches (already implemented)

### Chinese Characters Display as Boxes

**Cause:** Font not loaded
**Solution:** Check internet connection, Noto Sans TC should load from Google Fonts

## Files Created/Modified

### New Files:
- `migrate_database_i18n.py` - Database migration script
- `translate_content.py` - AI translation automation
- `qa_translations.py` - Translation validation
- `static/i18n.js` - Frontend language manager
- `I18N_README.md` - This documentation

### Modified Files:
- `api_secure.py` - Added language support to all endpoints
- `journal.html` - Added language switcher and i18n attributes
- `import_to_database.py` - Updated for new schema
- `twom_data.db` - Migrated schema (backup: twom_data.db.backup)

## Next Steps

1. **Translate UI Labels** (Manual, 5 minutes)
   - Use the SQL or Python script above
   - Test language switcher immediately

2. **Translate Small Batch** (Test, 15 minutes)
   - Translate rewards table (31 entries)
   - Validate with QA script
   - Test in browser

3. **Translate Full Content** (Production, 20 hours)
   - Translate scripts in batches of 100
   - Run QA validation after each batch
   - Generate review samples for manual QA

4. **Manual QA Review** (5%, 2-4 hours)
   - Review 100 random samples
   - Focus on complex entries with many references
   - Verify game mechanics terminology

5. **Deploy** (5 minutes)
   - Already deployed! Server running with i18n support
   - Users can switch languages immediately

## Support

**Questions or Issues?**
- Check logs: `tail -f /tmp/twom_api_secure.log`
- Verify database: `python3 qa_translations.py --stats`
- Test API: `curl http://localhost:5000/api/languages`

**Rollback if Needed:**
```bash
# Stop server
./server_secure.sh stop

# Restore backup
cp twom_data.db.backup twom_data.db

# Start server
./server_secure.sh start
```

---

**Implementation Date:** 2026-03-24
**Status:** ✅ Infrastructure Complete, ⏳ Content Translation Pending
**Version:** 3.0 (i18n-enabled)
