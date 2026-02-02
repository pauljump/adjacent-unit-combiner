# Vayo + Rough Quarters Migration Plan

**Date:** January 18, 2026
**Status:** Ready to execute
**Estimated time:** 4-6 hours total

---

## 📊 Audit Results

### ✅ Confirmed Duplicates Found

**Reddit Scraping:**
- Rough Quarters has **4 Python scripts** scraping Reddit
- Vayo has **1 JavaScript scraper** doing the same thing
- **Action:** Consolidate to Vayo

**Files to consolidate:**
```
rough-quarters/diamond-finder/strategies/
├── building_testimonials.py      ← Has Reddit scraper (DUPLICATE)
├── reddit_scraper_simple.py      ← Reddit scraper (DUPLICATE)
├── lived_there_loved_it.py       ← Reddit scraper (DUPLICATE)
└── reddit_discovery.py           ← Reddit scraper (DUPLICATE)

vayo/stuy-scrape-csv/
└── scrape-reddit.js              ← KEEP THIS ONE (working)
```

**StreetEasy Scraping:**
- Rough Quarters has `streeteasy_scraper.py` (not working - blocked)
- Vayo has `scrape-streeteasy.js` (exists, needs testing)
- **Action:** Use Vayo's version

**Realtor Data:**
- Rough Quarters reads `experiments/*.csv` (not in database)
- **Action:** Import to Vayo database

---

## 🎯 Migration Strategy

### **Principle: Vayo = All Scrapers, Rough Quarters = All Intelligence**

```
BEFORE (Messy):
Rough Quarters scrapes → stores in rough-quarters
Vayo scrapes → stores in Vayo
Data duplicated, scrapers duplicated

AFTER (Clean):
Vayo scrapes → stores in stuytown.db
Rough Quarters queries Vayo → adds intelligence → stores discoveries
Data centralized, scrapers centralized
```

---

## 📋 Migration Phases

### **Phase 1: Reddit Consolidation** (2 hours)

**Goal:** Stop duplicating Reddit scraping, use Vayo's scraper

#### Step 1.1: Enhance Vayo's Reddit Scraper (30 min)

**File:** `/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/scrape-reddit.js`

**Add to Vayo's scraper:**
```javascript
// Current: Scrapes r/NYCApartments for rental listings
// Add: Building testimonials searches

const TESTIMONIAL_SEARCHES = [
  'The Dakota apartment',
  'San Remo building',
  'lived at building NYC',
  'loved living at',
  'best building Manhattan',
  // ... (26 buildings from rough-quarters)
];

// Save to new table: reddit_testimonials
```

#### Step 1.2: Create reddit_testimonials Table (15 min)

**Add to stuytown.db:**
```sql
CREATE TABLE IF NOT EXISTS reddit_testimonials (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  building_name TEXT,
  address TEXT,
  bin TEXT,
  post_id TEXT UNIQUE,
  subreddit TEXT,
  post_title TEXT,
  post_body TEXT,
  author TEXT,
  posted_date DATE,
  scraped_date DATE DEFAULT CURRENT_TIMESTAMP,
  source_url TEXT,
  sentiment TEXT,  -- 'positive', 'negative', 'neutral'
  tags TEXT,       -- JSON: ['rough-quarters', 'testimonial', etc.]
  FOREIGN KEY (bin) REFERENCES buildings(bin)
);

CREATE INDEX idx_testimonials_bin ON reddit_testimonials(bin);
CREATE INDEX idx_testimonials_building ON reddit_testimonials(building_name);
```

**Script location:** `/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/migrations/add_testimonials_table.sql`

#### Step 1.3: Run Vayo's Scraper (15 min)

```bash
cd /Users/pjump/Desktop/projects/vayo/stuy-scrape-csv
node scrape-reddit.js --mode=testimonials
```

**Verify data:**
```bash
sqlite3 stuytown.db "SELECT COUNT(*) FROM reddit_testimonials;"
sqlite3 stuytown.db "SELECT building_name, COUNT(*) FROM reddit_testimonials GROUP BY building_name LIMIT 10;"
```

#### Step 1.4: Create VayoClient (30 min)

**File:** `/Users/pjump/Desktop/projects/rough-quarters/diamond-finder/core/vayo_client.py`

