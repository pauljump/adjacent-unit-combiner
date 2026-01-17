#!/usr/bin/env python3
"""
Scrape ALL Manhattan for-sale listings using HomeHarvest
"""

from homeharvest import scrape_property
import time

print("=" * 80)
print("SCRAPING ALL MANHATTAN FOR-SALE LISTINGS")
print("=" * 80)
print("\nThis may take several minutes...\n")

start = time.time()

try:
    # No limit = get as many as possible
    properties = scrape_property(
        location="Manhattan, NY",
        listing_type="for_sale",
        # No limit specified - will get all available
    )

    elapsed = time.time() - start

    print(f"\n{'='*80}")
    print(f"SCRAPING COMPLETE!")
    print(f"{'='*80}")
    print(f"\nTotal listings scraped: {len(properties)}")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Listings with unit numbers: {properties['unit'].notna().sum()}")

    # Save to file
    output_file = 'manhattan_all_listings.csv'
    properties.to_csv(output_file, index=False)
    print(f"\nSaved to: {output_file}")

    # Show sample
    print(f"\nSample listings:")
    cols = ['formatted_address', 'unit', 'list_price', 'beds', 'sqft']
    print(properties[cols].head(10))

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
