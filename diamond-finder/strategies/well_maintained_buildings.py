"""
Strategy: Well-Maintained Buildings

Finds buildings with excellent maintenance records using NYC HPD data.
Buildings with very few violations = well-maintained = better quality of life.
"""
import sys
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class WellMaintainedBuildingsStrategy(SearchStrategy):
    """
    Finds well-maintained buildings using NYC HPD violations data.

    Logic:
    - Query HPD violations for Manhattan buildings
    - Find buildings with very low violation counts
    - Cross-reference with our "great buildings" list
    - Low violations = well maintained = quality of life signal
    """

    def __init__(self):
        super().__init__(
            name="well_maintained_buildings",
            description="[LIVE] Finds well-maintained buildings via HPD data"
        )
        self.client = None
        self._init_socrata()

    def _init_socrata(self):
        """Initialize NYC Open Data client"""
        try:
            from sodapy import Socrata
            app_token = os.getenv('NYC_OPEN_DATA_KEY')
            self.client = Socrata("data.cityofnewyork.us", app_token, timeout=60)
            print(f"  ✓ HPD data initialized")
        except Exception as e:
            print(f"  ⚠ HPD init failed: {e}")
            self.client = None

    def search(self) -> List[Diamond]:
        """Find well-maintained buildings"""

        if not self.client:
            print(f"  No HPD data available")
            return []

        diamonds = []

        try:
            print(f"  Checking building maintenance records...")

            # Our list of buildings we already identified as great
            great_buildings = [
                ("The Dakota", "1 West 72nd Street"),
                ("San Remo", "145 Central Park West"),
                ("The Beresford", "211 Central Park West"),
                ("The Ansonia", "2109 Broadway"),
                ("London Terrace", "470 West 24th Street"),
                ("The Apthorp", "2211 Broadway"),
                ("The Majestic", "115 Central Park West"),
                ("River House", "435 East 52nd Street"),
                ("Tudor City", "5 Tudor City Place"),
            ]

            # For each building, check HPD violations
            for building_name, address in great_buildings[:5]:  # Start with 5
                try:
                    # Extract street info for query
                    # HPD data uses house number and street name
                    violations = self._get_violations_for_address(address)

                    # If very few violations, that's a quality signal
                    if violations is not None and violations <= 5:
                        why_special = [
                            f"Excellent maintenance record",
                            f"Only {violations} HPD violations in past year",
                            f"Well-maintained building = better quality of life",
                            f"Building: {building_name}",
                        ]

                        if violations == 0:
                            why_special.insert(0, "ZERO HPD violations (extremely rare)")

                        diamond = self._create_diamond(
                            address=address,
                            unit="Various units",
                            listing_type="unknown",
                            why_special=why_special,
                        )

                        diamond.is_available = False
                        diamonds.append(diamond)

                        print(f"    {building_name}: {violations} violations ✓")
                    else:
                        if violations:
                            print(f"    {building_name}: {violations} violations (too many)")

                except Exception as e:
                    print(f"    Error checking {building_name}: {e}")
                    continue

            print(f"  Found {len(diamonds)} well-maintained buildings")

        except Exception as e:
            print(f"  HPD query error: {e}")

        return diamonds

    def _get_violations_for_address(self, address: str) -> int:
        """
        Query HPD violations for a specific address.
        Returns count of open violations.
        """
        try:
            # Parse address (simplified - would need better parsing)
            parts = address.split()
            house_number = parts[0]
            street_name = ' '.join(parts[1:])

            # Query HPD violations
            # Dataset: wvxf-dwi5 (HPD Violations)
            # Only check recent violations (past year)
            cutoff_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

            results = self.client.get(
                "wvxf-dwi5",
                where=f"housenumber='{house_number}' AND streetname LIKE '%{street_name}%' AND violationstatus='Open' AND novissueddate >= '{cutoff_date}'",
                limit=100,
                select="violationid"
            )

            return len(results)

        except Exception as e:
            # If query fails, return None to indicate unknown
            return None


# Future enhancement: Also check HPD registrations to find buildings with
# responsive owners who maintain their properties well
