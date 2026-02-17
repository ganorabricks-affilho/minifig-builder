#!/usr/bin/env python3
"""
Get Minifigure Parts from BrickLink

Fetches the parts inventory for a minifigure by scraping BrickLink.
No API credentials needed - uses web scraping.

Usage:
    python3 src/get_minifig_parts.py col467
    python3 src/get_minifig_parts.py sw0001
    python3 src/get_minifig_parts.py sh034
"""

import sys
import argparse
import requests
import re
from typing import List, Dict


def get_minifig_parts(minifig_id: str) -> List[Dict]:
    """Fetch parts inventory by scraping BrickLink website.
    
    Parses the inventory table with structure:
    <TR class="IV_ITEM" ...>
      <TD ALIGN="CENTER">...[image]...</TD>
      <TD ALIGN="RIGHT">&nbsp;2&nbsp;</TD>
      <TD NOWRAP>&nbsp;<A HREF="...?P=30377&idColor=1">30377</A></TD>
      <TD><B>White Arm Mechanical, Battle Droid </B>...</TD>
      <TD ALIGN="RIGHT"></TD>
    </TR>
    """
    try:
        url = f"https://www.bricklink.com/catalogItemInv.asp?M={minifig_id}&viewCodes=Y&viewType=1"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        
        # Parse parts from the HTML
        parts = []
        
        # Pattern to match inventory item rows
        # Looking for: <TR class="IV_...IV_ITEM"...> with 5 TD cells
        # Cell 2: quantity (ALIGN="RIGHT")
        # Cell 3: part ID (in HREF link)
        # Cell 4: description (in <B> tag)
        
        # Match each TR with class containing "IV_ITEM"
        tr_pattern = r'<TR\s+class="[^"]*IV_ITEM[^"]*"[^>]*>(.*?)</TR>'
        tr_matches = re.findall(tr_pattern, html, re.DOTALL | re.IGNORECASE)
        
        print(f"\n🔍 Found {len(tr_matches)} inventory item rows\n")
        
        for tr_content in tr_matches:
            # Extract all TD cells from this row
            td_pattern = r'<TD[^>]*>(.*?)</TD>'
            td_cells = re.findall(td_pattern, tr_content, re.DOTALL | re.IGNORECASE)
            
            if len(td_cells) >= 4:
                # Cell index 1 (second cell): Quantity
                qty_match = re.search(r'(\d+)', td_cells[1])
                quantity = qty_match.group(1) if qty_match else '1'
                
                # Cell index 2 (third cell): Part ID
                part_id_match = re.search(r'HREF="[^"]*\?P=([0-9a-zA-Z]+)', td_cells[2], re.IGNORECASE)
                part_id = part_id_match.group(1) if part_id_match else ''
                
                # Cell index 3 (fourth cell): Description
                desc_match = re.search(r'<B>(.*?)</B>', td_cells[3], re.DOTALL)
                full_description = desc_match.group(1).strip() if desc_match else ''
                
                if part_id and full_description:
                    # Split description into color and part name
                    # Example: "White Arm Mechanical, Battle Droid "
                    parts_text = full_description.split(None, 1)
                    color = parts_text[0] if parts_text else ''
                    description = parts_text[1].strip() if len(parts_text) > 1 else full_description
                    
                    parts.append({
                        'part_id': part_id,
                        'description': description,
                        'quantity': quantity,
                        'color': color
                    })
        
        return parts
        
    except Exception as e:
        print(f"⚠️  Error fetching parts data: {e}")
        import traceback
        traceback.print_exc()
        return []


def display_parts_inventory(minifig_id: str, parts: List[Dict]):
    """Display parts inventory in a formatted way."""
    print(f"\n{'='*80}")
    print(f"PARTS INVENTORY: {minifig_id.upper()}")
    print(f"{'='*80}\n")
    
    if not parts:
        print("❌ No parts data available for this minifigure.")
        print("   The minifigure may not exist or inventory is not available.\n")
        return
    
    print(f"Total Parts: {len(parts)}\n")
    print(f"{'#':<4} {'Qty':<5} {'Part ID':<15} {'Color':<20} {'Description':<40}")
    print("-" * 85)
    
    for i, part in enumerate(parts, 1):
        part_id = part['part_id'][:14]
        quantity = part['quantity']
        color = part['color'][:19]
        description = part['description'][:39]
        
        print(f"{i:<4} {quantity:<5} {part_id:<15} {color:<20} {description:<40}")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Get BrickLink parts inventory for a minifigure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 src/get_minifig_parts.py col467
  python3 src/get_minifig_parts.py sw0001
  python3 src/get_minifig_parts.py sh034
        """
    )
    
    parser.add_argument(
        'fig_id',
        type=str,
        help='Minifigure ID (e.g., col467, sw0001, sh034)'
    )
    
    args = parser.parse_args()
    
    try:
        print(f"\n🔍 Fetching parts inventory for {args.fig_id}...")
        parts = get_minifig_parts(args.fig_id)
        display_parts_inventory(args.fig_id, parts)
        
        if parts:
            print("✅ Parts inventory retrieved successfully\n")
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
