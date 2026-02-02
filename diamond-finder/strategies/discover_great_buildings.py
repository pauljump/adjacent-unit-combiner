"""
Strategy: Discover Great Buildings (Data-Driven)

Instead of hardcoding 26 buildings, discover thousands using Vayo's database.

Discovery criteria:
1. Pre-war buildings (built before 1945) - classic construction
2. 20+ units (actual apartment buildings, not townhouses)
3. Low complaint ratio (complaints per unit)
4. Manhattan (expand to Brooklyn later)
5. Then score each discovered building
"""
import sys
import os
from pathlib import Path
from typing import List
import sqlite3

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class DiscoverGreatBuildingsStrategy(SearchStrategy):
    """
    Discovers great buildings from Vayo's 571K building database.
    Uses data signals, not manual curation.
    """

    def __init__(self):
        super().__init__(
            name="discover_great_buildings",
            description="[LIVE] Discovers great buildings from 571K building database"
        )
        self.vayo_db_path = "/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/stuytown.db"

    def search(self) -> List[Diamond]:
        """Discover buildings using data"""

        if not os.path.exists(self.vayo_db_path):
            print(f"  Vayo database not found: {self.vayo_db_path}")
            return []

        diamonds = []

        try:
            print(f"  Connecting to Vayo database (571K buildings)...")
            conn = sqlite3.connect(self.vayo_db_path)
            cursor = conn.cursor()

            # Query for great building candidates
            query = """
            SELECT
                b.bin,
                b.address,
                b.borough,
                b.num_units,
                b.year_built,
                COUNT(DISTINCT c.complaint_id) as complaint_count,
                CAST(COUNT(DISTINCT c.complaint_id) AS FLOAT) / NULLIF(b.num_units, 0) as complaint_ratio
            FROM buildings b
            LEFT JOIN complaints c ON b.bin = c.bin
            WHERE
                UPPER(b.borough) = 'MANHATTAN'
                AND b.year_built < 1945  -- Pre-war
                AND b.year_built > 1800  -- Valid years only
                AND b.num_units >= 20     -- Actual apartment buildings
                AND b.num_units <= 500    -- Not massive towers
            GROUP BY b.bin
            HAVING complaint_ratio < 10    -- Low complaints per unit (relaxed)
            ORDER BY complaint_ratio ASC, b.year_built ASC
            LIMIT 500                     -- Top 500 candidates (SCALE UP!)
            """

            cursor.execute(query)
            results = cursor.fetchall()

            print(f"  Found {len(results)} great building candidates")

            for row in results[:100]:  # Process top 100 (was 20)
                bin, address, borough, units, year_built, complaints, ratio = row

                why_special = [
                    f"Discovered from 571K building database",
                    f"Pre-war classic: Built {year_built}",
                    f"{units} units in building",
                    f"Only {complaints} total complaints",
                    f"Complaint ratio: {ratio:.2f} per unit (excellent!)",
                ]

                if ratio < 1:
                    why_special.insert(0, f"EXCEPTIONAL: Less than 1 complaint per unit!")

                diamond = self._create_diamond(
                    address=address,
                    unit="Various units",
                    listing_type="unknown",
                    why_special=why_special,
                )

                diamond.is_available = False
                diamonds.append(diamond)

            conn.close()

            print(f"  Created {len(diamonds)} building diamonds")

        except Exception as e:
            print(f"  Error querying Vayo database: {e}")
            import traceback
            traceback.print_exc()

        return diamonds


# Next iteration: Join with ACRIS to find low turnover buildings
# Next iteration: Join with energy benchmarking to find efficient buildings
# Next iteration: Expand to 1000s of buildings, not just 100
