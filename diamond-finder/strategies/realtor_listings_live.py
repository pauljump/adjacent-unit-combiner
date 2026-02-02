"""
Strategy: Realtor.com Listings (Live)

Finds actual available units in our "great buildings" using existing Realtor.com data.
This is our FIRST strategy that finds actual units people can rent/buy RIGHT NOW.
"""
import sys
import os
from pathlib import Path
from typing import List
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class RealtorListingsLiveStrategy(SearchStrategy):
    """
    Finds current available units in our great buildings using Realtor.com data.

    This strategy:
    1. Loads the Realtor.com Manhattan listings CSV (7,215 listings)
    2. Matches listings to our "great buildings" list
    3. Returns actual available units with real prices, photos, etc.
    """

    def __init__(self):
        super().__init__(
            name="realtor_listings_live",
            description="[LIVE] Finds available units in great buildings (Realtor.com)"
        )
        self.csv_path = "/Users/pjump/Desktop/projects/adjacent-unit-combiner/experiments/manhattan_all_listings.csv"

    def search(self) -> List[Diamond]:
        """Find available units in our great buildings"""

        if not os.path.exists(self.csv_path):
            print(f"  CSV not found: {self.csv_path}")
            return []

        diamonds = []

        try:
            print(f"  Loading Realtor.com listings...")
            df = pd.read_csv(self.csv_path)
            print(f"  Loaded {len(df)} Manhattan listings")

            # Our great buildings (addresses we've identified as excellent)
            great_buildings = {
                "1 West 72nd Street": "The Dakota",
                "145 Central Park West": "San Remo",
                "211 Central Park West": "The Beresford",
                "2109 Broadway": "The Ansonia",
                "470 West 24th Street": "London Terrace",
                "410 West 24th Street": "London Terrace Towers",
                "2211 Broadway": "The Apthorp",
                "115 Central Park West": "The Majestic",
                "435 East 52nd Street": "River House",
                "5 Tudor City Place": "Tudor City",
                "300 Central Park West": "The Eldorado",
                "225 West 86th Street": "The Belnord",
                "98 Riverside Drive": "The Stuyvesant",
            }

            # Search for each building
            for address, building_name in great_buildings.items():
                # Try different address formats
                address_patterns = [
                    address,
                    address.replace(" Street", " St"),
                    address.replace(" Avenue", " Ave"),
                    address.replace(" West ", " W "),
                    address.replace(" East ", " E "),
                ]

                matches = pd.DataFrame()
                for pattern in address_patterns:
                    # Search in both formatted_address and full_street_line
                    addr_matches = df[
                        (df['formatted_address'].str.contains(pattern, case=False, na=False)) |
                        (df['full_street_line'].str.contains(pattern, case=False, na=False))
                    ]
                    if len(addr_matches) > 0:
                        matches = pd.concat([matches, addr_matches])
                        break

                if len(matches) == 0:
                    continue

                matches = matches.drop_duplicates(subset=['listing_id'])

                print(f"    {building_name}: Found {len(matches)} available units")

                # Create diamonds for each available unit
                for _, listing in matches.iterrows():
                    why_special = [
                        f"CURRENTLY AVAILABLE in {building_name}",
                        f"Building identified as excellent (testimonials + maintenance)",
                    ]

                    # Add listing details
                    if pd.notna(listing.get('list_date')):
                        why_special.append(f"Listed: {listing['list_date'][:10]}")

                    if pd.notna(listing.get('text')) and len(str(listing['text'])) > 100:
                        # Add snippet of description
                        desc = str(listing['text'])[:200].replace('\n', ' ')
                        why_special.append(f"Description: {desc}...")

                    # Create diamond
                    diamond = self._create_diamond(
                        address=listing.get('formatted_address') or address,
                        unit=listing.get('unit') or '',
                        listing_type='sale' if listing.get('status') == 'FOR_SALE' else 'rental',
                        price=listing.get('list_price', 0),
                        why_special=why_special,
                    )

                    # Add detailed info
                    diamond.bedrooms = listing.get('beds')
                    diamond.sqft = listing.get('sqft')
                    diamond.url = listing.get('property_url')
                    diamond.is_available = True  # THIS IS KEY - it's available NOW

                    # Add photos
                    if pd.notna(listing.get('primary_photo')):
                        diamond.photos = [listing['primary_photo']]

                    diamonds.append(diamond)

            print(f"  Found {len(diamonds)} available units in great buildings")

        except Exception as e:
            print(f"  Error loading listings: {e}")
            import traceback
            traceback.print_exc()

        return diamonds
