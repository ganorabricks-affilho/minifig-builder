#!/usr/bin/env python3
"""
Test BrickLink Inventory Parameters

Discover what parameters work with catalogItemInv.asp
"""

import requests
import sys

def test_endpoint(minifig_id: str, extra_params: dict = None):
    """Test the inventory endpoint with different parameters."""
    base_params = {
        'M': minifig_id
    }
    
    if extra_params:
        base_params.update(extra_params)
    
    url = "https://www.bricklink.com/catalogItemInv.asp"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    print(f"\n{'='*80}")
    print(f"Testing: {url}")
    print(f"Parameters: {base_params}")
    print('='*80)
    
    try:
        response = requests.get(url, params=base_params, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        
        # Show some key indicators
        print(f"\n✓ Status: {response.status_code}")
        print(f"✓ Size: {len(html):,} bytes")
        print(f"✓ Final URL: {response.url}")
        
        # Look for key content markers
        if "Inventory of" in html:
            print("✓ Contains inventory data")
        if "Item No:" in html:
            print("✓ Contains item numbers")
        if "Qty" in html:
            print("✓ Contains quantities")
        
        # Save a sample with unique name based on parameters
        param_str = "_".join([f"{k}={v}" for k, v in base_params.items()])
        param_str = param_str.replace('/', '_').replace(':', '_')[:50]
        sample_file = f"/tmp/bricklink_inv_{param_str}.html"
        with open(sample_file, 'w') as f:
            f.write(html)
        print(f"\n💾 Saved full HTML to: {sample_file}")
        print("   Open this file to inspect the structure")
        
        return html
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    minifig_id = sys.argv[1] if len(sys.argv) > 1 else "sw0222"
    
    print(f"\n🔍 Testing BrickLink Inventory Endpoint")
    print(f"Minifig: {minifig_id}\n")
    
    # Test 1: Basic call
    print("\n📝 Test 1: Basic (just M parameter)")
    test_endpoint(minifig_id)
    
    # Test 2: With viewCodes
    print("\n📝 Test 2: With viewCodes=Y")
    test_endpoint(minifig_id, {'viewCodes': 'Y'})
    
    # Test 3: Try other common params
    print("\n📝 Test 3: Try viewType")
    test_endpoint(minifig_id, {'viewType': '1', 'viewCodes': 'Y'})
    
    print("\n📝 Test 4: Try colorID")
    test_endpoint(minifig_id, {'colorID': '0', 'viewCodes': 'Y'})
    
    print("\n📝 Test 5: Try itemType")
    test_endpoint(minifig_id, {'itemType': 'M', 'viewCodes': 'Y'})
    
    print("\n" + "="*80)
    print("💡 TIP: Compare the HTML files to see what changed")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
