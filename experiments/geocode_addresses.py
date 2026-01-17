#!/usr/bin/env python3
"""
Pre-geocode all addresses to make map loading instant
"""

import json
import requests
import time
from collections import defaultdict

print("Loading NYC pairs data...")
with open('nyc_all_adjacent_pairs.json', 'r') as f:
    pairs = json.load(f)

print(f"Total pairs: {len(pairs)}")

# Geocode cache
geocode_cache = {}

# Try to load existing cache
try:
    with open('geocode_cache.json', 'r') as f:
        geocode_cache = json.load(f)
    print(f"Loaded {len(geocode_cache)} cached addresses")
except FileNotFoundError:
    print("No cache found, starting fresh")

# Get unique addresses
addresses = list(set(pair['building'] for pair in pairs))
print(f"Unique addresses to geocode: {len(addresses)}")

# Geocode addresses
geocoded = 0
failed = 0

for i, address in enumerate(addresses):
    if address in geocode_cache:
        geocoded += 1
        continue

    print(f"Geocoding {i+1}/{len(addresses)}: {address[:50]}...")

    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'format': 'json',
                'q': address,
                'limit': 1
            },
            headers={'User-Agent': 'NYC Adjacent Units Analyzer'}
        )
        data = response.json()

        if data and len(data) > 0:
            geocode_cache[address] = {
                'lat': float(data[0]['lat']),
                'lon': float(data[0]['lon'])
            }
            geocoded += 1
            print(f"  ✓ Success")
        else:
            print(f"  ❌ No results")
            failed += 1

        # Save cache every 10 addresses
        if (i + 1) % 10 == 0:
            with open('geocode_cache.json', 'w') as f:
                json.dump(geocode_cache, f, indent=2)
            print(f"  💾 Saved cache ({geocoded} geocoded)")

        # Respect rate limit: 1 request per second
        time.sleep(1.1)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed += 1
        time.sleep(2)

print(f"\n✓ Geocoded: {geocoded}")
print(f"✗ Failed: {failed}")

# Save cache
with open('geocode_cache.json', 'w') as f:
    json.dump(geocode_cache, f, indent=2)
print("Saved geocode cache")

# Add coordinates to pairs
for pair in pairs:
    if pair['building'] in geocode_cache:
        pair['coordinates'] = geocode_cache[pair['building']]

# Count how many pairs have coordinates
with_coords = len([p for p in pairs if 'coordinates' in p])
print(f"\nPairs with coordinates: {with_coords}/{len(pairs)}")

# Save updated pairs
with open('nyc_all_adjacent_pairs.json', 'w') as f:
    json.dump(pairs, f, indent=2)

# Update pairs_data.js
with open('pairs_data.js', 'w') as f:
    f.write('// All NYC adjacent pairs (Manhattan + Brooklyn) - auto-generated\n')
    f.write('// Includes pre-geocoded coordinates for instant map rendering\n')
    f.write('const PAIRS_DATA = ')
    json.dump(pairs, f, indent=2)
    f.write(';\n')

print("Updated pairs_data.js with coordinates")
print("\n✅ Map will now load instantly!")
