# TWOM Database - Quick Start Guide

## What Was Done

1. **Excel Analysis**: Analyzed TMOM.xls with 3 sheets:
   - Lookup: 2 rows
   - Rewards: 31 rows
   - Scripts: 1950 rows

2. **Database Creation**: Created SQLite database (`twom_data.db`) with row number preservation

3. **REST API**: Built Flask-based API for web application access

4. **Test Interface**: Created HTML test page for easy testing

## Quick Start

### 1. Start the API Server

```bash
cd /home/boardgame/project/TWOM
source venv/bin/activate
python3 api.py
```

The server will run on `http://localhost:5000`

### 2. Open Test Interface

Open `test_api.html` in your web browser to test the API interactively.

### 3. Use from Your Web Application

```javascript
// Get script by row number
fetch('http://localhost:5000/api/scripts/100')
    .then(response => response.json())
    .then(data => console.log(data.content));

// Get reward by row number
fetch('http://localhost:5000/api/rewards/5')
    .then(response => response.json())
    .then(data => console.log(data.content));

// Search scripts
fetch('http://localhost:5000/api/search/scripts?q=shelter')
    .then(response => response.json())
    .then(data => console.log(`Found ${data.total} results`));
```

## Key Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `/api/stats` | Database statistics | `GET /api/stats` |
| `/api/scripts/<row>` | Get script by row number | `GET /api/scripts/100` |
| `/api/rewards/<row>` | Get reward by row number | `GET /api/rewards/5` |
| `/api/lookup/<row>` | Get lookup by row number | `GET /api/lookup/2` |
| `/api/search/scripts?q=<query>` | Search scripts | `GET /api/search/scripts?q=shelter` |
| `/api/search/rewards?q=<query>` | Search rewards | `GET /api/search/rewards?q=found` |

## Files Created

- `twom_data.db` - SQLite database with all data
- `api.py` - REST API server
- `import_to_database.py` - Database import script
- `test_api.html` - Interactive test interface
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation
- `QUICK_START.md` - This file

## Testing

```bash
# Test API stats
curl http://localhost:5000/api/stats

# Get script #100
curl http://localhost:5000/api/scripts/100

# Get reward #5
curl http://localhost:5000/api/rewards/5

# Search for "shelter"
curl "http://localhost:5000/api/search/scripts?q=shelter"
```

## Database Structure

All tables preserve original Excel row numbers for easy reference:

- **lookup**: Row numbers 1-2
- **rewards**: Row numbers 1-31
- **scripts**: Row numbers 1-1950

## Next Steps

1. Integrate the API into your web application
2. Customize the API endpoints as needed
3. Add authentication if required
4. Deploy to production server

For detailed documentation, see `README.md`
