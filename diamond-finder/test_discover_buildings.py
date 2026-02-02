"""Quick test of building discovery from Vayo database"""
import sys
sys.path.insert(0, '.')

from strategies.discover_great_buildings import DiscoverGreatBuildingsStrategy

print("Testing Building Discovery from 571K Buildings\n")
print("=" * 60)

strategy = DiscoverGreatBuildingsStrategy()
diamonds = strategy.search()

print(f"\n\nDISCOVERED {len(diamonds)} GREAT BUILDINGS:")
print("=" * 60)

for i, diamond in enumerate(diamonds, 1):
    print(f"\n{i}. {diamond.address}")
    print(f"   Why special:")
    for reason in diamond.why_special:
        print(f"     - {reason}")
