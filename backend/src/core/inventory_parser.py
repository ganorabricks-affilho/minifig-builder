"""Parser for BrickLink XML inventory files."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class InventoryPart:
    """Part in user's inventory."""
    part_id: str
    color_id: int
    quantity: int
    item_type: str
    price: float = 0.0
    remarks: str = ''


class InventoryParser:
    """Parser for BrickLink XML inventory."""
    
    def __init__(self, xml_path: Path):
        """Initialize inventory parser."""
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
        """Check if inventory has enough of a part.
        
        Returns:
            (has_enough, available, remarks, price)
        """
        key = (part_id, color_id)
        if key in self.inventory:
            inv_part = self.inventory[key]
            return (inv_part.quantity >= quantity, inv_part.quantity, inv_part.remarks, inv_part.price)
        return (False, 0, '', 0.0)
    
    def get_stats(self) -> Dict:
        """Get inventory statistics."""
        return {
            'unique_parts': len(self.inventory),
            'total_pieces': sum(p.quantity for p in self.inventory.values()),
        }
