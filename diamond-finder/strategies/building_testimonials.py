"""
Strategy: Building Testimonials Finder

Finds buildings with positive testimonials from Vayo's database.
NO SCRAPING - queries Vayo's centralized data hub.
"""
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond
from core.vayo_client import VayoClient


class BuildingTestimonialsStrategy(SearchStrategy):
    """
    Queries Vayo for Reddit testimonials about NYC buildings.
    Uses Vayo's centralized database - no scraping needed.
    """

    def __init__(self):
        super().__init__(
            name="building_testimonials",
            description="[LIVE] Finds testimonials from Vayo's database"
        )
        self.vayo = VayoClient()

    def search(self) -> List[Diamond]:
        """Query Vayo for building testimonials"""
        diamonds = []

        try:
            # List of well-known buildings to check for testimonials
            buildings = [
                # Central Park West Classics
                ("The Dakota", "1 West 72nd Street"),
                ("San Remo", "145 Central Park West"),
                ("The Beresford", "211 Central Park West"),
                ("The Eldorado", "300 Central Park West"),
                ("The Majestic", "115 Central Park West"),
                ("The Kenilworth", "151 Central Park West"),
                ("The Century", "25 Central Park West"),
                ("The Langham", "135 Central Park West"),
                ("The Ardsley", "320 Central Park West"),

                # Upper West Side
                ("The Ansonia", "2109 Broadway"),
                ("The Apthorp", "2211 Broadway"),
                ("The Belnord", "225 West 86th Street"),
                ("The Dorilton", "171 West 71st Street"),
                ("The Chatsworth", "344 West 72nd Street"),
                ("Schwab House", "11 Riverside Drive"),

                # Upper East Side
                ("River House", "435 East 52nd Street"),
                ("740 Park Avenue", "740 Park Avenue"),
                ("The Carlyle", "35 East 76th Street"),
                ("The Stuyvesant", "98 Riverside Drive"),

                # Midtown
                ("Alwyn Court", "180 West 58th Street"),
                ("The Osborne", "205 West 57th Street"),
                ("Tudor City", "5 Tudor City Place"),

                # Chelsea/Downtown
                ("London Terrace", "470 West 24th Street"),
                ("London Terrace Towers", "410 West 24th Street"),

                # Gramercy
                ("The Gramercy", "34 Gramercy Park East"),
            ]

            for building_name, address in buildings:
                try:
                    # Query Vayo's database instead of scraping
                    testimonials = self.vayo.get_building_testimonials(building_name=building_name)

                    # Filter for positive testimonials
                    positive_testimonials = []
                    for t in testimonials:
                        # Check sentiment if available
                        if t.get('sentiment') == 'positive':
                            positive_testimonials.append(t)
                        else:
                            # Fallback: check text for positive keywords
                            text = f"{t.get('post_title', '')} {t.get('post_body', '')}".lower()
                            positive_keywords = ['love', 'incredible', 'amazing', 'best', 'perfect', 'beautiful']
                            if any(kw in text for kw in positive_keywords):
                                positive_testimonials.append(t)

                    # If we found positive mentions, create a diamond
                    if len(positive_testimonials) > 0:
                        why_special = [
                            f"Found {len(positive_testimonials)} positive Reddit mentions",
                            f"Building: {building_name}",
                        ]

                        # Add testimonial excerpts (top 3)
                        for t in positive_testimonials[:3]:
                            excerpt = t.get('post_title', '')[:100]
                            if excerpt:
                                why_special.append(f"Example: \"{excerpt}\"")

                        diamond = self._create_diamond(
                            address=address,
                            unit="Various units",
                            listing_type="unknown",
                            why_special=why_special,
                            social_mentions=len(positive_testimonials),
                        )

                        diamond.is_available = False
                        diamonds.append(diamond)

                        print(f"  {building_name}: Found {len(positive_testimonials)} positive mentions")

                except Exception as e:
                    print(f"  Error querying {building_name}: {e}")
                    continue

            print(f"  Found {len(diamonds)} buildings with positive testimonials")

        except Exception as e:
            print(f"  Error: {e}")

        return diamonds
