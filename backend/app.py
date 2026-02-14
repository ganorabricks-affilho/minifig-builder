"""FastAPI backend server for minifig-builder."""

import os
import sys
import json
from pathlib import Path
from typing import Optional
from tempfile import TemporaryDirectory
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from core import (
    CachedBrickLinkAPI,
    InventoryParser,
    MinifigureFinder,
    MinifigMatch,
)
from core.minifig_finder import save_results_json

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Minifig Builder API",
    description="API for finding buildable LEGO minifigures from inventory",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use a proper session/state management)
latest_results = None
cache_status = {}


class ConfigRequest(BaseModel):
    """API credentials configuration."""
    consumer_key: str
    consumer_secret: str
    token: str
    token_secret: str


class AnalysisResult(BaseModel):
    """Analysis result model."""
    summary: dict
    complete: list
    incomplete: list


class ThemeResponse(BaseModel):
    """Theme information."""
    theme: str
    prefix: str
    count: int


# Helper functions
def load_csv_themes() -> dict:
    """Load themes from M.csv."""
    themes = {}
    csv_path = Path.cwd() / 'brickstore-data' / 'M.csv'
    
    if not csv_path.exists():
        return themes
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    minifig_id = parts[2]
                    theme = parts[3]
                    if minifig_id and theme:
                        # Extract theme prefix from minifig_id
                        prefix = ''.join([c for c in minifig_id if not c.isdigit()])
                        if prefix not in themes:
                            themes[prefix] = {'theme': theme, 'count': 0}
                        themes[prefix]['count'] += 1
    except Exception as e:
        print(f"Error loading themes: {e}")
    
    return themes


# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/config/status")
async def config_status():
    """Check if BrickLink API is configured."""
    try:
        # Try to initialize API to check credentials
        api = CachedBrickLinkAPI()
        return {
            "configured": True,
            "message": "BrickLink API configured successfully"
        }
    except ValueError as e:
        return {
            "configured": False,
            "message": str(e)
        }


