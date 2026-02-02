"""
Search strategies for finding diamond apartments

Each strategy implements a different method for discovering opportunities.
"""
from .adjacent_units import AdjacentUnitsStrategy
from .mock_finder import MockDiamondFinder
from .reddit_listener import RedditListenerStrategy
from .premium_sales_finder import PremiumSalesFinderStrategy
from .architectural_gems import ArchitecturalGemsStrategy
from .listing_archive_miner import ListingArchiveMinerStrategy

# Phase 2: Live data strategies
from .reddit_listener_live import RedditListenerLiveStrategy
from .premium_sales_live import PremiumSalesLiveStrategy

# Import additional strategies as they're created
__all__ = [
    'AdjacentUnitsStrategy',
    'MockDiamondFinder',
    'RedditListenerStrategy',
    'PremiumSalesFinderStrategy',
    'ArchitecturalGemsStrategy',
    'ListingArchiveMinerStrategy',
    'RedditListenerLiveStrategy',
    'PremiumSalesLiveStrategy',
]
