"""
Strategy: Reddit Discovery

Searches Reddit for general discussions about great NYC buildings/apartments.
Instead of searching for specific buildings, finds building names mentioned
in threads about "best apartments" or "favorite buildings".
"""
import sys
from pathlib import Path
from typing import List, Set
import time
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class RedditDiscoveryStrategy(SearchStrategy):
    """
    Discovers NYC buildings from open-ended Reddit discussions.
    Searches for terms like "best building" and extracts mentioned addresses.
    """

    def __init__(self):
        super().__init__(
            name="reddit_discovery",
            description="[LIVE] Discovers buildings from Reddit discussions"
        )

    def search(self) -> List[Diamond]:
        """Search Reddit for building discoveries"""
        diamonds = []

        try:
            import requests

            # More specific search queries about residential experiences
            search_queries = [
                "lived at building Manhattan loved",
                "apartment building recommend NYC",
                "best prewar Manhattan lived",
            ]

            headers = {'User-Agent': 'DiamondFinder/1.0'}
            subreddits = ['NYCApartments', 'AskNYC', 'nyc']

            discovered_buildings = {}  # address -> {name, mentions, testimonials}

            for query in search_queries:
                print(f"  Searching: '{query}'...")

                for subreddit in subreddits:
                    try:
                        url = f"https://www.reddit.com/r/{subreddit}/search.json"
                        params = {
                            'q': query,
                            'restrict_sr': 'on',
                            'sort': 'relevance',
                            'limit': 5,  # Keep small
                            't': 'all'
                        }

                        response = requests.get(url, params=params, headers=headers, timeout=10)

                        if response.status_code == 200:
                            data = response.json()
                            posts = data.get('data', {}).get('children', [])

                            for post in posts:
                                post_data = post.get('data', {})
                                title = post_data.get('title', '')
                                selftext = post_data.get('selftext', '')
                                text = f"{title} {selftext}"

                                # Extract potential building names
                                buildings = self._extract_building_names(text)

                                for building_name in buildings:
                                    if building_name not in discovered_buildings:
                                        discovered_buildings[building_name] = {
                                            'mentions': 0,
                                            'testimonials': []
                                        }

                                    discovered_buildings[building_name]['mentions'] += 1

                                    # Save a snippet
                                    snippet = (title + ' ' + selftext)[:150]
                                    discovered_buildings[building_name]['testimonials'].append(snippet)

                        time.sleep(1)  # Rate limit

                    except Exception as e:
                        print(f"    Error searching {subreddit}: {e}")
                        continue

                time.sleep(2)  # Between queries

            # Create diamonds from discoveries
            for building_name, data in discovered_buildings.items():
                if data['mentions'] >= 2:  # Only if mentioned multiple times
                    why_special = [
                        f"Discovered in {data['mentions']} Reddit discussions",
                        f"Building: {building_name}",
                        "Found organically in 'best building' conversations",
                    ]

                    # Add best testimonial
                    if data['testimonials']:
                        why_special.append(f"Example: \"{data['testimonials'][0]}\"")

                    diamond = self._create_diamond(
                        address=building_name,
                        unit="Various units",
                        listing_type="unknown",
                        why_special=why_special,
                        social_mentions=data['mentions'],
                    )

                    diamond.is_available = False
                    diamonds.append(diamond)

            print(f"  Discovered {len(diamonds)} buildings organically")

        except Exception as e:
            print(f"  Error: {e}")

        return diamonds

    def _extract_building_names(self, text: str) -> Set[str]:
        """
        Extract potential NYC residential building names from text.
        Focuses on named buildings and apartment addresses.
        """
        buildings = set()

        # Non-residential keywords to filter out
        exclude_keywords = [
            'pizza', 'bagel', 'cafe', 'restaurant', 'bar', 'subway', 'station',
            'church', 'cathedral', 'school', 'hospital', 'museum', 'store',
            'mall', 'plaza', 'market', 'bazaar', 'trader', 'cents',
            'oculus', 'tramway', 'bridge', 'tunnel', 'park', 'pond', 'lake'
        ]

        # Pattern 1: "The [Name]" - only for likely residential building names
        the_pattern = r'The [A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}'  # Max 3 words
        matches = re.findall(the_pattern, text)
        for match in matches:
            match_lower = match.lower()

            # Skip if contains excluded keywords
            if any(keyword in match_lower for keyword in exclude_keywords):
                continue

            # Skip overly generic names
            if match in ['The City', 'The Street', 'The Building', 'The Apartment',
                        'The Heights', 'The Local', 'The Radio', 'The Daily']:
                continue

            # Only include if it seems like a building name (ends with common suffixes or is known)
            if any(word in match for word in ['Dakota', 'Ansonia', 'Beresford', 'Apthorp',
                                               'Belnord', 'Dorilton', 'San Remo', 'Eldorado',
                                               'Majestic', 'Century', 'Langham', 'Chatsworth']):
                buildings.add(match)

        # Pattern 2: Street addresses like "145 Central Park West"
        # Only match full addresses with street numbers
        address_pattern = r'\d{1,5}\s+(?:East|West|North|South|Central\s+Park)\s+\w+(?:\s+\w+)*\s+(?:Street|Avenue|Place|Drive|Boulevard|Way|Road|West|East)'
        matches = re.findall(address_pattern, text)
        for match in matches:
            match_lower = match.lower()

            # Skip if contains excluded keywords
            if any(keyword in match_lower for keyword in exclude_keywords):
                continue

            # Only include Manhattan-area addresses
            if any(area in match for area in ['Park Avenue', 'Madison Avenue', 'Fifth Avenue',
                                               'Central Park', 'Broadway', 'Riverside',
                                               'East End', 'West End']):
                buildings.add(match.strip())

        return buildings
