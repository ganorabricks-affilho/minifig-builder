#!/usr/bin/env python3
"""
Update Minifigure Prices from BrickLink

Independently updates the price cache with latest 6-month average prices
from BrickLink API without fetching full minifigure data.

This allows you to keep minifigure data cached while periodically updating
prices on a separate schedule.

Usage (run from workspace root):
    python3 src/update_minifig_prices.py              # Update all cached minifigs
    python3 src/update_minifig_prices.py --minifig-list sw_figures.txt
    python3 src/update_minifig_prices.py --clear      # Clear price cache and rebuild
    python3 src/update_minifig_prices.py --list       # List all cached minifigs
"""

import json
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Set, List
from datetime import datetime
from fetch_bricklink_minifig import BrickLinkAPI


class PriceUpdater:
    """Updates minifigure prices in cache."""
    
    def __init__(self, cache_dir: Path = None):
        if cache_dir is None:
            # Use root workspace directory for cache
            script_dir = Path(__file__).parent
            cache_dir = script_dir.parent / '.api_cache'
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.minifig_cache_file = self.cache_dir / 'minifigures.json'
        self.price_cache_file = self.cache_dir / 'minifig_prices.json'
        
        self.api = None
        self.minifig_cache = {}
        self.price_cache = {}
    
    def load_caches(self):
        """Load both minifigure and price caches."""
        # Load minifigure cache to get list of minifigs
        if self.minifig_cache_file.exists():
            with open(self.minifig_cache_file, 'r') as f:
                self.minifig_cache = json.load(f)
        
        # Load price cache (may be empty)
        if self.price_cache_file.exists():
            with open(self.price_cache_file, 'r') as f:
                self.price_cache = json.load(f)
    
    def save_price_cache(self):
        """Save price cache to disk."""
        with open(self.price_cache_file, 'w') as f:
            json.dump(self.price_cache, f, indent=2)
    
    def get_minifig_ids_to_update(self, target_list: List[str] = None) -> Set[str]:
        """Get list of minifigure IDs to update."""
        if target_list:
            # Update specific minifigs from list
            return set(target_list)
        else:
            # Update all currently cached minifigs
            return set(self.minifig_cache.keys())
    
    def update_prices(self, minifig_ids: Set[str], clear_existing: bool = False):
        """Update prices for minifigures."""
        try:
            self.api = BrickLinkAPI()
        except ValueError as e:
            print(f"❌ Configuration Error:\n{e}")
            print("\nRun: python3 fetch_bricklink_minifig.py --setup")
            print("Then copy .env.example to .env and add your credentials.")
            return False
        
        if clear_existing:
            self.price_cache = {}
            print("🗑️  Cleared existing price cache")
        
        total = len(minifig_ids)
        updated = 0
        failed = 0
        
        print(f"\n📊 Updating {total} minifigures...")
        print("-" * 70)
        
        for i, minifig_id in enumerate(sorted(minifig_ids), 1):
            print(f"   {i:3}/{total}  Fetching prices for {minifig_id}...", end='\r')
            
            try:
                price_data = self.api.get_price_guide('MINIFIG', minifig_id)
                
                if price_data:
                    self.price_cache[minifig_id] = {
                        'data': price_data,
                        'updated': datetime.now().isoformat()
                    }
                    updated += 1
                else:
                    failed += 1
                
            except Exception as e:
                failed += 1
        
        print(" " * 70, end='\r')  # Clear line
        
        # Save updated cache
        self.save_price_cache()
        
        print("-" * 70)
        print(f"\n✅ Price update complete!")
        print(f"   Updated: {updated} minifigures")
        print(f"   Failed:  {failed} minifigures")
        print(f"   Cached file: {self.price_cache_file}")
        
        return True
    
    def list_cached_minifigs(self):
        """List all cached minifigures with price update status."""
        if not self.minifig_cache:
            print("❌ No minifigures cached. Run find_minifigs_api.py first.")
            return
        
        print(f"\n📦 Cached Minifigures ({len(self.minifig_cache)} total):")
        print("-" * 70)
        
        for minifig_id in sorted(self.minifig_cache.keys()):
            minifig_data = self.minifig_cache[minifig_id]
            minifig_name = minifig_data.get('item_data', {}).get('name', 'Unknown')
            
            has_price = minifig_id in self.price_cache
            price_status = "✅" if has_price else "⚪"
            
            if has_price:
                price_info = self.price_cache[minifig_id]
                updated = price_info.get('updated', 'Unknown')
                price_data = price_info.get('data', {})
                
                # Get 6-month average (ordered data)
                avg_new = price_data.get('ordered_new', {}).get('avg_price', 'N/A')
                avg_used = price_data.get('ordered_used', {}).get('avg_price', 'N/A')
                
                # Format prices
                if isinstance(avg_new, (int, float)):
                    price_str = f" - 6-Month: New=${avg_new:.2f}, Used=${avg_used:.2f}"
                else:
                    price_str = ""
                
                price_str += f" (Updated: {updated[:10]})"
            else:
                price_str = ""
            
            print(f"  {price_status}  {minifig_id:10s} - {minifig_name}{price_str}")
        
        print("-" * 70)
        not_priced = len(self.minifig_cache) - len(self.price_cache)
        print(f"\n📊 Summary:")
        print(f"   Total minifigs:  {len(self.minifig_cache)}")
        print(f"   With prices:     {len(self.price_cache)}")
        print(f"   Need updating:   {not_priced}")


def load_minifig_list(filepath: str) -> List[str]:
    """Load minifigure IDs from file."""
    minifigs = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip().upper()
                if line and not line.startswith('#'):
                    minifigs.append(line)
        return minifigs
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Update minifigure prices in cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 update_minifig_prices.py              # Update all cached minifigs
  python3 update_minifig_prices.py --minifig-list sw_figures.txt
  python3 update_minifig_prices.py --clear     # Clear and rebuild cache
  python3 update_minifig_prices.py --list      # Show cached minifigs
        """
    )
    
    parser.add_argument(
        '--minifig-list',
        type=str,
        help='File with minifigure IDs to update (one per line)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear price cache before updating'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all cached minifigures and their price status'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("💰 Minifigure Price Updater")
    print("=" * 70)
    
    updater = PriceUpdater()
    updater.load_caches()
    
    if args.list:
        updater.list_cached_minifigs()
        return
    
    if not updater.minifig_cache:
        print("\n❌ No minifigures cached.")
        print("   Run 'python3 find_minifigs_api.py' first to cache minifigures.")
        sys.exit(1)
    
    # Get minifigures to update
    if args.minifig_list:
        minifig_ids = set(load_minifig_list(args.minifig_list))
        if not minifig_ids:
            print("❌ No valid minifigure IDs found in file")
            sys.exit(1)
        print(f"📋 Loaded {len(minifig_ids)} minifigure IDs from file")
    else:
        minifig_ids = updater.get_minifig_ids_to_update()
        print(f"📋 Found {len(minifig_ids)} cached minifigures")
    
    # Update prices
    success = updater.update_prices(minifig_ids, clear_existing=args.clear)
    
    if not success:
        sys.exit(1)
    
    print("\n✨ Done! Prices cached in: .api_cache/minifig_prices.json (workspace root)")


if __name__ == "__main__":
    main()
