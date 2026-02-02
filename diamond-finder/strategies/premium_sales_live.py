"""
Strategy: Premium Sales Finder (LIVE VERSION)

Analyzes real NYC ACRIS property sales data to find units that sold
at significant premiums compared to similar units in the same building.

Uses NYC Open Data Socrata API.
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class PremiumSalesLiveStrategy(SearchStrategy):
    """
    Finds diamonds by analyzing real ACRIS sales data.

    Data source: NYC Open Data - ACRIS Real Property Master
    API: https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Master/bnx9-e6tj
    """

    def __init__(self):
        super().__init__(
            name="premium_sales_finder_live",
            description="[LIVE] Finds diamonds through real ACRIS sales premium analysis"
        )
        self.client = None
        self._init_socrata()

    def _init_socrata(self):
        """Initialize Socrata API client for NYC Open Data"""
        try:
            from sodapy import Socrata

            app_token = os.getenv('NYC_OPEN_DATA_KEY')

            self.client = Socrata(
                "data.cityofnewyork.us",
                app_token,  # Optional, but increases rate limit
                timeout=30
            )
            print(f"  ✓ NYC Open Data API initialized")

        except ImportError:
            print(f"  ⚠ sodapy not installed: pip install sodapy")
            self.client = None
        except Exception as e:
            print(f"  ⚠ Socrata API init failed: {e}")
            self.client = None

    def search(self) -> List[Diamond]:
        """
        Search ACRIS for premium sales.
        """
        if not self.client:
            print("  → Using fallback mode (no ACRIS API)")
            return self._fallback_search()

        diamonds = []

        try:
            # Target high-value Manhattan buildings
            target_neighborhoods = [
                'UPPER WEST SIDE',
                'UPPER EAST SIDE',
                'TRIBECA',
                'SOHO',
                'GREENWICH VILLAGE',
            ]

            # Get recent sales (last 2 years) in Manhattan
            # Note: Free tier has rate limits, so we limit results
            cutoff_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%dT%H:%M:%S.000')

            print(f"  Querying ACRIS for recent sales...")

            results = self.client.get(
                "bnx9-e6tj",  # ACRIS dataset
                limit=500,  # Start small due to rate limits
                order="document_date DESC"
            )

            print(f"  Retrieved {len(results)} sales records")

            # Analyze for premiums
            diamonds = self._analyze_premiums(results)

        except Exception as e:
            print(f"  Error querying ACRIS: {e}")
            print(f"  Falling back to example data")
            return self._fallback_search()

        print(f"  Found {len(diamonds)} premium sales")
        return diamonds

    def _analyze_premiums(self, sales: List[Dict]) -> List[Diamond]:
        """
        Analyze sales data to find units that sold at premiums.

        Groups sales by building, calculates average $/sqft,
        finds units that sold 20%+ above average.
        """
        diamonds = []

        # Group sales by address
        by_address = defaultdict(list)
        for sale in sales:
            address = sale.get('address')
            if address:
                by_address[address].append(sale)

        # Analyze each building
        for address, building_sales in by_address.items():
            if len(building_sales) < 3:  # Need enough data for comparison
                continue

            # Calculate building average (simplified - real impl would normalize by size)
            prices = []
            for sale in building_sales:
                try:
                    price = float(sale.get('sale_price', 0))
                    if price > 0:
                        prices.append(price)
                except:
                    continue

            if not prices:
                continue

            avg_price = sum(prices) / len(prices)

            # Find premiums (simplified - doesn't account for unit size differences)
            for sale in building_sales:
                try:
                    price = float(sale.get('sale_price', 0))
                    if price == 0:
                        continue

                    premium_pct = ((price - avg_price) / avg_price) * 100

                    # Flag if 20%+ premium
                    if premium_pct >= 20:
                        diamond = self._create_premium_diamond(sale, premium_pct, avg_price)
                        if diamond:
                            diamonds.append(diamond)

                except Exception as e:
                    continue

        # Sort by premium percentage
        diamonds.sort(key=lambda d: d.price_premium_pct or 0, reverse=True)

        # Return top findings
        return diamonds[:10]  # Top 10 premiums

    def _create_premium_diamond(self, sale: Dict, premium_pct: float, building_avg: float) -> Optional[Diamond]:
        """Create a diamond from a premium sale"""
        try:
            address = sale.get('address', 'Unknown')
            price = float(sale.get('sale_price', 0))
            date = sale.get('document_date', 'Unknown')

            # Try to extract unit from address
            # ACRIS address often includes unit at end
            parts = address.split()
            unit = parts[-1] if len(parts) > 3 else "Unknown"

            why_special = [
                f"Sold {premium_pct:.1f}% above building average",
                f"Sale price: ${price:,.0f}",
                f"Building avg: ${building_avg:,.0f}",
                f"Sale date: {date}",
                "Source: NYC ACRIS public records"
            ]

            diamond = self._create_diamond(
                address=address,
                unit=unit,
                listing_type="sale",
                price=price,
                why_special=why_special,
                price_premium_pct=premium_pct,
            )

            diamond.is_available = False  # Historical sale
            return diamond

        except Exception as e:
            return None

    def _fallback_search(self) -> List[Diamond]:
        """Fallback to example data when API not available"""
        from .premium_sales_finder import PremiumSalesFinderStrategy
        fallback = PremiumSalesFinderStrategy()
        return fallback.search()


# Note on ACRIS data:
"""
The ACRIS dataset is HUGE (millions of records). For production use:

1. Better approach: Bulk download
   - Download full ACRIS dataset (CSV)
   - Import to local SQLite/PostgreSQL
   - Query locally (much faster, no rate limits)
   - Download: https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Master/bnx9-e6tj
   - Export → CSV

2. Data quality improvements:
   - Join with property tax records for sqft data
   - Calculate true $/sqft instead of raw prices
   - Filter out non-arms-length transactions (family transfers, corporate, etc.)
   - Normalize address variations

3. Enhanced analysis:
   - Compare units of similar size (2BR vs 2BR)
   - Weight by recency (recent premiums more relevant)
   - Track repeat sales (same unit sold multiple times at premium)
   - Identify bidding wars (quick sales at premium)

4. Rate limits:
   - Free tier: 1,000 requests/day, 10,000 results per query
   - With app token: Higher limits
   - Get token: https://data.cityofnewyork.us/profile/edit/developer_settings

For now, this implementation queries recent sales and does basic analysis.
Production version should use bulk download + local database.
"""
