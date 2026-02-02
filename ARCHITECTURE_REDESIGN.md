# Architecture Redesign: Vayo + Rough Quarters

## 🎯 The Vision

**Two separate concerns, cleanly separated:**

### **Vayo = Data Acquisition Hub** 🏭
*"The central source for all NYC real estate data"*

- All scrapers live here
- All raw data stored here
- All data pipelines here
- Single massive database
- Reusable by ANY project

### **Rough Quarters = Discovery Intelligence** 🧠
*"Finding diamonds by querying Vayo's data"*

- NO scrapers (queries Vayo instead)
- Pure intelligence/discovery logic
- Strategies query Vayo's database
- Lightweight, focused

---

## 📊 Current State (Mixed Architecture)

**Problems:**
```
rough-quarters/
├── diamond-finder/
│   ├── strategies/
│   │   ├── realtor_listings_live.py    ← Reads CSV from experiments/
│   │   ├── building_testimonials.py    ← Has its own Reddit scraper
│   │   ├── discover_great_buildings.py ← Queries Vayo DB (good!)
│   └── ...
└── experiments/
    ├── manhattan_all_listings.csv      ← Data lives here (bad!)
    └── brooklyn_all_listings.csv

vayo/
├── stuy-scrape-csv/
│   ├── scrape-streeteasy.js            ← Scrapers live here
│   ├── scrape-craigslist.js
│   ├── scrape-reddit.js
│   └── stuytown.db                     ← 31.8GB database
```

**Issues:**
- Data scattered (CSVs in rough-quarters, DB in Vayo)
- Duplicate scraping logic (Reddit scraper in both places)
- rough-quarters doing too much (scraping + intelligence)

---

## 🎨 Target Architecture (Clean Separation)

```
/Users/pjump/Desktop/projects/
│
├── vayo/                           ← DATA ACQUISITION HUB
│   ├── scrapers/                   ← ALL scrapers here
│   │   ├── scrape-streeteasy.js
│   │   ├── scrape-realtor.js      ← Move from rough-quarters
│   │   ├── scrape-zillow.js       ← New
│   │   ├── scrape-reddit.js       ← Consolidate from rough-quarters
│   │   ├── scrape-craigslist.js
│   │   └── scrape-acris.js
│   │
│   ├── pipelines/                  ← Data processing
│   │   ├── geocode.py
│   │   ├── deduplicate.py
│   │   └── enrich.py
│   │
│   ├── data/                       ← SINGLE SOURCE OF TRUTH
│   │   └── vayo.db                ← Everything in ONE database
│   │       ├── buildings (571K)
│   │       ├── listings (current + historical)
│   │       ├── complaints (26M HPD)
│   │       ├── acris (16M property records)
│   │       ├── reddit_mentions
│   │       ├── rental_history
│   │       └── ... (all data)
│   │
│   └── README.md                   ← "Vayo: NYC Real Estate Data Hub"
│
└── rough-quarters/                 ← DISCOVERY INTELLIGENCE
    ├── diamond-finder/
    │   ├── strategies/             ← ONLY query logic (no scraping!)
    │   │   ├── discover_great_buildings.py
    │   │   ├── building_testimonials.py  ← Queries Vayo DB
    │   │   ├── realtor_listings.py       ← Queries Vayo DB
    │   │   └── ...
    │   │
    │   ├── core/
    │   │   ├── vayo_client.py      ← Client to query Vayo DB
    │   │   ├── scorer.py
    │   │   └── database.py         ← diamonds.db (discovery results only)
    │   │
    │   └── config.yaml
    │       vayo_db_path: "/Users/.../vayo/data/vayo.db"
    │
    └── README.md                    ← "Rough Quarters: Finding Diamonds"
```

---

## 🔄 Data Flow

```
VAYO (Data Acquisition)
├── Scrapers run daily → Raw data
├── Pipelines process → Clean data
└── Store in vayo.db → Single source of truth
     ↓
     ↓ (SQL queries)
     ↓
ROUGH QUARTERS (Discovery Intelligence)
├── Strategies query vayo.db
├── Apply intelligence/scoring
├── Find diamonds
└── Store in diamonds.db (157 discoveries)
     ↓
     ↓ (HTML digest)
     ↓
USER
└── Views diamonds in reports/latest.html
```

---

## 🚀 Migration Plan

### Phase 1: Consolidate Data in Vayo (This Week)

**Move scrapers to Vayo:**
```bash
# 1. Create vayo/scrapers/ directory
mkdir -p /Users/pjump/Desktop/projects/vayo/scrapers

# 2. Move/consolidate scrapers
# - scrape-realtor.py (new - reads Realtor CSV, loads to DB)
# - scrape-reddit.py (consolidate from rough-quarters)
# - scrape-zillow.py (new)
```

**Consolidate data into vayo.db:**
```sql
-- Add tables to vayo/data/vayo.db:
CREATE TABLE listings_current (
    -- From manhattan_all_listings.csv
    property_id TEXT,
    address TEXT,
    unit TEXT,
    price INTEGER,
    beds INTEGER,
    sqft INTEGER,
    status TEXT,
    listing_date DATE,
    ...
);

CREATE TABLE reddit_testimonials (
    -- From rough-quarters building_testimonials strategy
    building_name TEXT,
    address TEXT,
    mention_text TEXT,
    source_url TEXT,
    found_date DATE
);
```

