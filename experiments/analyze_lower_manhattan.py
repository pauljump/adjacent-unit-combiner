#!/usr/bin/env python3
"""
Analyze Lower Manhattan opportunities for a family of 5
"""

import json
import re

# Load data
with open('nyc_all_adjacent_pairs.json', 'r') as f:
    pairs = json.load(f)

# Filter for Lower Manhattan (below 30th St)
# Lower Manhattan neighborhoods: Financial District, Battery Park City, Tribeca,
# SoHo, West Village, East Village, Gramercy, Chelsea, Lower East Side

lower_manhattan_neighborhoods = [
    'Financial District', 'Battery Park City', 'Tribeca', 'SoHo',
    'West Village', 'East Village', 'Gramercy', 'Chelsea',
    'Lower East Side', 'Murray Hill'
]

# Also filter by street number if address contains it
def is_lower_manhattan(pair):
    # Check neighborhood
    if pair.get('neighborhood') in lower_manhattan_neighborhoods:
        return True

    # Check if Manhattan and street number < 30
    if pair.get('borough') == 'Manhattan':
        address = pair.get('building', '')
        # Look for street patterns like "E 25th St", "W 15th St", "20th St"
        match = re.search(r'([EW]\s+)?(\d+)(th|st|nd|rd)\s+St', address)
        if match:
            street_num = int(match.group(2))
            if street_num <= 30:
                return True

    return False

lower_manhattan_pairs = [p for p in pairs if is_lower_manhattan(p)]

print(f"Total Lower Manhattan pairs (below 30th St): {len(lower_manhattan_pairs)}")
print()

# Filter for family-friendly (need good space - at least 3000 sqft combined)
family_friendly = [
    p for p in lower_manhattan_pairs
    if p['combined']['sqft'] >= 3000
]

print(f"Pairs with 3000+ sqft (good for family of 5): {len(family_friendly)}")
print()

# Sort by different criteria
print("=" * 80)
print("TOP 10 BY INVESTMENT (Highest Savings)")
print("=" * 80)
by_savings = sorted(lower_manhattan_pairs, key=lambda p: p['economics']['potential_savings'], reverse=True)
for i, pair in enumerate(by_savings[:10], 1):
    savings = pair['economics']['potential_savings']
    sqft = pair['combined']['sqft']
    cost = pair['combined']['total_cost']
    neighborhood = pair.get('neighborhood', 'Unknown')

    print(f"\n{i}. {pair['building'][:50]}")
    print(f"   Neighborhood: {neighborhood}")
    print(f"   Combined: {sqft:,} sqft | {pair['unit_1']['beds'] + pair['unit_2']['beds']} total beds")
    print(f"   Total Cost: ${cost:,.0f}")
    print(f"   💰 Savings: ${savings:,.0f} ({pair['economics']['savings_percent']:.1f}%)")
    print(f"   Type: {pair['adjacency']['description']}")

print("\n" + "=" * 80)
print("TOP 10 FOR FAMILY LIVING (3000+ sqft, sorted by price/sqft)")
print("=" * 80)

# Calculate price per sqft for family-friendly options
for p in family_friendly:
    p['price_per_sqft'] = p['combined']['total_cost'] / p['combined']['sqft']

by_value = sorted(family_friendly, key=lambda p: p['price_per_sqft'])

for i, pair in enumerate(by_value[:10], 1):
    savings = pair['economics']['potential_savings']
    sqft = pair['combined']['sqft']
    cost = pair['combined']['total_cost']
    ppsf = pair['price_per_sqft']
    neighborhood = pair.get('neighborhood', 'Unknown')

    print(f"\n{i}. {pair['building'][:50]}")
    print(f"   Neighborhood: {neighborhood}")
    print(f"   Combined: {sqft:,} sqft | {pair['unit_1']['beds'] + pair['unit_2']['beds']} total beds")
    print(f"   Total Cost: ${cost:,.0f} (${ppsf:.0f}/sqft)")
    print(f"   💰 Savings: ${savings:,.0f} ({pair['economics']['savings_percent']:.1f}%)")
    print(f"   Type: {pair['adjacency']['description']}")

print("\n" + "=" * 80)
print("FAMILY-FRIENDLY NEIGHBORHOODS ANALYSIS")
print("=" * 80)

# Analyze by neighborhood
from collections import defaultdict
neighborhood_stats = defaultdict(lambda: {'count': 0, 'avg_sqft': 0, 'avg_cost': 0, 'avg_savings': 0})

for p in family_friendly:
    n = p.get('neighborhood', 'Unknown')
    neighborhood_stats[n]['count'] += 1
    neighborhood_stats[n]['avg_sqft'] += p['combined']['sqft']
    neighborhood_stats[n]['avg_cost'] += p['combined']['total_cost']
    neighborhood_stats[n]['avg_savings'] += p['economics']['potential_savings']

for n in neighborhood_stats:
    count = neighborhood_stats[n]['count']
    if count > 0:
        neighborhood_stats[n]['avg_sqft'] /= count
        neighborhood_stats[n]['avg_cost'] /= count
        neighborhood_stats[n]['avg_savings'] /= count

print("\nNeighborhoods with 3000+ sqft options:")
for n, stats in sorted(neighborhood_stats.items(), key=lambda x: x[1]['count'], reverse=True):
    if stats['count'] > 0:
        print(f"\n{n}: {stats['count']} options")
        print(f"  Avg: {stats['avg_sqft']:,.0f} sqft | ${stats['avg_cost']:,.0f} | Savings: ${stats['avg_savings']:,.0f}")

print("\n" + "=" * 80)
print("ULTRATHINK RECOMMENDATIONS")
print("=" * 80)
print("""
For a family of 5 with young kids in Lower Manhattan, consider:

BEST FOR INVESTMENT:
- Look for highest savings % in areas with appreciation potential
- Chelsea/West Village: Strong long-term value, good schools nearby
- Tribeca: Premium neighborhood, holds value well
- Gramercy: Quieter, family-friendly, good parks

BEST FOR LIVING WITH KIDS:
- Battery Park City: Best parks, waterfront, very family-oriented (if available)
- Tribeca: Excellent schools (PS 234), quiet, safe
- West Village: Charming, walkable, good elementary schools
- Gramercy: Gramercy Park access, quieter than most downtown

RED FLAGS TO AVOID:
- Lower East Side: Too noisy/busy for young kids
- East Village: Nightlife-heavy, less family-oriented
- Financial District: Dead on weekends, limited schools

SPACE REQUIREMENTS:
- Minimum 3000 sqft for 5 people comfortably
- Look for 3-4 combined bedrooms minimum
- Horizontal combinations (same floor) easier for young kids than vertical
""")
