# Frontend & Backend Setup Guide

This guide explains how to set up and run the Minifig Builder web application with React frontend and FastAPI backend.

## Project Structure

```
minifig-builder/
├── backend/                    # FastAPI server
│   ├── app.py                 # Main application
│   ├── requirements.txt        # Python dependencies
│   └── src/
│       ├── core/              # Core business logic modules
│       │   ├── cache_manager.py
│       │   ├── inventory_parser.py
│       │   └── minifig_finder.py
│       └── fetch_bricklink_minifig.py  # BrickLink API client
│
├── frontend/                   # React application
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── index.html             # HTML entry point
│   └── src/
│       ├── App.jsx            # Main component
│       ├── main.jsx           # React entry point
│       ├── index.css          # Global styles
│       ├── api/               # API client
│       ├── pages/             # Page components
│       └── components/        # Reusable components
│
└── src/                        # Original CLI scripts (still functional)
    └── *.py                   # Existing Python scripts
```

## Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend development)
- BrickLink API credentials ([get them here](https://www.bricklink.com/v2/api/register_consumer.page))

## Backend Setup

### 1. Create Python Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy existing `.env` file to backend directory or create a new one:

```bash
cp ../.env .env
```

Or manually create `.env`:

```
BRICKLINK_CONSUMER_KEY=your_consumer_key
BRICKLINK_CONSUMER_SECRET=your_consumer_secret
BRICKLINK_TOKEN=your_token
BRICKLINK_TOKEN_SECRET=your_token_secret
```

### 4. Run Backend Server

```bash
python app.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
```

This creates an optimized build in `frontend/dist/`

## Running Both Services

### Option 1: Separate Terminal Windows

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Option 2: Using Docker Compose (Optional)

Create `docker-compose.yml` in the root directory:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - BRICKLINK_CONSUMER_KEY=${BRICKLINK_CONSUMER_KEY}
      - BRICKLINK_CONSUMER_SECRET=${BRICKLINK_CONSUMER_SECRET}
      - BRICKLINK_TOKEN=${BRICKLINK_TOKEN}
      - BRICKLINK_TOKEN_SECRET=${BRICKLINK_TOKEN_SECRET}
    volumes:
      - .api_cache:/app/.api_cache
      - ./brickstore-data:/app/brickstore-data
      - ./bricklink-inventory:/app/bricklink-inventory

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

Then run:

```bash
docker-compose up
```

## API Endpoints

### Configuration
- `GET /api/config/status` - Check if API is configured
- `POST /api/config` - Set API credentials

### Analysis
- `POST /api/analyze` - Upload and analyze inventory (multipart form data)
- `GET /api/results` - Get latest analysis results

### Cache Management
- `GET /api/cache/status` - Get cache information
- `POST /api/cache/update-prices` - Update cached prices

### Search & Browse
- `GET /api/search?q=<query>&theme=<theme>` - Search minifigures
- `GET /api/themes` - Get list of available themes
- `GET /api/stats` - Get overall statistics
- `GET /health` - Health check

## Workflow

1. **Configure API Credentials**
   - Go to Settings tab
   - Enter your BrickLink API credentials
   - Save and validate

2. **Populate Cache** (First time only)
   - Run the CLI cache script:
     ```bash
     python3 src/cache_valuable_minifigs.py --theme sw --min-price 2.0
     ```
   - Or use the frontend Cache Manager (after implementing cache population endpoint)

3. **Upload Inventory**
   - Export your inventory as XML from BrickLink
   - Upload via the Upload tab
   - View results in Results tab

4. **Analyze Results**
   - Filter by match percentage, theme, or search
   - See which minifigures you can build completely
   - Check pricing information

5. **Update Prices** (Optional)
   - Use Cache Manager to update prices regularly
   - Keeps your market value data current

## Development Notes

### Adding New API Endpoints

1. Add endpoint to `backend/app.py`
2. Create corresponding API method in `frontend/src/api/client.js`
3. Create React component to use the endpoint
4. Update navigation if needed

### Backend Code Organization

- **app.py** - FastAPI router and endpoints
- **core/cache_manager.py** - Cache operations
- **core/inventory_parser.py** - XML parsing
- **core/minifig_finder.py** - Matching logic
- **fetch_bricklink_minifig.py** - BrickLink API client (existing, refactored imports)

### Frontend Architecture

- **App.jsx** - Main state management and routing
- **pages/** - Full page components
- **components/** - Reusable UI components
- **api/client.js** - Axios-based API client

## Troubleshooting

### Backend Won't Start
- Check Python version: `python3 --version` (need 3.8+)
- Verify virtual environment: `which python`
- Check dependencies: `pip list | grep fastapi`

### Frontend Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- --port 3001
```

### API Connection Issues
- Check backend is running: `curl http://localhost:8000/health`
- Check CORS is enabled in `backend/app.py`
- Check frontend proxy in `frontend/vite.config.js`

### Credentials Not Working
- Verify credentials are correct in BrickLink account settings
- Check `.env` file is in backend directory
- Backend must be restarted after `.env` changes

## Next Steps

1. Run `cache_valuable_minifigs.py` to populate cache
2. Export inventory XML from BrickLink
3. Start both backend and frontend
4. Configure API credentials in Settings
5. Upload inventory and view results!

## Support

For issues with original CLI tools, see the original README files in the project root.
