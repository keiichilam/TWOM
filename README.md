# TWOM Database & API

This project imports data from TMOM.xls Excel file into a SQLite database and provides a REST API for web applications to access the data by row number.

## Database Structure

The database contains three tables:

### 1. `lookup` Table
- `row_number` (INTEGER, PRIMARY KEY) - Original Excel row number
- `reward_num` (INTEGER) - Reward reference number
- `reward_result` (TEXT) - Reward result text
- `script_num` (INTEGER) - Script reference number
- `script_result` (TEXT) - Script result text

**Records:** 2 rows

### 2. `rewards` Table
- `row_number` (INTEGER, PRIMARY KEY) - Original Excel row number (1-31)
- `content` (TEXT) - Reward content text

**Records:** 31 rows

### 3. `scripts` Table
- `row_number` (INTEGER, PRIMARY KEY) - Original Excel row number (1-1950)
- `content` (TEXT) - Script content text

**Records:** 1950 rows

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install pandas openpyxl xlrd sqlalchemy flask flask-cors
```

### 2. Import Excel Data to Database

```bash
source venv/bin/activate
python3 import_to_database.py
```

This will create `twom_data.db` with all the data from TMOM.xls.

### 3. Start API Server

```bash
source venv/bin/activate
python3 api.py
```

The API server will start on `http://localhost:5000`

## API Endpoints

### Base URL
```
http://localhost:5000
```

### Available Endpoints

#### 1. API Documentation
```
GET /
```
Returns API information and available endpoints.

#### 2. Database Statistics
```
GET /api/stats
```
Returns the count of records in each table.

**Example Response:**
```json
{
  "lookup_count": 2,
  "rewards_count": 31,
  "scripts_count": 1950
}
```

#### 3. Get All Lookup Data
```
GET /api/lookup
```
Returns all lookup records.

#### 4. Get Lookup by Row Number
```
GET /api/lookup/<row_number>
```
Returns a specific lookup record.

**Example:**
```bash
curl http://localhost:5000/api/lookup/2
```

#### 5. Get All Rewards (Paginated)
```
GET /api/rewards?page=1&per_page=20
```
Returns paginated list of rewards.

**Parameters:**
- `page` (optional, default: 1) - Page number
- `per_page` (optional, default: 20) - Items per page

**Example Response:**
```json
{
  "page": 1,
  "per_page": 20,
  "total": 31,
  "total_pages": 2,
  "data": [
    {
      "row_number": 1,
      "content": "We've found a shortcut!..."
    }
  ]
}
```

#### 6. Get Reward by Row Number
```
GET /api/rewards/<row_number>
```
Returns a specific reward by its row number.

**Example:**
```bash
curl http://localhost:5000/api/rewards/5
```

**Example Response:**
```json
{
  "row_number": 5,
  "content": "We've found something!..."
}
```

#### 7. Get All Scripts (Paginated)
```
GET /api/scripts?page=1&per_page=20
```
Returns paginated list of scripts.

**Parameters:**
- `page` (optional, default: 1) - Page number
- `per_page` (optional, default: 20) - Items per page

#### 8. Get Script by Row Number
```
GET /api/scripts/<row_number>
```
Returns a specific script by its row number.

**Example:**
```bash
curl http://localhost:5000/api/scripts/100
```

**Example Response:**
```json
{
  "row_number": 100,
  "content": "The hallway of an abandoned building..."
}
```

#### 9. Search Scripts
```
GET /api/search/scripts?q=<query>&page=1&per_page=20
```
Search scripts by text content.

**Parameters:**
- `q` (required) - Search query
- `page` (optional, default: 1) - Page number
- `per_page` (optional, default: 20) - Items per page

**Example:**
```bash
curl "http://localhost:5000/api/search/scripts?q=package"
```

#### 10. Search Rewards
```
GET /api/search/rewards?q=<query>&page=1&per_page=20
```
Search rewards by text content.

**Example:**
```bash
curl "http://localhost:5000/api/search/rewards?q=found"
```

## Usage Examples

### JavaScript (Fetch API)

```javascript
// Get script by row number
async function getScript(rowNumber) {
    const response = await fetch(`http://localhost:5000/api/scripts/${rowNumber}`);
    const data = await response.json();
    return data;
}

// Get reward by row number
async function getReward(rowNumber) {
    const response = await fetch(`http://localhost:5000/api/rewards/${rowNumber}`);
    const data = await response.json();
    return data;
}

// Search scripts
async function searchScripts(query) {
    const response = await fetch(`http://localhost:5000/api/search/scripts?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    return data;
}

// Usage
getScript(100).then(script => {
    console.log('Script #100:', script.content);
});

getReward(5).then(reward => {
    console.log('Reward #5:', reward.content);
});

searchScripts('shelter').then(results => {
    console.log(`Found ${results.total} scripts containing 'shelter'`);
    results.data.forEach(script => {
        console.log(`Row ${script.row_number}:`, script.content.substring(0, 100));
    });
});
```

### Python

```python
import requests

# Get script by row number
response = requests.get('http://localhost:5000/api/scripts/100')
script = response.json()
print(f"Script #100: {script['content']}")

# Get reward by row number
response = requests.get('http://localhost:5000/api/rewards/5')
reward = response.json()
print(f"Reward #5: {reward['content']}")

# Search scripts
response = requests.get('http://localhost:5000/api/search/scripts', params={'q': 'shelter'})
results = response.json()
print(f"Found {results['total']} scripts containing 'shelter'")
```

### cURL

```bash
# Get database statistics
curl http://localhost:5000/api/stats

# Get script by row number
curl http://localhost:5000/api/scripts/100

# Get reward by row number
curl http://localhost:5000/api/rewards/5

# Search scripts
curl "http://localhost:5000/api/search/scripts?q=shelter"

# Get paginated scripts
curl "http://localhost:5000/api/scripts?page=2&per_page=10"
```

## Database File

The SQLite database file is located at:
```
/home/boardgame/project/TWOM/twom_data.db
```

You can query it directly using any SQLite client:

```bash
sqlite3 twom_data.db "SELECT * FROM scripts WHERE row_number = 100;"
```

## Files

- `TMOM.xls` - Original Excel file
- `twom_data.db` - SQLite database (generated)
- `import_to_database.py` - Script to import Excel data to database
- `api.py` - REST API server
- `analyze_excel.py` - Script to analyze Excel structure
- `test_api.html` - HTML test page for API
- `README.md` - This file

## Notes

- Row numbers are preserved from the original Excel file (1-based indexing)
- The API supports CORS, so you can call it from web browsers
- All text content is stored as-is from the Excel file
- The database includes indexes on frequently queried fields for better performance

## Production Deployment

For production use, consider:

1. Using a production WSGI server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

2. Using PostgreSQL instead of SQLite for better concurrent access
3. Adding authentication and rate limiting
4. Setting up proper CORS policies
5. Adding caching (e.g., Redis) for frequently accessed data
