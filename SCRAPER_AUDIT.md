# Scraper Audit: Rough Quarters vs Vayo

**Date:** January 18, 2026
**Purpose:** Identify what's being scraped, where it should live, and migration plan

---

## 🔍 Current State Analysis

### What Rough Quarters is Scraping

Let me check each strategy...

| Strategy | Scraping? | Data Source | Should Move to Vayo? |
|----------|-----------|-------------|---------------------|
| `adjacent_units.py` | ❌ No | Static analysis data | Keep (not scraping) |
| `discover_great_buildings.py` | ❌ No | Queries Vayo DB directly | ✅ Already using Vayo |
| `building_testimonials.py` | ⚠️ YES | **Reddit scraping** | ⚠️ **DUPLICATE** (Vayo has this!) |
| `well_maintained_buildings.py` | ❌ No | Queries HPD data | Keep (just queries) |
| `realtor_listings_live.py` | ⚠️ Sort of | **Reads CSV file** | ⚠️ Should import to Vayo |
| `long_tenure_simple.py` | ❌ No | Queries ACRIS | Keep (just queries) |
| `reddit_scraper_simple.py` | ⚠️ YES | **Reddit scraping** | ⚠️ **DUPLICATE** (Vayo has this!) |
| `lived_there_loved_it.py` | ⚠️ YES | **Reddit scraping** | ⚠️ **DUPLICATE** (Vayo has this!) |

**Finding:** We have 3 strategies doing Reddit scraping! Vayo already has `scrape-reddit.js`

---

### What Vayo Already Has

**Vayo's Scrapers (in `/vayo/stuy-scrape-csv/`):**

1. ✅ `scrape-reddit.js` - Reddit scraping (LIVE)
2. ✅ `scrape-streeteasy.js` - StreetEasy (LIVE)
3. ✅ `scrape-craigslist.js` - Craigslist (LIVE)
4. ✅ `scrape-facebook.js` - Facebook Marketplace (READY)
5. ✅ `scrape-dhcr.js` - Rent stabilization (LIVE)
6. ✅ `scrape-evictions.js` - Eviction data (LIVE)
7. ✅ `scrape-puppeteer.js` - Generic Puppeteer scraper (LIVE)

**Vayo's Database (stuytown.db - 30GB):**

- `buildings` (571,476 records) ✅
- `complaints` (26,165,975 HPD records) ✅
- `acris_real_property` (16M+ property records) ✅
- `craigslist_listings` (889 current) ✅
- `streeteasy_listings` (schema ready, 0 records)
- `current_rents` (rental history) ✅
- And 30 more tables

---

## 🎯 What Needs to Happen

### 1. **DUPLICATE: Reddit Scraping**

**Problem:**
- Rough Quarters has 3 Python scripts scraping Reddit
- Vayo has 1 JavaScript scraper doing the same thing

**Solution: Consolidate to Vayo**

**Keep in Vayo:**
```javascript
// vayo/stuy-scrape-csv/scrape-reddit.js
// Already working, already saving to DB
```

**Remove from Rough Quarters:**
```python
# DELETE or repurpose:
strategies/building_testimonials.py  (has Reddit scraper)
strategies/reddit_scraper_simple.py  (duplicate)
strategies/lived_there_loved_it.py   (duplicate)
```

**Replace with:**
```python
# strategies/building_testimonials.py (UPDATED)
from core.vayo_client import VayoClient

class BuildingTestimonialsStrategy:
    def search(self):
        vayo = VayoClient()
        # Query Vayo's database for Reddit data
        testimonials = vayo.get_reddit_testimonials()
        # Process and score
```

---

### 2. **CSV Data: Realtor Listings**

**Problem:**
- Rough Quarters reads CSVs from `experiments/` directory
- Data not in database, hard to query

**Solution: Import to Vayo**

**Create Vayo scraper:**
```javascript
// vayo/stuy-scrape-csv/scrapers/import-realtor-csv.js

const Database = require('better-sqlite3');
const fs = require('fs');
const csv = require('csv-parse/sync');

// Read manhattan_all_listings.csv
// Parse and insert into stuytown.db
// Add to existing 'craigslist_listings' table (rename to 'listings')
// Or create new 'realtor_listings' table
```

