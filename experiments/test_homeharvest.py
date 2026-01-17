#!/usr/bin/env python3
"""
Test HomeHarvest scraper to get real Manhattan listings
"""

from homeharvest import scrape_property

print("Fetching Manhattan for-sale listings...")

try:
    properties = scrape_property(
        location="Manhattan, NY",
        listing_type="for_sale",
        limit=50  # Just get 50 to test
    )

    print(f"\nFound {len(properties)} properties!")

    # Show sample with correct column names
    print("\nSample listings:")
    cols_to_show = ['formatted_address', 'unit', 'list_price', 'beds', 'full_baths', 'sqft']
    print(properties[cols_to_show].head(20))

    # Save to file
    properties.to_csv('experiments/manhattan_listings_real.csv', index=False)
    print(f"\nSaved {len(properties)} listings to experiments/manhattan_listings_real.csv")

    # Check for unit numbers
    with_units = properties[properties['unit'].notna()]
    print(f"\nListings with unit numbers: {len(with_units)}/{len(properties)}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
