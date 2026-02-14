#!/usr/bin/env python3
"""
API-Based Minifigure Finder

Uses BrickLink API to find which official minifigures you can build
from your parts inventory.

This approach:
- Uses cached minifigure data to avoid API calls
- Searches all cached minifigures efficiently
- More maintainable than binary database parsing
- Saves results to JSON by default

Usage (run from workspace root - minifig-builder folder):
    python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml
    python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml --output custom-results.json

Results are saved to: reports/buildable-minifigs.json (default)
"""

import xml.etree.ElementTree as ET
import json
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
from fetch_bricklink_minifig import BrickLinkAPI, MinifigPart


@dataclass
class InventoryPart:
    """Part in user's inventory."""
    part_id: str
    color_id: int
    quantity: int
    item_type: str
    price: float = 0.0
    remarks: str = ''


@dataclass
class MinifigMatch:
    """Minifigure match result."""
    minifig_id: str
    minifig_name: str
    year_released: Optional[int]
    category_name: str
    total_parts: int
    matched_parts: int
    missing_parts: int
    match_percentage: float
    can_build: bool
    missing_details: List[Dict]
    matched_details: List[Dict] = None
    price_data: Optional[Dict] = None


class CachedBrickLinkAPI(BrickLinkAPI):
    """BrickLink API with persistent disk cache."""
    
    def __init__(self, cache_dir: Path = None):
        super().__init__()
        if cache_dir is None:
            # Use root workspace directory for cache
            script_dir = Path(__file__).parent
            cache_dir = script_dir.parent / '.api_cache'
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
            except:
                return {}
        return {}
    
    def _load_price_cache(self) -> Dict:
        """Load cached price data from disk."""
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
            import datetime
            self.price_cache[minifig_id] = {
                'data': price_data,
                'updated': datetime.datetime.now().isoformat()
            }
            self._save_price_cache()
            
            return self.price_cache[minifig_id]
        except Exception as e:
            return None


class InventoryParser:
    """Parser for BrickLink XML inventory."""
    
    def __init__(self, xml_path: Path):
        self.xml_path = xml_path
        self.inventory: Dict[Tuple[str, int], InventoryPart] = {}
    
    def load(self) -> bool:
        """Load and parse XML inventory."""
        print(f"📂 Loading inventory: {self.xml_path.name}")
        
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            
            for item in root.findall('ITEM'):
                item_id = item.find('ITEMID').text
                item_type = item.find('ITEMTYPE').text
                color = int(item.find('COLOR').text)
                qty = int(item.find('QTY').text)
                price_elem = item.find('PRICE')
                price = float(price_elem.text) if price_elem is not None and price_elem.text else 0.0
                remarks_elem = item.find('REMARKS')
                remarks = remarks_elem.text if remarks_elem is not None and remarks_elem.text else ''
                
                if item_type in ['P', 'M']:
                    key = (item_id, color)
                    if key in self.inventory:
                        self.inventory[key].quantity += qty
                        # Keep first remarks if multiple entries
                        if not self.inventory[key].remarks and remarks:
                            self.inventory[key].remarks = remarks
                    else:
                        self.inventory[key] = InventoryPart(
                            part_id=item_id,
                            color_id=color,
                            quantity=qty,
                            item_type=item_type,
                            price=price,
                            remarks=remarks
                        )
            
            unique = len(self.inventory)
            total = sum(p.quantity for p in self.inventory.values())
            print(f"✅ Loaded: {unique:,} unique parts, {total:,} total pieces\n")
            return True
        except Exception as e:
            print(f"❌ Error loading inventory: {e}")
            return False
    
    def has_part(self, part_id: str, color_id: int, quantity: int = 1) -> Tuple[bool, int, str, float]:
        """Check if inventory has enough of a part. Returns (has_enough, available, remarks, price)."""
        key = (part_id, color_id)
        if key in self.inventory:
            inv_part = self.inventory[key]
            return (inv_part.quantity >= quantity, inv_part.quantity, inv_part.remarks, inv_part.price)
        return (False, 0, '', 0.0)