```python
"""
Vayo Client - Query interface for Vayo's data hub
"""
import sqlite3
from typing import List, Dict, Optional

class VayoClient:
    """
    Client to query Vayo's centralized NYC real estate database.

    Vayo Location: /Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/
    Database: stuytown.db (30GB)
    Tables: 36+ (buildings, complaints, listings, testimonials, etc.)
    """

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = "/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/stuytown.db"
        self.db_path = db_path

    def get_buildings(self, criteria: Optional[Dict] = None) -> List[Dict]:
        """
        Query buildings table (571,476 buildings)

        Args:
            criteria: Optional filters
                {
                    'borough': 'MANHATTAN',
                    'year_built': {'<': 1945},
                    'num_units': {'>=': 20, '<=': 500}
                }

        Returns:
            List of building dicts with keys: bin, address, borough, etc.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        query = "SELECT * FROM buildings WHERE 1=1"
        params = []

        if criteria:
            # Build WHERE clause dynamically
            # (Implementation details)
            pass

        cursor = conn.execute(query, params)
        buildings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return buildings

    def get_building_testimonials(self, building_name: str = None, bin: str = None) -> List[Dict]:
        """
        Get Reddit testimonials for a building.

        Args:
            building_name: e.g., "The Dakota"
            bin: NYC Building Identification Number

        Returns:
            List of testimonial dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        if bin:
            query = "SELECT * FROM reddit_testimonials WHERE bin = ?"
            params = [bin]
        elif building_name:
            query = "SELECT * FROM reddit_testimonials WHERE building_name LIKE ?"
            params = [f"%{building_name}%"]
        else:
            query = "SELECT * FROM reddit_testimonials"
            params = []

        cursor = conn.execute(query, params)
        testimonials = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return testimonials

    def get_complaints_for_building(self, bin: str) -> List[Dict]:
        """Get HPD complaints for a building (26M+ total complaints)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            "SELECT * FROM complaints WHERE bin = ?",
            [bin]
        )
        complaints = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return complaints

    def get_current_listings(self, source: str = None, address: str = None) -> List[Dict]:
        """
        Get current rental/sale listings.

        Args:
            source: 'craigslist', 'reddit', 'realtor', 'streeteasy'
            address: Filter by building address

        Returns:
            List of listing dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Note: Vayo currently has 'craigslist_listings' table
        # After Realtor import, this will be unified 'listings' table

        query = "SELECT * FROM craigslist_listings WHERE 1=1"
        params = []

        if source:
            query += " AND source = ?"
            params.append(source)

        if address:
            query += " AND address LIKE ?"
            params.append(f"%{address}%")

        cursor = conn.execute(query, params)
        listings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return listings

    def get_building_health_score(self, bin: str) -> int:
        """
        Get Vayo's building health score (0-100).

        Based on complaints per unit ratio.
        Used by Vayo's RentIntel "Apartment Carfax" reports.
        """
        conn = sqlite3.connect(self.db_path)

        # Get building info
        building = conn.execute(
            "SELECT num_units FROM buildings WHERE bin = ?",
            [bin]
        ).fetchone()

        if not building or not building[0]:
            conn.close()
            return 50  # Default

        units = building[0]

        # Count complaints
        complaint_count = conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE bin = ?",
            [bin]
        ).fetchone()[0]

        conn.close()

        # Vayo's scoring algorithm
        complaints_per_unit = complaint_count / units if units > 0 else 0

        if complaints_per_unit < 0.5:
            return 100
        elif complaints_per_unit < 1:
            return 95
        elif complaints_per_unit < 2:
            return 80
        elif complaints_per_unit < 5:
            return 60
        elif complaints_per_unit < 10:
            return 40
        else:
            return 20

    def get_rental_history(self, building_id: str, unit: str = None) -> List[Dict]:
        """Get rent history for a building/unit from current_rents table"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        if unit:
            query = "SELECT * FROM current_rents WHERE building_id = ? AND unit_number = ?"
            params = [building_id, unit]
        else:
            query = "SELECT * FROM current_rents WHERE building_id = ?"
            params = [building_id]

        cursor = conn.execute(query, params)
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return history
```

#### Step 1.5: Update Rough Quarters Strategy (30 min)

**File:** `strategies/building_testimonials.py`

