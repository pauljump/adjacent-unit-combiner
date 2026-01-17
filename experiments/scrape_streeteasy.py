#!/usr/bin/env python3
"""
StreetEasy scraper for Manhattan for-sale listings.
Collects building address, unit number, price, size, etc.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import List, Dict
from urllib.parse import urljoin


class StreetEasyScraper:
    BASE_URL = "https://streeteasy.com"
    SEARCH_URL = f"{BASE_URL}/for-sale/manhattan"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_listings(self, max_listings: int = 200) -> List[Dict]:
        """Scrape listings from StreetEasy"""
        listings = []
        page = 1

        print(f"Scraping up to {max_listings} Manhattan for-sale listings...")

        while len(listings) < max_listings:
            url = f"{self.SEARCH_URL}?page={page}"
            print(f"Fetching page {page}...")

            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                page_listings = self._parse_listings_page(soup)

                if not page_listings:
                    print("No more listings found")
                    break

                listings.extend(page_listings)
                print(f"  Found {len(page_listings)} listings (total: {len(listings)})")

                page += 1
                time.sleep(2)  # Be polite

            except Exception as e:
                print(f"Error on page {page}: {e}")
                break

        return listings[:max_listings]

    def _parse_listings_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse individual listings from a search results page"""
        listings = []

        # StreetEasy uses article tags with class 'searchCardList--listItem'
        # Note: These selectors may need adjustment based on actual HTML structure
        cards = soup.find_all('article', class_=re.compile(r'searchCardList'))

        if not cards:
            # Try alternative selector
            cards = soup.find_all('div', class_=re.compile(r'listingCard'))

        for card in cards:
            try:
                listing = self._parse_listing_card(card)
                if listing:
                    listings.append(listing)
            except Exception as e:
                print(f"  Error parsing card: {e}")
                continue

        return listings

    def _parse_listing_card(self, card) -> Dict:
        """Extract data from a single listing card"""
        listing = {}

        # Address
        address_elem = card.find('a', class_=re.compile(r'listingCard-globalLink'))
        if address_elem:
            listing['url'] = urljoin(self.BASE_URL, address_elem.get('href', ''))

        # Try to find address text
        address_text = card.find(class_=re.compile(r'address'))
        if address_text:
            listing['address'] = address_text.get_text(strip=True)

        # Price
        price_elem = card.find(class_=re.compile(r'price'))
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            listing['price_text'] = price_text
            listing['price'] = self._parse_price(price_text)

        # Details (beds, baths, sqft)
        details = card.find_all(class_=re.compile(r'detail'))
        for detail in details:
            text = detail.get_text(strip=True).lower()
            if 'bed' in text:
                listing['beds'] = text
            elif 'bath' in text:
                listing['baths'] = text
            elif 'sq ft' in text or 'sqft' in text:
                listing['sqft_text'] = text
                listing['sqft'] = self._parse_sqft(text)

        return listing if listing else None

    def _parse_price(self, price_text: str) -> int:
        """Extract numeric price from text like '$1,250,000'"""
        nums = re.sub(r'[^0-9]', '', price_text)
        return int(nums) if nums else 0

    def _parse_sqft(self, sqft_text: str) -> int:
        """Extract numeric sqft from text"""
        nums = re.sub(r'[^0-9]', '', sqft_text)
        return int(nums) if nums else 0


def main():
    scraper = StreetEasyScraper()
    listings = scraper.scrape_listings(max_listings=200)

    # Save to JSON
    output_file = 'experiments/listings_raw.json'
    with open(output_file, 'w') as f:
        json.dump(listings, f, indent=2)

    print(f"\nScraped {len(listings)} listings")
    print(f"Saved to {output_file}")

    # Preview
    if listings:
        print(f"\nSample listing:")
        print(json.dumps(listings[0], indent=2))


if __name__ == '__main__':
    main()
