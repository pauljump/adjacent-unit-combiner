"""Quick test of Reddit Discovery strategy"""
import sys
sys.path.insert(0, '.')

from strategies.reddit_discovery import RedditDiscoveryStrategy

print("Testing Reddit Discovery Strategy\n")
print("=" * 60)

strategy = RedditDiscoveryStrategy()
diamonds = strategy.search()

print(f"\n\nFOUND {len(diamonds)} DIAMONDS:")
print("=" * 60)

for i, diamond in enumerate(diamonds, 1):
    print(f"\n{i}. {diamond.address}")
    print(f"   Mentions: {diamond.social_mentions}")
    print(f"   Score: {diamond.score}")
    print(f"   Why special:")
    for reason in diamond.why_special[:3]:
        print(f"     - {reason}")
