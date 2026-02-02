"""
Strategy: Historical Premium Sales Finder

Analyzes NYC property sales records (ACRIS) to find units that sold
at significant premiums compared to similar units in the same building.

A unit that sells for 30% more than building average is probably exceptional.
"""
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class PremiumSalesFinderStrategy(SearchStrategy):
    """
    Finds diamonds by analyzing historical sales premiums.

    Logic:
    1. Get all sales in a building over last 10-20 years
    2. Calculate average $/sqft for the building
    3. Find units that sold 20%+ above average
    4. Those are likely diamonds

    Data source: NYC ACRIS (public property records)
    """

    def __init__(self):
        super().__init__(
            name="premium_sales_finder",
            description="Finds diamonds through historical sales premium analysis"
        )

    def search(self) -> List[Diamond]:
        """
        Search for units with historical sales premiums.

        For now, returns example diamonds.
        Real implementation will query ACRIS database.
        """
        diamonds = []

        # Example premium sales (in production, from ACRIS data)
        premium_sales = [
            {
                "address": "15 Central Park West",
                "unit": "18C",
                "sale_price": 12500000,
                "sale_date": "2022-03-15",
                "sqft": 3200,
                "price_per_sqft": 3906,
                "building_avg_psf": 2800,
                "premium_pct": 39.5,
                "bedrooms": 3,
                "why_premium": [
                    "Corner unit with Central Park views",
                    "Recently renovated by previous owner",
                    "Bidding war - 4 offers"
                ]
            },
            {
                "address": "443 Greenwich Street",
                "unit": "N10A",
                "sale_price": 7200000,
                "sale_date": "2023-06-20",
                "sqft": 2100,
                "price_per_sqft": 3429,
                "building_avg_psf": 2400,
                "premium_pct": 42.9,
                "bedrooms": 3,
                "why_premium": [
                    "Tadao Ando designed building",
                    "Rare 3BR layout in building",
                    "Private outdoor terrace"
                ]
            },
            {
                "address": "The Dakota, 1 West 72nd Street",
                "unit": "Various high-floor units",
                "sale_price": None,  # Multiple sales
                "sale_date": "Historical pattern",
                "sqft": None,
                "price_per_sqft": None,
                "building_avg_psf": None,
                "premium_pct": 50.0,
                "bedrooms": None,
                "why_premium": [
                    "Historic building, celebrity residents",
                    "High-floor units consistently sell 50%+ over low-floor",
                    "Architectural significance"
                ]
            },
            {
                "address": "88 Greenwich Street",
                "unit": "PH92A",
                "sale_price": 15000000,
                "sale_date": "2021-11-10",
                "sqft": 3500,
                "price_per_sqft": 4286,
                "building_avg_psf": 2600,
                "premium_pct": 64.8,
                "bedrooms": 4,
                "why_premium": [
                    "Penthouse unit with wraparound terrace",
                    "Water and Statue of Liberty views",
                    "Only 4BR in building"
                ]
            },
        ]

        for sale in premium_sales:
            why_special = [
                f"Sold {sale['premium_pct']:.1f}% above building average",
                f"Sale price: ${sale['sale_price']:,}" if sale['sale_price'] else "Multiple premium sales",
                f"Price/sqft: ${sale['price_per_sqft']:,.0f} vs ${sale['building_avg_psf']:,.0f} building avg"
                    if sale['price_per_sqft'] else "Consistent premium pricing",
            ]

            # Add specific reasons for premium
            why_special.extend(sale['why_premium'])

            # Add tenure signal if we have it
            why_special.append(f"Last sale: {sale['sale_date']}")

            diamond = self._create_diamond(
                address=sale["address"],
                unit=sale["unit"],
                listing_type="sale",  # Historical sale
                price=sale.get("sale_price"),
                bedrooms=sale.get("bedrooms"),
                sqft=sale.get("sqft"),
                why_special=why_special,
                price_premium_pct=sale["premium_pct"],
            )

            # Mark as not currently available
            diamond.is_available = False

            diamonds.append(diamond)

        return diamonds

    def _analyze_building_sales(self, address: str) -> dict:
        """
        Analyze all sales in a building to find premiums.

        Would query ACRIS for:
        1. All sales at this address in last 10 years
        2. Calculate avg $/sqft
        3. Find outliers (20%+ above avg)
        4. Return those units

        Returns:
            Dictionary with building stats and premium units
        """
        # Placeholder - real implementation in Phase 2
        return {
            "address": address,
            "total_sales": 0,
            "avg_price_per_sqft": 0,
            "premium_units": []
        }

    def _fetch_acris_data(self, borough: str = None, date_range: tuple = None) -> List[dict]:
        """
        Fetch NYC ACRIS property sales data.

        ACRIS is publicly available:
        https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Master/bnx9-e6tj

        Can query via:
        - Socrata API (free, rate limited)
        - Bulk download (better for large analysis)

        Returns:
            List of sale records
        """
        # Placeholder - real implementation in Phase 2
        return []


# Real implementation notes for Phase 2:
"""
To make this work with real ACRIS data:

1. Option A: Socrata API
   - Install: pip install sodapy
   - Query NYC Open Data API
   - Free but rate limited

   Example:
   from sodapy import Socrata
   client = Socrata("data.cityofnewyork.us", None)
   results = client.get("bnx9-e6tj", limit=10000, borough="MANHATTAN")

2. Option B: Bulk Download
   - Download full ACRIS dataset
   - Load into local SQLite
   - Query locally (faster, no rate limits)

3. Analysis approach:
   - Group sales by address
   - Calculate $/sqft for each sale (need to join with property data for sqft)
   - Find outliers per building
   - Score based on:
     * Size of premium (30% = higher score than 15%)
     * Consistency (sold at premium multiple times)
     * Recency (recent premiums weighted higher)

4. Data quality notes:
   - ACRIS has typos/variations in addresses (normalize)
   - Some sales missing sqft (need to join with tax records)
   - Corporate/trust sales need to be filtered
   - Transfer between family members (not market sales)

5. Enhancement:
   - Cross-reference with DOB data for unit details
   - Join with property tax records for sqft
   - Track ownership tenure (how long held before sale)
"""
