"""
Strategy: Listing Archive Miner

Searches historical listing archives (StreetEasy, Zillow, etc.) to find
apartments that had exceptional photos, descriptions, or engagement.

Even if not listed now, we catalog them as diamonds based on past evidence.
"""
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class ListingArchiveMinerStrategy(SearchStrategy):
    """
    Mines historical listing data to find diamonds.

    Sources:
    - StreetEasy cache (listings back to ~2005)
    - Zillow historical data
    - Wayback Machine archives
    - Real estate broker websites

    Signals:
    - High photo count (30+ photos = owner proud of it)
    - Premium descriptions ("one-of-a-kind", "trophy")
    - Quick sales (< 7 days = highly desirable)
    - High engagement (saves, views on listing sites)
    - Multiple past listings (churned but always premium)
    """

    def __init__(self):
        super().__init__(
            name="listing_archive_miner",
            description="Finds diamonds through historical listing analysis"
        )

    def search(self) -> List[Diamond]:
        """
        Search historical listing archives for exceptional apartments.

        Real implementation would scrape/query:
        - StreetEasy historical listings
        - Zillow past listings
        - Archive.org snapshots
        """
        diamonds = []

        # Example archived listings (in production, from actual archives)
        archived_listings = [
            {
                "address": "443 Greenwich Street",
                "unit": "PH53B",
                "listing_date": "2020-05-15",
                "listing_price": 15500000,
                "days_on_market": 4,
                "photo_count": 82,
                "bedrooms": 4,
                "sqft": 3850,
                "description_keywords": [
                    "one-of-a-kind",
                    "trophy penthouse",
                    "unobstructed views",
                    "private terrace",
                    "Tadao Ando"
                ],
                "broker": "Corcoran",
                "views": 15000,  # Listing views
                "saves": 450,  # User saves
            },
            {
                "address": "70 Vestry Street",
                "unit": "9A",
                "listing_date": "2019-11-20",
                "listing_price": 9750000,
                "days_on_market": 3,
                "photo_count": 65,
                "bedrooms": 3,
                "sqft": 2900,
                "description_keywords": [
                    "Robert A.M. Stern",
                    "museum-quality",
                    "Hudson River views",
                    "private outdoor space"
                ],
                "broker": "Douglas Elliman",
                "views": 12000,
                "saves": 380,
            },
            {
                "address": "15 Central Park West",
                "unit": "18C",
                "listing_date": "2021-08-10",
                "listing_price": 12000000,
                "days_on_market": 2,
                "photo_count": 55,
                "bedrooms": 3,
                "sqft": 3200,
                "description_keywords": [
                    "corner residence",
                    "Central Park",
                    "Robert A.M. Stern",
                    "full-floor feel"
                ],
                "broker": "Brown Harris Stevens",
                "views": 18000,
                "saves": 520,
            },
            {
                "address": "56 Leonard Street",
                "unit": "54B",
                "listing_date": "2018-03-25",
                "listing_price": 13500000,
                "days_on_market": 6,
                "photo_count": 72,
                "bedrooms": 3,
                "sqft": 2900,
                "description_keywords": [
                    "Jenga building",
                    "Herzog & de Meuron",
                    "sky garage",
                    "360 views"
                ],
                "broker": "Sotheby's",
                "views": 22000,
                "saves": 650,
            },
        ]

        for listing in archived_listings:
            why_special = [
                f"Historical listing: {listing['listing_date']}",
                f"Sold in {listing['days_on_market']} days (high demand)",
                f"Professional photo shoot: {listing['photo_count']} photos",
                f"Listed at ${listing['listing_price']:,}",
                f"{listing['views']:,} views, {listing['saves']} saves (high engagement)",
            ]

            # Add description keywords as signals
            keywords_str = ", ".join(listing['description_keywords'])
            why_special.append(f"Described as: {keywords_str}")

            # Add broker signal (top brokers get best listings)
            why_special.append(f"Listed by {listing['broker']}")

            diamond = self._create_diamond(
                address=listing["address"],
                unit=listing["unit"],
                listing_type="sale",
                price=listing.get("listing_price"),
                bedrooms=listing.get("bedrooms"),
                sqft=listing.get("sqft"),
                why_special=why_special,
                photos=[f"archive_photo_{i}" for i in range(listing['photo_count'])],
            )

            # Not currently listed - we're cataloging from archive
            diamond.is_available = False

            diamonds.append(diamond)

        return diamonds

    def _search_streeteasy_archive(self, date_range: tuple = None) -> List[dict]:
        """
        Search StreetEasy historical listings.

        StreetEasy keeps cache of past listings with:
        - Photos (usually preserved)
        - Descriptions
        - Price history
        - Days on market
        - Engagement metrics (views, saves)

        Can search by:
        - Neighborhood
        - Price range
        - Date range
        - Quick sales (< 7 days)
        - High engagement

        Returns:
            List of historical listings
        """
        # Placeholder - real implementation in Phase 2
        return []

    def _analyze_listing_quality(self, listing: dict) -> float:
        """
        Score listing quality to identify exceptional apartments.

        Signals:
        - Photo count (30+ = high quality)
        - Professional photography (detect quality)
        - Description richness (superlatives, details)
        - Price point (top 10% for area)
        - Days on market (< 7 days = very desirable)
        - Engagement (views, saves, shares)
        - Broker quality (top firms)

        Returns:
            Quality score 0-100
        """
        score = 0

        # Photo count (max 30 points)
        photo_count = listing.get('photo_count', 0)
        score += min(photo_count / 2, 30)

        # Quick sale (max 25 points)
        dom = listing.get('days_on_market', 999)
        if dom <= 3:
            score += 25
        elif dom <= 7:
            score += 20
        elif dom <= 14:
            score += 15

        # Engagement (max 25 points)
        views = listing.get('views', 0)
        saves = listing.get('saves', 0)
        score += min(views / 1000, 15)
        score += min(saves / 50, 10)

        # Description keywords (max 20 points)
        premium_keywords = [
            'one-of-a-kind', 'trophy', 'museum-quality',
            'exceptional', 'rare', 'unique', 'masterpiece',
            'architectural', 'iconic', 'legendary'
        ]
        description = listing.get('description', '').lower()
        keyword_count = sum(1 for kw in premium_keywords if kw in description)
        score += min(keyword_count * 4, 20)

        return min(score, 100)


