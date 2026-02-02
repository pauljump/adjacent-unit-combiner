# Vayo + Rough Quarters Architecture

**Date:** January 18, 2026

---

## 🏗️ What Each Project Actually Is

### **Vayo = RentIntel Platform** 🏭
*"Carfax for Apartments" - Rental transparency platform*

**Purpose:** Help NYC renters avoid bad landlords and find fair deals

**What it does:**
- Scrapes 889+ rental listings (Craigslist, Reddit, Facebook)
- Links to 26M HPD complaints
- Generates "Apartment Carfax" reports
- Building health scores (0-100)
- Rent history tracking

**Database:** 30GB `stuytown.db` with 36 tables
- `buildings` (571K)
- `complaints` (26M HPD)
- `craigslist_listings` (889 current)
- `streeteasy_listings` (schema ready, 0 records)
- `current_rents` (rent history)
- `acris_real_property` (16M records)
- And 30 more tables

**Target user:** Renters looking for transparency (avoid slumlords)

---

### **Rough Quarters = Diamond Discovery Engine** 💎
*"Finding diamond apartments in the rough"*

**Purpose:** Find exceptional places to live (quality of life)

**What it does:**
- Discovers great buildings from 571K database
- Reddit testimonials ("I loved living there")
- Maintenance quality (zero violations)
- Long tenure analysis (people stayed 30 years)
- Combination opportunities (adjacent units)

**Database:** `diamonds.db` (157 discoveries)

**Target user:** People looking for exceptional homes (not just safe rentals)

---

## 🎯 The Overlap

**What they share:**
- Both need NYC building data (571K buildings)
- Both query HPD complaints (26M records)
- Both scrape Reddit
- Both use ACRIS property data
- Both need geocoding

**What's different:**
- Vayo: Current listings, rental prices, tenant transparency
- Rough Quarters: Quality of life, long-term tenure, testimonials, diamonds

---

## 🏛️ Recommended Architecture

### **Option A: Shared Data Hub (RECOMMENDED)**

```
SHARED DATA HUB (Vayo DB)
/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/
├── stuytown.db (30GB)          ← SINGLE SOURCE OF TRUTH
│   ├── buildings (571K)
│   ├── complaints (26M HPD)
│   ├── acris_real_property (16M)
│   ├── current_rents
│   ├── craigslist_listings
│   └── ... (36 tables total)
│
├── scrapers/
│   ├── scrape-streeteasy.js    ← Rental focus
│   ├── scrape-reddit.js        ← Shared
│   ├── scrape-craigslist.js
│   └── ... (7 scrapers)
│
└── scripts/
    ├── generate-carfax.js      ← Vayo-specific (rental transparency)
    ├── geocode-listings.js     ← Shared utility
    └── ...

VAYO PROJECT (RentIntel Product)
/Users/pjump/Desktop/projects/vayo/
├── stuy-scrape-csv/            ← Data hub (above)
├── server.js                   ← Web UI for rental reports
└── README.md                   ← "RentIntel - Carfax for Apartments"

ROUGH QUARTERS PROJECT (Diamond Finder)
/Users/pjump/Desktop/projects/rough-quarters/
├── diamond-finder/
│   ├── strategies/
│   │   ├── discover_great_buildings.py
│   │   ├── building_testimonials.py
│   │   └── ... (6 strategies)
│   │
│   ├── core/
│   │   ├── vayo_client.py      ← NEW: Query vayo DB
│   │   └── ...
│   │
│   ├── data/
│   │   └── diamonds.db         ← Discovery results only
│   │
│   └── config.yaml
│       vayo_db: "/Users/.../vayo/stuy-scrape-csv/stuytown.db"
│
└── README.md                   ← "Rough Quarters - Diamond Discovery"
```

**Benefits:**
- ✅ Single database (no duplication)
- ✅ Both projects query same data
- ✅ Scrapers run once, both projects benefit
- ✅ Clear separation of concerns
- ✅ Vayo stays focused on rental transparency
- ✅ Rough Quarters stays focused on quality discovery

---