@app.post("/api/config")
async def set_config(config: ConfigRequest):
    """Configure BrickLink API credentials."""
    try:
        # Validate credentials by attempting to create API instance
        # Set environment variables
        os.environ['BRICKLINK_CONSUMER_KEY'] = config.consumer_key
        os.environ['BRICKLINK_CONSUMER_SECRET'] = config.consumer_secret
        os.environ['BRICKLINK_TOKEN'] = config.token
        os.environ['BRICKLINK_TOKEN_SECRET'] = config.token_secret
        
        # Try to initialize and make a test call
        api = CachedBrickLinkAPI()
        
        # Save to .env file
        env_path = Path.cwd() / '.env'
        env_content = f"""BRICKLINK_CONSUMER_KEY={config.consumer_key}
BRICKLINK_CONSUMER_SECRET={config.consumer_secret}
BRICKLINK_TOKEN={config.token}
BRICKLINK_TOKEN_SECRET={config.token_secret}
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        return {
            "success": True,
            "message": "API credentials configured successfully"
        }
    except Exception as e:
        # Clear failed credentials
        for key in ['BRICKLINK_CONSUMER_KEY', 'BRICKLINK_CONSUMER_SECRET', 
                   'BRICKLINK_TOKEN', 'BRICKLINK_TOKEN_SECRET']:
            os.environ.pop(key, None)
        
        raise HTTPException(
            status_code=400,
            detail=f"Configuration failed: {str(e)}"
        )


@app.post("/api/analyze")
async def analyze_inventory(file: UploadFile = File(...)):
    """Upload inventory file and perform analysis."""
    global latest_results
    
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be XML format")
    
    try:
        # Save uploaded file temporarily
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / file.filename
            
            # Save uploaded file
            contents = await file.read()
            with open(temp_path, 'wb') as f:
                f.write(contents)
            
            # Initialize API and inventory
            try:
                api = CachedBrickLinkAPI()
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"API not configured: {str(e)}")
            
            inventory = InventoryParser(temp_path)
            if not inventory.load():
                raise HTTPException(status_code=400, detail="Failed to parse inventory file")
            
            # Get cached minifigs
            minifig_ids = api.get_cached_minifig_ids()
            if not minifig_ids:
                raise HTTPException(
                    status_code=400,
                    detail="No minifigures in cache. Run cache_valuable_minifigs.py first."
                )
            
            # Find matches
            finder = MinifigureFinder(inventory, api)
            matches = finder.search_minifigs(minifig_ids, use_cache_only=True)
            
            # Build response
            complete = [m for m in matches if m.can_build]
            incomplete = [m for m in matches if not m.can_build]
            
            def match_to_dict(m: MinifigMatch):
                """Convert MinifigMatch to dictionary."""
                price_summary = None
                if m.price_data:
                    price_info = m.price_data.get('data', {})
                    if price_info:
                        ordered_new = price_info.get('ordered_new', {})
                        ordered_used = price_info.get('ordered_used', {})
                        avg_new = ordered_new.get('avg_price')
                        avg_used = ordered_used.get('avg_price')
                        
                        if avg_new is not None or avg_used is not None:
                            price_summary = {}
                            if avg_new is not None:
                                price_summary['new_condition'] = avg_new
                            if avg_used is not None:
                                price_summary['used_condition'] = avg_used
                
                return {
                    'minifig_id': m.minifig_id,
                    'minifig_name': m.minifig_name,
                    'year_released': m.year_released,
                    'category_name': m.category_name,
                    'total_parts': m.total_parts,
                    'matched_parts': m.matched_parts,
                    'missing_parts': m.missing_parts,
                    'match_percentage': m.match_percentage,
                    'can_build': m.can_build,
                    'prices_6month_average': price_summary,
                    'all_parts': m.matched_details if m.matched_details else [],
                    'missing_details': m.missing_details
                }
            
            latest_results = {
                'summary': {
                    'total_checked': len(matches),
                    'complete_matches': len(complete),
                    'incomplete_matches': len(incomplete)
                },
                'complete': [match_to_dict(m) for m in complete],
                'incomplete': [match_to_dict(m) for m in incomplete]
            }
            
            return latest_results
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/results")
async def get_results():
    """Get latest analysis results."""
    global latest_results
    
    if latest_results is None:
        raise HTTPException(status_code=404, detail="No analysis results available")
    
    return latest_results


@app.get("/api/cache/status")
async def cache_status():
    """Get cache status information."""
    try:
        api = CachedBrickLinkAPI()
        status = api.get_cache_status()
        return {
            "minifig_count": status['minifig_count'],
            "price_count": status['price_count'],
            "minifig_cache_file": status['minifig_cache_file'],
            "price_cache_file": status['price_cache_file'],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"API not configured: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache status: {str(e)}")


@app.post("/api/cache/update-prices")
async def update_cache_prices(background_tasks: BackgroundTasks):
    """Trigger price cache update."""
    try:
        api = CachedBrickLinkAPI()
        minifig_ids = api.get_cached_minifig_ids()
        
        if not minifig_ids:
            raise HTTPException(status_code=400, detail="No minifigures in cache")
        
        # Add background task to update prices
        def update_prices():
            for minifig_id in minifig_ids:
                api.get_price_with_cache(minifig_id, use_cache_only=False)
        
        background_tasks.add_task(update_prices)
        
        return {"message": f"Price update started for {len(minifig_ids)} minifigures"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"API not configured: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating prices: {str(e)}")


@app.get("/api/search")
async def search_minifigs(q: str = "", theme: str = ""):
    """Search cached minifigures by name or theme."""
    global latest_results
    
    try:
        api = CachedBrickLinkAPI()
        minifig_ids = api.get_cached_minifig_ids()
        
        results = []
        for minifig_id in minifig_ids:
            data = api.get_minifig_with_cache(minifig_id, use_cache_only=True)
            if data:
                name = data['item_data'].get('name', '').lower()
                category = data['item_data'].get('category_name', '').lower()
                
                # Filter by search query and theme
                if (q.lower() in name or q.lower() in minifig_id.lower()):
                    if not theme or theme.lower() in category:
                        results.append({
                            'minifig_id': minifig_id,
                            'name': data['item_data'].get('name', ''),
                            'category': category,
                            'year': data['item_data'].get('year_released'),
                            'parts_count': len(data['parts'])
                        })
        
        return {"results": results[:50]}  # Limit to 50 results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/themes")
async def get_themes():
    """Get list of available themes."""
    themes = load_csv_themes()
    
    theme_list = [
        {
            "theme": info["theme"],
            "prefix": prefix,
            "count": info["count"]
        }
        for prefix, info in sorted(themes.items())
    ]
    
    return {"themes": theme_list}


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics."""
    global latest_results
    
    try:
        api = CachedBrickLinkAPI()
        status = api.get_cache_status()
        
        stats = {
            "cache": {
                "minifig_count": status['minifig_count'],
                "price_count": status['price_count']
            },
            "latest_analysis": None
        }
        
        if latest_results:
            stats["latest_analysis"] = latest_results["summary"]
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
