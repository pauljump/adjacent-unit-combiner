"""
Strategy: StreetEasy Building Scraper

Scrapes StreetEasy building pages to find exceptional units.
Looks for buildings with multiple listings to analyze patterns.
"""
import sys
from pathlib import Path
from typing import List, Dict
import re
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class StreetEasyScraperStrategy(SearchStrategy):
    """
    Scrapes StreetEasy for exceptional apartments.

    Targets:
    - Buildings with high-value listings
    - Units with exceptional features (terrace, views, etc.)
    - Quick sales (days on market)
    - Premium pricing
    """

    def __init__(self):
        super().__init__(
            name="streeteasy_scraper",
            description="[LIVE] Scrapes StreetEasy for exceptional listings"
        )

    def search(self) -> List[Diamond]:
        """Scrape StreetEasy for diamonds"""
        diamonds = []

        try:
            import requests
            from bs4 import BeautifulSoup

            # Target high-value neighborhoods
            neighborhoods = [
                'upper-west-side',
                'upper-east-side',
                'tribeca',
                'soho',
                'greenwich-village',
            ]

            for neighborhood in neighborhoods:
                print(f"  Searching {neighborhood}...")

                try:
                    # Search sales in neighborhood
                    url = f"https://streeteasy.com/for-sale/{neighborhood}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }

                    response = requests.get(url, headers=headers, timeout=10)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Find listing cards
                        listings = soup.find_all('article', class_='item')
                        print(f"    Found {len(listings)} listings")

                        for listing in listings[:10]:  # Top 10 per neighborhood
                            diamond = self._parse_listing(listing)
                            if diamond:
                                diamonds.append(diamond)

                        time.sleep(2)  # Be polite

                except Exception as e:
                    print(f"    Error: {e}")
                    continue

            print(f"  Found {len(diamonds)} diamonds from StreetEasy")

        except ImportError:
            print(f"  ⚠ beautifulsoup4 not installed: pip install beautifulsoup4")
            diamonds = []
        except Exception as e:
            print(f"  Error scraping StreetEasy: {e}")
            diamonds = []

        return diamonds

    def _parse_listing(self, listing_element) -> Diamond:
        """Parse a StreetEasy listing card"""
        try:
            # Extract address
            address_elem = listing_element.find('a', class_='building-link')
            if not address_elem:
                return None
            address = address_elem.text.strip()

            # Extract unit
            unit_elem = listing_element.find('span', class_='unit')
            unit = unit_elem.text.strip() if unit_elem else "Unknown"

            # Extract price
            price_elem = listing_element.find('span', class_='price')
            price_text = price_elem.text.strip() if price_elem else None
            price = self._parse_price(price_text)

            # Extract details
            details_elem = listing_element.find('div', class_='details')
            bedrooms = None
            sqft = None

            if details_elem:
                details_text = details_elem.text

                # Extract bedrooms
                bed_match = re.search(r'(\d+)\s*bed', details_text, re.IGNORECASE)
                if bed_match:
                    bedrooms = int(bed_match.group(1))

                # Extract sqft
                sqft_match = re.search(r'([\d,]+)\s*sqft', details_text, re.IGNORECASE)
                if sqft_match:
                    sqft = float(sqft_match.group(1).replace(',', ''))

            # Extract features/amenities
            features = []

            # Look for premium features in description
            desc_elem = listing_element.find('div', class_='description')
            if desc_elem:
                desc_text = desc_elem.text.lower()

                premium_keywords = {
                    'terrace': 'Private terrace',
                    'outdoor': 'Outdoor space',
                    'views': 'Exceptional views',
                    'corner': 'Corner unit',
                    'penthouse': 'Penthouse',
                    'duplex': 'Duplex',
                    'washer': 'In-unit laundry',
                    'doorman': 'Doorman building',
                    'central park': 'Central Park views',
                }

                for keyword, feature in premium_keywords.items():
                    if keyword in desc_text:
                        features.append(feature)

            # Only catalog if it has premium features
            if not features:
                return None

            why_special = [
                f"Listed on StreetEasy",
                f"Price: ${price:,.0f}" if price else "Price available",
            ]
            why_special.extend(features)

            diamond = self._create_diamond(
                address=address,
                unit=unit,
                listing_type="sale",
                price=price,
                bedrooms=bedrooms,
                sqft=sqft,
                why_special=why_special,
            )

            return diamond

        except Exception as e:
            return None

    def _parse_price(self, price_text: str) -> float:
        """Parse price string to float"""
        if not price_text:
            return None

        try:
            # Remove $, commas
            price_text = price_text.replace('$', '').replace(',', '')

            # Handle millions/thousands
            if 'M' in price_text.upper():
                return float(price_text.upper().replace('M', '')) * 1000000
            elif 'K' in price_text.upper():
                return float(price_text.upper().replace('K', '')) * 1000
            else:
                return float(price_text)
        except:
            return None


# Note on StreetEasy scraping:
"""
StreetEasy has anti-scraping measures. Better approaches:

1. Use their API if available (check for partner programs)
2. Scrape slowly with delays (2-3 seconds between requests)
3. Rotate User-Agents
4. Use proxies if scaling up
5. Cache results aggressively
6. Focus on building pages (less dynamic than search results)

For production:
- Consider using a scraping service (ScrapingBee, etc.)
- Or find if StreetEasy has a data feed/API for partners
- Or manually curate target buildings and scrape those specifically

Legal note:
- StreetEasy's ToS prohibits automated scraping
- This is for educational/personal use
- For commercial use, contact StreetEasy for API access
"""
