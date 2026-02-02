"""
Strategy: Reddit Scraper (No Auth Required)

Scrapes public Reddit data without API credentials.
Uses Reddit's JSON API which is publicly accessible.
"""
import sys
from pathlib import Path
import re
from typing import List, Dict
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class RedditScraperSimpleStrategy(SearchStrategy):
    """
    Scrapes public Reddit data without authentication.
    Uses Reddit's public JSON endpoints.
    """

    def __init__(self):
        super().__init__(
            name="reddit_scraper_simple",
            description="[LIVE] Scrapes public Reddit data (no auth required)"
        )

    def search(self) -> List[Diamond]:
        """Search Reddit's public JSON API"""
        diamonds = []

        try:
            import requests

            # Reddit's public JSON API (no auth needed)
            # Just add .json to any Reddit URL
            subreddits_searches = [
                ('NYCApartments', 'apartment'),
                ('AskNYC', 'apartment'),
                ('nyc', 'views'),
            ]

            findings = {}

            headers = {
                'User-Agent': 'DiamondFinder/1.0'
            }

            for subreddit, search_term in subreddits_searches:
                try:
                    # Search via public JSON API
                    url = f"https://www.reddit.com/r/{subreddit}/search.json"
                    params = {
                        'q': search_term,
                        'restrict_sr': 'on',
                        'sort': 'relevance',
                        'limit': 25,
                        't': 'year'
                    }

                    print(f"  Searching r/{subreddit} for '{search_term}'...")
                    response = requests.get(url, params=params, headers=headers, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])

                        print(f"    Found {len(posts)} posts")

                        for post in posts:
                            post_data = post.get('data', {})
                            title = post_data.get('title', '')
                            selftext = post_data.get('selftext', '')
                            text = f"{title} {selftext}"

                            # Extract apartment mentions
                            mentions = self._extract_apartments(text)

                            for mention in mentions:
                                key = f"{mention['address']}_{mention.get('unit', 'unknown')}"
                                if key in findings:
                                    findings[key]['mentions'] += 1
                                    findings[key]['quotes'].append(text[:150])
                                else:
                                    findings[key] = {
                                        **mention,
                                        'mentions': 1,
                                        'quotes': [text[:150]],
                                        'subreddit': subreddit,
                                    }

                        # Be polite to Reddit's servers
                        time.sleep(2)
                    else:
                        print(f"    HTTP {response.status_code}")

                except Exception as e:
                    print(f"    Error: {e}")
                    continue

            # Convert to diamonds
            for key, finding in findings.items():
                why_special = [
                    f"Found on Reddit: {finding['mentions']} mention(s)",
                    f"Source: r/{finding['subreddit']}",
                ]

                if finding['quotes']:
                    why_special.append(f"Context: \"{finding['quotes'][0]}\"")

                diamond = self._create_diamond(
                    address=finding['address'],
                    unit=finding.get('unit', 'Unknown'),
                    listing_type="unknown",
                    why_special=why_special,
                    social_mentions=finding['mentions'],
                )

                diamonds.append(diamond)

            print(f"  Found {len(diamonds)} diamonds from Reddit scraping")

        except ImportError:
            print(f"  ⚠ requests library not found")
            diamonds = []
        except Exception as e:
            print(f"  Error scraping Reddit: {e}")
            diamonds = []

        return diamonds

    def _extract_apartments(self, text: str) -> List[Dict]:
        """Extract NYC apartment mentions"""
        mentions = []

        # Famous NYC buildings
        famous_buildings = {
            'the dakota': '1 West 72nd Street',
            'san remo': '145 Central Park West',
            'the beresford': '211 Central Park West',
            'the eldorado': '300 Central Park West',
            '15 central park west': '15 Central Park West',
            '432 park': '432 Park Avenue',
        }

        text_lower = text.lower()

        for name, address in famous_buildings.items():
            if name in text_lower:
                mentions.append({'address': address, 'unit': None})

        # Street address patterns
        patterns = [
            r'(\d+\s+(?:East|West|North|South)?\s*\d*(?:st|nd|rd|th)?\s+(?:Street|St|Avenue|Ave))',
            r'(\d+\s+Central\s+Park\s+(?:West|East))',
            r'(\d+\s+Broadway)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                address = match.group(1).strip()

                # Look for unit nearby
                unit_search = text[match.end():match.end()+30]
                unit_pattern = r'(?:unit|apt|apartment|#)\s*([A-Z0-9]+)'
                unit_match = re.search(unit_pattern, unit_search, re.IGNORECASE)

                unit = unit_match.group(1) if unit_match else None

                mentions.append({
                    'address': address,
                    'unit': unit
                })

        return mentions
