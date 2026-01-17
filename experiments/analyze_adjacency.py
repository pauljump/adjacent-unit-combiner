#!/usr/bin/env python3
"""
Analyze Manhattan listings to find adjacent units that can be combined.
Implements adjacency detection logic from IDEA-155.
"""

import json
from collections import defaultdict
from typing import List, Dict, Tuple
import re


class AdjacencyAnalyzer:
    def __init__(self, listings: List[Dict]):
        self.listings = listings
        self.by_building = self._group_by_building()

    def _group_by_building(self) -> Dict[str, List[Dict]]:
        """Group listings by building address"""
        grouped = defaultdict(list)
        for listing in self.listings:
            grouped[listing["address"]].append(listing)
        return grouped

    def find_adjacent_pairs(self) -> List[Dict]:
        """Find all adjacent unit pairs across all buildings"""
        all_pairs = []

        for building_address, units in self.by_building.items():
            if len(units) < 2:
                continue

            # Check all pairs of units in this building
            for i, unit_a in enumerate(units):
                for unit_b in units[i + 1:]:
                    adjacency = self._check_adjacency(unit_a, unit_b)
                    if adjacency:
                        pair = self._create_pair_record(unit_a, unit_b, adjacency)
                        all_pairs.append(pair)

        return all_pairs

    def _check_adjacency(self, unit_a: Dict, unit_b: Dict) -> Dict:
        """
        Check if two units are adjacent.
        Returns adjacency info with type and confidence, or None.
        """
        # Horizontal adjacency: same floor, adjacent positions
        if (unit_a["floor"] == unit_b["floor"] and
            abs(unit_a["position"] - unit_b["position"]) == 1):
            return {
                "type": "horizontal",
                "confidence": 0.95,
                "description": f"Same floor, adjacent units"
            }

        # Vertical adjacency: consecutive floors, same position
        if (abs(unit_a["floor"] - unit_b["floor"]) == 1 and
            unit_a["position"] == unit_b["position"]):
            return {
                "type": "vertical",
                "confidence": 0.90,
                "description": f"Vertical stack, consecutive floors"
            }

        # Diagonal adjacency: corner units (consecutive floor + adjacent position)
        if (abs(unit_a["floor"] - unit_b["floor"]) == 1 and
            abs(unit_a["position"] - unit_b["position"]) == 1):
            return {
                "type": "diagonal",
                "confidence": 0.70,
                "description": f"Diagonal (corner units)"
            }

        return None

    def _create_pair_record(self, unit_a: Dict, unit_b: Dict, adjacency: Dict) -> Dict:
        """Create a detailed record for an adjacent pair"""
        combined_sqft = unit_a["sqft"] + unit_b["sqft"]
        combined_price = unit_a["price"] + unit_b["price"]
        estimated_reno = self._estimate_renovation_cost(unit_a, unit_b)
        total_cost = combined_price + estimated_reno

        # Estimate market value of equivalent large unit
        market_comp = self._estimate_market_comp(combined_sqft)
        potential_savings = market_comp - total_cost

        return {
            "building": unit_a["address"],
            "unit_1": {
                "unit": unit_a["unit"],
                "floor": unit_a["floor"],
                "beds": unit_a["beds"],
                "sqft": unit_a["sqft"],
                "price": unit_a["price"],
            },
            "unit_2": {
                "unit": unit_b["unit"],
                "floor": unit_b["floor"],
                "beds": unit_b["beds"],
                "sqft": unit_b["sqft"],
                "price": unit_b["price"],
            },
            "combined": {
                "sqft": combined_sqft,
                "purchase_cost": combined_price,
                "renovation_estimate": estimated_reno,
                "total_cost": total_cost,
            },
            "adjacency": adjacency,
            "economics": {
                "market_comp_value": market_comp,
                "potential_savings": potential_savings,
                "savings_percent": round((potential_savings / market_comp) * 100, 1) if market_comp > 0 else 0,
            }
        }

    def _estimate_renovation_cost(self, unit_a: Dict, unit_b: Dict) -> int:
        """Estimate cost to combine units (wall removal, kitchen/bath integration)"""
        # Base cost for wall removal and integration
        base_cost = 50000

        # Additional costs based on combined size
        combined_sqft = unit_a["sqft"] + unit_b["sqft"]
        if combined_sqft > 1500:
            base_cost += 30000  # Larger units need more work

        # If both units have kitchens (not studios), assume we're removing one
        # and upgrading the other
        if unit_a.get("beds", 0) > 0 or unit_b.get("beds", 0) > 0:
            base_cost += 25000

        return base_cost

    def _estimate_market_comp(self, sqft: int) -> int:
        """Estimate market value of a comparable single unit"""
        # Premium pricing for larger units (higher $/sqft)
        if sqft < 800:
            price_per_sqft = 1400
        elif sqft < 1200:
            price_per_sqft = 1550
        elif sqft < 1800:
            price_per_sqft = 1650
        else:
            price_per_sqft = 1750

        # Add a premium because buying large units is hard/rare
        scarcity_premium = 1.15

        return int(sqft * price_per_sqft * scarcity_premium)

    def generate_report(self, pairs: List[Dict]) -> str:
        """Generate a human-readable analysis report"""
        lines = []
        lines.append("=" * 80)
        lines.append("ADJACENT UNIT COMBINER - ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary stats
        lines.append(f"Total listings analyzed: {len(self.listings)}")
        lines.append(f"Buildings with listings: {len(self.by_building)}")
        lines.append(f"Adjacent pairs found: {len(pairs)}")
        lines.append("")

        if not pairs:
            lines.append("No adjacent pairs found in this dataset.")
            return "\n".join(lines)

        # Adjacency type breakdown
        type_counts = defaultdict(int)
        for pair in pairs:
            type_counts[pair["adjacency"]["type"]] += 1

        lines.append("Adjacency Types:")
        for adj_type, count in sorted(type_counts.items()):
            lines.append(f"  {adj_type.capitalize()}: {count}")
        lines.append("")

        # Economic summary
        total_savings = sum(p["economics"]["potential_savings"] for p in pairs)
        avg_savings = total_savings / len(pairs) if pairs else 0
        positive_savings = [p for p in pairs if p["economics"]["potential_savings"] > 0]

        lines.append("Economic Analysis:")
        lines.append(f"  Pairs with positive savings: {len(positive_savings)} ({len(positive_savings)/len(pairs)*100:.1f}%)")
        lines.append(f"  Average potential savings: ${avg_savings:,.0f}")
        lines.append(f"  Total opportunity value: ${total_savings:,.0f}")
        lines.append("")

        # Top opportunities (by savings)
        lines.append("=" * 80)
        lines.append("TOP OPPORTUNITIES (by potential savings)")
        lines.append("=" * 80)
        lines.append("")

        sorted_pairs = sorted(pairs, key=lambda p: p["economics"]["potential_savings"], reverse=True)
        for i, pair in enumerate(sorted_pairs[:10], 1):
            self._format_pair(lines, i, pair)

        return "\n".join(lines)

    def _format_pair(self, lines: List[str], rank: int, pair: Dict):
        """Format a single pair for display"""
        lines.append(f"#{rank}. {pair['building']}")
        lines.append(f"    Units: {pair['unit_1']['unit']} + {pair['unit_2']['unit']}")
        lines.append(f"    Adjacency: {pair['adjacency']['description']} ({pair['adjacency']['confidence']*100:.0f}% confidence)")
        lines.append(f"    Unit 1: {pair['unit_1']['beds']}, {pair['unit_1']['sqft']} sqft, ${pair['unit_1']['price']:,}")
        lines.append(f"    Unit 2: {pair['unit_2']['beds']}, {pair['unit_2']['sqft']} sqft, ${pair['unit_2']['price']:,}")
        lines.append(f"    Combined: {pair['combined']['sqft']} sqft")
        lines.append(f"    Total cost: ${pair['combined']['total_cost']:,} (purchase: ${pair['combined']['purchase_cost']:,}, reno: ${pair['combined']['renovation_estimate']:,})")
        lines.append(f"    Market comp: ${pair['economics']['market_comp_value']:,}")

        savings = pair['economics']['potential_savings']
        savings_pct = pair['economics']['savings_percent']
        if savings > 0:
            lines.append(f"    💰 SAVINGS: ${savings:,} ({savings_pct}%)")
        else:
            lines.append(f"    ⚠️  PREMIUM: ${abs(savings):,} (more expensive than market)")
        lines.append("")


def main():
    # Load synthetic data
    with open('experiments/listings_synthetic.json', 'r') as f:
        listings = json.load(f)

    # Run analysis
    analyzer = AdjacencyAnalyzer(listings)
    pairs = analyzer.find_adjacent_pairs()

    # Save detailed results
    output_file = 'experiments/adjacent_pairs.json'
    with open(output_file, 'w') as f:
        json.dump(pairs, f, indent=2)
    print(f"Saved {len(pairs)} pairs to {output_file}\n")

    # Generate and display report
    report = analyzer.generate_report(pairs)
    print(report)

    # Save report
    report_file = 'experiments/analysis_report.txt'
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to {report_file}")


if __name__ == '__main__':
    main()
