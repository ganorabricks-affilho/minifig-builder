"""Minifigure finder logic."""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from fetch_bricklink_minifig import MinifigPart
from .cache_manager import CachedBrickLinkAPI
from .inventory_parser import InventoryParser


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


class MinifigureFinder:
    """Find buildable minifigures using BrickLink API."""
    
    def __init__(self, inventory: InventoryParser, api: CachedBrickLinkAPI):
        """Initialize minifigure finder."""
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
