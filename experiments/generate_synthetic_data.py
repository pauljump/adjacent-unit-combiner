#!/usr/bin/env python3
"""
Generate realistic synthetic Manhattan for-sale listing data.
Based on actual building patterns, unit numbering, and price ranges.
"""

import json
import random
from typing import List, Dict

# Real Manhattan addresses with typical unit patterns
BUILDINGS = [
    {"address": "123 West 72nd Street", "floors": 12, "units_per_floor": 6, "pattern": "letter"},  # 3A, 3B, 3C...
    {"address": "315 West 86th Street", "floors": 15, "units_per_floor": 8, "pattern": "letter"},
    {"address": "200 East 82nd Street", "floors": 20, "units_per_floor": 4, "pattern": "letter"},
    {"address": "45 West 67th Street", "floors": 18, "units_per_floor": 6, "pattern": "number"},  # 301, 302, 303...
    {"address": "180 West End Avenue", "floors": 25, "units_per_floor": 8, "pattern": "letter"},
    {"address": "225 Central Park West", "floors": 16, "units_per_floor": 4, "pattern": "letter"},
    {"address": "301 East 78th Street", "floors": 12, "units_per_floor": 6, "pattern": "letter"},
    {"address": "150 West 51st Street", "floors": 30, "units_per_floor": 10, "pattern": "number"},
    {"address": "520 Park Avenue", "floors": 14, "units_per_floor": 3, "pattern": "letter"},
    {"address": "30 Lincoln Plaza", "floors": 28, "units_per_floor": 8, "pattern": "number"},
    {"address": "15 West 63rd Street", "floors": 20, "units_per_floor": 6, "pattern": "letter"},
    {"address": "400 Central Park West", "floors": 18, "units_per_floor": 4, "pattern": "letter"},
    {"address": "205 West 76th Street", "floors": 10, "units_per_floor": 8, "pattern": "letter"},
    {"address": "118 East 93rd Street", "floors": 8, "units_per_floor": 4, "pattern": "letter"},
    {"address": "88 Greenwich Street", "floors": 35, "units_per_floor": 12, "pattern": "number"},
]

# Unit type distributions (beds, sqft range, price per sqft)
UNIT_TYPES = [
    {"beds": "Studio", "sqft_range": (400, 600), "price_per_sqft": 1400},
    {"beds": "1 Bed", "sqft_range": (550, 850), "price_per_sqft": 1500},
    {"beds": "2 Bed", "sqft_range": (900, 1400), "price_per_sqft": 1600},
    {"beds": "3 Bed", "sqft_range": (1500, 2200), "price_per_sqft": 1700},
]


def generate_unit_number(floor: int, position: int, pattern: str) -> str:
    """Generate unit number based on building pattern"""
    if pattern == "letter":
        # Format: 3A, 3B, 12C, etc.
        letter = chr(65 + position)  # A, B, C...
        return f"{floor}{letter}"
    else:
        # Format: 301, 302, 1205, etc.
        return f"{floor}{position:02d}"


def generate_listing(building: Dict, floor: int, position: int) -> Dict:
    """Generate a single listing"""
    unit_type = random.choice(UNIT_TYPES)
    sqft = random.randint(*unit_type["sqft_range"])
    price = sqft * unit_type["price_per_sqft"] + random.randint(-50000, 50000)

    unit_number = generate_unit_number(floor, position, building["pattern"])

    return {
        "address": building["address"],
        "unit": unit_number,
        "floor": floor,
        "position": position,  # Position on floor (0, 1, 2...)
        "beds": unit_type["beds"],
        "sqft": sqft,
        "price": price,
        "price_per_sqft": round(price / sqft),
    }


def generate_dataset(num_listings: int = 200) -> List[Dict]:
    """Generate a realistic dataset with some adjacent pairs"""
    listings = []

    # Strategy: Randomly select buildings and floors, sometimes put multiple units from same floor
    for _ in range(num_listings):
        building = random.choice(BUILDINGS)
        floor = random.randint(3, building["floors"])  # Skip ground floors
        position = random.randint(0, building["units_per_floor"] - 1)

        listing = generate_listing(building, floor, position)
        listings.append(listing)

    # Deliberately create some adjacent pairs for testing
    # Horizontal pairs (same floor, adjacent positions)
    for _ in range(10):
        building = random.choice(BUILDINGS)
        floor = random.randint(3, building["floors"])
        position = random.randint(0, building["units_per_floor"] - 2)

        listings.append(generate_listing(building, floor, position))
        listings.append(generate_listing(building, floor, position + 1))

    # Vertical pairs (same position, adjacent floors)
    for _ in range(8):
        building = random.choice(BUILDINGS)
        floor = random.randint(3, building["floors"] - 1)
        position = random.randint(0, building["units_per_floor"] - 1)

        listings.append(generate_listing(building, floor, position))
        listings.append(generate_listing(building, floor + 1, position))

    # Remove duplicates (same building + unit)
    seen = set()
    unique_listings = []
    for listing in listings:
        key = (listing["address"], listing["unit"])
        if key not in seen:
            seen.add(key)
            unique_listings.append(listing)

    return unique_listings


def main():
    listings = generate_dataset(num_listings=200)

    # Save to JSON
    output_file = 'experiments/listings_synthetic.json'
    with open(output_file, 'w') as f:
        json.dump(listings, f, indent=2)

    print(f"Generated {len(listings)} synthetic listings")
    print(f"Saved to {output_file}")

    # Stats
    buildings = set(l["address"] for l in listings)
    print(f"\nDataset stats:")
    print(f"  Unique buildings: {len(buildings)}")
    print(f"  Avg listings per building: {len(listings) / len(buildings):.1f}")

    # Buildings with multiple listings
    from collections import Counter
    building_counts = Counter(l["address"] for l in listings)
    multi_listing_buildings = {b: c for b, c in building_counts.items() if c > 1}
    print(f"  Buildings with 2+ listings: {len(multi_listing_buildings)}")

    # Preview
    print(f"\nSample listings:")
    for listing in listings[:3]:
        print(f"  {listing['address']} #{listing['unit']} - {listing['beds']}, {listing['sqft']} sqft, ${listing['price']:,}")


if __name__ == '__main__':
    main()
