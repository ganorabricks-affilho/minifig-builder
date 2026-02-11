"""Command-line interface for the minifig builder."""

import argparse
import json
import sys
from pathlib import Path
from .parser import BricklinkXMLParser
from .minifig import MinifigBuilder


def load_value_data(filepath: str) -> dict:
    """Load value data from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Value data file not found: {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in value data file: {filepath}")
        return {}


def format_minifigure(minifig, index: int) -> str:
    """Format a minifigure for display."""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"Minifigure #{index + 1} (Estimated Value: ${minifig.value:.2f})")
    lines.append(f"{'='*60}")
    
    if minifig.head:
        lines.append(f"  Head:     {minifig.head.item_id} (Color: {minifig.head.color_id})")
        if minifig.head.name:
            lines.append(f"            {minifig.head.name}")
    
    if minifig.headgear:
        lines.append(f"  Headgear: {minifig.headgear.item_id} (Color: {minifig.headgear.color_id})")
        if minifig.headgear.name:
            lines.append(f"            {minifig.headgear.name}")
    
    if minifig.torso:
        lines.append(f"  Torso:    {minifig.torso.item_id} (Color: {minifig.torso.color_id})")
        if minifig.torso.name:
            lines.append(f"            {minifig.torso.name}")
    
    if minifig.legs:
        lines.append(f"  Legs:     {minifig.legs.item_id} (Color: {minifig.legs.color_id})")
        if minifig.legs.name:
            lines.append(f"            {minifig.legs.name}")
    
    if minifig.accessories:
        lines.append(f"  Accessories: {len(minifig.accessories)} item(s)")
        for acc in minifig.accessories:
            lines.append(f"    - {acc.item_id} (Color: {acc.color_id})")
    
    return '\n'.join(lines)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Build LEGO minifigures from Bricklink XML inventory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m minifig_builder input.xml
  python -m minifig_builder input.xml --values values.json
  python -m minifig_builder input.xml --max 5
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to Bricklink XML inventory file'
    )
    
    parser.add_argument(
        '--values', '-v',
        help='Path to JSON file with part values (6-month averages)',
        default=None
    )
    
    parser.add_argument(
        '--max', '-m',
        type=int,
        help='Maximum number of minifigures to display',
        default=None
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for results (JSON format)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Load value data if provided
    value_data = {}
    if args.values:
        value_data = load_value_data(args.values)
        print(f"Loaded value data for {len(value_data)} parts")
    
    # Parse XML file
    print(f"\nParsing inventory file: {args.input_file}")
    xml_parser = BricklinkXMLParser()
    try:
        parts = xml_parser.parse_file(args.input_file)
        print(f"Found {len(parts)} parts in inventory")
    except Exception as e:
        print(f"Error parsing XML file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Build minifigures
    print("\nBuilding minifigures...")
    builder = MinifigBuilder(value_data=value_data)
    minifigures = builder.build_minifigures(parts)
    
    if not minifigures:
        print("\nNo complete minifigures can be built from the available parts.")
        print("\nPart summary:")
        categorized = builder.categorize_parts(parts)
        for category, parts_list in categorized.items():
            if parts_list:
                print(f"  {category.capitalize()}: {len(parts_list)} part(s)")
        sys.exit(0)
    
    print(f"\n✓ Found {len(minifigures)} complete minifigure(s)!")
    
    # Limit output if requested
    display_count = len(minifigures)
    if args.max and args.max < len(minifigures):
        display_count = args.max
        print(f"  (Showing top {display_count} by value)")
    
    # Display minifigures
    for i in range(display_count):
        print(format_minifigure(minifigures[i], i))
    
    # Save to output file if requested
    if args.output:
        output_data = []
        for minifig in minifigures:
            data = {
                'value': minifig.value,
                'head': {'id': minifig.head.item_id, 'color': minifig.head.color_id} if minifig.head else None,
                'headgear': {'id': minifig.headgear.item_id, 'color': minifig.headgear.color_id} if minifig.headgear else None,
                'torso': {'id': minifig.torso.item_id, 'color': minifig.torso.color_id} if minifig.torso else None,
                'legs': {'id': minifig.legs.item_id, 'color': minifig.legs.color_id} if minifig.legs else None,
                'accessories': [{'id': a.item_id, 'color': a.color_id} for a in minifig.accessories]
            }
            output_data.append(data)
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n✓ Results saved to: {args.output}")
    
    print()


if __name__ == '__main__':
    main()
