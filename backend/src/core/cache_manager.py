"""Cache management for BrickLink API data."""

import json
import datetime
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import asdict
import sys
import os

# Import from sibling package
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from fetch_bricklink_minifig import BrickLinkAPI
except ImportError:
    # Fallback for when running from different directories
    from ..fetch_bricklink_minifig import BrickLinkAPI


class CachedBrickLinkAPI(BrickLinkAPI):
    """BrickLink API with persistent disk cache."""
    
    def __init__(self, cache_dir: Path = None):
        """Initialize cached API."""
        super().__init__()
        if cache_dir is None:
            # Use workspace root (minifig-builder) for cache
            cache_dir = Path(__file__).resolve().parents[3] / '.api_cache'
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.minifig_cache_file = self.cache_dir / 'minifigures.json'
        self.price_cache_file = self.cache_dir / 'minifig_prices.json'
        self.minifig_cache = self._load_minifig_cache()
        self.price_cache = self._load_price_cache()
    
    def _load_minifig_cache(self) -> Dict:
        """Load cached minifigure data from disk."""
        if self.minifig_cache_file.exists():
            try:
                with open(self.minifig_cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _load_price_cache(self) -> Dict:
        """Load cached price data from disk."""
        if self.price_cache_file.exists():
            try:
                with open(self.price_cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_minifig_cache(self):
        """Save minifigure cache to disk."""
        with open(self.minifig_cache_file, 'w') as f:
            json.dump(self.minifig_cache, f, indent=2)
    
    def _save_price_cache(self):
        """Save price cache to disk."""
        with open(self.price_cache_file, 'w') as f:
            json.dump(self.price_cache, f, indent=2)
    
    def get_minifig_with_cache(self, minifig_id: str, use_cache_only: bool = False) -> Optional[Dict]:
        """Get minifigure data with caching."""
        # Check cache first
        if minifig_id in self.minifig_cache:
            return self.minifig_cache[minifig_id]
        
        if use_cache_only:
            return None
        
        # Fetch from API
        try:
            item_data = self.get_item('MINIFIG', minifig_id)
            parts = self.get_minifigure_inventory(minifig_id)
            
            # Cache the result
            self.minifig_cache[minifig_id] = {
                'item_data': item_data,
                'parts': [asdict(p) for p in parts]
            }
            self._save_minifig_cache()
            
            return self.minifig_cache[minifig_id]
        except Exception as e:
            print(f"⚠️  Failed to fetch {minifig_id}: {e}")
            return None
    
    def get_price_with_cache(self, minifig_id: str, use_cache_only: bool = False) -> Optional[Dict]:
        """Get minifigure price guide with caching."""
        # Check cache first
        if minifig_id in self.price_cache:
            return self.price_cache[minifig_id]
        
        if use_cache_only:
            return None
        
        # Fetch from API
        try:
            price_data = self.get_price_guide('MINIFIG', minifig_id)
            
            # Cache the result (store timestamp for reference)
            self.price_cache[minifig_id] = {
                'data': price_data,
                'updated': datetime.datetime.now().isoformat()
            }
            self._save_price_cache()
            
            return self.price_cache[minifig_id]
        except Exception as e:
            return None
    
    def get_cached_minifig_ids(self) -> List[str]:
        """Load minifigure IDs from cache file."""
        if self.minifig_cache_file.exists():
            try:
                with open(self.minifig_cache_file, 'r') as f:
                    cache = json.load(f)
                    return sorted(list(cache.keys()))
            except Exception:
                return []
        return []
    
    def get_cache_status(self) -> Dict:
        """Get cache status information."""
        return {
            'minifig_count': len(self.minifig_cache),
            'minifig_cache_file': str(self.minifig_cache_file),
            'price_count': len(self.price_cache),
            'price_cache_file': str(self.price_cache_file),
        }