## 🔄 Data Flow

```
NYC Open Data APIs
    ↓
VAYO SCRAPERS (in vayo/stuy-scrape-csv/)
    ├─ scrape-streeteasy.js
    ├─ scrape-reddit.js
    ├─ scrape-craigslist.js
    └─ scrape-facebook.js
    ↓
VAYO DATABASE (stuytown.db - 30GB)
    ├─ buildings (571K)
    ├─ complaints (26M)
    ├─ listings (current rentals)
    ├─ acris (property records)
    └─ current_rents (rental history)
    ↓
    ├──────────────────┬──────────────────┐
    ↓                  ↓                  ↓
VAYO PRODUCT   ROUGH QUARTERS    FUTURE PROJECTS
(RentIntel)    (Diamond Finder)  (Reuse same data)
    ↓                  ↓
Carfax Reports     Diamond Discovery
Rental transparency   Quality of life
```

---

## 🛠️ Implementation Plan

### Phase 1: Connect Rough Quarters to Vayo DB (Next 2 Hours)

**1. Create Vayo Client in Rough Quarters**
```python
# rough-quarters/diamond-finder/core/vayo_client.py

import sqlite3

class VayoClient:
    """Client to query Vayo's shared data hub"""

    def __init__(self):
        self.db_path = "/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/stuytown.db"

    def get_buildings(self, criteria=None):
        """Query buildings table (571K buildings)"""
        conn = sqlite3.connect(self.db_path)
        # SELECT * FROM buildings WHERE ...

    def get_complaints_for_building(self, bin):
        """Get HPD complaints for a building"""
        conn = sqlite3.connect(self.db_path)
        # SELECT * FROM complaints WHERE bin = ?

    def get_current_listings(self, address=None):
        """Get current rental listings"""
        conn = sqlite3.connect(self.db_path)
        # SELECT * FROM craigslist_listings WHERE ...

    def get_building_health_score(self, bin):
        """Get Vayo's building health score"""
        # Use Vayo's scoring algorithm

    def get_rental_history(self, building_id, unit):
        """Get rent history for specific unit"""
        # SELECT * FROM current_rents WHERE ...
```

**2. Update Rough Quarters Config**
```yaml
# rough-quarters/diamond-finder/config.yaml

vayo:
  database_path: "/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/stuytown.db"
  use_shared_data: true
```

**3. Update Strategies to Use Vayo Client**
```python
# strategies/discover_great_buildings.py

from core.vayo_client import VayoClient

class DiscoverGreatBuildingsStrategy:
    def __init__(self):
        self.vayo = VayoClient()

    def search(self):
        # Query Vayo DB instead of separate query
        buildings = self.vayo.get_buildings({
            'borough': 'MANHATTAN',
            'year_built': {'<': 1945},
            'num_units': {'>=': 20, '<=': 500}
        })
        # ... rest of logic
```

**4. Remove Duplicate Scrapers from Rough Quarters**
- Delete `building_testimonials.py` Reddit scraper
- Use Vayo's `scrape-reddit.js` instead
- Query results from Vayo DB

---

### Phase 2: Add Rough Quarters-Specific Data to Vayo DB (Week 2)

**Option A: Add tables to stuytown.db**
```sql
-- Add to Vayo's stuytown.db
CREATE TABLE rough_quarters_discoveries (
    id INTEGER PRIMARY KEY,
    bin TEXT,                    -- Link to Vayo's buildings table
    address TEXT,
    discovery_score INTEGER,     -- Rough Quarters quality score
    discovery_date DATE,
    found_by_strategies TEXT,    -- JSON array
    why_special TEXT,           -- JSON array
    FOREIGN KEY (bin) REFERENCES buildings(bin)
);

CREATE TABLE rough_quarters_testimonials (
    id INTEGER PRIMARY KEY,
    bin TEXT,
    source TEXT,                -- 'reddit', 'streeteasy_comments', etc.
    testimonial_text TEXT,
    found_date DATE,
    FOREIGN KEY (bin) REFERENCES buildings(bin)
);
```

