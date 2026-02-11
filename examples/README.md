# LEGO Minifigure Builder - Examples

This directory contains sample files to demonstrate the functionality of the minifig builder.

## Sample Files

### sample_inventory.xml
A complete inventory file with enough parts to build 3 complete minifigures:
- 2 heads (different types)
- 2 torsos (different types)  
- 2 legs (different colors of the same type)
- 1 headgear piece
- Some accessories and non-minifig parts

**Usage:**
```bash
python -m minifig_builder examples/sample_inventory.xml
```

### sample_values.json
Value data for the parts in the sample inventory, representing 6-month average prices in USD.

**Usage:**
```bash
python -m minifig_builder examples/sample_inventory.xml --values examples/sample_values.json
```

### single_minifig.xml
A minimal inventory with just enough parts for one complete minifigure (head, torso, legs).

**Usage:**
```bash
python -m minifig_builder examples/single_minifig.xml
```

### incomplete_inventory.xml
An incomplete inventory that cannot build any complete minifigures (only heads and torsos, no legs).
Demonstrates how the app handles incomplete inventories.

**Usage:**
```bash
python -m minifig_builder examples/incomplete_inventory.xml
```

## Creating Your Own Inventory Files

### From BrickStore
1. Open BrickStore application
2. Add your LEGO parts to the inventory
3. Export as Bricklink XML: File → Export → Bricklink XML
4. Use the exported file with this tool

### Value Data
To create your own value data file:
1. Visit Bricklink.com for each part
2. Find the 6-month average sale price
3. Create a JSON file mapping part IDs to prices:
```json
{
  "part_id_1": 1.25,
  "part_id_2": 0.50,
  "part_id_3": 2.00
}
```

## Expected Output

When running with value data, minifigures are sorted by total estimated value (highest first):

```
Loaded value data for 7 parts

Parsing inventory file: examples/sample_inventory.xml
Found 9 parts in inventory

Building minifigures...

✓ Found 3 complete minifigure(s)!

============================================================
Minifigure #1 (Estimated Value: $3.85)
============================================================
  Head:     3626bpb0002 (Color: 3)
            Minifigure, Head Smirk
  Torso:    973pb0256 (Color: 4)
            Minifigure, Torso Fire Logo
  Legs:     970c00 (Color: 7)
            Minifigure, Hips and Legs Plain
...
```
