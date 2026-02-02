"""
Generate beautiful HTML reports for daily diamond digests
"""
from datetime import datetime
from pathlib import Path
from typing import List
import yaml

from .models import Diamond, StrategyPerformance
from .database import DiamondDatabase


class DiamondReporter:
    """Generates HTML reports of diamond findings"""

    def __init__(self, db: DiamondDatabase, config_path: str = "config.yaml"):
        self.db = db
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration"""
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except:
            return {
                'delivery': {'max_per_day': 5},
                'scoring': {'min_score': 80}
            }

    def generate_daily_digest(self, diamonds: List[Diamond] = None, output_path: str = None) -> str:
        """
        Generate HTML digest of top diamonds

        Args:
            diamonds: List of diamonds to include. If None, uses top from database
            output_path: Path to save HTML. If None, saves to data/reports/

        Returns:
            Path to generated HTML file
        """
        # Get diamonds if not provided
        if diamonds is None:
            max_diamonds = self.config.get('delivery', {}).get('max_per_day', 5)
            min_score = self.config.get('scoring', {}).get('min_score', 80)
            diamonds = self.db.get_top_diamonds(limit=max_diamonds, min_score=min_score)

        # Get strategy stats
        strategy_stats = self.db.get_all_strategy_performance()
        active_strategies = [s for s in strategy_stats if s.is_active]

        # Generate HTML
        html = self._generate_html(diamonds, active_strategies)

        # Save to file
        if output_path is None:
            reports_dir = Path("data/reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = reports_dir / f"digest_{timestamp}.html"

        with open(output_path, 'w') as f:
            f.write(html)

        # Also save as latest.html for easy access
        latest_path = Path(output_path).parent / "latest.html"
        with open(latest_path, 'w') as f:
            f.write(html)

        return str(output_path)

    def _generate_html(self, diamonds: List[Diamond], strategies: List[StrategyPerformance]) -> str:
        """Generate HTML content"""

        # Calculate stats
        total_diamonds = self.db.get_diamond_count()
        active_count = len(strategies)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diamond Finder - {datetime.now().strftime("%B %d, %Y")}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header .date {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .diamond {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .diamond:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        .diamond-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}
        .diamond-title {{
            font-size: 1.5em;
            font-weight: 600;
            color: #667eea;
        }}
        .score {{
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 1.1em;
        }}
        .score.excellent {{
            background: #10b981;
        }}
        .listing-type {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .listing-type.sale {{
            background: #dbeafe;
            color: #1e40af;
        }}
        .listing-type.rental {{
            background: #fef3c7;
            color: #92400e;
        }}
        .price {{
            font-size: 1.3em;
            font-weight: 600;
            color: #1f2937;
            margin: 10px 0;
        }}
        .specs {{
            color: #6b7280;
            margin: 10px 0;
        }}
        .why-special {{
            margin: 15px 0;
        }}
        .why-special h4 {{
            margin: 0 0 10px 0;
            color: #374151;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .why-special ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .why-special li {{
            margin: 5px 0;
            color: #4b5563;
        }}
        .meta {{
            display: flex;
            gap: 15px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
            font-size: 0.9em;
            color: #6b7280;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 10px;
            transition: background 0.2s;
        }}
        .btn:hover {{
            background: #5568d3;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stats h3 {{
            margin: 0 0 15px 0;
            color: #374151;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f9fafb;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #6b7280;
            margin-top: 5px;
        }}
        .no-diamonds {{
            text-align: center;
            padding: 60px 20px;
            color: #6b7280;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6b7280;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💎 Diamond Finder</h1>
        <div class="date">{datetime.now().strftime("%A, %B %d, %Y")}</div>
    </div>

    <div class="stats">
        <h3>📊 System Status</h3>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">{len(diamonds)}</div>
                <div class="stat-label">Today's Top Diamonds</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_diamonds}</div>
                <div class="stat-label">Total in Database</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{active_count}</div>
                <div class="stat-label">Active Strategies</div>
            </div>
        </div>
    </div>
"""

        if not diamonds:
            html += """
    <div class="no-diamonds">
        <h2>No diamonds found yet</h2>
        <p>The system is running and will deliver discoveries soon.</p>
    </div>
"""
        else:
            for i, diamond in enumerate(diamonds, 1):
                score_class = "excellent" if diamond.score >= 90 else ""

                # Format price
                if diamond.listing_type == "sale":
                    price_str = f"${diamond.price:,.0f}" if diamond.price else "Price TBD"
                else:
                    price_str = f"${diamond.price:,.0f}/mo" if diamond.price else "Rent TBD"

                # Format specs
                specs = []
                if diamond.bedrooms:
                    specs.append(f"{diamond.bedrooms} bed")
                if diamond.sqft:
                    specs.append(f"{diamond.sqft:,.0f} sqft")
                specs_str = " • ".join(specs) if specs else "Details TBD"

                # Why special
                why_items = "".join([f"<li>{reason}</li>" for reason in diamond.why_special[:6]])

                # Metadata
                strategies = ", ".join(diamond.found_by_strategies)
                photo_count = len(diamond.photos)

                html += f"""
    <div class="diamond">
        <div class="diamond-header">
            <div>
                <div class="listing-type {diamond.listing_type}">{diamond.listing_type}</div>
                <div class="diamond-title">#{i}. {diamond.address}, Unit {diamond.unit}</div>
            </div>
            <div class="score {score_class}">{diamond.score:.0f}/100</div>
        </div>

        <div class="price">{price_str}</div>
        <div class="specs">{specs_str}</div>

        <div class="why-special">
            <h4>Why This Is Special:</h4>
            <ul>{why_items}</ul>
        </div>

        <div class="meta">
            <div class="meta-item">📸 {photo_count} photos</div>
            <div class="meta-item">🔍 Found by: {strategies}</div>
        </div>

        {f'<a href="{diamond.listing_url}" class="btn" target="_blank">View Listing →</a>' if diamond.listing_url else ''}
    </div>
"""

        html += """
    <div class="footer">
        Generated by Diamond Finder • Run locally on your machine
    </div>
</body>
</html>
"""

        return html
