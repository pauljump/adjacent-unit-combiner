"""
Strategy: "Lived There, Loved It" Finder

Searches for people talking about apartments they LOVED living in.
Not "nice apartment" but "I lived there 10 years, best place ever."

This is pure quality of life signal.
"""
import sys
from pathlib import Path
import re
from typing import List, Dict
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class LivedThereLovedItStrategy(SearchStrategy):
    """
    Finds apartments through "I lived there and it was incredible" mentions.

    Search patterns:
    - "I lived at X for Y years"
    - "Best apartment I ever had"
    - "Never wanted to leave"
    - "The light was incredible"
    - "Perfect layout"
    """

    def __init__(self):
        super().__init__(
            name="lived_there_loved_it",
            description="[LIVE] Finds apartments people loved living in (social proof)"
        )

    def search(self) -> List[Diamond]:
        """Search for lived-experience testimonials"""
        diamonds = []

        try:
            import requests

            subreddits_and_searches = [
                ('NYCApartments', 'lived best apartment'),
                ('NYCApartments', 'amazing apartment loved'),
                ('AskNYC', 'lived incredible apartment'),
                ('AskNYC', 'never wanted to leave'),
                ('nyc', 'best apartment ever'),
                ('ApartmentPorn', 'lived nyc'),
            ]

            findings = {}
            headers = {'User-Agent': 'DiamondFinder/1.0'}

            for subreddit, query in subreddits_and_searches:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/search.json"
                    params = {
                        'q': query,
                        'restrict_sr': 'on',
                        'sort': 'relevance',
                        'limit': 25,
                        't': 'all'  # All time, not just recent
                    }

                    print(f"  Searching r/{subreddit} for '{query}'...")
                    response = requests.get(url, params=params, headers=headers, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])

                        for post in posts:
                            post_data = post.get('data', {})
                            title = post_data.get('title', '')
                            selftext = post_data.get('selftext', '')
                            text = f"{title} {selftext}"

                            # Look for quality of life testimonials
                            if self._is_lived_testimonial(text):
                                mentions = self._extract_apartments(text)

                                for mention in mentions:
                                    key = f"{mention['address']}_{mention.get('unit', 'unknown')}"

                                    # Extract what made it special
                                    special_features = self._extract_quality_signals(text)

                                    if key in findings:
                                        findings[key]['mentions'] += 1
                                        findings[key]['quotes'].append(text[:200])
                                        findings[key]['features'].extend(special_features)
                                    else:
                                        findings[key] = {
                                            **mention,
                                            'mentions': 1,
                                            'quotes': [text[:200]],
                                            'features': special_features,
                                            'subreddit': subreddit,
                                        }

                        time.sleep(2)

                except Exception as e:
                    print(f"    Error: {e}")
                    continue

            # Convert to diamonds
            for key, finding in findings.items():
                why_special = [
                    f"Lived-experience testimonial: {finding['mentions']} mention(s)",
                    f"Quote: \"{finding['quotes'][0]}\"",
                ]

                # Add specific quality signals
                for feature in set(finding['features']):
                    why_special.append(f"Quality noted: {feature}")

                diamond = self._create_diamond(
                    address=finding['address'],
                    unit=finding.get('unit', 'Unknown'),
                    listing_type="unknown",
                    why_special=why_special,
                    social_mentions=finding['mentions'],
                )

                diamonds.append(diamond)

            print(f"  Found {len(diamonds)} lived-experience diamonds")

        except Exception as e:
            print(f"  Error: {e}")

        return diamonds

    def _is_lived_testimonial(self, text: str) -> bool:
        """Check if text is a lived-experience testimonial"""
        text_lower = text.lower()

        testimonial_patterns = [
            r'i lived (at|in|there)',
            r'lived there for \d+ years',
            r'best apartment',
            r'never wanted to leave',
            r'loved living',
            r'incredible apartment',
            r'perfect (light|layout|space|apartment)',
            r'amazing (place|apartment|views|light)',
        ]

        return any(re.search(pattern, text_lower) for pattern in testimonial_patterns)

    def _extract_quality_signals(self, text: str) -> List[str]:
        """Extract what made the apartment special"""
        signals = []
        text_lower = text.lower()

        quality_patterns = {
            'light': ['light', 'bright', 'sunny', 'morning sun'],
            'views': ['view', 'central park', 'river', 'skyline'],
            'space': ['spacious', 'layout', 'high ceiling', 'loft'],
            'quiet': ['quiet', 'peaceful', 'no noise'],
            'outdoor': ['terrace', 'balcony', 'outdoor'],
            'character': ['pre-war', 'original', 'charm', 'character'],
        }

        for category, keywords in quality_patterns.items():
            if any(kw in text_lower for kw in keywords):
                signals.append(category)

        return signals

    def _extract_apartments(self, text: str) -> List[Dict]:
        """Extract apartment addresses"""
        mentions = []

        # Famous buildings
        famous = {
            'the dakota': '1 West 72nd Street',
            'beresford': '211 Central Park West',
            'san remo': '145 Central Park West',
            'ansonia': '2109 Broadway',
        }

        text_lower = text.lower()
        for name, address in famous.items():
            if name in text_lower:
                mentions.append({'address': address, 'unit': None})

        # Street addresses
        patterns = [
            r'(\d+\s+(?:East|West|North|South)?\s*\d*(?:st|nd|rd|th)?\s+(?:Street|St|Avenue|Ave))',
            r'(\d+\s+Central\s+Park\s+(?:West|East))',
            r'(\d+\s+Broadway)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                address = match.group(1).strip()
                mentions.append({'address': address, 'unit': None})

        return mentions
