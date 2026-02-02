"""
Data models for the Diamond Finder system
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
import json


@dataclass
class Diamond:
    """Represents a potential diamond apartment find"""

    # Identification
    address: str
    unit: str
    id: str = field(default="")  # Generated from address + unit

    # Basic info
    listing_type: str = "sale"  # "sale" or "rental"
    price: Optional[float] = None
    bedrooms: Optional[int] = None
    sqft: Optional[float] = None

    # Scoring
    score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    # Evidence
    why_special: List[str] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)
    floor_plan_url: Optional[str] = None
    listing_url: Optional[str] = None

    # Discovery metadata
    found_by_strategies: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.now)

    # Enrichment data
    price_premium_pct: Optional[float] = None
    tenure_years: Optional[int] = None
    social_mentions: int = 0

    # Status
    is_available: bool = True
    last_checked: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.id:
            self.id = f"{self.address.lower().replace(' ', '_')}_{self.unit.lower()}"

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'address': self.address,
            'unit': self.unit,
            'listing_type': self.listing_type,
            'price': self.price,
            'bedrooms': self.bedrooms,
            'sqft': self.sqft,
            'score': self.score,
            'score_breakdown': json.dumps(self.score_breakdown),
            'why_special': json.dumps(self.why_special),
            'photos': json.dumps(self.photos),
            'floor_plan_url': self.floor_plan_url,
            'listing_url': self.listing_url,
            'found_by_strategies': json.dumps(self.found_by_strategies),
            'discovered_at': self.discovered_at.isoformat(),
            'price_premium_pct': self.price_premium_pct,
            'tenure_years': self.tenure_years,
            'social_mentions': self.social_mentions,
            'is_available': self.is_available,
            'last_checked': self.last_checked.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Diamond':
        """Create Diamond from database row"""
        data = dict(data)

        # Parse JSON fields
        if isinstance(data.get('score_breakdown'), str):
            data['score_breakdown'] = json.loads(data['score_breakdown'])
        if isinstance(data.get('why_special'), str):
            data['why_special'] = json.loads(data['why_special'])
        if isinstance(data.get('photos'), str):
            data['photos'] = json.loads(data['photos'])
        if isinstance(data.get('found_by_strategies'), str):
            data['found_by_strategies'] = json.loads(data['found_by_strategies'])

        # Parse datetime fields
        if isinstance(data.get('discovered_at'), str):
            data['discovered_at'] = datetime.fromisoformat(data['discovered_at'])
        if isinstance(data.get('last_checked'), str):
            data['last_checked'] = datetime.fromisoformat(data['last_checked'])

        return cls(**data)


@dataclass
class StrategyPerformance:
    """Tracks performance of a search strategy"""

    strategy_name: str
    diamonds_found_90plus: int = 0
    diamonds_found_80plus: int = 0
    total_candidates: int = 0
    total_photos_found: int = 0
    unique_buildings: int = 0

    first_run: datetime = field(default_factory=datetime.now)
    last_run: datetime = field(default_factory=datetime.now)
    runs_count: int = 0

    is_active: bool = True

    @property
    def precision(self) -> float:
        """Quality: ratio of high-scoring finds to total candidates"""
        if self.total_candidates == 0:
            return 0.0
        return self.diamonds_found_90plus / self.total_candidates

    @property
    def diversity(self) -> float:
        """Diversity: finding different buildings"""
        if self.diamonds_found_80plus == 0:
            return 0.0
        return self.unique_buildings / self.diamonds_found_80plus

    @property
    def richness(self) -> float:
        """Evidence quality: avg photos per diamond"""
        if self.diamonds_found_80plus == 0:
            return 0.0
        return self.total_photos_found / self.diamonds_found_80plus

    @property
    def strategy_score(self) -> float:
        """Overall strategy effectiveness score"""
        return (self.precision * 0.4) + (self.diversity * 0.3) + (min(self.richness / 10, 1.0) * 0.3)

    def to_dict(self) -> dict:
        return {
            'strategy_name': self.strategy_name,
            'diamonds_found_90plus': self.diamonds_found_90plus,
            'diamonds_found_80plus': self.diamonds_found_80plus,
            'total_candidates': self.total_candidates,
            'total_photos_found': self.total_photos_found,
            'unique_buildings': self.unique_buildings,
            'first_run': self.first_run.isoformat(),
            'last_run': self.last_run.isoformat(),
            'runs_count': self.runs_count,
            'is_active': self.is_active,
            'precision': self.precision,
            'diversity': self.diversity,
            'richness': self.richness,
            'strategy_score': self.strategy_score
        }
