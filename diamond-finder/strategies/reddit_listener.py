"""
Strategy: Reddit Social Listening

Searches Reddit for mentions of exceptional apartments.
Catalogs diamonds based on social proof, regardless of availability.
"""
import sys
from pathlib import Path
import re
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class RedditListenerStrategy(SearchStrategy):
    """
    Finds diamonds through Reddit social listening.

    Searches for:
    - Direct apartment mentions with praise
    - Building + unit combinations
    - People describing exceptional features

    Example signals:
    - "I lived in 315 West 86th St unit 8D for 10 years, best apartment ever"
    - "The corner units at 88 Central Park West are incredible"
    - "Just saw an amazing loft at 112 Greene Street"
    """

    def __init__(self):
        super().__init__(
            name="reddit_social_listener",
            description="Finds diamonds through Reddit social proof and mentions"
        )

    def search(self) -> List[Diamond]:
        """
        Search Reddit for apartment mentions.

        For now, returns example diamonds that WOULD be found.
        Real implementation will use Reddit API or web scraping.
        """
        diamonds = []

        # Example discoveries (in production, these would come from actual Reddit searches)
        reddit_finds = [
            {
                "address": "88 Central Park West",
                "unit": "12B",
                "source": "r/NYCApartments",
                "quote": "Lived here for 15 years. The B-line corner units have the best Central Park views in the building. Don't ever want to leave.",
                "mentions": 3,
                "keywords": ["corner", "views", "Central Park"],
                "price": None,  # Not for sale
                "bedrooms": None,
                "sqft": None,
            },
            {
                "address": "112 Greene Street",
                "unit": "5",
                "source": "r/ApartmentPorn",
                "quote": "The lofts on floor 5 are insane. 15ft ceilings, original cast iron columns, keyed elevator.",
                "mentions": 2,
                "keywords": ["loft", "high ceilings", "original details", "private elevator"],
                "price": None,
                "bedrooms": 2,
                "sqft": 2400,
            },
            {
                "address": "The Eldorado, 300 Central Park West",
                "unit": "Tower apartments",
                "source": "r/nyc",
                "quote": "The tower units at the Eldorado are architectural masterpieces. Art Deco perfection.",
                "mentions": 1,
                "keywords": ["tower", "Art Deco", "architectural"],
                "price": None,
                "bedrooms": None,
                "sqft": None,
            },
        ]

        for find in reddit_finds:
            why_special = [
                f"Social proof: Reddit mentions ({find['mentions']} times)",
                f"Quote: \"{find['quote'][:100]}...\"",
                f"Source: {find['source']}",
            ]

            # Add keyword-based reasons
            for keyword in find['keywords']:
                why_special.append(f"Mentioned feature: {keyword}")

            diamond = self._create_diamond(
                address=find["address"],
                unit=find["unit"],
                listing_type="unknown",  # Not currently listed
                price=find.get("price"),
                bedrooms=find.get("bedrooms"),
                sqft=find.get("sqft"),
                why_special=why_special,
                social_mentions=find["mentions"],
            )

            diamonds.append(diamond)

        return diamonds

    def _extract_address_from_text(self, text: str) -> Optional[tuple]:
        """
        Extract NYC address and unit from text.

        Patterns to match:
        - "315 West 86th Street unit 8D"
        - "88 Central Park West, 12B"
        - "Building at 112 Greene St apt 5"

        Returns:
            (address, unit) tuple or None
        """
        # This is a simplified version - real implementation would be more robust
        patterns = [
            r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Place|Road))[,\s]+(?:unit|apt|apartment)?\s*([A-Z0-9]+)',
            r'(\d+\s+Central Park\s+(?:West|East))[,\s]+(?:unit|apt)?\s*([A-Z0-9]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return (match.group(1), match.group(2))

        return None

    def _search_reddit_api(self, subreddits: List[str], keywords: List[str]) -> List[dict]:
        """
        Search Reddit using API or PRAW.

        This would be the real implementation in Phase 2.
        Would search for posts/comments containing keywords like:
        - "incredible apartment"
        - "best unit in building"
        - "amazing loft"
        - "perfect apartment"
        etc.

        Returns:
            List of posts/comments with apartment mentions
        """
        # Placeholder - real implementation coming
        return []


# Real implementation notes for Phase 2:
"""
To make this work with real Reddit data:

1. Install: pip install praw

2. Get Reddit API credentials:
   - Go to https://www.reddit.com/prefs/apps
   - Create an app
   - Get client_id and client_secret

3. Search subreddits:
   - r/NYCApartments
   - r/AskNYC
   - r/nyc
   - r/ApartmentPorn
   - r/InteriorDesign

4. Search terms:
   - "best apartment"
   - "incredible views"
   - "dream apartment"
   - "amazing loft"
   - "perfect location"
   - Building names + praise

5. Extract:
   - Address/building from text
   - Unit number if mentioned
   - Context (why special)
   - Upvotes (social proof)

6. Catalog everything found, even without unit numbers
   (can catalog "88 CPW corner units" as a group)
"""