**Benefits:**
- All data in ONE place
- Vayo becomes reusable data hub
- rough-quarters just queries it

---

### Phase 2: Update Rough Quarters to Query Vayo (Next Week)

**Create Vayo client:**
```python
# rough-quarters/diamond-finder/core/vayo_client.py

import sqlite3

class VayoClient:
    """Client to query Vayo's central data hub"""

    def __init__(self, db_path="/Users/.../vayo/data/vayo.db"):
        self.db_path = db_path

    def get_current_listings(self, address=None):
        """Get current listings from Vayo"""
        conn = sqlite3.connect(self.db_path)
        # Query listings_current table
        ...

    def get_building_testimonials(self, building_name):
        """Get Reddit testimonials from Vayo"""
        conn = sqlite3.connect(self.db_path)
        # Query reddit_testimonials table
        ...

    def get_great_buildings(self, criteria):
        """Get buildings matching criteria"""
        # Query buildings table with filters
        ...
```

**Update strategies:**
```python
# strategies/realtor_listings.py

from core.vayo_client import VayoClient

class RealtorListingsStrategy(SearchStrategy):
    def __init__(self):
        self.vayo = VayoClient()

    def search(self):
        # Query Vayo instead of reading CSV
        listings = self.vayo.get_current_listings()
        ...
```

---

### Phase 3: Vayo Becomes Production Data Hub (Month 2)

**Scheduled scraping:**
```bash
# Vayo crontab - runs all scrapers
0 2 * * * cd /path/to/vayo && node scrapers/scrape-streeteasy.js
0 3 * * * cd /path/to/vayo && python scrapers/scrape-realtor.py
0 4 * * * cd /path/to/vayo && python scrapers/scrape-reddit.py
```

**Data freshness:**
- StreetEasy: Daily
- Realtor.com: Daily
- Reddit: Daily
- ACRIS: Weekly (slow-changing)
- HPD: Monthly

**Vayo becomes:**
- Single source of truth for ALL NYC real estate data
- Reusable by other projects
- Well-maintained, scheduled updates
- Clean API for querying

---

## 📁 New Directory Structure

```
vayo/
├── README.md                       # "NYC Real Estate Data Hub"
├── scrapers/                       # All data acquisition
│   ├── scrape-streeteasy.js
│   ├── scrape-realtor.py          # NEW
│   ├── scrape-zillow.py           # NEW
│   ├── scrape-reddit.py           # CONSOLIDATED
│   ├── scrape-craigslist.js
│   └── scrape-acris.py
├── pipelines/                      # Data processing
│   ├── deduplicate.py
│   ├── geocode.py
│   └── enrich.py
├── data/
│   └── vayo.db                    # SINGLE DATABASE
└── sql/                           # Schema definitions
    ├── create_tables.sql
    └── migrations/

rough-quarters/
├── README.md                      # "Finding Diamonds (queries Vayo)"
└── diamond-finder/
    ├── strategies/                # ONLY discovery logic
    ├── core/
    │   ├── vayo_client.py        # Query interface to Vayo
    │   └── ...
    └── data/
        └── diamonds.db            # Discovery results only
```

---

## 💡 Key Benefits

### Separation of Concerns
- **Vayo:** "Get me all NYC real estate data"
- **Rough Quarters:** "Find me diamonds from that data"

### Reusability
- Other projects can use Vayo's data
- Vayo becomes central infrastructure
- rough-quarters is just one consumer

### Maintainability
- Scrapers in one place
- Data in one place
- Clear boundaries

### Scalability
- Add new scrapers to Vayo → all projects benefit
- Add new discovery strategies to rough-quarters → focused
- Database grows in one place

---

## 🎯 First Steps (Next 1 Hour)

### 1. Create Vayo Data Hub Structure
```bash
cd /Users/pjump/Desktop/projects/vayo
mkdir -p scrapers pipelines sql data
```

### 2. Move Realtor Data to Vayo
```bash
# Copy CSV to Vayo
cp rough-quarters/experiments/*.csv vayo/data/

# Create import script
# vayo/scrapers/import-realtor-csv.py
```

### 3. Create Vayo Client in Rough Quarters
```python
# rough-quarters/diamond-finder/core/vayo_client.py
# Simple query interface
```

### 4. Update One Strategy to Use Vayo
```python
# Update realtor_listings.py to query Vayo instead of CSV
```

---

## 🤔 Decision Points

**Question 1:** Keep existing vayo/stuy-scrape-csv/stuytown.db OR create new vayo/data/vayo.db?

**Options:**
- A) Use existing stuytown.db (31GB already has data)
- B) Create new vayo.db (fresh start, cleaner schema)

**Recommendation:** Use existing stuytown.db, add new tables as needed

---

**Question 2:** Move rough-quarters/experiments/ data to Vayo?

**Yes!**
```bash
mv rough-quarters/experiments/ vayo/raw-data/
# Keep rough-quarters lightweight
```

---

## 🎬 Ready to Start?

**Next action:** Create Vayo hub structure and move first data source?

1. Set up vayo/scrapers/ directory
2. Move Realtor CSVs to Vayo
3. Create import script to load into vayo.db
4. Update rough-quarters to query Vayo

**Want me to start?**