**Option B: Keep diamonds.db separate (lighter weight)**
- Rough Quarters maintains `diamonds.db` for discoveries
- Queries Vayo for source data
- Stores only discovery results

**Recommendation:** Option B (keep separate) - cleaner boundaries

---

### Phase 3: Consolidate Scrapers in Vayo (Month 2)

**Move to Vayo:**
- Any new scrapers (Zillow, Apartments.com)
- Realtor.com data import
- StreetEasy when anti-bot is solved

**Keep in Rough Quarters:**
- Pure discovery logic (strategies)
- Scoring algorithms
- Diamond database

---

## 📁 Final Directory Structure

```
/Users/pjump/Desktop/projects/

vayo/                                    ← DATA HUB
├── README.md                            "Vayo: NYC Real Estate Data Platform"
├── stuy-scrape-csv/
│   ├── stuytown.db                     ← 30GB, 36 tables, SHARED
│   ├── scrapers/
│   │   ├── scrape-streeteasy.js
│   │   ├── scrape-reddit.js            ← Shared scraper
│   │   ├── scrape-craigslist.js
│   │   └── scrape-realtor.js           ← ADD: Import Realtor CSVs
│   ├── scripts/
│   │   ├── geocode-listings.js         ← Shared utility
│   │   └── generate-carfax.js          ← Vayo-specific
│   ├── server.js                       ← RentIntel web UI
│   └── README.md                       "RentIntel - Carfax for Apartments"
│
└── experiments/                         ← Move to Vayo
    └── (Realtor CSVs moved here)

rough-quarters/                          ← DISCOVERY ENGINE
├── README.md                            "Rough Quarters - Finding Diamonds"
├── diamond-finder/
│   ├── strategies/                      ← Pure discovery logic
│   │   ├── discover_great_buildings.py  (queries Vayo)
│   │   ├── quality_of_life_scorer.py    (adds intelligence)
│   │   └── ...
│   ├── core/
│   │   ├── vayo_client.py              ← NEW: Query interface
│   │   └── ...
│   ├── data/
│   │   └── diamonds.db                 ← Discovery results (157 diamonds)
│   └── config.yaml
│       vayo_db: "/path/to/vayo/stuytown.db"
└── docs/
    └── (strategy docs, scaling docs)
```

---

## 🎯 Key Decisions

### ✅ What We're Doing

1. **Keep projects separate** - Different products, different users
2. **Share data infrastructure** - Both query Vayo's stuytown.db
3. **Vayo = Data Hub** - All scrapers, all source data
4. **Rough Quarters = Intelligence** - Discovery logic, quality scoring
5. **diamonds.db stays separate** - Lightweight, focused

### ❌ What We're NOT Doing

1. Merging projects (they serve different purposes)
2. Duplicating scrapers (consolidate in Vayo)
3. Duplicating data (single source of truth)
4. Moving Vayo's rental focus (it's good as-is)

---

## 🚀 Next Steps (Next 1 Hour)

### Immediate Action:

1. **Create VayoClient**
   ```bash
   touch rough-quarters/diamond-finder/core/vayo_client.py
   ```

2. **Update config.yaml**
   ```yaml
   vayo:
     database_path: "/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/stuytown.db"
   ```

3. **Test connection**
   ```python
   from core.vayo_client import VayoClient
   vayo = VayoClient()
   buildings = vayo.get_buildings()
   print(f"Connected! {len(buildings)} buildings available")
   ```

4. **Update one strategy**
   - Pick `discover_great_buildings.py`
   - Replace direct DB query with VayoClient
   - Verify it works

---

## 💡 The Vision

**Vayo** becomes your NYC real estate data platform:
- All scrapers
- All source data
- Reusable by ANY project

**Rough Quarters** becomes pure intelligence:
- Queries Vayo for data
- Adds quality-of-life scoring
- Finds diamonds

**Future projects** can also use Vayo:
- Investment analysis tool
- Gentrification tracker
- Landlord reputation app
- Anything needing NYC real estate data

**Clean, scalable, maintainable.** ✨

---

Ready to build the VayoClient?
