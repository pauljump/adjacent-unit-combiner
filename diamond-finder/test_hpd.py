"""Quick test of HPD violations strategy"""
import sys
sys.path.insert(0, '.')

from strategies.well_maintained_buildings import WellMaintainedBuildingsStrategy

print("Testing HPD Well-Maintained Buildings Strategy\n")
print("=" * 60)

strategy = WellMaintainedBuildingsStrategy()
diamonds = strategy.search()

print(f"\n\nFOUND {len(diamonds)} WELL-MAINTAINED BUILDINGS:")
print("=" * 60)

for i, diamond in enumerate(diamonds, 1):
    print(f"\n{i}. {diamond.address}")
    print(f"   Why special:")
    for reason in diamond.why_special:
        print(f"     - {reason}")
