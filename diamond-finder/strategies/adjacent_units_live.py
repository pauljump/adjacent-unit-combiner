"""
Strategy: Adjacent Units Live Finder

Searches current StreetEasy/Zillow listings to find adjacent unit opportunities.
This creates REAL diamonds you can act on now.
"""
import sys
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class AdjacentUnitsLiveStrategy(SearchStrategy):
    """
    Finds CURRENT listings where multiple units in same building are for sale.
    You could buy both and combine = unique living experience.
    """

    def __init__(self):
        super().__init__(
            name="adjacent_units_live",
            description="[LIVE] Finds current listings you can combine into unique homes"
        )

    def search(self) -> List[Diamond]:
        """Search current listings for combination opportunities"""
        diamonds = []

        try:
            import requests
            from bs4 import BeautifulSoup

            # Target neighborhoods with multiple listings
            search_urls = [
                "https://streeteasy.com/for-sale/upper-west-side/price:-3000000%7Carea%3E1000",
                "https://streeteasy.com/for-sale/upper-east-side/price:-3000000%7Carea%3E1000",
            ]

            all_listings = []

            for url in search_urls:
                try:
                    print(f"  Searching current StreetEasy listings...")
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                    }

                    response = requests.get(url, headers=headers, timeout=10)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        listings = soup.find_all('article', class_='item')

                        print(f"    Found {len(listings)} current listings")

                        for listing in listings:
                            parsed = self._parse_listing(listing)
                            if parsed:
                                all_listings.append(parsed)

                except Exception as e:
                    print(f"    Error: {e}")
                    continue

            # Group by building
            by_building = defaultdict(list)
            for listing in all_listings:
                by_building[listing['building']].append(listing)

            # Find buildings with 2+ units for sale
            print(f"  Analyzing {len(by_building)} buildings for combination opportunities...")

            for building, units in by_building.items():
                if len(units) >= 2:
                    # Found a building with multiple units for sale!
                    # Check if they could be combined

                    for i, unit1 in enumerate(units):
                        for unit2 in units[i+1:]:
                            # Could these be combined?
                            if self._could_combine(unit1, unit2):
                                diamond = self._create_combination_diamond(unit1, unit2, building)
                                if diamond:
                                    diamonds.append(diamond)

            print(f"  Found {len(diamonds)} live combination opportunities")

        except ImportError:
            print(f"  ⚠ beautifulsoup4 needed: pip install beautifulsoup4")
        except Exception as e:
            print(f"  Error: {e}")

        return diamonds

    def _parse_listing(self, listing_elem) -> Dict:
        """Parse a listing from StreetEasy"""
        try:
            # Extract building address
            building_elem = listing_elem.find('a', class_='building-link')
            if not building_elem:
                return None
            building = building_elem.text.strip()

            # Extract unit
            unit_elem = listing_elem.find('span', class_='unit')
            unit = unit_elem.text.strip() if unit_elem else None

            # Extract price
            price_elem = listing_elem.find('span', class_='price')
            price_text = price_elem.text.strip() if price_elem else None
            price = self._parse_price(price_text)

            # Extract details
            details_elem = listing_elem.find('div', class_='details')
            beds = None
            sqft = None

            if details_elem:
                text = details_elem.text

                bed_match = re.search(r'(\d+)\s*bed', text, re.IGNORECASE)
                if bed_match:
                    beds = int(bed_match.group(1))

                sqft_match = re.search(r'([\d,]+)\s*sqft', text, re.IGNORECASE)
                if sqft_match:
                    sqft = float(sqft_match.group(1).replace(',', ''))

            if not unit:
                return None

            return {
                'building': building,
                'unit': unit,
                'price': price,
                'beds': beds,
                'sqft': sqft,
            }

        except:
            return None

    def _could_combine(self, unit1: Dict, unit2: Dict) -> bool:
        """Check if two units could potentially be combined"""

        # Same floor check (if unit numbers reveal floor)
        try:
            # Extract floor from unit (e.g., "12A" → 12)
            floor1 = int(''.join(filter(str.isdigit, unit1['unit'][:2])))
            floor2 = int(''.join(filter(str.isdigit, unit2['unit'][:2])))

            # Adjacent floors or same floor
            if abs(floor1 - floor2) <= 1:
                return True

        except:
            # Can't determine floors, assume possible
            return True

        return False

    def _create_combination_diamond(self, unit1: Dict, unit2: Dict, building: str) -> Diamond:
        """Create a diamond for a combination opportunity"""

        total_price = (unit1['price'] or 0) + (unit2['price'] or 0)
        total_sqft = (unit1['sqft'] or 0) + (unit2['sqft'] or 0)
        total_beds = (unit1['beds'] or 0) + (unit2['beds'] or 0)

        if total_price == 0 or total_sqft == 0:
            return None

        why_special = [
            f"LIVE OPPORTUNITY: Two units currently for sale",
            f"Units {unit1['unit']} + {unit2['unit']}",
            f"Combined: {total_sqft:,.0f} sqft, {total_beds} bedrooms",
            f"Total cost: ${total_price:,.0f}",
            "Create unique home you can't buy otherwise",
            "Through-floor or side-by-side configuration",
            "Available NOW - can act immediately"
        ]

        diamond = self._create_diamond(
            address=building,
            unit=f"{unit1['unit']}+{unit2['unit']}",
            listing_type="sale",
            price=total_price,
            bedrooms=total_beds,
            sqft=total_sqft,
            why_special=why_special,
        )

        # This IS available
        diamond.is_available = True

        return diamond

    def _parse_price(self, price_text: str) -> float:
        """Parse price string"""
        if not price_text:
            return None
        try:
            price_text = price_text.replace('$', '').replace(',', '')
            if 'M' in price_text.upper():
                return float(price_text.upper().replace('M', '')) * 1000000
            return float(price_text)
        except:
            return None
