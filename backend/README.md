# Backend - FastAPI Server

The REST API backend for Minifig Builder.

## Features

- **REST API** - Clean, documented endpoints for all operations
- **Secure Config** - Server-side storage of BrickLink API credentials
- **Inventory Analysis** - Process XML inventory files and find buildable minifigures
- **Cache Management** - Persistent caching of minifigure and price data
- **Search & Browse** - Query cached minifigures by name, ID, themes
- **Background Tasks** - Async price updates without blocking requests

## Technology Stack

- **FastAPI** - Modern async Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python 3.8+** - Core language

## Project Structure

```
backend/
├── app.py                     # Main FastAPI application
├── requirements.txt           # Python dependencies
└── src/
    ├── __init__.py
    ├── fetch_bricklink_minifig.py  # BrickLink API client (from parent src/)
    └── core/
        ├── __init__.py
        ├── cache_manager.py    # Cache operations
        ├── inventory_parser.py # XML parsing logic
        └── minifig_finder.py   # Matching algorithm
```

## API Endpoints

### Configuration
- `GET /api/config/status` - Check API configuration status
- `POST /api/config` - Configure BrickLink API credentials

### Analysis
- `POST /api/analyze` - Upload and analyze inventory (form data)
- `GET /api/results` - Get latest analysis results

### Cache
- `GET /api/cache/status` - Get cache information
- `POST /api/cache/update-prices` - Update cached prices (background task)

### Search
- `GET /api/search?q=<query>&theme=<theme>` - Search minifigures
- `GET /api/themes` - Get available themes

### Stats
- `GET /api/stats` - Get overall statistics
- `GET /health` - Health check

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Credentials
Create `.env` file with BrickLink API credentials:
```
BRICKLINK_CONSUMER_KEY=xxx
BRICKLINK_CONSUMER_SECRET=xxx
BRICKLINK_TOKEN=xxx
BRICKLINK_TOKEN_SECRET=xxx
```

### 4. Run Server
```bash
python app.py
```

Server runs at `http://localhost:8000`

## Development

### Debug Mode
```bash
python app.py  # Already has reload=True
```

The server auto-reloads on file changes.

### Testing Endpoints
Use the built-in Swagger UI at `http://localhost:8000/docs`

## Core Modules

### cache_manager.py
Manages persistent caching of minifigure and price data.

**Key Classes:**
- `CachedBrickLinkAPI` - API client with disk caching

**Key Methods:**
- `get_minifig_with_cache()` - Get/cache minifigure data
- `get_price_with_cache()` - Get/cache price data
- `get_cached_minifig_ids()` - List cached minifigures
- `get_cache_status()` - Cache statistics

### inventory_parser.py
Parses BrickLink XML inventory files.

**Key Classes:**
- `InventoryParser` - Parses XML inventory
- `InventoryPart` - Individual part data

**Key Methods:**
- `load()` - Load and parse XML file
- `has_part()` - Check inventory for part
- `get_stats()` - Get inventory statistics

### minifig_finder.py
Core matching algorithm to find buildable minifigures.

**Key Classes:**
- `MinifigureFinder` - Matches minifigs to inventory
- `MinifigMatch` - Match result data

**Key Methods:**
- `check_minifig()` - Check single minifigure
- `search_minifigs()` - Check multiple minifigures
- `save_results_json()` - Export results

## Workflow

1. **Credentials** → User configures BrickLink API via `/api/config`
2. **Upload** → User uploads inventory XML to `/api/analyze`
3. **Analysis** → Backend parses XML and checks against cached minifigs
4. **Results** → Frontend retrieves results via `/api/results`
5. **Filtering** → Frontend filters/searches results
6. **Price Update** → Background task updates prices via `/api/cache/update-prices`

## Environment Variables

```
BRICKLINK_CONSUMER_KEY      # Required - BrickLink API key
BRICKLINK_CONSUMER_SECRET   # Required - BrickLink API secret
BRICKLINK_TOKEN             # Required - BrickLink access token
BRICKLINK_TOKEN_SECRET      # Required - BrickLink token secret
BACKEND_PORT                # Optional - Server port (default: 8000)
```

## Error Handling

All endpoints return:
- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

All errors include descriptive `detail` messages.

## Performance Considerations

- **Caching** - Minifig data cached on disk to avoid API calls
- **Async** - Background tasks don't block main thread
- **Rate Limiting** - Respects BrickLink API rate limits during cache updates
- **File Operations** - Large JSON files streamed where possible

## Security

- **No Credentials in Frontend** - API keys stored server-side only
- **Environment Variables** - Credentials loaded from `.env`, never committed
- **CORS Enabled** - Frontend can access API (configurable)
- **Input Validation** - Pydantic validates all inputs

## Monitoring

Check API health:
```bash
curl http://localhost:8000/health
```

View API docs:
```bash
open http://localhost:8000/docs
```

Check cache status:
```bash
curl http://localhost:8000/api/cache/status
```
