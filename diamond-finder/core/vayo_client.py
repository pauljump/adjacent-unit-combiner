"""
Vayo Client - Query interface for Vayo's data hub

Vayo is the centralized NYC real estate data platform that scrapes,
stores, and serves data from 10+ sources into a single 30GB database.

This client provides a clean Python interface for Rough Quarters to
query Vayo's data without needing to scrape or duplicate data.
"""
import sqlite3
from typing import List, Dict, Optional


class VayoClient:
    """
    Client to query Vayo's centralized NYC real estate database.

    Vayo Location: /Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/
    Database: stuytown.db (30GB)
    Tables: 36+ (buildings, complaints, listings, testimonials, etc.)
    """

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = "/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/stuytown.db"
        self.db_path = db_path

    def get_buildings(self, criteria: Optional[Dict] = None) -> List[Dict]:
        """
        Query buildings table (571,476 buildings)

        Args:
            criteria: Optional filters
                {
                    'borough': 'MANHATTAN',
                    'year_built': {'<': 1945},
                    'num_units': {'>=': 20, '<=': 500}
                }

        Returns:
            List of building dicts with keys: bin, address, borough, etc.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        query = "SELECT * FROM buildings WHERE 1=1"
        params = []

        if criteria:
            # Borough filter
            if 'borough' in criteria:
                query += " AND UPPER(borough) = ?"
                params.append(criteria['borough'].upper())

            # Year built filter
            if 'year_built' in criteria:
                if isinstance(criteria['year_built'], dict):
                    for op, value in criteria['year_built'].items():
                        query += f" AND year_built {op} ?"
                        params.append(value)
                else:
                    query += " AND year_built = ?"
                    params.append(criteria['year_built'])

            # Num units filter
            if 'num_units' in criteria:
                if isinstance(criteria['num_units'], dict):
                    for op, value in criteria['num_units'].items():
                        query += f" AND num_units {op} ?"
                        params.append(value)
                else:
                    query += " AND num_units = ?"
                    params.append(criteria['num_units'])

        cursor = conn.execute(query, params)
        buildings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return buildings

    def get_building_testimonials(self, building_name: str = None, bin: str = None) -> List[Dict]:
        """
        Get Reddit testimonials for a building.

        Args:
            building_name: e.g., "The Dakota"
            bin: NYC Building Identification Number

        Returns:
            List of testimonial dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        if bin:
            query = "SELECT * FROM reddit_testimonials WHERE bin = ?"
            params = [bin]
        elif building_name:
            query = "SELECT * FROM reddit_testimonials WHERE building_name LIKE ?"
            params = [f"%{building_name}%"]
        else:
            query = "SELECT * FROM reddit_testimonials"
            params = []

        cursor = conn.execute(query, params)
        testimonials = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return testimonials

    def get_complaints_for_building(self, bin: str) -> List[Dict]:
        """Get HPD complaints for a building (26M+ total complaints)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            "SELECT * FROM complaints WHERE bin = ?",
            [bin]
        )
        complaints = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return complaints

    def get_current_listings(self, source: str = None, address: str = None) -> List[Dict]:
        """
        Get current rental/sale listings.

        Args:
            source: 'craigslist', 'reddit', 'realtor', 'streeteasy'
            address: Filter by building address

        Returns:
            List of listing dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Note: Currently using craigslist_listings table
        # After Realtor import, will be unified 'listings' table
        query = "SELECT * FROM craigslist_listings WHERE 1=1"
        params = []

        if source:
            query += " AND source = ?"
            params.append(source)

        if address:
            query += " AND address LIKE ?"
            params.append(f"%{address}%")

        cursor = conn.execute(query, params)
        listings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return listings

    def get_building_health_score(self, bin: str) -> int:
        """
        Get Vayo's building health score (0-100).

        Based on complaints per unit ratio.
        Used by Vayo's RentIntel "Apartment Carfax" reports.
        """
        conn = sqlite3.connect(self.db_path)

        # Get building info
        building = conn.execute(
            "SELECT num_units FROM buildings WHERE bin = ?",
            [bin]
        ).fetchone()

        if not building or not building[0]:
            conn.close()
            return 50  # Default

        units = building[0]

        # Count complaints
        complaint_count = conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE bin = ?",
            [bin]
        ).fetchone()[0]

        conn.close()

        # Vayo's scoring algorithm
        complaints_per_unit = complaint_count / units if units > 0 else 0

        if complaints_per_unit < 0.5:
            return 100
        elif complaints_per_unit < 1:
            return 95
        elif complaints_per_unit < 2:
            return 80
        elif complaints_per_unit < 5:
            return 60
        elif complaints_per_unit < 10:
            return 40
        else:
            return 20

    def get_rental_history(self, building_id: str, unit: str = None) -> List[Dict]:
        """Get rent history for a building/unit from current_rents table"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        if unit:
            query = "SELECT * FROM current_rents WHERE building_id = ? AND unit_number = ?"
            params = [building_id, unit]
        else:
            query = "SELECT * FROM current_rents WHERE building_id = ?"
            params = [building_id]

        cursor = conn.execute(query, params)
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return history
