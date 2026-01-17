#!/usr/bin/env python3
import pandas as pd
import re
from analyze_adjacency import AdjacencyAnalyzer

def parse_unit(u):
    if pd.isna(u): return None, None
    u = str(u).strip()
    u = re.sub(r'^(Apt|Unit|Ph|#)\s+', '', u)
    m = re.match(r'(\d+)([A-Z])', u)
    if m: return int(m.group(1)), ord(m.group(2)) - ord('A')
    if u.isdigit() and len(u) >= 3: return int(u[:-2]), int(u[-2:])
    return None, None

df = pd.read_csv('manhattan_500.csv')
listings = []
for _, r in df.iterrows():
    if pd.isna(r['unit']): continue
    floor, pos = parse_unit(r['unit'])
    if floor is None: continue
    addr = re.sub(r'\s+(Apt|Unit|#|Ph)\s+[\w\-/]+', '', r['formatted_address']).strip()
    listings.append({'address': addr, 'unit': str(r['unit']), 'floor': floor, 'position': pos,
                     'beds': int(r['beds']) if pd.notna(r['beds']) else 0,
                     'sqft': int(r['sqft']) if pd.notna(r['sqft']) else 500,
                     'price': int(r['list_price']) if pd.notna(r['list_price']) else 0})

print(f'Parsed {len(listings)} listings from 500 total')
analyzer = AdjacencyAnalyzer(listings)
pairs = analyzer.find_adjacent_pairs()
print(f'\n{"="*80}')
print(f'FOUND {len(pairs)} ADJACENT PAIRS FROM REAL MANHATTAN DATA!')
print(f'{"="*80}\n')

for i, p in enumerate(pairs[:10], 1):
    savings = p['economics']['potential_savings']
    print(f'{i}. {p["building"]}')
    print(f'   Units: {p["unit_1"]["unit"]} + {p["unit_2"]["unit"]}')
    print(f'   Type: {p["adjacency"]["description"]} ({p["adjacency"]["confidence"]*100:.0f}% confidence)')
    print(f'   Combined cost: ${p["combined"]["total_cost"]:,}')
    print(f'   Market value: ${p["economics"]["market_comp_value"]:,}')
    if savings > 0:
        print(f'   💰 SAVE: ${savings:,} ({p["economics"]["savings_percent"]:.1f}%)')
    print()
