# Diamond Finder - Search Strategies

## Overview

The Diamond Finder uses **multiple parallel search strategies** to discover exceptional apartments from different data sources. Each strategy looks for diamonds in a unique way.

**Key Concept:** We catalog diamonds whether they're available or not. The goal is to build an inventory of every exceptional apartment that exists, then monitor for availability signals separately.

## Active Strategies (6)

### 1. **Adjacent Units Combiner**
**File:** `strategies/adjacent_units.py`
**What it finds:** Opportunities to buy two adjacent apartments and combine them

**How it works:**
- Analyzes building floor plates
- Identifies units that could be combined (horizontal, vertical, diagonal)
- Calculates arbitrage: cost to buy both + renovation vs market value of combined unit
- Flags when savings potential is 15%+

**Example find:**
```
315 West 86th Street, Units 4G + 5G
- Vertical stack, consecutive floors (90% confidence)
- Combined: 4,053 sqft
- Total cost: $6,946,897 (purchase + $105k reno)
- Market comp: $8,156,662
- Savings: $1,209,765 (14.8%)
```

**Current status:** Using existing adjacent-unit analysis data
**Phase 2:** Automate daily scanning of new listings

---

### 2. **Reddit Social Listener**
**File:** `strategies/reddit_listener.py`
**What it finds:** Apartments mentioned on Reddit with social proof

**How it works:**
- Searches Reddit for apartment mentions (r/NYCApartments, r/AskNYC, r/nyc, etc.)
- Looks for praise: "best apartment ever", "incredible views", "dream place"
- Extracts address + unit from text
- Catalogs based on social proof, even if not currently listed

**Example find:**
```
88 Central Park West, Unit 12B
- Social proof: 3 Reddit mentions
- Quote: "Lived here for 15 years. The B-line corner units have
  the best Central Park views in the building."
- Found by: r/NYCApartments
```

**Current status:** Example data (would-be finds)
**Phase 2:** Real Reddit API integration with PRAW

---

### 3. **Premium Sales Finder**
**File:** `strategies/premium_sales_finder.py`
**What it finds:** Units that sold at significant premiums (20%+ above building average)

**How it works:**
- Queries NYC ACRIS (public property records)
- Analyzes all sales in a building
- Calculates $/sqft for each sale
- Flags units that sold 20%+ above average = probably exceptional
- Catalogs even though not currently for sale

**Example find:**
```
15 Central Park West, Unit 18C
- Sold 39.5% above building average
- Sale price: $12,500,000 ($3,906/sqft)
- Building avg: $2,800/sqft
- Last sale: 2022-03-15
- Reason: Corner unit with Central Park views, bidding war
```

**Current status:** Example data
**Phase 2:** ACRIS API integration or bulk download

---

### 4. **Architectural Gems**
**File:** `strategies/architectural_gems.py`
**What it finds:** Objectively exceptional units based on architecture/position

**How it works:**
- Analyzes building floor plans (NYC DOB records)
- Identifies rare configurations:
  - Corner units (2+ exposures)
  - Top floors (views, but not overpriced penthouses)
  - Outdoor space (terraces, balconies)
  - Unique layouts (duplexes, through-floor)
- Catalogs units regardless of availability

**Example find:**
```
The Beresford, 211 Central Park West
- Tower units (ending in 'A' on floors 15+)
- Only 3 tower corner units in entire building
- 360-degree views of Central Park and Hudson
- Art Deco architectural masterpiece
- Original 1929 layouts with 14ft ceilings
```

**Current status:** Example data for famous buildings
**Phase 2:** DOB floor plan analysis, PLUTO data integration

---

### 5. **Listing Archive Miner**
**File:** `strategies/listing_archive_miner.py`
**What it finds:** Apartments with exceptional historical listings

**How it works:**
- Searches StreetEasy/Zillow historical listings (cache back to ~2005)
- Identifies exceptional listings by:
  - High photo count (30+ photos)
  - Premium descriptions ("one-of-a-kind", "trophy")
  - Quick sales (< 7 days = high demand)
  - High engagement (views, saves)
- Catalogs units even if not currently listed

**Example find:**
```
443 Greenwich Street, Unit PH53B
- Listed 2020-05-15, sold in 4 days
- 82 professional photos
- 15,000 views, 450 saves
- Described as: "one-of-a-kind trophy penthouse"
- Listed by: Corcoran (top broker)
```

**Current status:** Example data
**Phase 2:** StreetEasy/Zillow scraping, Wayback Machine integration

---

### 6. **Mock Finder** (Test Data)
**File:** `strategies/mock_finder.py`
**What it finds:** Nothing (generates test data for validation)

**Purpose:** Provides realistic example diamonds to test scoring, reporting, and database systems

**Status:** Active for testing, will be removed once real strategies have live data

---

## How Strategies Work Together

