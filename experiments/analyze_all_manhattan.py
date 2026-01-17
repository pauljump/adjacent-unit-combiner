#!/usr/bin/env python3
"""
Analyze ALL Manhattan listings for adjacent units
"""

import pandas as pd
import json
import re
from analyze_adjacency import AdjacencyAnalyzer
from collections import Counter

def parse_unit_number(unit_str):
    """Extract floor and position from unit number"""
    if pd.isna(unit_str) or not unit_str:
        return None, None

    unit_str = str(unit_str).strip()

    # Remove prefixes like "Apt", "Unit", "#", "Ph"
    unit_str = re.sub(r'^(Apt|Unit|Ph|#)\s+', '', unit_str)

    # Try patterns like "4D", "12C", "5F", "18I"
    match = re.match(r'(\d+)([A-Z])$', unit_str)
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


print("=" * 80)
print("ANALYZING ALL MANHATTAN LISTINGS FOR ADJACENT UNITS")
print("=" * 80)
print()

# Load data
print("Loading 7,214 Manhattan listings...")
df = pd.read_csv('manhattan_all_listings.csv')

print(f"Total listings: {len(df)}")
print(f"With unit numbers: {df['unit'].notna().sum()}")
print()

# Parse and normalize
print("Parsing unit numbers and normalizing addresses...")
listings = []
parse_failures = 0

for _, row in df.iterrows():
    if pd.isna(row['unit']) or not row['unit']:
        continue

    floor, position = parse_unit_number(row['unit'])
    if floor is None or position is None:
        parse_failures += 1
        continue

    # Normalize address (remove unit from it)
    address = row['formatted_address']
    if pd.notna(row['unit']):
        # Remove unit-like patterns from address
        address = re.sub(r'\s+(Apt|Unit|#|Ph)\s+[\w\-/]+', '', address)

    listing = {
        "address": address.strip(),
        "unit": str(row['unit']),
        "floor": floor,
        "position": position,
        "beds": int(row['beds']) if pd.notna(row['beds']) else 0,
        "sqft": int(row['sqft']) if pd.notna(row['sqft']) else 500,
        "price": int(row['list_price']) if pd.notna(row['list_price']) else 0,
    }
    listings.append(listing)

print(f"✓ Successfully parsed {len(listings)} listings")
print(f"✗ Failed to parse {parse_failures} unit numbers")
print()

# Save parsed data
with open('manhattan_parsed_all.json', 'w') as f:
    json.dump(listings, f, indent=2)
print(f"Saved parsed data to manhattan_parsed_all.json")
print()

# Analyze buildings
print("Analyzing building distribution...")
building_counts = Counter(l['address'] for l in listings)
multi_unit_buildings = {addr: count for addr, count in building_counts.items() if count > 1}
print(f"Total unique buildings: {len(building_counts)}")
print(f"Buildings with 2+ listings: {len(multi_unit_buildings)}")
print()

# Show top buildings
print("Top 10 buildings by number of listings:")
for addr, count in building_counts.most_common(10):
    print(f"  {count:2d} units: {addr}")
print()

# Run adjacency analysis
print("=" * 80)
print("RUNNING ADJACENCY DETECTION...")
print("=" * 80)
print()

analyzer = AdjacencyAnalyzer(listings)
pairs = analyzer.find_adjacent_pairs()

print(f"\n{'='*80}")
print(f"🎯 FOUND {len(pairs)} ADJACENT PAIRS!")
print(f"{'='*80}\n")

# Save all pairs
with open('manhattan_adjacent_pairs_all.json', 'w') as f:
    json.dump(pairs, f, indent=2)
print(f"Saved all {len(pairs)} pairs to manhattan_adjacent_pairs_all.json\n")

# Analyze pairs
if pairs:
    # Adjacency type breakdown
    type_counts = Counter(p['adjacency']['type'] for p in pairs)
    print("Adjacency types:")
    for adj_type, count in sorted(type_counts.items()):
        print(f"  {adj_type.capitalize()}: {count}")
    print()

    # Economics
    positive_savings = [p for p in pairs if p['economics']['potential_savings'] > 0]
    total_savings = sum(p['economics']['potential_savings'] for p in positive_savings)
    avg_savings = total_savings / len(positive_savings) if positive_savings else 0

    print("Economics:")
    print(f"  Pairs with positive savings: {len(positive_savings)} ({len(positive_savings)/len(pairs)*100:.1f}%)")
    print(f"  Average savings: ${avg_savings:,.0f}")
    print(f"  Total opportunity: ${total_savings:,.0f}")
    print()

    # Top 20 opportunities
    print("=" * 80)
    print("TOP 20 OPPORTUNITIES (by savings)")
    print("=" * 80)
    print()

    sorted_pairs = sorted(pairs, key=lambda p: p['economics']['potential_savings'], reverse=True)
    for i, pair in enumerate(sorted_pairs[:20], 1):
        savings = pair['economics']['potential_savings']
        print(f"#{i}. {pair['building']}")
        print(f"    Units: {pair['unit_1']['unit']} + {pair['unit_2']['unit']}")
        print(f"    Type: {pair['adjacency']['description']} ({pair['adjacency']['confidence']*100:.0f}%)")
        print(f"    Combined: {pair['combined']['sqft']} sqft, ${pair['combined']['total_cost']:,}")
        if savings > 0:
            print(f"    💰 SAVE: ${savings:,} ({pair['economics']['savings_percent']:.1f}%)")
        else:
            print(f"    ⚠️  Premium: ${abs(savings):,}")
        print()

print("\nAnalysis complete!")
