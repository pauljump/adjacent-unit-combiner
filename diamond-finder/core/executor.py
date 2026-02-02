"""
Strategy executor - runs all search strategies and aggregates results
"""
import importlib
import sys
from pathlib import Path
from typing import List
from datetime import datetime

from .models import Diamond, StrategyPerformance
from .database import DiamondDatabase
from .scorer_quality_of_life import score_diamond_qol
from .strategy_base import SearchStrategy


class StrategyExecutor:
    """Executes all active search strategies"""

    def __init__(self, db: DiamondDatabase):
        self.db = db
        self.strategies: List[SearchStrategy] = []

    def load_strategies(self):
        """Dynamically load all strategy modules"""
        strategies_dir = Path(__file__).parent.parent / "strategies"

        # Import all strategy classes
        sys.path.insert(0, str(strategies_dir.parent))

        try:
            from strategies.adjacent_units import AdjacentUnitsStrategy
            from strategies.discover_great_buildings import DiscoverGreatBuildingsStrategy
            from strategies.building_testimonials import BuildingTestimonialsStrategy
            from strategies.long_tenure_simple import LongTenureSimpleStrategy
            from strategies.well_maintained_buildings import WellMaintainedBuildingsStrategy
            from strategies.realtor_listings_live import RealtorListingsLiveStrategy
            # from strategies.reddit_discovery import RedditDiscoveryStrategy  # Disabled: too noisy

            self.strategies = [
                AdjacentUnitsStrategy(),  # Your original combinations
                DiscoverGreatBuildingsStrategy(),  # DATA-DRIVEN: Discover 100s from 571K buildings!
                BuildingTestimonialsStrategy(),  # LIVE: Reddit testimonials (26 buildings)
                LongTenureSimpleStrategy(),  # LIVE: Long tenure (20+ years)
                WellMaintainedBuildingsStrategy(),  # LIVE: HPD violations data
                RealtorListingsLiveStrategy(),  # LIVE: Actual available units! (Realtor.com)
                # RedditDiscoveryStrategy(),  # Disabled: pattern matching too noisy
            ]

            print(f"Loaded {len(self.strategies)} strategies")
            for strategy in self.strategies:
                print(f"  - {strategy.name}: {strategy.description}")

        except Exception as e:
            print(f"Error loading strategies: {e}")
            import traceback
            traceback.print_exc()

    def run_all_strategies(self) -> List[Diamond]:
        """
        Execute all strategies and return aggregated, scored diamonds

        Returns:
            List of scored Diamond objects
        """
        all_diamonds = []
        diamonds_by_id = {}  # For deduplication

        print(f"\n{'='*60}")
        print(f"Running {len(self.strategies)} strategies...")
        print(f"{'='*60}\n")

        for strategy in self.strategies:
            print(f"Running: {strategy.name}")

            try:
                # Execute strategy
                candidates = strategy.search()
                print(f"  Found {len(candidates)} candidates")

                # Initialize performance tracking
                perf = self.db.get_strategy_performance(strategy.name)
                if not perf:
                    perf = StrategyPerformance(strategy_name=strategy.name)

                perf.last_run = datetime.now()
                perf.runs_count += 1
                perf.total_candidates += len(candidates)

                # Track unique buildings
                unique_buildings = set()

                # Score each candidate
                for diamond in candidates:
                    # Score the diamond (quality of life focused)
                    score_diamond_qol(diamond)

                    # Track unique buildings
                    unique_buildings.add(diamond.address)

                    # Track photos
                    perf.total_photos_found += len(diamond.photos)

                    # Update performance stats
                    if diamond.score >= 90:
                        perf.diamonds_found_90plus += 1
                    if diamond.score >= 80:
                        perf.diamonds_found_80plus += 1

                    # Merge with existing diamonds (same ID from different strategies)
                    if diamond.id in diamonds_by_id:
                        existing = diamonds_by_id[diamond.id]
                        # Merge strategies
                        existing.found_by_strategies = list(set(
                            existing.found_by_strategies + diamond.found_by_strategies
                        ))
                        # Merge social mentions (take max, since they should be the same)
                        existing.social_mentions = max(existing.social_mentions, diamond.social_mentions)
                        # Merge why_special
                        existing.why_special = list(set(existing.why_special + diamond.why_special))
                        # Merge photos
                        existing.photos = list(set(existing.photos + diamond.photos))
                        # Re-score with merged data
                        score_diamond_qol(existing)
                        # Track updated score
                        if existing.score >= 90:
                            perf.diamonds_found_90plus += 1
                        if existing.score >= 80:
                            perf.diamonds_found_80plus += 1
                        # Save merged diamond to database
                        self.db.save_diamond(existing)
                    else:
                        diamonds_by_id[diamond.id] = diamond
                        # Save to database
                        self.db.save_diamond(diamond)

                # Update unique buildings count
                perf.unique_buildings = len(unique_buildings)

                # Save performance
                self.db.update_strategy_performance(perf)

                print(f"  Performance: {perf.diamonds_found_80plus} diamonds (80+), {perf.diamonds_found_90plus} diamonds (90+)")

            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()

        # Get all unique diamonds
        all_diamonds = list(diamonds_by_id.values())

        # Sort by score
        all_diamonds.sort(key=lambda d: d.score, reverse=True)

        print(f"\n{'='*60}")
        print(f"Total unique diamonds: {len(all_diamonds)}")
        print(f"Saved to database: {self.db.get_diamond_count()} total")
        print(f"{'='*60}\n")

        return all_diamonds

    def get_strategy_stats(self) -> List[StrategyPerformance]:
        """Get performance stats for all strategies"""
        return self.db.get_all_strategy_performance()
