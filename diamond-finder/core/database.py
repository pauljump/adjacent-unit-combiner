"""
Database operations for Diamond Finder
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from .models import Diamond, StrategyPerformance


class DiamondDatabase:
    """Manages diamond storage and retrieval"""

    def __init__(self, db_path: str = "data/diamonds.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS diamonds (
                    id TEXT PRIMARY KEY,
                    address TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    listing_type TEXT,
                    price REAL,
                    bedrooms INTEGER,
                    sqft REAL,
                    score REAL,
                    score_breakdown TEXT,
                    why_special TEXT,
                    photos TEXT,
                    floor_plan_url TEXT,
                    listing_url TEXT,
                    found_by_strategies TEXT,
                    discovered_at TEXT,
                    price_premium_pct REAL,
                    tenure_years INTEGER,
                    social_mentions INTEGER,
                    is_available INTEGER,
                    last_checked TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS strategy_performance (
                    strategy_name TEXT PRIMARY KEY,
                    diamonds_found_90plus INTEGER DEFAULT 0,
                    diamonds_found_80plus INTEGER DEFAULT 0,
                    total_candidates INTEGER DEFAULT 0,
                    total_photos_found INTEGER DEFAULT 0,
                    unique_buildings INTEGER DEFAULT 0,
                    first_run TEXT,
                    last_run TEXT,
                    runs_count INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_score ON diamonds(score DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_discovered_at ON diamonds(discovered_at DESC)
            """)

            conn.commit()

    def save_diamond(self, diamond: Diamond) -> bool:
        """Save or update a diamond"""
        with sqlite3.connect(self.db_path) as conn:
            # Check if diamond exists
            existing = conn.execute(
                "SELECT id, found_by_strategies FROM diamonds WHERE id = ?",
                (diamond.id,)
            ).fetchone()

            if existing:
                # Update: merge strategies
                import json
                existing_strategies = json.loads(existing[1]) if existing[1] else []
                all_strategies = list(set(existing_strategies + diamond.found_by_strategies))
                diamond.found_by_strategies = all_strategies

                # Get diamond data
                data = diamond.to_dict()

                # Only update if new score is higher
                existing_score = conn.execute(
                    "SELECT score FROM diamonds WHERE id = ?", (diamond.id,)
                ).fetchone()[0]

                if diamond.score > existing_score:
                    conn.execute("""
                        UPDATE diamonds SET
                            score = ?, score_breakdown = ?, why_special = ?,
                            photos = ?, found_by_strategies = ?, last_checked = ?
                        WHERE id = ?
                    """, (
                        data['score'], data['score_breakdown'], data['why_special'],
                        data['photos'], data['found_by_strategies'], data['last_checked'],
                        diamond.id
                    ))
                else:
                    # Just update strategies and last_checked
                    conn.execute("""
                        UPDATE diamonds SET
                            found_by_strategies = ?, last_checked = ?
                        WHERE id = ?
                    """, (data['found_by_strategies'], data['last_checked'], diamond.id))

            else:
                # Insert new
                data = diamond.to_dict()
                conn.execute("""
                    INSERT INTO diamonds VALUES (
                        :id, :address, :unit, :listing_type, :price, :bedrooms, :sqft,
                        :score, :score_breakdown, :why_special, :photos, :floor_plan_url,
                        :listing_url, :found_by_strategies, :discovered_at,
                        :price_premium_pct, :tenure_years, :social_mentions,
                        :is_available, :last_checked
                    )
                """, data)

            conn.commit()
            return True

    def get_top_diamonds(self, limit: int = 10, min_score: float = 80) -> List[Diamond]:
        """Get top scoring diamonds"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM diamonds
                WHERE score >= ? AND is_available = 1
                ORDER BY score DESC, discovered_at DESC
                LIMIT ?
            """, (min_score, limit)).fetchall()

            return [Diamond.from_dict(dict(row)) for row in rows]

    def get_recent_diamonds(self, days: int = 1) -> List[Diamond]:
        """Get diamonds discovered in last N days"""
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if days > 1:
            from datetime import timedelta
            cutoff = cutoff - timedelta(days=days - 1)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM diamonds
                WHERE discovered_at >= ?
                ORDER BY score DESC
            """, (cutoff.isoformat(),)).fetchall()

            return [Diamond.from_dict(dict(row)) for row in rows]

    def get_diamond_count(self) -> int:
        """Get total number of diamonds in database"""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM diamonds").fetchone()[0]

    def update_strategy_performance(self, perf: StrategyPerformance):
        """Save or update strategy performance"""
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT strategy_name FROM strategy_performance WHERE strategy_name = ?",
                (perf.strategy_name,)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE strategy_performance SET
                        diamonds_found_90plus = ?,
                        diamonds_found_80plus = ?,
                        total_candidates = ?,
                        total_photos_found = ?,
                        unique_buildings = ?,
                        last_run = ?,
                        runs_count = ?,
                        is_active = ?
                    WHERE strategy_name = ?
                """, (
                    perf.diamonds_found_90plus,
                    perf.diamonds_found_80plus,
                    perf.total_candidates,
                    perf.total_photos_found,
                    perf.unique_buildings,
                    perf.last_run.isoformat(),
                    perf.runs_count,
                    perf.is_active,
                    perf.strategy_name
                ))
            else:
                conn.execute("""
                    INSERT INTO strategy_performance VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (
                    perf.strategy_name,
                    perf.diamonds_found_90plus,
                    perf.diamonds_found_80plus,
                    perf.total_candidates,
                    perf.total_photos_found,
                    perf.unique_buildings,
                    perf.first_run.isoformat(),
                    perf.last_run.isoformat(),
                    perf.runs_count,
                    perf.is_active
                ))

            conn.commit()

    def get_strategy_performance(self, strategy_name: str) -> Optional[StrategyPerformance]:
        """Get performance stats for a strategy"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT * FROM strategy_performance WHERE strategy_name = ?
            """, (strategy_name,)).fetchone()

            if not row:
                return None

            data = dict(row)
            data['first_run'] = datetime.fromisoformat(data['first_run'])
            data['last_run'] = datetime.fromisoformat(data['last_run'])
            data['is_active'] = bool(data['is_active'])

            return StrategyPerformance(**data)

    def get_all_strategy_performance(self) -> List[StrategyPerformance]:
        """Get performance stats for all strategies"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM strategy_performance
                ORDER BY is_active DESC, last_run DESC
            """).fetchall()

            result = []
            for row in rows:
                data = dict(row)
                data['first_run'] = datetime.fromisoformat(data['first_run'])
                data['last_run'] = datetime.fromisoformat(data['last_run'])
                data['is_active'] = bool(data['is_active'])
                result.append(StrategyPerformance(**data))

            return result
