"""Minifigure matching and building logic."""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from .parser import Part


# Common minifigure part categories based on Bricklink categorization
MINIFIG_CATEGORIES = {
    'head': ['Minifigure, Head', 'Minifig Head'],
    'headgear': ['Minifigure, Headgear', 'Minifig Headgear', 'Minifigure, Hair'],
    'torso': ['Minifigure, Torso', 'Minifig Torso'],
    'legs': ['Minifigure, Legs', 'Minifig Legs', 'Minifigure, Hips and Legs'],
    'accessories': ['Minifigure, Accessory', 'Minifig Accessory']
}


@dataclass
class Minifigure:
    """Represents a complete or partial minifigure."""
    head: Optional[Part] = None
    headgear: Optional[Part] = None
    torso: Optional[Part] = None
    legs: Optional[Part] = None
    accessories: List[Part] = None
    value: float = 0.0
    
    def __post_init__(self):
        if self.accessories is None:
            self.accessories = []
    
    def is_complete(self) -> bool:
        """Check if minifigure has all required parts."""
        # A complete minifigure needs at least head, torso, and legs
        return self.head is not None and self.torso is not None and self.legs is not None
    
    def completeness_score(self) -> float:
        """Calculate how complete this minifigure is (0-1)."""
        score = 0.0
        if self.head:
            score += 0.3
        if self.torso:
            score += 0.3
        if self.legs:
            score += 0.3
        if self.headgear:
            score += 0.1
        return score
    
    def __repr__(self):
        parts = []
        if self.head:
            parts.append(f"Head: {self.head.item_id}")
        if self.headgear:
            parts.append(f"Headgear: {self.headgear.item_id}")
        if self.torso:
            parts.append(f"Torso: {self.torso.item_id}")
        if self.legs:
            parts.append(f"Legs: {self.legs.item_id}")
        if self.accessories:
            parts.append(f"Accessories: {len(self.accessories)}")
        return f"Minifigure({', '.join(parts)}, value=${self.value:.2f})"


class MinifigBuilder:
    """Build complete minifigures from available parts."""
    
    def __init__(self, value_data: Optional[Dict[str, float]] = None):
        """Initialize the builder with optional value data."""
        self.value_data = value_data or {}
    
    def categorize_parts(self, parts: List[Part]) -> Dict[str, List[Part]]:
        """Categorize parts by their type."""
        categorized = {
            'head': [],
            'headgear': [],
            'torso': [],
            'legs': [],
            'accessories': [],
            'other': []
        }
        
        for part in parts:
            # Only process minifigure parts
            if part.item_type != 'P':  # P = Part
                continue
            
            part_name = (part.name or '').lower()
            category_name = (part.category_id or '').lower()
            
            categorized_flag = False
            
            # Try to categorize based on name and category
            if any(x in part_name for x in ['head', 'minifig head', 'minifigure head']) and \
               'headgear' not in part_name and 'hair' not in part_name:
                categorized['head'].append(part)
                categorized_flag = True
            elif any(x in part_name for x in ['hair', 'hat', 'helmet', 'headgear', 'minifig headgear']):
                categorized['headgear'].append(part)
                categorized_flag = True
            elif any(x in part_name for x in ['torso', 'minifig torso', 'minifigure torso']):
                categorized['torso'].append(part)
                categorized_flag = True
            elif any(x in part_name for x in ['legs', 'hips', 'minifig legs', 'minifigure legs']):
                categorized['legs'].append(part)
                categorized_flag = True
            elif any(x in part_name for x in ['accessory', 'weapon', 'tool']):
                categorized['accessories'].append(part)
                categorized_flag = True
            
            if not categorized_flag:
                categorized['other'].append(part)
        
        return categorized
    
    def build_minifigures(self, parts: List[Part]) -> List[Minifigure]:
        """Build all possible complete minifigures from available parts."""
        categorized = self.categorize_parts(parts)
        minifigures = []
        
        # Track which parts have been used
        used_heads = []
        used_torsos = []
        used_legs = []
        used_headgear = []
        
        # Build as many complete minifigures as possible
        for head in categorized['head']:
            for torso in categorized['torso']:
                for legs in categorized['legs']:
                    # Check if we have enough quantity of each part
                    head_key = (head.item_id, head.color_id)
                    torso_key = (torso.item_id, torso.color_id)
                    legs_key = (legs.item_id, legs.color_id)
                    
                    head_used = used_heads.count(head_key)
                    torso_used = used_torsos.count(torso_key)
                    legs_used = used_legs.count(legs_key)
                    
                    if head_used < head.qty and torso_used < torso.qty and legs_used < legs.qty:
                        minifig = Minifigure(head=head, torso=torso, legs=legs)
                        
                        # Try to add headgear if available
                        for headgear in categorized['headgear']:
                            headgear_key = (headgear.item_id, headgear.color_id)
                            headgear_used = used_headgear.count(headgear_key)
                            if headgear_used < headgear.qty:
                                minifig.headgear = headgear
                                used_headgear.append(headgear_key)
                                break
                        
                        # Calculate value
                        minifig.value = self._calculate_value(minifig)
                        
                        minifigures.append(minifig)
                        used_heads.append(head_key)
                        used_torsos.append(torso_key)
                        used_legs.append(legs_key)
        
        # Sort by value (highest first)
        minifigures.sort(key=lambda m: m.value, reverse=True)
        
        return minifigures
    
    def _calculate_value(self, minifig: Minifigure) -> float:
        """Calculate the estimated value of a minifigure."""
        value = 0.0
        
        if minifig.head:
            value += self.value_data.get(minifig.head.item_id, 0.5)
        if minifig.headgear:
            value += self.value_data.get(minifig.headgear.item_id, 0.3)
        if minifig.torso:
            value += self.value_data.get(minifig.torso.item_id, 1.0)
        if minifig.legs:
            value += self.value_data.get(minifig.legs.item_id, 0.8)
        
        for accessory in minifig.accessories:
            value += self.value_data.get(accessory.item_id, 0.2)
        
        return value