class MinifigureFinder:
    """Find buildable minifigures using BrickLink API."""
    
    def __init__(self, inventory: InventoryParser, api: CachedBrickLinkAPI):
        self.inventory = inventory
        self.api = api
    
    def check_minifig(self, minifig_id: str, use_cache_only: bool = False) -> Optional[MinifigMatch]:
        """Check if a minifigure can be built from inventory."""
        data = self.api.get_minifig_with_cache(minifig_id, use_cache_only)
        
        if not data:
            return None
        
        # Try to get price data from cache
        price_info = self.api.get_price_with_cache(minifig_id, use_cache_only)
        
        item_data = data['item_data']
        parts_data = data['parts']
        
        # Convert to MinifigPart objects
        parts = [MinifigPart(**p) for p in parts_data]
        
        # Filter to regular parts (not alternates/counterparts)
        regular_parts = [p for p in parts if not p.is_alternate and not p.is_counterpart]
        
        if not regular_parts:
            return None
        
        # Check each part
        matched = 0
        missing = []
        matched_parts = []
        
        for part in regular_parts:
            has_enough, available, remarks, price = self.inventory.has_part(
                part.part_id, part.color_id, part.quantity
            )
            
            if has_enough:
                matched += 1
                matched_parts.append({
                    'part_id': part.part_id,
                    'part_name': part.part_name,
                    'color_id': part.color_id,
                    'color_name': part.color_name,
                    'quantity': part.quantity,
                    'price': price,
                    'total_price': price * part.quantity,
                    'remarks': remarks
                })
            else:
                missing.append({
                    'part_id': part.part_id,
                    'part_name': part.part_name,
                    'color_id': part.color_id,
                    'color_name': part.color_name,
                    'needed': part.quantity,
                    'available': available,
                    'short_by': part.quantity - available,
                    'price': price,
                    'remarks': remarks if available > 0 else ''
                })
        
        total = len(regular_parts)
        match_pct = (matched / total * 100) if total > 0 else 0
        
        return MinifigMatch(
            minifig_id=minifig_id,
            minifig_name=item_data.get('name', 'Unknown'),
            year_released=item_data.get('year_released'),
            category_name=item_data.get('category_name', 'Unknown'),
            total_parts=total,
            matched_parts=matched,
            missing_parts=total - matched,
            match_percentage=match_pct,
            can_build=matched == total,
            missing_details=missing,
            matched_details=matched_parts,
            price_data=price_info
        )
    
    def search_minifigs(self, minifig_ids: List[str], use_cache_only: bool = False) -> List[MinifigMatch]:
        """Search multiple minifigures."""
        print(f"🔍 Checking {len(minifig_ids)} minifigures...")
        if use_cache_only:
            print("   (Using cached data only)")
        
        matches = []
        
        for i, minifig_id in enumerate(minifig_ids, 1):
            if i % 10 == 0 or i == len(minifig_ids):
                print(f"   Progress: {i}/{len(minifig_ids)}", end='\r')
            
            match = self.check_minifig(minifig_id, use_cache_only)
            if match:
                matches.append(match)
            
            # Rate limiting (only if not using cache)
            if not use_cache_only:
                time.sleep(0.15)
        
        print()  # New line
        matches.sort(key=lambda m: (m.match_percentage, m.year_released or 0), reverse=True)
        return matches


def get_cached_minifig_ids(cache_dir: Path = None) -> List[str]:
    """Load minifigure IDs from cache file."""
    if cache_dir is None:
        # Use root workspace directory for cache
        script_dir = Path(__file__).parent
        cache_dir = script_dir.parent / '.api_cache'
    minifig_cache_file = cache_dir / 'minifigures.json'
    if minifig_cache_file.exists():
        try:
            with open(minifig_cache_file, 'r') as f:
                cache = json.load(f)
                return sorted(list(cache.keys()))
        except:
            return []
    return []