**Replace scraping code with:**
```python
from core.vayo_client import VayoClient

class BuildingTestimonialsStrategy(SearchStrategy):
    def __init__(self):
        super().__init__(
            name="building_testimonials",
            description="[LIVE] Finds testimonials from Vayo's database"
        )
        self.vayo = VayoClient()

    def search(self) -> List[Diamond]:
        diamonds = []

        # List of buildings to check
        buildings = [
            ("The Dakota", "1 West 72nd Street"),
            ("San Remo", "145 Central Park West"),
            # ... (full list)
        ]

        for building_name, address in buildings:
            # Query Vayo instead of scraping
            testimonials = self.vayo.get_building_testimonials(building_name)

            if len(testimonials) > 0:
                why_special = [
                    f"Found {len(testimonials)} positive Reddit mentions",
                    f"Building: {building_name}",
                ]

                # Add testimonial excerpts
                for t in testimonials[:3]:  # Top 3
                    excerpt = t['post_title'][:100]
                    why_special.append(f"Example: \"{excerpt}\"")

                diamond = self._create_diamond(
                    address=address,
                    unit="Various units",
                    listing_type="unknown",
                    why_special=why_special,
                )

                diamond.social_mentions = len(testimonials)
                diamond.is_available = False
                diamonds.append(diamond)

        return diamonds
```

#### Step 1.6: Test & Delete Duplicates (15 min)

**Test:**
```bash
cd /Users/pjump/Desktop/projects/rough-quarters/diamond-finder
python3 run.py daily
# Verify it finds testimonials from Vayo
```

**Delete old scrapers:**
```bash
# Archive first (just in case)
mkdir archive/
mv strategies/reddit_scraper_simple.py archive/
mv strategies/lived_there_loved_it.py archive/
mv strategies/reddit_discovery.py archive/

# Update executor.py to remove from imports
```

---

### **Phase 2: Realtor Data Import** (1.5 hours)

**Goal:** Move Realtor CSV data into Vayo's database

#### Step 2.1: Move CSV Files (5 min)

```bash
mkdir -p /Users/pjump/Desktop/projects/vayo/data/raw
mv /Users/pjump/Desktop/projects/rough-quarters/experiments/*.csv \
   /Users/pjump/Desktop/projects/vayo/data/raw/
```

#### Step 2.2: Create Import Script (45 min)

**File:** `/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/scrapers/import-realtor-csv.js`

```javascript
/**
 * Import Realtor.com CSV data into Vayo database
 */
const Database = require('better-sqlite3');
const fs = require('fs');
const csv = require('csv-parse/sync');

const DB_PATH = '../stuytown.db';
const CSV_DIR = '../../data/raw/';

const db = new Database(DB_PATH);

// First, rename table to be source-agnostic
db.exec(`
  ALTER TABLE craigslist_listings RENAME TO listings;
`);

// Add source column if not exists
db.exec(`
  ALTER TABLE listings ADD COLUMN IF NOT EXISTS data_source TEXT DEFAULT 'craigslist';
`);

// Read Realtor CSVs
const manhattanCsv = fs.readFileSync(CSV_DIR + 'manhattan_all_listings.csv', 'utf-8');
const brooklynCsv = fs.readFileSync(CSV_DIR + 'brooklyn_all_listings.csv', 'utf-8');

const manhattanListings = csv.parse(manhattanCsv, { columns: true });
const brooklynListings = csv.parse(brooklynCsv, { columns: true });

console.log(`Loaded ${manhattanListings.length} Manhattan listings`);
console.log(`Loaded ${brooklynListings.length} Brooklyn listings`);

// Insert into database
const insert = db.prepare(`
  INSERT OR IGNORE INTO listings (
    post_id, url, title, price, address, neighborhood,
    bedrooms, bathrooms, square_feet, description,
    posted_at, scraped_at, source, data_source, bin
  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'realtor', 'realtor', ?)
`);

let inserted = 0;

for (const listing of [...manhattanListings, ...brooklynListings]) {
  try {
    insert.run(
      `realtor_${listing.property_id}`,  // Unique ID
      listing.property_url,
      listing.formatted_address,
      listing.list_price || null,
      listing.full_street_line,
      listing.city,
      listing.beds || null,
      (listing.full_baths || 0) + (listing.half_baths || 0) * 0.5,
      listing.sqft || null,
      listing.text || '',
      listing.list_date || new Date().toISOString(),
      new Date().toISOString(),
      null  // BIN (will geocode later)
    );
    inserted++;
  } catch (err) {
    // Ignore duplicates
    if (!err.message.includes('UNIQUE')) {
      console.error('Error inserting:', err.message);
    }
  }
}

console.log(`✅ Imported ${inserted} Realtor listings`);
db.close();
```