### 1. **Complementary Discovery**
Different strategies find the same diamonds via different signals:

```
315 West 86th Street, Unit 8D might be found by:
✓ Premium Sales Finder: Sold 28% above building avg
✓ Listing Archive Miner: 47 photos in 2019 listing
✓ Reddit Listener: "Best unit in the building" mention
✓ Architectural Gems: Corner SE with terrace

= High confidence this is a diamond (4 strategies agree)
```

### 2. **Scoring Consensus**
When multiple strategies find the same unit, it gets a **consensus bonus** (+2 points per additional strategy, max +10)

### 3. **Evidence Aggregation**
Each strategy contributes different evidence:
- Premium Sales: Price history, tenure
- Archive Miner: Photos, descriptions
- Reddit: Social proof, quotes
- Architectural: Layout analysis, rarity

All evidence merges into one comprehensive diamond profile.

---

## Strategy Performance Tracking

The system automatically tracks each strategy's effectiveness:

**Metrics:**
- **Precision**: Ratio of high-scoring finds to total candidates
- **Diversity**: Finding different buildings (not just same building repeatedly)
- **Richness**: Average photos/evidence per find
- **Strategy Score**: Weighted combination of above (0-1 scale)

**Example:**
```
Strategy: premium_sales_finder
- Diamonds found (90+): 12
- Diamonds found (80+): 45
- Total candidates: 200
- Precision: 0.225 (22.5% hit rate)
- Diversity: 0.89 (finds spread across buildings)
- Richness: 0.80 (good photo/evidence quality)
- Strategy Score: 0.615 (performs well)
```

**Self-Improvement:**
- Strategies scoring < 0.2 for 30+ days = deprecated
- Top performers inform new strategy generation (Phase 2)

---

## Coming in Phase 2: Real Data Integration

### Reddit Listener
```python
# Install: pip install praw
# Get Reddit API credentials
# Search: r/NYCApartments, r/AskNYC, r/nyc
# Extract addresses from comments/posts
# Catalog with social proof score
```

### Premium Sales Finder
```python
# Install: pip install sodapy
# Query NYC ACRIS via Socrata API
# Or: Bulk download ACRIS dataset
# Analyze building-level sales patterns
# Flag premium sales (20%+ above avg)
```

### Architectural Gems
```python
# Access NYC DOB floor plans
# Query PLUTO for building data
# Analyze floor plates, exposures
# Identify rare configurations
# Cross-ref with famous architects
```

### Listing Archive Miner
```python
# Scrape StreetEasy historical listings
# Parse Zillow past sales
# Use Wayback Machine for old broker sites
# Extract photos, descriptions, engagement
# Score listing quality
```

---

## Current Results

**Run:** `python3 run.py all`

**Output:**
```
Loaded 6 strategies
Running 6 strategies...

adjacent_units_combiner: Found 3 candidates
mock_finder: Found 5 candidates
reddit_social_listener: Found 3 candidates
premium_sales_finder: Found 4 candidates
architectural_gems: Found 5 candidates
listing_archive_miner: Found 4 candidates

Total unique diamonds: 21
Top score: 90
```

**Database:** 21 diamonds cataloged
**Digest:** `data/reports/latest.html` (beautiful HTML report)

---

## Adding New Strategies

### Template
```python
from core.strategy_base import SearchStrategy
from core.models import Diamond

class MyNewStrategy(SearchStrategy):
    def __init__(self):
        super().__init__(
            name="my_new_strategy",
            description="What this strategy does"
        )

    def search(self) -> List[Diamond]:
        diamonds = []

        # Your discovery logic here
        # Could be: API call, web scraping, database query, etc.

        diamond = self._create_diamond(
            address="123 Main Street",
            unit="5A",
            listing_type="sale",  # or "rental" or "unknown"
            price=1000000,
            bedrooms=2,
            sqft=1500,
            why_special=[
                "Reason 1 why this is exceptional",
                "Reason 2",
                "Reason 3"
            ],
            # Optional fields:
            price_premium_pct=25.0,  # 25% premium
            tenure_years=20,          # Held 20 years
            social_mentions=3,        # 3 mentions found
            photos=["url1", "url2"],  # Photo URLs
        )

        diamonds.append(diamond)
        return diamonds
```

### Integration
1. Create file in `strategies/`
2. Import in `strategies/__init__.py`
3. Add to executor in `core/executor.py`
4. Run: `python3 run.py daily`

---

## Philosophy

**These strategies embody the core vision:**

1. **Catalog Everything** - If it's exceptional, catalog it (available or not)
2. **Multiple Sources** - Same diamond found different ways = higher confidence
3. **Objective Signals** - Price premiums, social proof, architectural analysis (not opinions)
4. **Evidence-Based** - Every diamond backed by concrete evidence
5. **Self-Improving** - Track performance, deprecate low performers, evolve

The system gets smarter over time without human intervention.
