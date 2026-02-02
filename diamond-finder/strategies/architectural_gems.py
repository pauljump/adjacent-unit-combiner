"""
Strategy: Architectural Gems Finder

Analyzes building floor plans and layouts to identify rare,
exceptional unit configurations - regardless of current availability.

Logic: In any building, certain units are objectively better due to:
- Corner locations (more light, more views)
- Top floors (but not overpriced penthouses)
- Outdoor space (terraces, balconies)
- Unique layouts (duplexes, through-floor)
- Size outliers (largest unit on floor)
"""
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class ArchitecturalGemsStrategy(SearchStrategy):
    """
    Finds diamonds through architectural analysis.

    Identifies exceptional units by analyzing:
    1. Building floor plans (NYC DOB records)
    2. Unit positions (corner, top floor, etc.)
    3. Outdoor space (terraces, balconies)
    4. Rare configurations
    """

    def __init__(self):
        super().__init__(
            name="architectural_gems",
            description="Finds diamonds through building/floor plan analysis"
        )

    def search(self) -> List[Diamond]:
        """
        Analyze buildings to find architectural gems.

        Real implementation would:
        1. Query DOB for building floor plans
        2. Analyze unit positions and features
        3. Identify rare/exceptional configurations
        """
        diamonds = []

        # Example architectural gems (in production, from floor plan analysis)
        gems = [
            {
                "address": "The Beresford, 211 Central Park West",
                "unit": "Tower units (ending in 'A' on floors 15+)",
                "why_special": [
                    "Only 3 tower corner units in entire building",
                    "360-degree views of Central Park and Hudson",
                    "Art Deco architectural masterpiece",
                    "Original 1929 layouts with 14ft ceilings",
                    "Private elevator access to tower units"
                ],
                "rarity_score": 95,
                "estimated_units": 3,
            },
            {
                "address": "200 Amsterdam Avenue",
                "unit": "Penthouse units 60-61",
                "why_special": [
                    "Only 2 units on top floor",
                    "Private terraces (1,000+ sqft each)",
                    "Through-floor possible (combine 60+61)",
                    "Unobstructed Central Park views",
                    "Robert A.M. Stern design"
                ],
                "rarity_score": 92,
                "estimated_units": 2,
            },
            {
                "address": "443 Greenwich Street",
                "unit": "Corner N-line units",
                "why_special": [
                    "Tadao Ando's only NYC residential building",
                    "Corner N-line: 2 exposures vs 1 for other units",
                    "Northern light (preferred for artists)",
                    "Only 12 N-line units in 53-story building",
                    "Floor-to-ceiling windows"
                ],
                "rarity_score": 88,
                "estimated_units": 12,
            },
            {
                "address": "The Woolworth Tower Residences, 2 Park Place",
                "unit": "Former office floors (24-29)",
                "why_special": [
                    "Historic Woolworth Building conversion",
                    "Original 1913 terra cotta and Gothic details",
                    "Units with original office ceiling heights (12-14ft)",
                    "Some units have original gilded ceilings",
                    "Only 33 residential units in landmark building"
                ],
                "rarity_score": 90,
                "estimated_units": 6,
            },
            {
                "address": "160 Leroy Street",
                "unit": "Units with Hudson River views (West-facing)",
                "why_special": [
                    "Ian Schrager building in West Village",
                    "Only west-facing units have river views",
                    "Floor-to-ceiling glass",
                    "Approximately 40% of units",
                    "Herzog & de Meuron architecture"
                ],
                "rarity_score": 82,
                "estimated_units": 24,
            },
        ]

        for gem in gems:
            why_special = gem['why_special'].copy()
            why_special.insert(0, f"Architectural rarity score: {gem['rarity_score']}/100")
            why_special.append(f"Estimated {gem['estimated_units']} such units exist")

            diamond = self._create_diamond(
                address=gem["address"],
                unit=gem["unit"],
                listing_type="unknown",  # Not about current listings
                why_special=why_special,
            )

            # These aren't currently available - we're just cataloging they exist
            diamond.is_available = False

            diamonds.append(diamond)

        return diamonds

    def _analyze_building_geometry(self, address: str) -> dict:
        """
        Analyze building floor plan to identify best units.

        Would use:
        1. NYC DOB floor plans
        2. Building height data
        3. Surrounding building heights (for view analysis)
        4. Sun path analysis

        Identifies:
        - Corner units
        - Top floor units
        - Units with terraces/outdoor space
        - Through-floor potential
        - View corridors

        Returns:
            Dictionary with exceptional units identified
        """
        # Placeholder - real implementation in Phase 2
        return {
            "corner_units": [],
            "top_floor_units": [],
            "terrace_units": [],
            "view_units": [],
        }

    def _fetch_dob_floor_plans(self, address: str) -> Optional[dict]:
        """
        Fetch building floor plans from NYC DOB.

        NYC Department of Buildings has:
        - Original building plans
        - Alteration records
        - Certificate of Occupancy layouts

        Available via:
        - DOB NOW portal
        - Public records request
        - Some digitized in Building Information System (BIS)

        Returns:
            Floor plan data if available
        """
        # Placeholder - real implementation in Phase 2
        return None

    def _identify_rare_configurations(self, building_data: dict) -> List[dict]:
        """
        Identify rare unit configurations in a building.

        Analyzes:
        1. Unit count by layout type
        2. Position (corner vs interior)
        3. Exposure (number of exterior walls)
        4. Floor level
        5. Outdoor space
        6. Ceiling height
        7. Special features (private elevator, etc.)

        Rare = 20% or less of units have this configuration

        Returns:
            List of rare unit identifiers
        """
        # Placeholder - real implementation in Phase 2
        return []


# Real implementation notes for Phase 2:
"""
To make this work with real building data:

1. Data Sources:
   - NYC DOB BIS (Building Information System)
     * Floor plans for many buildings
     * Alteration records
     * C of O documents

   - NYC PLUTO (tax lot data)
     * Building footprint
     * Number of floors
     * Year built

   - StreetEasy building pages
     * Often show floor plans
     * List unit mix (# of each layout)

   - Offering plans (for condos/co-ops)
     * Detailed floor plans
     * Unit mix
     * Available from NY AG office

2. Analysis Approach:

   a) Corner Detection:
      - Building footprint + unit positions
      - Corner = 2+ exterior walls
      - Worth 20-30% premium typically

   b) View Analysis:
      - Unit floor + direction
      - Surrounding building heights (PLUTO)
      - Identify view corridors
      - Sun path (south/east = morning sun)

   c) Outdoor Space:
      - Setbacks in building (stepped design)
      - Units on setback floors = terrace potential
      - Roof access

   d) Rarity Scoring:
      - Building has 200 units
      - Only 8 are corners = 4% = high rarity score
      - Only 12 have terraces = 6% = high rarity

   e) Architectural Significance:
      - Famous architect (Tadao Ando, Robert A.M. Stern, etc.)
      - Landmark status
      - Unique features (original details, ceiling heights)

3. Target Buildings:
   - Start with famous/landmark buildings
   - Pre-war (1920s-1940s) often have best details
   - Architect-designed modern buildings
   - Boutique buildings (fewer units = more rarity)

4. Output Format:
   - "Building X, units Y-Z are the gems"
   - Specific units if identifiable
   - Groups if not ("corner units")
   - Catalog ALL of them for monitoring

5. Examples of Rare Features:
   - Private elevator
   - Duplex/triplex
   - Through-floor potential
   - Wraparound terrace
   - Original fireplaces/details
   - Double-height ceilings
   - Outdoor fireplace
   - Plunge pool
"""
