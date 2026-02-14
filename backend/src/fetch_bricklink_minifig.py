#!/usr/bin/env python3
"""
BrickLink API Minifigure Parser

Fetches minifigure inventory data directly from BrickLink API.

Prerequisites:
    - BrickLink API credentials (Consumer Key, Consumer Secret, Token, Token Secret)
    - Set as environment variables or in .env file

Environment Variables:
    BRICKLINK_CONSUMER_KEY
    BRICKLINK_CONSUMER_SECRET
    BRICKLINK_TOKEN
    BRICKLINK_TOKEN_SECRET

Usage:
    python3 fetch_bricklink_minifig.py SH0031
    python3 fetch_bricklink_minifig.py SH0031 --output json
    python3 fetch_bricklink_minifig.py SH0031 --output csv
"""

import sys
import os
import json
import csv
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from requests_oauthlib import OAuth1Session
import requests
from urllib.parse import urlencode


@dataclass
class MinifigPart:
    """Represents a part in a minifigure's inventory."""
    part_id: str
    part_name: str
    color_id: int
    color_name: str
    quantity: int
    is_alternate: bool
    is_counterpart: bool
    is_extra: bool
    is_spare: bool


class BrickLinkAPI:
    """BrickLink API client with OAuth1 authentication."""
    
    BASE_URL = "https://api.bricklink.com/api/store/v1"
    
    def __init__(self):
        """Initialize BrickLink API client."""
        # Try to load from environment
        self.consumer_key = os.getenv('BRICKLINK_CONSUMER_KEY')
        self.consumer_secret = os.getenv('BRICKLINK_CONSUMER_SECRET')
        self.token = os.getenv('BRICKLINK_TOKEN')
        self.token_secret = os.getenv('BRICKLINK_TOKEN_SECRET')
        
        # Try to load from .env file if not in environment
        if not all([self.consumer_key, self.consumer_secret, self.token, self.token_secret]):
            self._load_from_env_file()
        
        if not all([self.consumer_key, self.consumer_secret, self.token, self.token_secret]):
            raise ValueError(
                "BrickLink API credentials not found!\n\n"
                "Please set environment variables:\n"
                "  BRICKLINK_CONSUMER_KEY\n"
                "  BRICKLINK_CONSUMER_SECRET\n"
                "  BRICKLINK_TOKEN\n"
                "  BRICKLINK_TOKEN_SECRET\n\n"
                "Or create a .env file with these values.\n\n"
                "Get your API credentials from: https://www.bricklink.com/v2/api/register_consumer.page"
            )
        
        self.session = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.token,
            resource_owner_secret=self.token_secret
        )
        
        # Cache for API responses
        self.color_cache: Dict[int, Dict] = {}
        self.item_cache: Dict[str, Dict] = {}
    
    def _load_from_env_file(self):
        """Try to load credentials from .env file."""
        # Look for .env in the root workspace directory
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent.parent  # Go up to project root
        env_file = root_dir / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        
                        if key == 'BRICKLINK_CONSUMER_KEY':
                            self.consumer_key = value
                        elif key == 'BRICKLINK_CONSUMER_SECRET':
                            self.consumer_secret = value
                        elif key == 'BRICKLINK_TOKEN':
                            self.token = value
                        elif key == 'BRICKLINK_TOKEN_SECRET':
                            self.token_secret = value
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make an authenticated API request."""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('meta', {}).get('code') != 200:
                error_msg = data.get('meta', {}).get('message', 'Unknown error')
                raise Exception(f"BrickLink API error: {error_msg}")
            
            return data.get('data', {})
            
        except Exception as e:
            raise Exception(f"API request failed: {e}")
    
    def get_item(self, item_type: str, item_id: str) -> Dict:
        """Get item details."""
        cache_key = f"{item_type}:{item_id}"
        
        if cache_key in self.item_cache:
            return self.item_cache[cache_key]
        
        endpoint = f"/items/{item_type}/{item_id}"
        data = self._make_request(endpoint)
        
        self.item_cache[cache_key] = data
        time.sleep(0.1)  # Rate limiting
        
        return data
    
    def get_color(self, color_id: int) -> Dict:
        """Get color details."""
        if color_id in self.color_cache:
            return self.color_cache[color_id]
        
        endpoint = f"/colors/{color_id}"
        data = self._make_request(endpoint)
        
        self.color_cache[color_id] = data
        time.sleep(0.1)  # Rate limiting
        
        return data
    
    def get_subsets(self, item_type: str, item_id: str) -> List[Dict]:
        """Get subsets/inventory for an item."""
        endpoint = f"/items/{item_type}/{item_id}/subsets"
        data = self._make_request(endpoint)
        
        return data if isinstance(data, list) else []
    
    def get_price_guide(self, item_type: str, item_id: str, color_id: int = 0) -> Dict:
        """Fetch price guide data by scraping BrickLink website.
        
        Returns data structure with price info for each condition/time combination.
        """
        try:
            # Map item type to BrickLink letter code
            type_map = {
                'PART': 'P',
                'MINIFIG': 'M',
                'SET': 'S',
                'BOOK': 'B',
                'GEAR': 'G',
                'INSTRUCTION': 'I',
                'CATALOG': 'C',
                'ORIGINAL_BOX': 'O'
            }
            type_letter = type_map.get(item_type, item_type[0])
            
            params = {
                'a': type_letter,
                'itemID': item_id,
                'colorID': color_id,
                'vcID': '1',  # USD
                'viewExclude': 'Y',
                'ajView': 'Y'  # AJAX view only
            }
            
            url = "https://www.bricklink.com/priceGuideSummary.asp"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            # Fetch the page
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            html = response.text
            
            # Extract all prices from the HTML
            price_pattern = r'US \$([0-9,.]+)'
            prices = [float(p.replace(',', '')) for p in re.findall(price_pattern, html)]
            
            # Extract all quantities/lots from before prices
            # Numbers appear in pattern: &nbsp;{number}&nbsp;</TD>
            number_pattern = r'&nbsp;(\d+)&nbsp;</TD>'
            numbers = [int(n) for n in re.findall(number_pattern, html)]
            
            if len(prices) < 16 or len(numbers) < 8:
                return {}
            
            # Structure: 4 rows (2 sections × 2 conditions)
            # Each row has: lots, quantity, 4 prices (min, avg, qty_avg, max)
            # Total numbers: 2 cols × 4 rows = 8
            # Total prices: 4 prices × 4 rows = 16
            
            result = {
                'ordered_new': {
                    'lots': numbers[0],
                    'quantity': numbers[1],
                    'min_price': prices[0],
                    'avg_price': prices[1],
                    'qty_avg_price': prices[2],
                    'max_price': prices[3]
                },
                'ordered_used': {
                    'lots': numbers[2],
                    'quantity': numbers[3],
                    'min_price': prices[4],
                    'avg_price': prices[5],
                    'qty_avg_price': prices[6],
                    'max_price': prices[7]
                },
                'inventory_new': {
                    'lots': numbers[4],
                    'quantity': numbers[5],
                    'min_price': prices[8],
                    'avg_price': prices[9],
                    'qty_avg_price': prices[10],
                    'max_price': prices[11]
                },
                'inventory_used': {
                    'lots': numbers[6],
                    'quantity': numbers[7],
                    'min_price': prices[12],
                    'avg_price': prices[13],
                    'qty_avg_price': prices[14],
                    'max_price': prices[15]
                }
            }
            
            return result
            
        except Exception as e:
            return {}
    
    def _parse_price_guide(self, data: Dict) -> Dict:
        """Legacy method - no longer needed but kept for compatibility."""
        return data
    
    def get_minifigure_inventory(self, minifig_id: str) -> List[MinifigPart]:
        """Get complete inventory for a minifigure with all details."""
        print(f"🔍 Fetching inventory for {minifig_id}...")
        
        # Get subsets (parts)
        subsets = self.get_subsets('MINIFIG', minifig_id)
        
        if not subsets:
            return []
        
        parts = []
        total = len(subsets)
        
        for i, entry in enumerate(subsets, 1):
            print(f"   Fetching part details... {i}/{total}", end='\r')
            
            # Extract data from entry - entries already contain full info from subsets API
            entries_list = entry.get('entries', [])
            
            for item_entry in entries_list:
                item_info = item_entry.get('item', {})
                part_no = item_info.get('no', 'Unknown')
                part_type = item_info.get('type', 'PART')
                part_name = item_info.get('name', 'Unknown Part')
                
                color_id = item_entry.get('color_id', 0)
                quantity = item_entry.get('quantity', 1)
                is_alternate = item_entry.get('is_alternate', False)
                is_counterpart = item_entry.get('is_counterpart', False)
                is_extra = item_entry.get('extra_quantity', 0) > 0
                is_spare = item_entry.get('is_spare', False)
                
                # Get color name (if color_id is valid)
                color_name = 'Not Applicable'
                if color_id > 0:
                    try:
                        color_data = self.get_color(color_id)
                        color_name = color_data.get('color_name', f'Color {color_id}')
                    except Exception as e:
                        color_name = f'Color {color_id}'
                
                parts.append(MinifigPart(
                    part_id=part_no,
                    part_name=part_name,
                    color_id=color_id,
                    color_name=color_name,
                    quantity=quantity,
                    is_alternate=is_alternate,
                    is_counterpart=is_counterpart,
                    is_extra=is_extra,
                    is_spare=is_spare
                ))
        
        print()  # New line after progress
        return parts


def print_minifigure_info(minifig_id: str, minifig_data: Dict, parts: List[MinifigPart]):
    """Pretty print minifigure information."""
    print("\n" + "="*70)
    print(f"🧱 Minifigure: {minifig_id} - {minifig_data.get('name', 'Unknown')}")
    print("="*70)
    print(f"Category: {minifig_data.get('category_name', 'Unknown')}")
    
    year = minifig_data.get('year_released')
    if year:
        print(f"Year: {year}")
    
    weight = minifig_data.get('weight')
    if weight:
        print(f"Weight: {weight}g")
    
    print(f"Total Parts: {len(parts)}")
    print("\n" + "-"*70)
    print("Parts List:")
    print("-"*70)
    
    for i, part in enumerate(parts, 1):
        flags = []
        if part.is_alternate:
            flags.append('ALT')
        if part.is_counterpart:
            flags.append('CP')
        if part.is_extra:
            flags.append('EXTRA')
        if part.is_spare:
            flags.append('SPARE')
        
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        
        print(f"{i:2}. {part.quantity:2}x {part.part_id:15s} - {part.part_name}")
        print(f"     Color: {part.color_name:20s} (#{part.color_id:3d}){flag_str}")


def export_to_json(minifig_id: str, minifig_data: Dict, parts: List[MinifigPart], output_file: str):
    """Export minifigure data to JSON."""
    data = {
        'minifig_id': minifig_id,
        'minifig_name': minifig_data.get('name', 'Unknown'),
        'category': minifig_data.get('category_name', 'Unknown'),
        'year_released': minifig_data.get('year_released'),
        'weight': minifig_data.get('weight'),
        'total_parts': len(parts),
        'parts': [
            {
                'part_id': p.part_id,
                'part_name': p.part_name,
                'color_id': p.color_id,
                'color_name': p.color_name,
                'quantity': p.quantity,
                'is_alternate': p.is_alternate,
                'is_counterpart': p.is_counterpart,
                'is_extra': p.is_extra,
                'is_spare': p.is_spare
            }
            for p in parts
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_file}")


def export_to_csv(parts: List[MinifigPart], output_file: str):
    """Export minifigure parts to CSV."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Part ID', 'Part Name', 'Color ID', 'Color Name', 
                        'Quantity', 'Alternate', 'Counterpart', 'Extra', 'Spare'])
        
        for part in parts:
            writer.writerow([
                part.part_id,
                part.part_name,
                part.color_id,
                part.color_name,
                part.quantity,
                part.is_alternate,
                part.is_counterpart,
                part.is_extra,
                part.is_spare
            ])
    
    print(f"\n💾 Saved to: {output_file}")


