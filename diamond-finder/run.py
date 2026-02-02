#!/usr/bin/env python3
"""
Diamond Finder - Main Orchestrator

Usage:
    python run.py daily      # Run daily search
    python run.py digest     # Generate digest from existing data
    python run.py evolve     # Self-improvement (generate new strategies)
    python run.py stats      # Show strategy performance stats
"""
import sys
import argparse
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import DiamondDatabase
from core.executor import StrategyExecutor
from core.reporter import DiamondReporter


def run_daily_search(db: DiamondDatabase):
    """Run all strategies and find diamonds"""
    print("\n" + "="*60)
    print("DIAMOND FINDER - DAILY SEARCH")
    print("="*60 + "\n")

    # Create executor and load strategies
    executor = StrategyExecutor(db)
    executor.load_strategies()

    # Run all strategies
    diamonds = executor.run_all_strategies()

    print(f"\n✅ Daily search complete!")
    print(f"   Found {len(diamonds)} unique diamonds")
    print(f"   Top score: {diamonds[0].score:.0f}" if diamonds else "   No diamonds found")

    return diamonds


def generate_digest(db: DiamondDatabase, output_path: str = None):
    """Generate HTML digest"""
    print("\n" + "="*60)
    print("GENERATING DIGEST")
    print("="*60 + "\n")

    reporter = DiamondReporter(db)
    html_path = reporter.generate_daily_digest(output_path=output_path)

    print(f"\n✅ Digest generated!")
    print(f"   📄 {html_path}")
    print(f"   📄 {Path(html_path).parent / 'latest.html'}")

    # Try to open in browser
    try:
        import webbrowser
        latest = Path(html_path).parent / "latest.html"
        webbrowser.open(f"file://{latest.absolute()}")
        print(f"\n   🌐 Opened in browser")
    except:
        pass

    return html_path


def show_stats(db: DiamondDatabase):
    """Show strategy performance statistics"""
    print("\n" + "="*60)
    print("STRATEGY PERFORMANCE STATS")
    print("="*60 + "\n")

    strategies = db.get_all_strategy_performance()

    if not strategies:
        print("No strategy performance data yet. Run daily search first.")
        return

    # Sort by strategy score
    strategies.sort(key=lambda s: s.strategy_score, reverse=True)

    print(f"{'Strategy':<30} {'Score':>8} {'80+':>6} {'90+':>6} {'Runs':>6} {'Status':>10}")
    print("-" * 80)

    for s in strategies:
        status = "ACTIVE" if s.is_active else "INACTIVE"
        print(f"{s.strategy_name:<30} {s.strategy_score:>8.3f} {s.diamonds_found_80plus:>6} "
              f"{s.diamonds_found_90plus:>6} {s.runs_count:>6} {status:>10}")

    print("\n" + "="*60)
    print(f"Total strategies: {len(strategies)}")
    print(f"Active: {sum(1 for s in strategies if s.is_active)}")
    print("="*60 + "\n")


def evolve_strategies(db: DiamondDatabase):
    """
    Self-improvement: analyze performance and generate new strategies

    This is a placeholder for Phase 2. Will use LLM to:
    1. Analyze which strategies are performing well
    2. Identify gaps
    3. Generate new strategy code
    4. Deploy new strategies
    """
    print("\n" + "="*60)
    print("STRATEGY EVOLUTION (Coming in Phase 2)")
    print("="*60 + "\n")

    print("This feature will:")
    print("  1. Analyze strategy performance")
    print("  2. Identify patterns in successful finds")
    print("  3. Generate new search strategies using LLM")
    print("  4. Deprecate low-performing strategies")
    print("\nFor now, strategies are manually created.")
    print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Diamond Finder - Autonomous apartment discovery")
    parser.add_argument(
        'command',
        choices=['daily', 'digest', 'stats', 'evolve', 'all'],
        help='Command to execute'
    )
    parser.add_argument(
        '--output',
        help='Output path for digest (optional)'
    )

    args = parser.parse_args()

    # Initialize database
    db = DiamondDatabase()

    # Execute command
    if args.command == 'daily':
        run_daily_search(db)
        print("\n💡 Tip: Run 'python run.py digest' to see the results in HTML")

    elif args.command == 'digest':
        generate_digest(db, args.output)

    elif args.command == 'stats':
        show_stats(db)

    elif args.command == 'evolve':
        evolve_strategies(db)

    elif args.command == 'all':
        # Run everything: search + digest
        run_daily_search(db)
        generate_digest(db, args.output)
        show_stats(db)

    print("\n✨ Done!\n")


if __name__ == "__main__":
    main()
