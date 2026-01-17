#!/usr/bin/env python3
"""
Remove duplicate pairs from the dataset
"""

import json
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Loading NYC pairs data...")
with open('nyc_all_adjacent_pairs.json', 'r') as f:
    pairs = json.load(f)

print(f"Total pairs before deduplication: {len(pairs)}")

# Deduplicate
seen = set()
unique_pairs = []

for pair in pairs:
    building = pair['building']
    unit1 = pair['unit_1']['unit']
    unit2 = pair['unit_2']['unit']

    # Sort units to catch A+B and B+A duplicates
    units = tuple(sorted([unit1, unit2]))
    key = (building, units)

    if key not in seen:
        seen.add(key)
        unique_pairs.append(pair)

print(f"Duplicates removed: {len(pairs) - len(unique_pairs)}")
print(f"Unique pairs: {len(unique_pairs)}")

# Save deduplicated data
with open('nyc_all_adjacent_pairs.json', 'w') as f:
    json.dump(unique_pairs, f, indent=2)
print("Saved to nyc_all_adjacent_pairs.json")

# Update pairs_data.js
with open('pairs_data.js', 'w') as f:
    f.write('// All NYC adjacent pairs (Manhattan + Brooklyn) - auto-generated\n')
    f.write('const PAIRS_DATA = ')
    json.dump(unique_pairs, f, indent=2)
    f.write(';\n')
print("Updated pairs_data.js")

# Calculate new stats
total_savings = sum(p['economics']['potential_savings'] for p in unique_pairs if p['economics']['potential_savings'] > 0)
avg_savings = total_savings / len([p for p in unique_pairs if p['economics']['potential_savings'] > 0])

print(f"\nNew stats:")
print(f"Total pairs: {len(unique_pairs)}")
print(f"Total opportunity: ${total_savings:,.0f}")
print(f"Average savings: ${avg_savings:,.0f}")