**Update Rough Quarters:**
```python
# strategies/realtor_listings.py
from core.vayo_client import VayoClient

class RealtorListingsStrategy:
    def search(self):
        vayo = VayoClient()
        listings = vayo.get_current_listings(source='realtor')
        # Process
```

---

### 3. **Query Strategies (Keep as-is)**

These are fine - they just query existing data:

✅ `discover_great_buildings.py` - Queries Vayo DB (good!)
✅ `well_maintained_buildings.py` - Queries HPD data
✅ `long_tenure_simple.py` - Queries ACRIS
✅ `adjacent_units.py` - Static analysis

**No changes needed** - just ensure they use VayoClient

---

## 📋 Migration Checklist

### Phase 1: Consolidate Reddit Scraping (Priority 1)

- [ ] **Document Vayo's Reddit scraper**
  - What it scrapes (subreddits, search terms)
  - Database schema (where it saves)
  - How to run it

- [ ] **Add Rough Quarters search terms to Vayo**
  - Current: Vayo scrapes r/NYCApartments for rentals
  - Add: Building testimonials, "lived there loved it" searches
  - Save to database with tags for rough-quarters usage

- [ ] **Create Vayo table for testimonials**
  ```sql
  CREATE TABLE reddit_testimonials (
    id INTEGER PRIMARY KEY,
    building_name TEXT,
    address TEXT,
    bin TEXT,
    post_id TEXT,
    subreddit TEXT,
    title TEXT,
    body TEXT,
    sentiment TEXT,  -- 'positive', 'negative', 'neutral'
    posted_date DATE,
    scraped_date DATE,
    source_url TEXT,
    tags TEXT,  -- JSON: ['rough-quarters', 'building-review', etc.]
    FOREIGN KEY (bin) REFERENCES buildings(bin)
  );
  ```

- [ ] **Update Vayo scraper to populate new table**
  ```javascript
  // scrape-reddit.js - add testimonial extraction
  // When finding posts about buildings, insert into reddit_testimonials
  ```

- [ ] **Create VayoClient method**
  ```python
  def get_building_testimonials(self, building_name=None, bin=None):
      """Get Reddit testimonials from Vayo DB"""
  ```

- [ ] **Update Rough Quarters strategies**
  - Replace scraping code with VayoClient queries
  - Test that it finds same data

- [ ] **Delete duplicate Python scrapers**
  - Archive old code (just in case)
  - Remove from active strategies

---

### Phase 2: Import Realtor Data to Vayo (Priority 2)

- [ ] **Decide database schema**
  - Option A: Add to existing `craigslist_listings` (rename to `listings`)
  - Option B: Create separate `realtor_listings` table
  - **Recommendation:** Option A (unified listings table)

- [ ] **Update listings table schema**
  ```sql
  ALTER TABLE craigslist_listings RENAME TO listings;

  -- Add source tracking
  ALTER TABLE listings ADD COLUMN data_source TEXT DEFAULT 'craigslist';
  -- 'craigslist', 'reddit', 'realtor', 'streeteasy', etc.
  ```

- [ ] **Create CSV import script**
  ```javascript
  // vayo/stuy-scrape-csv/scrapers/import-realtor-csv.js
  // Read experiments/*.csv
  // Parse, normalize, insert into listings table
  ```

- [ ] **Move CSV files to Vayo**
  ```bash
  mv rough-quarters/experiments/*.csv vayo/data/raw/
  ```

- [ ] **Run import**
  ```bash
  node scrapers/import-realtor-csv.js
  ```

- [ ] **Update VayoClient**
  ```python
  def get_current_listings(self, source=None, building_address=None):
      """Get listings from Vayo DB, optionally filter by source"""
  ```

- [ ] **Update Rough Quarters strategy**
  - Use VayoClient instead of reading CSV

---

### Phase 3: Documentation (Priority 3)

- [ ] **Create Vayo README**
  - What Vayo is (NYC real estate data hub)
  - What it scrapes
  - Database schema
  - How to add new scrapers
  - How other projects can use it

- [ ] **Create Rough Quarters docs**
  - How it uses Vayo
  - VayoClient API reference
  - Adding new strategies (when to scrape vs query)