#### Step 2.3: Run Import (10 min)

```bash
cd /Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/scrapers
node import-realtor-csv.js
```

**Verify:**
```bash
sqlite3 ../stuytown.db "SELECT data_source, COUNT(*) FROM listings GROUP BY data_source;"
# Should show: craigslist: 889, realtor: 7214
```

#### Step 2.4: Update VayoClient (already has get_current_listings) ✅

#### Step 2.5: Update Rough Quarters Strategy (30 min)

**File:** `strategies/realtor_listings.py` (rename from realtor_listings_live.py)

```python
from core.vayo_client import VayoClient

class RealtorListingsStrategy(SearchStrategy):
    def __init__(self):
        super().__init__(
            name="realtor_listings",
            description="[LIVE] Finds available units in great buildings (Realtor.com data)"
        )
        self.vayo = VayoClient()

    def search(self) -> List[Diamond]:
        diamonds = []

        # Get all discovered great buildings from our database
        # (buildings we've identified as diamonds)
        great_buildings = self._get_discovered_buildings()

        # Query Vayo for Realtor listings in those buildings
        for building_address in great_buildings:
            listings = self.vayo.get_current_listings(
                source='realtor',
                address=building_address
            )

            for listing in listings:
                # Create diamond for each available unit
                diamond = self._create_diamond(
                    address=listing['address'],
                    unit=listing.get('unit', 'N/A'),
                    listing_type="for_sale",
                    price=listing.get('price'),
                )

                diamond.bedrooms = listing.get('bedrooms')
                diamond.sqft = listing.get('square_feet')
                diamond.url = listing.get('url')
                diamond.is_available = True

                diamonds.append(diamond)

        return diamonds
```

---

### **Phase 3: Documentation** (30-60 min)

#### Step 3.1: Update Vayo README

**File:** `/Users/pjump/Desktop/projects/vayo/README.md`

```markdown
# Vayo - NYC Real Estate Data Hub

**The central data infrastructure for NYC real estate projects**

Vayo is a comprehensive data platform that scrapes, stores, and serves NYC real estate data from 10+ sources into a single 30GB database.

## What Vayo Provides

**Database:** `stuytown.db` (30GB SQLite)
- 571,476 NYC buildings
- 26M+ HPD complaints
- 16M+ ACRIS property transactions
- 8,000+ current listings (Craigslist, Reddit, Realtor)
- Reddit testimonials
- Rent history
- And 30+ more tables

**Scrapers:** 8 active data sources
- StreetEasy
- Craigslist
- Reddit
- Realtor.com
- Facebook Marketplace
- DHCR (rent stabilization)
- NYC Open Data (complaints, violations, permits)
- And more

## Projects Using Vayo

1. **Vayo/RentIntel** - "Carfax for Apartments"
   - Rental transparency platform
   - Building health scores
   - Helps renters avoid slumlords

2. **Rough Quarters** - Diamond apartment discovery
   - Finds exceptional homes
   - Quality of life scoring
   - Queries Vayo for data

3. **Your project here** - Reusable data hub

## Quick Start

### Query the Database

```javascript
const Database = require('better-sqlite3');
const db = new Database('./stuytown.db');

// Get building info
const building = db.prepare('SELECT * FROM buildings WHERE bin = ?').get('1018055');

// Get complaints
const complaints = db.prepare('SELECT * FROM complaints WHERE bin = ?').all('1018055');

// Get current listings
const listings = db.prepare('SELECT * FROM listings WHERE address LIKE ?').all('%24th Street%');
```

### Run a Scraper

```bash
# Scrape Reddit
node scrape-reddit.js

# Import Realtor data
node scrapers/import-realtor-csv.js

