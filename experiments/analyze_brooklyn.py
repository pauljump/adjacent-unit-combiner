#!/usr/bin/env python3
"""
Analyze Brooklyn listings for adjacent units
"""

import pandas as pd
import json
import re
from analyze_adjacency import AdjacencyAnalyzer
from collections import Counter

# Brooklyn zip code to neighborhood mapping
brooklyn_zip_to_neighborhood = {
    '11201': 'Brooklyn Heights', '11205': 'Fort Greene', '11206': 'Williamsburg',
    '11211': 'Williamsburg', '11215': 'Park Slope', '11217': 'Park Slope',
    '11238': 'Prospect Heights', '11216': 'Bedford-Stuyvesant', '11221': 'Bushwick',
    '11222': 'Greenpoint', '11249': 'Williamsburg', '11231': 'Red Hook',
    '11232': 'Sunset Park', '11220': 'Sunset Park', '11209': 'Bay Ridge',
    '11228': 'Dyker Heights', '11214': 'Bensonhurst', '11223': 'Gravesend',
    '11224': 'Coney Island', '11235': 'Brighton Beach', '11229': 'Midwood',
    '11230': 'Midwood', '11204': 'Borough Park', '11219': 'Borough Park',
    '11218': 'Kensington', '11210': 'Flatbush', '11225': 'Crown Heights',
    '11213': 'Crown Heights', '11212': 'Brownsville', '11203': 'East Flatbush',
    '11226': 'Flatbush', '11207': 'East New York', '11208': 'East New York',
    '11236': 'Canarsie', '11239': 'East New York', '11234': 'Mill Basin',
}

def parse_unit_number(unit_str):
    """Extract floor and position from unit number"""
    if pd.isna(unit_str) or not unit_str:
        return None, None

    unit_str = str(unit_str).strip()
    unit_str = re.sub(r'^(Apt|Unit|Ph|#)\s+', '', unit_str)

    # Try patterns like "4D", "12C", "5F"
    match = re.match(r'(\d+)([A-Z])$', unit_str)
    if match:
        floor = int(match.group(1))
        letter = match.group(2)
        position = ord(letter) - ord('A')
        return floor, position

    # Try patterns like "301", "1205"
    if unit_str.isdigit() and len(unit_str) >= 3:
        floor = int(unit_str[:-2])
        position = int(unit_str[-2:])
        return floor, position
    elif unit_str.isdigit() and len(unit_str) == 1:
        floor = 1
        position = int(unit_str)
        return floor, position

    return None, None


print("=" * 80)
print("ANALYZING BROOKLYN LISTINGS FOR ADJACENT UNITS")
print("=" * 80)
print()

# Load Brooklyn data
df = pd.read_csv('brooklyn_all_listings.csv')
print(f"Total Brooklyn listings: {len(df)}")
print(f"With unit numbers: {df['unit'].notna().sum()}")
print()

# Parse and normalize
print("Parsing unit numbers...")
listings = []
parse_failures = 0

for _, row in df.iterrows():
    if pd.isna(row['unit']) or not row['unit']:
        continue

    floor, position = parse_unit_number(row['unit'])
    if floor is None or position is None:
        parse_failures += 1
        continue

    # Normalize address
    address = row['formatted_address']
    if pd.notna(row['unit']):
        address = re.sub(r'\s+(Apt|Unit|#|Ph)\s+[\w\-/]+', '', address)

    # Get neighborhood from zip
    zip_code = str(row['zip_code']) if pd.notna(row['zip_code']) else None
    neighborhood = brooklyn_zip_to_neighborhood.get(zip_code, 'Brooklyn (Other)')

    listing = {
        "address": address.strip(),
        "unit": str(row['unit']),
        "floor": floor,
        "position": position,
        "beds": int(row['beds']) if pd.notna(row['beds']) else 0,
        "sqft": int(row['sqft']) if pd.notna(row['sqft']) else 500,
        "price": int(row['list_price']) if pd.notna(row['list_price']) else 0,
        "neighborhood": neighborhood,
        "borough": "Brooklyn",
        "url": row.get('property_url', '')
    }
    listings.append(listing)

print(f"✓ Parsed {len(listings)} listings")
print(f"✗ Failed {parse_failures} unit numbers")
print()

# Building stats
building_counts = Counter(l['address'] for l in listings)
multi_unit_buildings = {addr: count for addr, count in building_counts.items() if count > 1}
print(f"Unique buildings: {len(building_counts)}")
print(f"Buildings with 2+ listings: {len(multi_unit_buildings)}")
print()

# Top buildings
print("Top 10 Brooklyn buildings:")
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
print(f"🎯 FOUND {len(pairs)} ADJACENT PAIRS IN BROOKLYN!")
print(f"{'='*80}\n")

# Add neighborhoods and URLs to pairs
for pair in pairs:
    # Get neighborhood from first listing
    pair['neighborhood'] = listings[0]['neighborhood'] if listings else 'Brooklyn'
    pair['borough'] = 'Brooklyn'

    # Try to add URLs
    for listing in listings:
        if listing['address'] == pair['building']:
            if listing['unit'] == pair['unit_1']['unit']:
                pair['unit_1']['url'] = listing.get('url', '')
            if listing['unit'] == pair['unit_2']['unit']:
                pair['unit_2']['url'] = listing.get('url', '')

# Save
with open('brooklyn_adjacent_pairs.json', 'w') as f:
    json.dump(pairs, f, indent=2)
print(f"Saved to brooklyn_adjacent_pairs.json\n")

# Stats
if pairs:
    type_counts = Counter(p['adjacency']['type'] for p in pairs)
    print("Adjacency types:")
    for adj_type, count in sorted(type_counts.items()):
        print(f"  {adj_type.capitalize()}: {count}")
    print()

    positive_savings = [p for p in pairs if p['economics']['potential_savings'] > 0]
    print(f"Pairs with positive savings: {len(positive_savings)} ({len(positive_savings)/len(pairs)*100:.1f}%)")

    if positive_savings:
        total_savings = sum(p['economics']['potential_savings'] for p in positive_savings)
        avg_savings = total_savings / len(positive_savings)
        print(f"Average savings: ${avg_savings:,.0f}")
        print(f"Total opportunity: ${total_savings:,.0f}")
        print()

    # Top 10
    sorted_pairs = sorted(pairs, key=lambda p: p['economics']['potential_savings'], reverse=True)
    print("Top 10 Brooklyn opportunities:")
    for i, pair in enumerate(sorted_pairs[:10], 1):
        savings = pair['economics']['potential_savings']
        print(f"{i}. {pair['building']}")
        print(f"   {pair['unit_1']['unit']} + {pair['unit_2']['unit']}")
        if savings > 0:
            print(f"   💰 ${savings:,.0f} ({pair['economics']['savings_percent']:.1f}%)")
        print()