def save_results_json(matches: List[MinifigMatch], output_file: Path):
    """Save match results to JSON file."""
    complete = [m for m in matches if m.can_build]
    incomplete = [m for m in matches if not m.can_build]
    
    # Convert to dictionaries with only necessary data
    def match_to_dict(match: MinifigMatch) -> Dict:
        d = asdict(match)
        
        # Extract 6-month average prices
        price_summary = None
        if d['price_data']:
            price_info = d['price_data'].get('data', {})
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
            'minifig_id': d['minifig_id'],
            'minifig_name': d['minifig_name'],
            'year_released': d['year_released'],
            'category_name': d['category_name'],
            'total_parts': d['total_parts'],
            'matched_parts': d['matched_parts'],
            'missing_parts': d['missing_parts'],
            'match_percentage': d['match_percentage'],
            'can_build': d['can_build'],
            'prices_6month_average': price_summary,
            'all_parts': d['matched_details'] if d['matched_details'] else [],
            'missing_details': d['missing_details']
        }
    
    output_data = {
        'summary': {
            'total_checked': len(matches),
            'complete_matches': len(complete),
            'incomplete_matches': len(incomplete)
        },
        'complete': [match_to_dict(m) for m in complete],
        'incomplete': [match_to_dict(m) for m in incomplete]
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")


def print_results(matches: List[MinifigMatch], complete_only: bool = False):
    """Print match results."""
    if not matches:
        print("\n❌ No matches found in checked minifigures.")
        print("   Tip: Check more minifigure IDs or expand the search list")
        return
    
    complete = [m for m in matches if m.can_build]
    partial = [m for m in matches if not m.can_build]
    
    print(f"\n{'='*80}")
    print(f"  MINIFIGURE BUILD ANALYSIS")
    print(f"{'='*80}")
    
    if complete:
        print(f"\n✅ COMPLETE MATCHES ({len(complete)} minifigures):")
        print(f"{'-'*80}")
        
        for match in complete[:20]:
            print(f"\n🎯 {match.minifig_id} - {match.minifig_name}")
            if match.year_released:
                print(f"   Year: {match.year_released}")
            print(f"   Category: {match.category_name}")
            print(f"   Parts: {match.total_parts} (100% match)")
            print(f"   Status: ✅ CAN BUILD NOW!")
            
            # Calculate total parts value
            if match.matched_details:
                parts_total = sum(p['total_price'] for p in match.matched_details)
                print(f"   💵 Parts Total Value: ${parts_total:.2f}")
            
            # Show price if available
            if match.price_data:
                price_info = match.price_data.get('data', {})
                if price_info:
                    # Show 6-month average prices (ordered listings)
                    ordered_new = price_info.get('ordered_new', {})
                    ordered_used = price_info.get('ordered_used', {})
                    avg_new = ordered_new.get('avg_price')
                    avg_used = ordered_used.get('avg_price')
                    
                    if avg_new or avg_used:
                        print(f"   💰 Minifig Market Value (6-Month Avg):")
                        if avg_new:
                            profit_new = avg_new - parts_total if match.matched_details else 0
                            print(f"      • New: ${avg_new:.2f} (profit: ${profit_new:+.2f})")
                        if avg_used:
                            profit_used = avg_used - parts_total if match.matched_details else 0
                            print(f"      • Used: ${avg_used:.2f} (profit: ${profit_used:+.2f})")
            
            if match.matched_details:
                print(f"\n   📦 Parts from your inventory:")
                for i, part_detail in enumerate(match.matched_details, 1):
                    qty_str = f"{part_detail['quantity']}x" if part_detail['quantity'] > 1 else "1x"
                    price_str = f"${part_detail['price']:.2f}" if part_detail['price'] > 0 else "$0.00"
                    total_str = f"${part_detail['total_price']:.2f}" if part_detail['total_price'] > 0 else "$0.00"
                    remarks_str = f" [{part_detail['remarks']}]" if part_detail['remarks'] else ""
                    print(f"      {i}. {qty_str} {part_detail['part_id']} - {part_detail['part_name']}")
                    print(f"         Color: {part_detail['color_name']} | Price: {price_str} ea. | Total: {total_str}{remarks_str}")
        
        if len(complete) > 20:
            print(f"\n   ... and {len(complete) - 20} more complete matches")
    
    if partial and not complete_only:
        print(f"\n⚠️  PARTIAL MATCHES ({len(partial)} minifigures):")
        print(f"{'-'*80}")
        print(f"   {len(partial)} additional minifigures have partial matches")
        print(f"   See JSON report for complete details: reports/buildable-minifigs.json")
    
    print(f"\n{'='*80}")


def main():
    parser = argparse.ArgumentParser(
        description='Find buildable LEGO minifigures from cached data'
    )
    parser.add_argument('inventory', type=Path, help='BrickLink XML inventory file')
    parser.add_argument('--output', type=Path, 
                        help='Save results to JSON file (default: reports/buildable-minifigs.json)')
    
    args = parser.parse_args()
    
    if not args.inventory.exists():
        print(f"❌ Inventory file not found: {args.inventory}")
        sys.exit(1)
    
    # Load inventory
    inventory = InventoryParser(args.inventory)
    if not inventory.load():
        sys.exit(1)
    
    # Initialize API
    try:
        api = CachedBrickLinkAPI()
        print("✅ BrickLink API initialized\n")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Get minifigure list from cache
    minifig_ids = get_cached_minifig_ids(api.cache_dir)
    if not minifig_ids:
        print("❌ No minifigures found in cache.")
        print("   Run: python3 cache_valuable_minifigs.py <theme> to populate the cache")
        sys.exit(1)
    print(f"📋 Using {len(minifig_ids)} minifigures from cache\n")
    
    # Find matches
    finder = MinifigureFinder(inventory, api)
    matches = finder.search_minifigs(minifig_ids, use_cache_only=True)
    
    # Display results
    print_results(matches, complete_only=False)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        # Default to reports/buildable-minifigs.json
        reports_dir = Path.cwd() / 'reports'
        reports_dir.mkdir(exist_ok=True)
        output_file = reports_dir / 'buildable-minifigs.json'
    
    # Save to JSON
    save_results_json(matches, output_file)


if __name__ == '__main__':
    main()
