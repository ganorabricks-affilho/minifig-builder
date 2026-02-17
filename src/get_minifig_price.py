#!/usr/bin/env python3
"""
Get Minifigure Price from BrickLink

Fetches current price guide data for a minifigure by scraping BrickLink.
No API credentials needed - uses web scraping.

Usage:
    python3 src/get_minifig_price.py col467
    python3 src/get_minifig_price.py sw0001
    python3 src/get_minifig_price.py sh034
"""

import sys
import argparse
import requests
import re
from typing import Dict


def get_minifig_price(minifig_id: str) -> Dict:
    """Fetch price guide data by scraping BrickLink website."""
    try:
        params = {
            'a': 'M',  # Minifigure type
            'itemID': minifig_id,
            'colorID': 0,
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
        number_pattern = r'&nbsp;(\d+)&nbsp;</TD>'
        numbers = [int(n) for n in re.findall(number_pattern, html)]
        
        if len(prices) < 16 or len(numbers) < 8:
            return {}
        
        # Structure: 4 rows (2 sections × 2 conditions)
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
        print(f"⚠️  Error fetching price data: {e}")
        return {}


def format_price_section(title: str, data: Dict) -> str:
    """Format a price section nicely."""
    if not data:
        return f"{title}: No data available"
    
    lines = [
        f"{title}:",
        f"  Lots: {data['lots']:,} | Quantity: {data['quantity']:,}",
        f"  Min:     ${data['min_price']:>8.2f}",
        f"  Average: ${data['avg_price']:>8.2f}",
        f"  Qty Avg: ${data['qty_avg_price']:>8.2f}",
        f"  Max:     ${data['max_price']:>8.2f}"
    ]
    return "\n".join(lines)


def display_price_guide(minifig_id: str, price_data: Dict):
    """Display price guide in a formatted way."""
    print(f"\n{'='*80}")
    print(f"PRICE GUIDE: {minifig_id.upper()}")
    print(f"{'='*80}\n")
    
    if not price_data:
        print("❌ No price data available for this minifigure.")
        print("   The minifigure may not exist or has no price history.\n")
        return
    
    # Past 6 Months (Sold Items)
    print("📊 PAST 6 MONTHS (Sold Items)")
    print("-" * 80)
    print(format_price_section("New Condition", price_data.get('ordered_new', {})))
    print()
    print(format_price_section("Used Condition", price_data.get('ordered_used', {})))
    print()
    
    # Current Inventory (For Sale)
    print("🏪 CURRENT INVENTORY (For Sale)")
    print("-" * 80)
    print(format_price_section("New Condition", price_data.get('inventory_new', {})))
    print()
    print(format_price_section("Used Condition", price_data.get('inventory_used', {})))
    print()
    
    # Summary
    avg_used = price_data.get('ordered_used', {}).get('avg_price', 0)
    avg_new = price_data.get('ordered_new', {}).get('avg_price', 0)
    
    if avg_used > 0 or avg_new > 0:
        print("💰 QUICK SUMMARY")
        print("-" * 80)
        if avg_used > 0:
            print(f"  6-Month Average (Used): ${avg_used:.2f}")
        if avg_new > 0:
            print(f"  6-Month Average (New):  ${avg_new:.2f}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Get BrickLink price guide for a minifigure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 src/get_minifig_price.py col467
  python3 src/get_minifig_price.py sw0001
  python3 src/get_minifig_price.py sh034
        """
    )
    
    parser.add_argument(
        'fig_id',
        type=str,
        help='Minifigure ID (e.g., col467, sw0001, sh034)'
    )
    
    args = parser.parse_args()
    
    try:
        print(f"\n🔍 Fetching price data for {args.fig_id}...")
        price_data = get_minifig_price(args.fig_id)
        display_price_guide(args.fig_id, price_data)
        
        if price_data:
            print("✅ Price data retrieved successfully\n")
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