# Scrape Craigslist
node scrape-puppeteer.js 100
```

## Database Schema

See [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for full documentation.

**Key Tables:**
- `buildings` - 571K NYC buildings with BINs
- `complaints` - 26M HPD complaints
- `listings` - Current rentals/sales (Craigslist, Realtor, etc.)
- `reddit_testimonials` - Building testimonials
- `acris_real_property` - 16M property transactions
- `current_rents` - Rent history

## Adding a New Scraper

See [SCRAPER_GUIDE.md](docs/SCRAPER_GUIDE.md)

## Using Vayo from Other Projects

**Python Example (Rough Quarters):**
```python
from vayo_client import VayoClient

vayo = VayoClient()
buildings = vayo.get_buildings({'borough': 'MANHATTAN'})
testimonials = vayo.get_building_testimonials('The Dakota')
```

**JavaScript Example:**
```javascript
const db = new Database('/path/to/vayo/stuytown.db');
const buildings = db.prepare('SELECT * FROM buildings WHERE borough = ?').all('MANHATTAN');
```

## License

ISC

---

**Status:** Production-ready data hub serving multiple projects
```

#### Step 3.2: Create DATABASE_SCHEMA.md

**File:** `/Users/pjump/Desktop/projects/vayo/docs/DATABASE_SCHEMA.md`

```markdown
# Vayo Database Schema

**Database:** `stuytown.db` (30GB)
**Tables:** 36+
**Records:** 50M+

## Core Tables

### buildings
NYC building registry (571,476 records)

| Column | Type | Description |
|--------|------|-------------|
| bin | TEXT PRIMARY KEY | Building Identification Number (unique per building) |
| bbl | TEXT | Borough-Block-Lot (tax lot, may include multiple buildings) |
| address | TEXT | Street address |
| borough | TEXT | MANHATTAN, BROOKLYN, QUEENS, BRONX, STATEN ISLAND |
| year_built | INTEGER | Year of construction |
| num_units | INTEGER | Number of residential units |
| building_class | TEXT | NYC building classification |
| lat, lon | REAL | Geographic coordinates |

**Indexes:**
- PRIMARY KEY (bin)
- INDEX on borough, year_built, num_units

---

### complaints
HPD complaints (26,165,975 records)

| Column | Type | Description |
|--------|------|-------------|
| complaint_id | INTEGER PRIMARY KEY | Unique complaint ID |
| bin | TEXT | Foreign key to buildings.bin |
| unit_number | TEXT | Apartment number (if applicable) |
| complaint_type | TEXT | Category (HEAT, WATER, PEST, etc.) |
| status | TEXT | OPEN, CLOSED |
| date_received | DATE | When complaint was filed |

**Indexes:**
- PRIMARY KEY (complaint_id)
- INDEX on bin (for fast building lookups)

---

### listings
Current rental/sale listings (8,000+ records, growing)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| post_id | TEXT UNIQUE | Source-prefixed ID (e.g., "realtor_123", "reddit_abc") |
| url | TEXT | Listing URL |
| title | TEXT | Listing title/description |
| price | INTEGER | Rent or sale price |
| address | TEXT | Street address |
| neighborhood | TEXT | NYC neighborhood |
| bedrooms | INTEGER | Number of bedrooms |
| bathrooms | REAL | Number of bathrooms (1.5 = 1 full + 1 half) |
| square_feet | INTEGER | Unit size in sqft |
| description | TEXT | Full listing description |
| posted_at | DATETIME | When listing was posted |
| scraped_at | DATETIME | When we scraped it |
| source | TEXT | Original subreddit/site |
| data_source | TEXT | 'craigslist', 'reddit', 'realtor', 'streeteasy' |
| bin | TEXT | Building ID (foreign key to buildings.bin) |

**Indexes:**
- UNIQUE (post_id)
- INDEX on bin, address, data_source

---

### reddit_testimonials
Building testimonials from Reddit (NEW)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| building_name | TEXT | e.g., "The Dakota" |
| address | TEXT | Building address |
| bin | TEXT | Foreign key to buildings.bin |
| post_id | TEXT UNIQUE | Reddit post ID |
| subreddit | TEXT | r/NYCApartments, r/AskNYC, etc. |
| post_title | TEXT | Post title |
| post_body | TEXT | Post content |
| posted_date | DATE | When post was created |
| scraped_date | DATE | When we found it |
| source_url | TEXT | Full Reddit URL |
| sentiment | TEXT | 'positive', 'negative', 'neutral' |
| tags | TEXT | JSON array: ['rough-quarters', 'testimonial'] |

**Indexes:**
- UNIQUE (post_id)
- INDEX on bin, building_name

---

### current_rents
Rent history by unit

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| building_id | TEXT | Building identifier |
| unit_number | TEXT | Apartment number |
| bin | TEXT | Foreign key to buildings.bin |
| current_rent | INTEGER | Current monthly rent |
| bedrooms | INTEGER | Unit size |
| last_updated | DATE | When rent was last updated |
| is_stabilized | INTEGER | 1 if rent-stabilized |

**Indexes:**
- UNIQUE (building_id, unit_number)
- INDEX on bin

---

### acris_real_property
NYC property transactions (16M+ records)

| Column | Type | Description |
|--------|------|-------------|
| document_id | TEXT PRIMARY KEY | ACRIS document ID |
| recorded_datetime | DATETIME | When transaction was recorded |
| document_amt | INTEGER | Transaction amount |
| doc_type | TEXT | DEED, MORTGAGE, etc. |
| crfn | TEXT | City Register File Number |
| (many more columns) |

---

## Table Relationships

```
buildings (571K)
    ↓ bin
    ├─→ complaints (26M) - HPD complaints by building
    ├─→ listings (8K) - Current rentals/sales
    ├─→ reddit_testimonials (NEW) - Social proof
    ├─→ current_rents - Rent history
    └─→ acris_real_property (16M) - Property transactions
