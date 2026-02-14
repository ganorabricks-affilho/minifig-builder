#!/usr/bin/env python3
"""
Cache Valuable Minifigures Only

Iterates through all minifigure IDs from M.csv and only caches minifigures
where 6-month used sales average price > $3 (indicating resale value).

This is smart caching - only stores minifigs worth tracking economically.

Usage:
    python3 cache_valuable_minifigs.py              # Check all themes
    python3 cache_valuable_minifigs.py --theme sw   # Star Wars only
    python3 cache_valuable_minifigs.py --min-price 5  # Only price > $5
"""

import json
import sys
import time
import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import asdict
from fetch_bricklink_minifig import BrickLinkAPI
from bricklink_price import fetch_minifig_price


class ValueableMinifigCache:
    """Cache minifigures based on price criteria."""
    
    def _parse_themes_from_csv(self) -> Dict:
        """Parse themes and minifig IDs from M.csv file."""
        csv_path = Path(__file__).parent.parent / 'brickstore-data' / 'M.csv'
        
        if not csv_path.exists():
            raise FileNotFoundError(
                f"M.csv not found at {csv_path}\n"
                "Run: python3 src/download_brickstore_data.py to download it."
            )
        
        themes = {}
        prefix_pattern = re.compile(r'^[A-Za-z]+')
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)  # Skip header
            next(reader)  # Skip empty line
            
            for row in reader:
                if len(row) < 3:
                    continue
                
                minifig_id = row[2].strip()
                category_name = row[1].strip()
                
                # Extract theme prefix using regex
                match = prefix_pattern.match(minifig_id)
                if not match:
                    continue
                
                prefix = match.group().lower()
                
                # Initialize theme if not seen before
                if prefix not in themes:
                    # Derive simple theme name from category
                    theme_name = category_name.split(' / ')[0]
                    themes[prefix] = {
                        'ids': [],
                        'name': theme_name
                    }
                
                # Add ID to theme (keep original case for BrickLink API)
                themes[prefix]['ids'].append(minifig_id)
        
        return themes
    
    def __init__(self, cache_dir: Path = None, min_price: float = 3.0):
        if cache_dir is None:
            # Use root workspace directory for cache
            script_dir = Path(__file__).parent
            cache_dir = script_dir.parent / '.api_cache'
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.minifig_cache_file = self.cache_dir / 'minifigures.json'
        self.price_cache_file = self.cache_dir / 'minifig_prices.json'
        self.min_price = min_price
        
        # Parse themes from CSV
        self._themes = self._parse_themes_from_csv()
        
        self.api = BrickLinkAPI()
        self.minifig_cache = self._load_minifig_cache()
        self.price_cache = self._load_price_cache()
        
        self.checked = 0
        self.valid = 0
        self.cached = 0
        self.valuable = 0
        self.skipped = 0
    
    def _load_minifig_cache(self) -> Dict:
        """Load existing minifigure cache."""
        if self.minifig_cache_file.exists():
            try:
                with open(self.minifig_cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _load_price_cache(self) -> Dict:
        """Load existing price cache."""
        if self.price_cache_file.exists():
            try:
                with open(self.price_cache_file, 'r') as f:
                    return json.load(f)
            except:
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
    
    def minifig_exists(self, minifig_id: str) -> Tuple[bool, Dict]:
        """Check if minifigure exists in BrickLink and return item data."""
        try:
            item = self.api.get_item('MINIFIG', minifig_id)
            return bool(item), item if item else {}
        except:
            return False, {}
    
    def get_price_data(self, minifig_id: str) -> Dict:
        """Get price guide data for a minifigure."""
        return fetch_minifig_price(self.api, minifig_id)
    
    def get_minifig_parts(self, minifig_id: str) -> List[Dict]:
        """Get parts list for a minifigure."""
        try:
            parts = self.api.get_minifigure_inventory(minifig_id)
            return [asdict(p) for p in parts] if parts else []
        except:
            return []
    
    def is_valuable(self, price_data: Dict, price_field: str = 'ordered_used') -> Tuple[bool, float]:
        """Check if minifigure meets price criteria."""
        if price_field not in price_data:
            return False, 0
        
        avg_price = price_data[price_field].get('avg_price', 0)
        return avg_price >= self.min_price, avg_price
    
    def cache_theme(self, theme: str) -> None:
        """Cache valuable minifigures from a specific theme."""
        theme_lower = theme.lower()
        
        if theme_lower not in self._themes:
            print(f"❌ Unknown theme: {theme}")
            print(f"   Available themes: {', '.join(sorted(self._themes.keys()))}")
            return
        
        theme_data = self._themes[theme_lower]
        theme_name = theme_data['name']
        minifig_ids = theme_data['ids']
        
        print(f"\n📊 Caching {theme_name} minifigures ({len(minifig_ids)} IDs from CSV)...")
        print(f"   Filtering for avg_price > ${self.min_price}")
        print("-" * 70)
        
        for minifig_id in minifig_ids:
            self.checked += 1
            
            # Skip if already cached
            if minifig_id in self.minifig_cache:
                self.skipped += 1
                continue
            
            # Show progress
            if self.checked % 50 == 0:
                print(f"   Checked: {self.checked} | Valid: {self.valid} | Cached: {self.cached} | Valuable: {self.valuable}")
            
            # Check if exists
            exists, item_data = self.minifig_exists(minifig_id)
            if not exists:
                continue
            
            self.valid += 1
            
            # Get price data
            price_data = self.get_price_data(minifig_id)
            
            if not price_data:
                continue
            
            # Check if meets price criteria
            is_valuable, avg_price = self.is_valuable(price_data)
            
            if is_valuable:
                self.valuable += 1
                
                # Fetch minifigure parts
                parts = self.get_minifig_parts(minifig_id)
                
                # Cache minifigure data (item_data + parts)
                self.minifig_cache[minifig_id] = {
                    'item_data': item_data,
                    'parts': parts
                }
                
                # Cache the price
                self.price_cache[minifig_id] = {
                    'data': price_data,
                    'updated': datetime.now().isoformat()
                }
                self.cached += 1
                
                # Get minifig name
                minifig_name = item_data.get('name', 'Unknown')
                parts_count = len(parts)
                
                condition = 'Used' if 'ordered_used' in price_data else 'New'
                print(f"✅ {minifig_id} - ${avg_price:.2f} ({condition}) - {parts_count} parts - {minifig_name[:35]}")
                
                # Save periodically
                if self.cached % 10 == 0:
                    self._save_minifig_cache()
                    self._save_price_cache()
            
            # Rate limiting
            time.sleep(0.15)
        
        print("-" * 70)
    
    def summarize(self) -> None:
        """Print summary of caching session."""
        print("\n" + "=" * 70)
        print("  CACHING SUMMARY")
        print("=" * 70)
        print(f"Minifigures checked:    {self.checked}")
        print(f"Already cached (skipped): {self.skipped}")
        print(f"Valid minifigures:      {self.valid}")
        print(f"Valuable (>${self.min_price}):       {self.valuable}")
        print(f"Cached minifigures:     {self.cached}")
        print(f"Minifigure cache:       {self.minifig_cache_file}")
        print(f"Price cache:            {self.price_cache_file}")
        print("=" * 70)
        
        if self.cached > 0:
            self._save_minifig_cache()
            self._save_price_cache()
            print(f"\n✅ Cached {self.cached} valuable minifigures:")
            print(f"   • Minifigure data (item details + parts list)")
            print(f"   • Price data (6-month + current market prices)")
        else:
            print("\n⚠️  No valuable minifigures found matching criteria")


def main():
    parser = argparse.ArgumentParser(
        description="Cache only valuable minifigures (resale value > $2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cache_valuable_minifigs.py                    # All themes from M.csv
  python3 cache_valuable_minifigs.py --theme sw         # Star Wars only
  python3 cache_valuable_minifigs.py --theme SW         # Case-insensitive
  python3 cache_valuable_minifigs.py --min-price 5      # Only > $5 value
  python3 cache_valuable_minifigs.py --theme hp sh cas  # Multiple themes
        """
    )
    
    parser.add_argument(
        '--theme',
        action='append',
        dest='themes',
        help='Theme(s) to cache (e.g., sw, hp, cas). Themes auto-discovered from M.csv'
    )
    parser.add_argument(
        '--min-price',
        type=float,
        default=2.0,
        help='Minimum average price to cache (default: $2.00)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("💰 Valuable Minifigure Cache")
    print("=" * 70)
    
    cacher = ValueableMinifigCache(min_price=args.min_price)
    
    # Normalize theme names to lowercase
    if args.themes:
        themes_to_cache = [t.lower() for t in args.themes]
    else:
        themes_to_cache = sorted(cacher._themes.keys())
    
    for theme in themes_to_cache:
        cacher.cache_theme(theme)
    
    cacher.summarize()
    
    print("\n💡 Next steps:")
    print("   python3 update_minifig_prices.py --list  # View all cached prices")
    print("   python3 find_minifigs_api.py ganorabricks-store.xml --use-cache-only  # Find buildable")


if __name__ == "__main__":
    main()
