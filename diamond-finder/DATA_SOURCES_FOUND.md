# NYC Listing & Building Data Sources - DISCOVERED

## 🎯 JACKPOT: YOU ALREADY HAVE THE DATA!

### 1. **Realtor.com Listings (CURRENT & HUGE)**

**Location:** `/Users/pjump/Desktop/projects/adjacent-unit-combiner/experiments/`

**Files:**
- `manhattan_all_listings.csv` - **30MB, 7,215 listings**
- `brooklyn_all_listings.csv` - **21MB**
- `manhattan_listings_real.csv` - **227KB**

**Created:** January 17, 2026 (YESTERDAY!)

**Data includes:**
- Property URL, listing ID, MLS ID
- Full address, unit, beds, baths, sqft
- List price, sold price, price history
- Photos (primary + alt photos URLs)
- Full descriptions
- Agent/broker info
- Latitude/longitude
- Status (FOR_SALE, Active, etc.)

**This is CURRENT LIVE DATA - ready to use!**

---

### 2. **Vayo Project - Comprehensive NYC Database**

**Location:** `/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/`

**Database:** `stuytown.db` - **31.8 GB!!**

**What's inside:**

```
571,476 buildings
26,165,975 HPD complaints
16,796,755 ACRIS records (property transfers, deeds)
889 Craigslist listings
```

**Tables:**
- `buildings` - 571K NYC buildings with BIN, BBL, address, floors, units, year built
- `complaints` - 26M complaint records
- `acris_master` - 16M property transfer records
- `acris_parties` - Party information for transfers
- `dob_complaints`, `dob_permits` - DOB violations and permits
- `ecb_violations` - ECB violations
- `evictions`, `eviction_filings` - Eviction records
- `hpd_contacts` - Building owner/contact info
- `craigslist_listings` - 889 Craigslist rental listings
- `energy_benchmarking` - Building energy data
- `certificates_of_occupancy` - C of O records

**This database has EVERYTHING we were querying from NYC Open Data APIs!**

---

### 3. **StreetEasy Scraper (WORKING CODE)**

**Location:** `/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/scrape-streeteasy.js`

**Status:** Complete, functional scraper

**Features:**
- Scrapes streeteasy.com/for-rent
- Extracts: address, unit, price, beds, baths, sqft, amenities, description
- Event-sourced architecture
- Stores in SQLite database
- Handles rate limiting and retries
- User-Agent rotation

**Can be run to get current StreetEasy listings!**

---

### 4. **Other Scrapers in Vayo**

**Location:** `/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/`

**Available scrapers:**
- `scrape-craigslist.js` - Craigslist rental listings
- `scrape-facebook.js` - Facebook Marketplace
- `scrape-reddit.js` - Reddit housing posts
- `scrape-puppeteer.js` - Browser automation for complex sites
- `scrape-dhcr.js` - DHCR rent stabilization data
- `scrape-evictions.js` - Eviction filings

---

### 5. **NYBits Historical Data**

**Location:** `/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/`

**Files:**
- `nybits-all-buildings.txt` - 875KB of building data
- `scripts/archive-nybits.js` - Archiver script
- `scripts/parse-nybits-archived.js` - Parser

**Logs indicate this was actively scraped/archived**

---

## 🚀 IMMEDIATE ACTION PLAN

### Option 1: Use Existing Realtor.com Data (FASTEST)