def create_env_template():
    """Create a .env.example file with instructions."""
    template = """# BrickLink API Credentials
# Get your credentials from: https://www.bricklink.com/v2/api/register_consumer.page

BRICKLINK_CONSUMER_KEY=your_consumer_key_here
BRICKLINK_CONSUMER_SECRET=your_consumer_secret_here
BRICKLINK_TOKEN=your_token_here
BRICKLINK_TOKEN_SECRET=your_token_secret_here
"""
    
    with open('.env.example', 'w') as f:
        f.write(template)
    
    print("📝 Created .env.example file")
    print("   Copy it to .env and add your BrickLink API credentials")


def main():
    """Main execution."""
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_bricklink_minifig.py <MINIFIG_ID> [--output json|csv]")
        print("Example: python3 fetch_bricklink_minifig.py SH0031")
        print("Example: python3 fetch_bricklink_minifig.py SH0031 --output json")
        print("\nSetup:")
        print("  1. Get API credentials from: https://www.bricklink.com/v2/api/register_consumer.page")
        print("  2. Set environment variables or create .env file")
        print("  3. Run: python3 fetch_bricklink_minifig.py --setup  (to create .env.example)")
        sys.exit(1)
    
    if sys.argv[1] == '--setup':
        create_env_template()
        sys.exit(0)
    
    minifig_id = sys.argv[1].upper()
    output_format = None
    
    if len(sys.argv) > 2 and sys.argv[2] == '--output':
        if len(sys.argv) > 3:
            output_format = sys.argv[3].lower()
    
    print("="*70)
    print("🧱 BrickLink Minifigure Fetcher")
    print("="*70)
    
    try:
        # Initialize API client
        print("\n🔐 Authenticating with BrickLink API...")
        api = BrickLinkAPI()
        
        # Get minifigure info
        print(f"📦 Fetching minifigure: {minifig_id}")
        minifig_data = api.get_item('MINIFIG', minifig_id)
        
        # Get inventory
        parts = api.get_minifigure_inventory(minifig_id)
        
        if not parts:
            print(f"\n⚠️  No parts found for minifigure {minifig_id}")
            print("   This minifigure may not have inventory data available.")
            sys.exit(1)
        
        print(f"✅ Found {len(parts)} parts")
        
        # Display information
        print_minifigure_info(minifig_id, minifig_data, parts)
        
        # Export if requested
        if output_format == 'json':
            export_to_json(minifig_id, minifig_data, parts, f"{minifig_id}_parts.json")
        elif output_format == 'csv':
            export_to_csv(parts, f"{minifig_id}_parts.csv")
        
        print("\n✨ Done!")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error:\n{e}")
        print("\nRun: python3 fetch_bricklink_minifig.py --setup")
        print("Then copy .env.example to .env and add your credentials.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
