#!/usr/bin/env python3
"""
Check for markers that might be overlapping (same or very close coordinates)
"""

import json
from collections import defaultdict

print("Loading pairs data...")
with open('nyc_all_adjacent_pairs.json', 'r') as f:
    pairs = json.load(f)

# Find pairs with coordinates
pairs_with_coords = [p for p in pairs if 'coordinates' in p]
print(f"Total pairs: {len(pairs)}")
print(f"Pairs with coordinates: {len(pairs_with_coords)}")

# Group by coordinates (rounded to 4 decimal places to catch very close markers)
coords_groups = defaultdict(list)
for pair in pairs_with_coords:
    lat = round(pair['coordinates']['lat'], 4)
    lon = round(pair['coordinates']['lon'], 4)
    coords_groups[(lat, lon)].append(pair['building'])

# Find overlapping markers
overlapping = {coords: buildings for coords, buildings in coords_groups.items() if len(buildings) > 1}

print(f"\nUnique coordinate locations: {len(coords_groups)}")
print(f"Locations with overlapping markers: {len(overlapping)}")

if overlapping:
    print("\nTop 10 locations with most overlapping markers:")
    sorted_overlaps = sorted(overlapping.items(), key=lambda x: len(x[1]), reverse=True)
    for i, ((lat, lon), buildings) in enumerate(sorted_overlaps[:10], 1):
        print(f"\n{i}. ({lat}, {lon}) - {len(buildings)} buildings:")
        for building in buildings[:5]:  # Show first 5
            print(f"   - {building}")
        if len(buildings) > 5:
            print(f"   ... and {len(buildings) - 5} more")

# Summary
total_markers_on_map = len(coords_groups)
markers_hidden_by_overlap = len(pairs_with_coords) - total_markers_on_map

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total pairs with geocoded addresses: {len(pairs_with_coords)}")
print(f"Unique marker positions on map: {total_markers_on_map}")
print(f"Markers 'hidden' by overlap: {markers_hidden_by_overlap}")
print(f"\nIf you see fewer markers than expected, it's likely because")
print(f"{markers_hidden_by_overlap} pairs are at the same buildings as other pairs.")