```python
# diamond-finder/strategies/realtor_listings_live.py

import pandas as pd
from typing import List
from .strategy_base import SearchStrategy
from .models import Diamond

class RealtorListingsLive(SearchStrategy):
    def search(self) -> List[Diamond]:
        # Read the CSV
        df = pd.read_csv('/Users/pjump/Desktop/projects/adjacent-unit-combiner/experiments/manhattan_all_listings.csv')

        # Get our great buildings
        great_buildings = [
            "1 West 72nd Street",  # The Dakota
            "145 Central Park West",  # San Remo
            # ... etc
        ]

        diamonds = []
        for building in great_buildings:
            # Find current listings in this building
            matches = df[df['formatted_address'].str.contains(building, na=False)]

            for _, listing in matches.iterrows():
                diamond = self._create_diamond(
                    address=listing['formatted_address'],
                    unit=listing['unit'] or '',
                    listing_type='sale' if listing['status'] == 'FOR_SALE' else 'rental',
                    price=listing['list_price'],
                    url=listing['property_url'],
                    why_special=[
                        f"CURRENTLY AVAILABLE in {building}",
                        f"Building score: {building_score}/100",
                        f"Listed: {listing['list_date']}"
                    ]
                )
                diamond.bedrooms = listing['beds']
                diamond.sqft = listing['sqft']
                diamond.photos = listing['primary_photo']
                diamonds.append(diamond)

        return diamonds
```

**Effort:** 30 minutes
**Data freshness:** January 17, 2026
**Coverage:** 7,215 Manhattan listings

---

### Option 2: Connect to Vayo Database (MOST COMPREHENSIVE)

```python
# diamond-finder/strategies/vayo_buildings_live.py

import sqlite3
from typing import List
from .strategy_base import SearchStrategy
from .models import Diamond

class VayoBuildingsLiveStrategy(SearchStrategy):
    def __init__(self):
        super().__init__(
            name="vayo_buildings_live",
            description="[LIVE] Uses Vayo's 571K building database"
        )
        self.db = sqlite3.connect('/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/stuytown.db')

    def search(self) -> List[Diamond]:
        # Query buildings with our great addresses
        cursor = self.db.cursor()

        cursor.execute('''
            SELECT b.address, b.num_units, b.year_built,
                   COUNT(DISTINCT c.id) as complaint_count
            FROM buildings b
            LEFT JOIN complaints c ON b.bin = c.bin
            WHERE b.address IN (
                '1 WEST 72ND STREET',
                '145 CENTRAL PARK WEST',
                '2109 BROADWAY'
            )
            GROUP BY b.address
        ''')

        for row in cursor.fetchall():
            address, units, year, complaints = row

            diamond = self._create_diamond(
                address=address,
                unit="Various units",
                listing_type="unknown",
                why_special=[
                    f"{units} units in building",
                    f"Built {year}",
                    f"Only {complaints} complaints (from 26M records)",
                    "Found in comprehensive NYC building database"
                ]
            )
            diamonds.append(diamond)

        return diamonds
```

**Effort:** 1 hour
**Data:** 571,476 buildings, 26M complaints, 16M ACRIS records
**Coverage:** ALL NYC buildings

---

### Option 3: Run StreetEasy Scraper (FRESHEST)

```bash
cd /Users/pjump/Desktop/projects/vayo/stuy-scrape-csv

# Install dependencies
npm install

# Run scraper (targets our buildings)
node scrape-streeteasy.js --buildings="1 West 72nd Street,145 Central Park West"
```

**Effort:** 2-3 hours (setup + run)
**Data freshness:** Real-time
**Legal:** Gray area, use carefully

---

## 📊 RECOMMENDATION

**Immediate (TODAY):**
1. Use Option 1 (Realtor.com CSV) - it's already there, 7K listings, current
2. Filter for buildings in our "great buildings" list
3. Get actual available units RIGHT NOW

**This Week:**
1. Connect to Vayo database (Option 2)
2. Cross-reference buildings with low complaints + our testimonials
3. Get the full picture: building history + current listings

**This Month:**
1. Set up StreetEasy scraper to run weekly
2. Keep data fresh
3. Alert when units become available in great buildings

---

## 💡 THE REAL WIN

**You don't need GitHub scrapers - you already have:**
- 7,215 current Manhattan listings (Realtor.com)
- 571,476 NYC buildings (Vayo)
- 26M+ complaint records (Vayo)
- 16M+ ACRIS property transfers (Vayo)
- Working scrapers for StreetEasy, Craigslist, Facebook, Reddit

**The data is LOCAL, READY, and COMPREHENSIVE.**

Just need to connect Diamond Finder to it!