```

## Usage Examples

**Get building with all related data:**
```sql
-- Building info
SELECT * FROM buildings WHERE bin = '1018055';

-- Complaints
SELECT COUNT(*) FROM complaints WHERE bin = '1018055';

-- Current listings
SELECT * FROM listings WHERE bin = '1018055';

-- Testimonials
SELECT * FROM reddit_testimonials WHERE bin = '1018055';
```

**Find buildings with zero complaints:**
```sql
SELECT b.*
FROM buildings b
LEFT JOIN complaints c ON b.bin = c.bin
WHERE b.borough = 'MANHATTAN'
  AND b.num_units >= 20
GROUP BY b.bin
HAVING COUNT(c.complaint_id) = 0;
```

---

For full list of tables, run:
```bash
sqlite3 stuytown.db ".tables"
```
```

#### Step 3.3: Update Rough Quarters README

**File:** `/Users/pjump/Desktop/projects/rough-quarters/README.md`

Add section:
```markdown
## Data Architecture

Rough Quarters uses **Vayo** as its data hub.

**Vayo** is a centralized NYC real estate data platform that:
- Scrapes 10+ data sources
- Stores 30GB in single database
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
```

---

## 🎯 Success Checklist

After completing all phases:

- [ ] **Zero duplicate scrapers**
  - Reddit scraping only in Vayo
  - StreetEasy only in Vayo
  - All scraping consolidated

- [ ] **Single source of truth**
  - All data in Vayo's stuytown.db
  - No CSVs being read directly
  - Rough Quarters queries Vayo

- [ ] **Documentation complete**
  - Vayo README explains data hub
  - DATABASE_SCHEMA.md documents all tables
  - VayoClient API documented
  - Rough Quarters README explains architecture

- [ ] **Tests passing**
  - `python3 run.py all` works
  - Finds same number of diamonds
  - All strategies use VayoClient

- [ ] **Clean codebase**
  - Old scrapers archived
  - CSV files moved to Vayo
  - Clear separation of concerns

---

## 📅 Timeline

**Total estimated time:** 4-6 hours

- Phase 1 (Reddit): 2 hours
- Phase 2 (Realtor): 1.5 hours
- Phase 3 (Docs): 30-60 min
- Testing: 30 min
- Cleanup: 30 min

**Can be done incrementally:**
- Day 1: Phase 1 (Reddit consolidation)
- Day 2: Phase 2 (Realtor import)
- Day 3: Phase 3 (Documentation) + cleanup

---

## 🚀 Ready to Execute?

All steps documented, ready to start **Phase 1: Reddit Consolidation**.

**Next command:**
```bash
cd /Users/pjump/Desktop/projects/vayo/stuy-scrape-csv
# Create reddit_testimonials table
# Update scrape-reddit.js
# Run scraper
```

Want to begin?