# Real implementation notes for Phase 2:
"""
To make this work with real archived data:

1. StreetEasy Historical Data:
   - URL pattern: streeteasy.com/building/[address]/[unit]
   - Often preserves old listings
   - Photos cached (may need to scrape)
   - Price history available
   - Can use Wayback Machine for older listings

2. Zillow Historical:
   - Similar to StreetEasy
   - "More" → "Price/Tax History" shows all listings
   - Photos sometimes preserved

3. Web Scraping Approach:
   a) Identify target buildings
   b) Enumerate units (1A, 1B, 2A, etc.)
   c) Check if listing exists in archives
   d) Extract: photos, price, description, dates
   e) Score quality

4. Archive.org (Wayback Machine):
   - Can find old broker website listings
   - Photos often preserved
   - Use: pip install waybackpy

5. Engagement Signals:
   - StreetEasy shows "X people saved this"
   - Can estimate views from URL patterns
   - Quick sales = high demand

6. Photo Analysis:
   - Count photos
   - Analyze quality (resolution, professional vs phone)
   - Types of photos (detail shots = pride of ownership)
   - Virtual tours = premium listing

7. Description Analysis:
   - Length (longer = more detail)
   - Superlatives (trophy, exceptional, etc.)
   - Specific features mentioned
   - Architectural details

8. Broker Signal:
   - Top brokers (Corcoran, Douglas Elliman, Sotheby's, etc.)
   - Get best/most exclusive listings
   - Presence of top broker = likely exceptional

9. Price History Pattern:
   - Multiple listings, always at premium
   - vs multiple listings with price drops (not a diamond)
   - Consistent premium = true diamond

10. Output:
    - Catalog unit with archive evidence
    - Store photos for reference
    - Mark as "not currently available"
    - Monitor for re-listing
"""
