"""
Strategy: Mock Diamond Finder (For Testing)

Generates realistic-looking test data to validate the system works.
This will be replaced with real strategies once we have API access.
"""
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond
from typing import List


class MockDiamondFinder(SearchStrategy):
    """
    Generates mock diamonds for testing.
    Simulates what real strategies would find.
    """

    def __init__(self):
        super().__init__(
            name="mock_finder",
            description="Test strategy that generates realistic mock data"
        )

    def search(self) -> List[Diamond]:
        """Generate mock diamonds"""
        diamonds = []

        # Mock sale diamonds
        sale_examples = [
            {
                "address": "180 East 79th Street",
                "unit": "14A",
                "price": 8300000,
                "bedrooms": 3,
                "sqft": 2594,
                "why_special": [
                    "Owner held for 47 years (extreme tenure)",
                    "Through-floor duplex with private elevator",
                    "Sold $3,200/sqft when building averages $1,800/sqft",
                    "Original 1920s pre-war details preserved",
                    "Sold off-market, never publicly listed"
                ],
                "tenure_years": 47,
                "price_premium_pct": 77.8,
                "photos": 68,
            },
            {
                "address": "25 Central Park West",
                "unit": "19B",
                "price": 4200000,
                "bedrooms": 2,
                "sqft": 1850,
                "why_special": [
                    "Corner unit with Central Park views",
                    "Owner held 28 years before estate sale",
                    "Pre-war building with white glove service",
                    "Rare B-line unit (only 4 in building)"
                ],
                "tenure_years": 28,
                "price_premium_pct": 35.0,
                "photos": 42,
            },
            {
                "address": "443 Greenwich Street",
                "unit": "11C",
                "price": 6800000,
                "bedrooms": 3,
                "sqft": 2100,
                "why_special": [
                    "Tadao Ando designed building",
                    "Rare 3BR layout (only 6 in building)",
                    "Private terrace (400 sqft outdoor space)",
                    "Tribeca location with Hudson River views"
                ],
                "price_premium_pct": 42.0,
                "photos": 55,
            },
        ]

        for ex in sale_examples:
            diamond = self._create_diamond(
                address=ex["address"],
                unit=ex["unit"],
                listing_type="sale",
                price=ex["price"],
                bedrooms=ex["bedrooms"],
                sqft=ex["sqft"],
                why_special=ex["why_special"],
                tenure_years=ex.get("tenure_years"),
                price_premium_pct=ex.get("price_premium_pct"),
                photos=["placeholder"] * ex.get("photos", 0),
                listing_url=f"https://streeteasy.com/building/{ex['address'].replace(' ', '-').lower()}/{ex['unit']}"
            )
            diamonds.append(diamond)

        # Mock rental diamonds
        rental_examples = [
            {
                "address": "112 Greene Street",
                "unit": "5",
                "price": 5200,  # monthly rent
                "bedrooms": 2,
                "sqft": 2400,
                "why_special": [
                    "2,400 sqft loft in SoHo",
                    "Market value: $7,500/mo (31% below market)",
                    "Owner-occupied (renting while traveling)",
                    "Original 1880s cast iron details",
                    "Private keyed elevator"
                ],
                "price_premium_pct": -31.0,  # Negative = discount
                "photos": 38,
            },
            {
                "address": "88 Central Park West",
                "unit": "12B",
                "price": 8500,
                "bedrooms": 3,
                "sqft": 2100,
                "why_special": [
                    "Central Park views from 12th floor",
                    "Owner renting temporarily (might sell soon)",
                    "Pre-war classic with original details",
                    "Below market for CPW location"
                ],
                "tenure_years": 15,
                "price_premium_pct": -15.0,
                "photos": 28,
            },
        ]

        for ex in rental_examples:
            diamond = self._create_diamond(
                address=ex["address"],
                unit=ex["unit"],
                listing_type="rental",
                price=ex["price"],
                bedrooms=ex["bedrooms"],
                sqft=ex["sqft"],
                why_special=ex["why_special"],
                tenure_years=ex.get("tenure_years"),
                price_premium_pct=ex.get("price_premium_pct"),
                photos=["placeholder"] * ex.get("photos", 0),
                listing_url=f"https://streeteasy.com/rental/{ex['address'].replace(' ', '-').lower()}/{ex['unit']}"
            )
            diamonds.append(diamond)

        return diamonds
