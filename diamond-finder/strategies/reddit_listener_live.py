"""
Strategy: Reddit Social Listening (LIVE VERSION)

Searches Reddit for mentions of exceptional apartments using real Reddit API.
Catalogs diamonds based on social proof, regardless of availability.
"""
import sys
import os
import re
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.strategy_base import SearchStrategy
from core.models import Diamond


class RedditListenerLiveStrategy(SearchStrategy):
    """
    Finds diamonds through real Reddit social listening using PRAW.

    Searches:
    - r/NYCApartments
    - r/AskNYC
    - r/nyc
    - r/ApartmentPorn
    - r/InteriorDesign

    For keywords like:
    - "incredible apartment"
    - "best unit"
    - "amazing views"
    - Building names + praise
    """

    def __init__(self):
        super().__init__(
            name="reddit_social_listener_live",
            description="[LIVE] Finds diamonds through real Reddit API social listening"
        )
        self.reddit = None
        self._init_reddit()

    def _init_reddit(self):
        """Initialize Reddit API connection"""
        try:
            import praw

            # Try to get credentials from environment
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'DiamondFinder/1.0')

            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                print(f"  ✓ Reddit API initialized")
            else:
                print(f"  ⚠ No Reddit credentials found (set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)")
                print(f"    Get credentials: https://www.reddit.com/prefs/apps")
                self.reddit = None

        except ImportError:
            print(f"  ⚠ PRAW not installed: pip install praw")
            self.reddit = None
        except Exception as e:
            print(f"  ⚠ Reddit API init failed: {e}")
            self.reddit = None

    def search(self) -> List[Diamond]:
        """
        Search Reddit for apartment mentions.
        """
        if not self.reddit:
            print("  → Using fallback mode (no Reddit API)")
            return self._fallback_search()

        diamonds = []

        # Subreddits to search
        subreddits = [
            'NYCApartments',
            'AskNYC',
            'nyc',
            'ApartmentPorn',
            'InteriorDesign',
        ]

        # Search terms
        search_queries = [
            'incredible apartment new york',
            'best apartment nyc',
            'dream apartment manhattan',
            'amazing loft',
            'perfect views',
            'corner unit',
        ]

        findings = {}  # De-duplicate by address+unit

        try:
            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)

                for query in search_queries:
                    try:
                        # Search recent posts and comments
                        for submission in subreddit.search(query, time_filter='year', limit=20):
                            # Extract from title and selftext
                            text = f"{submission.title} {submission.selftext}"
                            mentions = self._extract_apartments(text)

                            for mention in mentions:
                                key = f"{mention['address']}_{mention.get('unit', 'unknown')}"
                                if key in findings:
                                    findings[key]['mentions'] += 1
                                    findings[key]['quotes'].append(text[:200])
                                else:
                                    findings[key] = {
                                        **mention,
                                        'mentions': 1,
                                        'quotes': [text[:200]],
                                        'subreddit': subreddit_name,
                                    }

                    except Exception as e:
                        print(f"  Warning: Search failed for '{query}' in r/{subreddit_name}: {e}")
                        continue

        except Exception as e:
            print(f"  Error searching Reddit: {e}")

        # Convert findings to diamonds
        for key, finding in findings.items():
            why_special = [
                f"Social proof: {finding['mentions']} Reddit mention(s)",
                f"Source: r/{finding['subreddit']}",
            ]

            # Add best quote
            if finding['quotes']:
                best_quote = finding['quotes'][0]
                why_special.append(f"Quote: \"{best_quote}...\"")

            diamond = self._create_diamond(
                address=finding['address'],
                unit=finding.get('unit', 'Unknown'),
                listing_type="unknown",
                why_special=why_special,
                social_mentions=finding['mentions'],
            )

            diamonds.append(diamond)

        print(f"  Found {len(diamonds)} diamonds from Reddit")
        return diamonds

    def _fallback_search(self) -> List[Diamond]:
        """Fallback to example data when API not available"""
        from .reddit_listener import RedditListenerStrategy
        fallback = RedditListenerStrategy()
        return fallback.search()

    def _extract_apartments(self, text: str) -> List[Dict]:
        """
        Extract NYC apartment mentions from text.

        Returns list of dicts with 'address' and optional 'unit'
        """
        mentions = []

        # Common NYC building names (famous buildings)
        famous_buildings = {
            'the dakota': '1 West 72nd Street',
            'san remo': '145 Central Park West',
            'the beresford': '211 Central Park West',
            'the eldorado': '300 Central Park West',
            'the ansonia': '2109 Broadway',
            '15 central park west': '15 Central Park West',
            '432 park': '432 Park Avenue',
            'one57': '157 West 57th Street',
        }

        text_lower = text.lower()

        # Check for famous buildings
        for name, address in famous_buildings.items():
            if name in text_lower:
                mentions.append({'address': address, 'unit': None})

        # Pattern: street address
        # Examples:
        # - "315 West 86th Street"
        # - "88 Central Park West"
        # - "112 Greene Street apt 5"

        patterns = [
            # Number + Street Name + (Street|St|Avenue|Ave) + optional unit
            r'(\d+\s+(?:East|West|North|South)?\s*\d*(?:st|nd|rd|th)?\s+(?:Street|St|Avenue|Ave|Place|Road))',
            # Central Park West/East patterns
            r'(\d+\s+Central\s+Park\s+(?:West|East))',
            # Broadway patterns
            r'(\d+\s+Broadway)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                address = match.group(1).strip()

                # Try to find unit number nearby
                # Look 20 characters ahead for patterns like "unit 5A", "apt 12B", "#8D"
                unit_search = text[match.end():match.end()+30]
                unit_pattern = r'(?:unit|apt|apartment|#)\s*([A-Z0-9]+)'
                unit_match = re.search(unit_pattern, unit_search, re.IGNORECASE)

                unit = unit_match.group(1) if unit_match else None

                mentions.append({
                    'address': address,
                    'unit': unit
                })

        return mentions


# Usage instructions:
"""
To enable live Reddit searching:

1. Get Reddit API credentials:
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" type
   - Fill in:
     * name: DiamondFinder
     * redirect uri: http://localhost:8080
   - Copy the client_id (under app name) and client_secret

2. Set environment variables:
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USER_AGENT="DiamondFinder/1.0"

   Or create a .env file (see .env.example)

3. Run the system:
   python3 run.py daily

The strategy will automatically use live Reddit data if credentials are found,
or fall back to example data if not.
"""
