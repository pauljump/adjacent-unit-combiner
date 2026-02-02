"""
Strategy: Adjacent Unit Combiner

Finds opportunities to buy two adjacent apartments and combine them.
This is the original strategy that inspired the whole project!
"""
import sys
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond
from typing import List


class AdjacentUnitsStrategy(SearchStrategy):
    """
    Finds adjacent unit combination opportunities.

    For now, this uses the existing adjacent-unit-combiner analysis.
    In the future, this can be automated to run continuously.
    """

    def __init__(self):
        super().__init__(
            name="adjacent_units_combiner",
            description="Find opportunities to combine adjacent apartments for arbitrage"
        )

    def search(self) -> List[Diamond]:
        """
        Search for adjacent unit opportunities.

        For the initial implementation, we'll use the existing analysis data.
        """
        diamonds = []

        # Import the existing analysis data if available
        try:
            # This is a placeholder - in a real implementation, we'd either:
            # 1. Re-run the adjacent units analysis
            # 2. Read from the cached results
            # 3. Query StreetEasy/Zillow for current listings and analyze

            # For now, let's create some example diamonds based on the top opportunities
            # from the analysis report we saw earlier

            examples = [
                {
                    "address": "315 West 86th Street",
                    "units": ("4G", "5G"),
                    "price_total": 6841897,
                    "sqft_combined": 4053,
                    "savings": 1209765,
                    "confidence": 90,
                    "adjacency": "Vertical stack, consecutive floors"
                },
                {
                    "address": "45 West 67th Street",
                    "units": ("1001", "1002"),
                    "price_total": 6994184,
                    "sqft_combined": 4091,
                    "savings": 1133953,
                    "confidence": 95,
                    "adjacency": "Same floor, adjacent units"
                },
                {
                    "address": "118 East 93rd Street",
                    "units": ("5A", "4B"),
                    "price_total": 5701493,
                    "sqft_combined": 3422,
                    "savings": 1080281,
                    "confidence": 70,
                    "adjacency": "Diagonal (corner units)"
                },
            ]

            for ex in examples:
                # Create a diamond for the combination opportunity
                why_special = [
                    f"Adjacent unit combination: {ex['units'][0]} + {ex['units'][1]}",
                    f"{ex['adjacency']} ({ex['confidence']}% confidence)",
                    f"Combined: {ex['sqft_combined']:,.0f} sqft",
                    f"Potential savings: ${ex['savings']:,.0f} ({ex['savings']/ex['price_total']*100:.1f}%)",
                    "Arbitrage through combination premium"
                ]

                diamond = self._create_diamond(
                    address=ex["address"],
                    unit=f"{ex['units'][0]}+{ex['units'][1]}",
                    listing_type="sale",
                    price=ex["price_total"],
                    sqft=ex["sqft_combined"],
                    why_special=why_special,
                    price_premium_pct=ex['savings']/ex['price_total']*100  # Treat savings as premium
                )

                diamonds.append(diamond)

        except Exception as e:
            print(f"Warning: Could not load adjacent units data: {e}")

        return diamonds
