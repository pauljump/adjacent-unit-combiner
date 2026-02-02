"""Quick test of Realtor Listings Live strategy"""
import sys
sys.path.insert(0, '.')

from strategies.realtor_listings_live import RealtorListingsLiveStrategy

print("Testing Realtor Listings Live Strategy\n")
print("=" * 60)

strategy = RealtorListingsLiveStrategy()
diamonds = strategy.search()

print(f"\n\nFOUND {len(diamonds)} AVAILABLE UNITS:")
print("=" * 60)

for i, diamond in enumerate(diamonds[:10], 1):  # Show first 10
    print(f"\n{i}. {diamond.address} - Unit {diamond.unit}")
    print(f"   Price: ${diamond.price:,}")
    print(f"   Beds: {diamond.bedrooms}, Sqft: {diamond.sqft}")
    print(f"   Available: {diamond.is_available}")
    print(f"   URL: {diamond.url}")
    print(f"   Why special:")
    for reason in diamond.why_special[:3]:
        print(f"     - {reason}")

if len(diamonds) > 10:
    print(f"\n... and {len(diamonds) - 10} more units")