- [ ] **Create shared data dictionary**
  - All tables in stuytown.db
  - Column definitions
  - Relationships
  - Example queries

- [ ] **Architecture diagram**
  - Visual showing Vayo → Rough Quarters flow
  - Where scrapers live
  - Where data lives
  - Who queries what

---

## 🏗️ Proposed Vayo Structure (After Migration)

```
/Users/pjump/Desktop/projects/vayo/
│
├── README.md                           ← Document the data hub
│   - What Vayo is
│   - How to use it
│   - How to contribute scrapers
│
├── stuy-scrape-csv/                    ← Main data hub
│   │
│   ├── stuytown.db                     ← 30GB single source of truth
│   │
│   ├── scrapers/                       ← ALL scrapers here
│   │   ├── scrape-reddit.js            ✅ Existing
│   │   ├── scrape-streeteasy.js        ✅ Existing
│   │   ├── scrape-craigslist.js        ✅ Existing
│   │   ├── scrape-facebook.js          ✅ Existing
│   │   ├── import-realtor-csv.js       ← NEW: Import Realtor data
│   │   └── scrape-zillow.js            ← FUTURE: Zillow scraper
│   │
│   ├── data/                           ← Raw data storage
│   │   └── raw/
│   │       ├── manhattan_all_listings.csv  ← Moved from rough-quarters
│   │       └── brooklyn_all_listings.csv
│   │
│   ├── docs/                           ← Documentation
│   │   ├── DATABASE_SCHEMA.md          ← NEW: All tables documented
│   │   ├── SCRAPER_GUIDE.md            ← NEW: How to add scrapers
│   │   └── API_REFERENCE.md            ← NEW: VayoClient methods
│   │
│   └── scripts/
│       ├── geocode-listings.js         ← Shared utility
│       └── generate-carfax.js          ← Vayo-specific (RentIntel)
│
└── server.js                           ← RentIntel web UI
```

---

## 📊 Data Flow (After Migration)

```
EXTERNAL SOURCES
├── Reddit API
├── Craigslist
├── StreetEasy
├── Realtor.com CSVs
├── NYC Open Data
└── Facebook Marketplace
    ↓
VAYO SCRAPERS (Single location)
├── scrape-reddit.js           → reddit_testimonials table
├── import-realtor-csv.js      → listings table
├── scrape-streeteasy.js       → listings table
└── (7+ scrapers)
    ↓
VAYO DATABASE (stuytown.db - 30GB)
├── buildings (571K)
├── complaints (26M HPD)
├── listings (Realtor + Craigslist + Reddit + StreetEasy)
├── reddit_testimonials (NEW)
├── acris_real_property (16M)
└── 36+ tables
    ↓
VAYO CLIENT (Query Interface)
├── get_buildings()
├── get_building_testimonials()
├── get_current_listings()
├── get_rental_history()
└── get_building_health_score()
    ↓
CONSUMING PROJECTS
├── Vayo/RentIntel (Carfax for apartments)
├── Rough Quarters (Diamond discovery)
└── Future projects (reuse same data)
```

---

## 🎯 Success Criteria

After migration, we should have:

✅ **Zero duplicate scrapers**
- Reddit: Only in Vayo
- Realtor: Only in Vayo
- All scraping in one place

✅ **Single database**
- All data in stuytown.db
- No CSV files being read directly
- Clean query interface

✅ **Clear documentation**
- README for Vayo (what it is)
- README for Rough Quarters (how to use)
- Database schema documented
- VayoClient API documented

✅ **Working data flow**
- Vayo scrapers run → populate DB
- Rough Quarters queries → finds data
- Both projects work independently

✅ **Reusable infrastructure**
- Future projects can use Vayo
- Easy to add new scrapers
- Clean separation of concerns

---

## 📝 Next Steps

1. **Review this audit** - Make sure architecture makes sense
2. **Approve migration plan** - Any changes needed?
3. **Start Phase 1** - Consolidate Reddit scraping
4. **Document as we go** - Create docs in parallel
5. **Test thoroughly** - Ensure nothing breaks

---

**Ready to start the migration?** We'll do it incrementally with full documentation.
