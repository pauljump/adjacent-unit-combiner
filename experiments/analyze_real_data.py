#!/usr/bin/env python3
"""
Analyze REAL Manhattan listings for adjacent units
"""

import pandas as pd
import json
import re
from analyze_adjacency import AdjacencyAnalyzer


def parse_unit_number(unit_str):
    """Extract floor and position from unit number"""
    if pd.isna(unit_str) or not unit_str:
        return None, None

    unit_str = str(unit_str).strip()

    # Remove prefixes like "Apt", "Unit", "#", "Ph"
    unit_str = re.sub(r'^(Apt|Unit|Ph|#)\s+', '', unit_str)

    # Try patterns like "4D", "12C", "5F", "18I"
    match = re.match(r'(\d+)([A-Z])', unit_str)
    if match:
        floor = int(match.group(1))
        letter = match.group(2)
        position = ord(letter) - ord('A')
        return floor, position

    # Try patterns like "301", "1205", "201" (floor + position)
    if unit_str.isdigit():
        if len(unit_str) >= 3:
            floor = int(unit_str[:-2])
            position = int(unit_str[-2:])
            return floor, position
        elif len(unit_str) == 1:
            # Single digit like "3" - assume it's a position on floor 1
            floor = 1
            position = int(unit_str)
            return floor, position

    return None, None


# Load real data
print("Loading real Manhattan listings...")
df = pd.read_csv('experiments/manhattan_listings_real.csv')

print(f"Total listings: {len(df)}")
print(f"With units: {df['unit'].notna().sum()}")

# Convert to format our analyzer expects
listings = []
for _, row in df.iterrows():
    if pd.isna(row['unit']) or not row['unit']:
        continue

    floor, position = parse_unit_number(row['unit'])
    if floor is None or position is None:
        continue

    # Normalize address (remove unit from it)
    address = row['formatted_address']
    if pd.notna(row['unit']):
        # Remove unit-like patterns from address
        address = re.sub(r'\s+(Apt|Unit|#)\s+[\w\-/]+', '', address)
        address = re.sub(r'\s+Unit\s+\d+', '', address)

    listing = {
        "address": address.strip(),
        "unit": str(row['unit']),
        "floor": floor,
        "position": position,
        "beds": row['beds'] if pd.notna(row['beds']) else 0,
        "sqft": int(row['sqft']) if pd.notna(row['sqft']) else 500,
        "price": int(row['list_price']) if pd.notna(row['list_price']) else 0,
    }
    listings.append(listing)

print(f"\nParsed {len(listings)} listings with valid floor/unit numbers")

# Save parsed listings
with open('experiments/manhattan_parsed.json', 'w') as f:
    json.dump(listings, f, indent=2)

# Run adjacency analysis
analyzer = AdjacencyAnalyzer(listings)
pairs = analyzer.find_adjacent_pairs()

print(f"\n{'='*80}")
print(f"FOUND {len(pairs)} ADJACENT PAIRS!")
print(f"{'='*80}\n")

if pairs:
    # Show details
    for i, pair in enumerate(pairs[:10], 1):
        print(f"#{i}. {pair['building']}")
        print(f"    Units: {pair['unit_1']['unit']} + {pair['unit_2']['unit']}")
        print(f"    Type: {pair['adjacency']['description']} ({pair['adjacency']['confidence']*100:.0f}% confidence)")
        print(f"    Unit 1: {pair['unit_1']['beds']} beds, {pair['unit_1']['sqft']} sqft, ${pair['unit_1']['price']:,}")
        print(f"    Unit 2: {pair['unit_2']['beds']} beds, {pair['unit_2']['sqft']} sqft, ${pair['unit_2']['price']:,}")

        if pair['economics']['potential_savings'] > 0:
            print(f"    💰 Potential savings: ${pair['economics']['potential_savings']:,}")
        print()

    # Save results
    with open('experiments/manhattan_adjacent_pairs.json', 'w') as f:
        json.dump(pairs, f, indent=2)
    print(f"\nSaved {len(pairs)} pairs to experiments/manhattan_adjacent_pairs.json")
else:
    print("\nNo adjacent pairs found in this sample.")
    print("This is expected - only 50 listings across many buildings.")
    print("\nTo find pairs, we'd need:")
    print("  - More listings (500-1000+)")
    print("  - Focus on specific buildings with multiple listings")
