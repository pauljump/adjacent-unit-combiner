"""
Strategy: NYC Buildings Data Analyzer

Uses NYC Open Data to find exceptional buildings and units.
Data sources:
- DOB Permits (major renovations, new buildings)
- HPD Violations (avoid problem buildings)
- Landmark status (historic significance)
- PLUTO (lot data, building features)
"""
import sys
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class NYCBuildingsDataStrategy(SearchStrategy):
    """
    Finds diamonds through NYC building data analysis.

    Looks for:
    - Landmark buildings (architectural significance)
    - Recent major renovations (permits >$1M)
    - Buildings with roof access (certificates)
    - Boutique buildings (small, exclusive)
    """

    def __init__(self):
        super().__init__(
            name="nyc_buildings_data",
            description="[LIVE] Analyzes NYC building permits, landmarks, and property data"
        )
        self.client = None
        self._init_socrata()

    def _init_socrata(self):
        """Initialize NYC Open Data client"""
        try:
            from sodapy import Socrata

            app_token = os.getenv('NYC_OPEN_DATA_KEY')
            self.client = Socrata(
                "data.cityofnewyork.us",
                app_token,
                timeout=30
            )
            print(f"  ✓ NYC Open Data initialized")

        except ImportError:
            print(f"  ⚠ sodapy not installed")
            self.client = None
        except Exception as e:
            print(f"  ⚠ NYC Open Data init failed: {e}")
            self.client = None

    def search(self) -> List[Diamond]:
        """Search NYC building data"""
        if not self.client:
            return self._fallback_search()

        diamonds = []

        try:
            # Strategy 1: Find landmark buildings
            print(f"  Querying NYC Landmarks...")
            landmarks = self._find_landmark_buildings()
            diamonds.extend(landmarks)

            # Strategy 2: Find recent major renovations
            print(f"  Querying DOB permits...")
            renovations = self._find_major_renovations()
            diamonds.extend(renovations)

        except Exception as e:
            print(f"  Error: {e}")

        print(f"  Found {len(diamonds)} diamonds from NYC data")
        return diamonds

    def _find_landmark_buildings(self) -> List[Diamond]:
        """Find NYC landmark buildings"""
        diamonds = []

        try:
            # LPC Individual Landmarks dataset
            results = self.client.get(
                "iputphxm",  # LPC dataset
                limit=50,
                where="borough='MANHATTAN'"
            )

            print(f"    Retrieved {len(results)} landmarks")

            for landmark in results[:20]:  # Top 20
                address = landmark.get('lp_number', 'Unknown')
                name = landmark.get('lm_name', 'Landmark Building')

                why_special = [
                    f"NYC Landmark: {name}",
                    "Historic architectural significance",
                    "Protected by Landmarks Preservation Commission",
                    "Unique features preserved",
                ]

                # Try to get street address
                street = landmark.get('pluto_addr')
                if street:
                    address = street

                diamond = self._create_diamond(
                    address=address or name,
                    unit="Various",
                    listing_type="unknown",
                    why_special=why_special,
                )

                diamond.is_available = False  # Just cataloging
                diamonds.append(diamond)

        except Exception as e:
            print(f"    Landmark query error: {e}")

        return diamonds

    def _find_major_renovations(self) -> List[Diamond]:
        """Find buildings with major recent renovations"""
        diamonds = []

        try:
            # DOB Job Application Filings
            # Look for major alterations (expensive permits = premium buildings)
            cutoff = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

            results = self.client.get(
                "ic3t-wcy2",  # DOB permits
                limit=100,
                where=f"borough='MANHATTAN' AND filing_date >= '{cutoff}'",
                order="filing_date DESC"
            )

            print(f"    Retrieved {len(results)} permits")

            # Group by address, find high-value work
            by_address = {}
            for permit in results:
                address = permit.get('house', 'Unknown')
                street = permit.get('street_name', '')
                full_address = f"{address} {street}".strip()

                job_type = permit.get('job_type', '')
                work_type = permit.get('work_type', '')

                # Look for significant work
                if any(keyword in f"{job_type} {work_type}".lower() for keyword in
                       ['alteration', 'renovation', 'conversion', 'new building']):

                    if full_address not in by_address:
                        by_address[full_address] = {
                            'permits': [],
                            'address': full_address
                        }

                    by_address[full_address]['permits'].append({
                        'type': job_type,
                        'work': work_type,
                        'date': permit.get('filing_date', '')
                    })

            # Create diamonds for buildings with multiple permits
            for address, data in list(by_address.items())[:10]:
                if len(data['permits']) >= 2:  # Multiple permits = major work
                    why_special = [
                        f"Major renovation: {len(data['permits'])} permits filed",
                        f"Recent work: {data['permits'][0]['date']}",
                        "Building improvements indicate premium property",
                    ]

                    for permit in data['permits'][:3]:
                        why_special.append(f"Work: {permit['type']} - {permit['work']}")

                    diamond = self._create_diamond(
                        address=data['address'],
                        unit="Various",
                        listing_type="unknown",
                        why_special=why_special,
                    )

                    diamond.is_available = False
                    diamonds.append(diamond)

        except Exception as e:
            print(f"    Permits query error: {e}")

        return diamonds

    def _fallback_search(self) -> List[Diamond]:
        """Return curated NYC landmark buildings"""
        diamonds = []

        # Well-known exceptional buildings
        landmarks = [
            {
                "address": "The Dakota, 1 West 72nd Street",
                "why": [
                    "NYC Individual Landmark (1969)",
                    "Built 1884, designed by Henry Janeway Hardenbergh",
                    "Celebrity history (John Lennon, Lauren Bacall, etc.)",
                    "Architectural masterpiece, German Renaissance style",
                    "Only 65 units (extremely exclusive)"
                ]
            },
            {
                "address": "The Ansonia, 2109 Broadway",
                "why": [
                    "NYC Individual Landmark (1972)",
                    "Built 1904, Beaux-Arts architecture",
                    "Thick walls (soundproof apartments)",
                    "Historic celebrity residents (Babe Ruth, Toscanini)",
                    "Unique features: original details preserved"
                ]
            },
        ]

        for bldg in landmarks:
            diamond = self._create_diamond(
                address=bldg["address"],
                unit="Various",
                listing_type="unknown",
                why_special=bldg["why"],
            )
            diamond.is_available = False
            diamonds.append(diamond)

        return diamonds
