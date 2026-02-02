# Rough Quarters

**Finding diamond apartments in the rough** 💎🏠

An autonomous discovery engine that finds exceptional places to live by analyzing 571K+ NYC buildings through multiple data strategies - whether they're available or not.

---

## What This Does

**Traditional apartment search:** *"Show me 2BR under $3M"*

**Rough Quarters:** *"Find apartments where people lived 30 years because they loved it. Find buildings with zero violations. Find pre-war gems. Find combination opportunities. Cross-validate everything."*

**We discover diamonds in the rough:**
- Not currently listed? We find them anyway.
- Hidden in data? We extract them.
- Require insider knowledge? We build it from 571K buildings.

---

## Current Stats

- **157 diamonds cataloged** (from 0 two days ago)
- **100 discovered** from 571,476 building database
- **14 available units** you can buy/rent RIGHT NOW
- **6 active strategies** (and growing)
- **$0/month** cost (all free data sources)

---

## How It Works

### 6 Search Strategies Running in Parallel

1. **Data-Driven Building Discovery** ⭐ NEW
   - Queries 571,476 NYC buildings
   - Finds pre-war gems with excellent maintenance
   - Discovered 100 candidates in first run

2. **Social Proof Mining**
   - Reddit testimonials: "I lived there 15 years, best apartment ever"
   - Finding 15+ buildings with organic mentions

3. **Maintenance Quality Analysis**
   - NYC HPD violations data (26M+ complaints)
   - Found 5 buildings with ZERO violations

4. **Live Availability Tracking**
   - Cross-references great buildings with 7,214 current listings
   - Found 14 available units in exceptional buildings

5. **Adjacent Unit Combiner** (the original idea)
   - 3 combinations identified
   - Creates unique living experiences you can't buy otherwise

6. **Tenure Analysis** (in progress)
   - 16M ACRIS property records
   - Finding apartments people held 20-40 years

### Cross-Strategy Validation

Buildings found by MULTIPLE strategies = highest confidence

**Example: San Remo (145 Central Park West)** - Score: 47/100
- ✓ Discovered from database (built 1890, 0 complaints)
- ✓ Reddit testimonial
- ✓ Zero HPD violations
= **High confidence diamond**

---

## Quick Start

```bash
cd rough-quarters/diamond-finder
python3 run.py all              # Run all strategies
open data/reports/latest.html   # View results
```

**Run automatically (crontab):**
```bash
0 3 * * * cd /path/to/rough-quarters/diamond-finder && python3 run.py daily
```

---

## What Gets Discovered

**Not about:**
- ❌ Cheapest price
- ❌ Celebrity penthouses
- ❌ Obvious luxury
- ❌ Investment returns

**About:**
- ✅ Where people stay 30 years (they loved it)
- ✅ Perfect light and views
- ✅ Exceptional maintenance (zero violations)
- ✅ Unique living experiences
- ✅ Buildings with soul (pre-war classics)

---

## The Data

**Active Sources:**
- 571,476 NYC buildings (Vayo database)
- 7,214 current Manhattan listings (Realtor.com)
- 26M HPD complaints (maintenance quality)
- 16M ACRIS records (ownership/tenure)
- Reddit testimonials (social proof)

**Coming Soon:**
- StreetEasy historical listings
- Zillow rental history
- NYC DOB floor plans (sun exposure)
- Energy benchmarking
- Brooklyn, Queens expansion

---

## Data Architecture

Rough Quarters uses **Vayo** as its data hub.

**Vayo** is a centralized NYC real estate data platform that:
- Scrapes 10+ data sources
- Stores 30GB in single database (`stuytown.db`)
- Provides clean query interface
- Reusable by multiple projects

**Rough Quarters:**
- Queries Vayo for source data (buildings, complaints, listings, testimonials)
- Adds discovery intelligence (quality of life scoring)
- Stores discoveries in local `diamonds.db`

**Architecture:**
```
Vayo (Data Hub)
├── Scrapers → stuytown.db (30GB)
    ↓
Rough Quarters (Intelligence)
├── Strategies query Vayo
├── Score quality of life
└── Store discoveries → diamonds.db
```

**VayoClient Usage:**
```python
from core.vayo_client import VayoClient

vayo = VayoClient()

# Get buildings
buildings = vayo.get_buildings({'borough': 'MANHATTAN'})

# Get testimonials
testimonials = vayo.get_building_testimonials('The Dakota')

# Get current listings
listings = vayo.get_current_listings(source='realtor')
```

See [Vayo documentation](../vayo/README.md) for full API.

---

## The Evolution

**Week 1:** "Find adjacent units you can combine" (1 arbitrage idea)

**Week 2:** "What else is a diamond?" (added testimonials, maintenance)

**Week 3:** 🚀 **BREAKTHROUGH** - Data-driven discovery from 571K buildings

**Journey:**
- From: 26 hardcoded buildings → finding 19
- To: 500 candidates analyzed → 100 processed → 157 cataloged
- Growth: +185% in 2 days

---

## Project Structure

```
rough-quarters/
├── README.md                    # This file
├── IDEA-CARD.md                # Full concept & vision
├── STATUS.md                   # Current status & metrics
├── diamond-finder/             # The discovery engine
│   ├── strategies/             # 6 search strategies
│   ├── core/                   # Scoring, database
│   ├── data/
│   │   └── diamonds.db         # 157 diamonds cataloged
│   └── run.py                  # Main orchestrator
├── experiments/                # Data sources
│   ├── manhattan_all_listings.csv  # 7,214 listings
│   └── brooklyn_all_listings.csv
└── docs/
    ├── SCALING_SUCCESS.md      # How we went from 55→157
    ├── DATA_SOURCES_FOUND.md   # All available data
    └── DATA_EXPANSION_ROADMAP.md
```

---

## Vision

> "I want it to always be searching for me, always finding new ways to search, always trying to impress me."

**✅ ACHIEVED:**
- Autonomous (runs daily, no intervention)
- Multi-strategy (6+ methods, growing)
- Self-improving (cross-validates, scales)
- Always discovering (571K buildings → 1,000s more)

---

## Metrics

**Discovery Rate:** 100+ buildings per run
**Database Growth:** 55 → 157 diamonds (+185% in 2 days)
**Availability:** 14 units you can buy/rent NOW
**Cross-Validation:** Buildings found by 2+ strategies score 2x higher
**Cost:** $0/month

---

## Links

- [Full Idea Card](./IDEA-CARD.md) - Complete vision & roadmap
- [Current Status](./STATUS.md) - What's working right now
- [Scaling Success](./diamond-finder/SCALING_SUCCESS.md) - How we scaled
- [Data Sources](./diamond-finder/DATA_SOURCES_FOUND.md) - What data we have

---

**Rough Quarters** - *Finding diamond apartments in the rough* 💎🏠
