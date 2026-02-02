# Rough Quarters - Project Structure

## 📁 Directory Layout

```
/Users/pjump/Desktop/projects/rough-quarters/          ← MAIN PROJECT
│
├── README.md                          # Project overview
├── IDEA-CARD.md                      # Full concept & vision
├── STATUS.md                         # Current status
├── NEXT_PRIORITIES.md                # What to build next
│
├── diamond-finder/                    ← THE DISCOVERY ENGINE (where we build)
│   │
│   ├── strategies/                    ← Search strategies (ADD NEW ONES HERE)
│   │   ├── adjacent_units.py
│   │   ├── discover_great_buildings.py
│   │   ├── building_testimonials.py
│   │   ├── well_maintained_buildings.py
│   │   ├── realtor_listings_live.py  ← We're updating this one
│   │   └── long_tenure_simple.py
│   │
│   ├── core/                          ← Core logic
│   │   ├── executor.py               # Runs strategies
│   │   ├── scorer_quality_of_life.py # Scoring algorithm
│   │   ├── database.py               # SQLite operations
│   │   └── models.py                 # Data models
│   │
│   ├── data/                          ← Data storage
│   │   ├── diamonds.db               # 157 diamonds cataloged
│   │   └── reports/                  # HTML digests
│   │       └── latest.html
│   │
│   ├── run.py                        ← MAIN ENTRY POINT
│   ├── config.yaml                   # Configuration
│   └── requirements.txt              # Dependencies
│
├── experiments/                       ← Raw data sources
│   ├── manhattan_all_listings.csv    # 7,214 listings
│   └── brooklyn_all_listings.csv
│
└── docs/                             ← Documentation
    ├── SCALING_SUCCESS.md
    ├── DATA_SOURCES_FOUND.md
    └── DATA_EXPANSION_ROADMAP.md
```

---

## 🎯 Where We Build Things

### Adding New Strategies
**Location:** `diamond-finder/strategies/`

Example: Creating a new strategy
```bash
cd /Users/pjump/Desktop/projects/rough-quarters/diamond-finder/strategies
# Create new_strategy.py
# Add to strategies/__init__.py
# Add to core/executor.py
```

### Updating Existing Strategies
**Location:** `diamond-finder/strategies/realtor_listings_live.py`

This is what we're updating now to match ALL discovered buildings.

### Core Logic Changes
**Location:** `diamond-finder/core/`

- Scoring: `scorer_quality_of_life.py`
- Database: `database.py`
- Execution: `executor.py`

### Running the System
**From:** `diamond-finder/` directory

```bash
cd /Users/pjump/Desktop/projects/rough-quarters/diamond-finder
python3 run.py all          # Run everything
python3 run.py daily        # Daily search
python3 run.py digest       # Generate report
python3 run.py stats        # Strategy performance
```

---

## 🔧 Current Working Directory

**You are here:** `/Users/pjump/Desktop/projects/rough-quarters/diamond-finder`

This is the **discovery engine** - where all the code lives and runs.

---

## 📊 Data Locations

### Internal Data (Managed by System)
- **Database:** `diamond-finder/data/diamonds.db` (157 diamonds)
- **Reports:** `diamond-finder/data/reports/`
- **Cache:** `diamond-finder/data/cache/`

### External Data Sources
- **Realtor.com listings:** `../experiments/manhattan_all_listings.csv`
- **Vayo database:** `/Users/pjump/Desktop/projects/vayo/stuy-scrape-csv/stuytown.db`

---

## 🚀 Quick Reference

**Building something new?**
→ Add to `diamond-finder/strategies/`

**Updating existing code?**
→ Edit in `diamond-finder/strategies/` or `diamond-finder/core/`

**Running the system?**
→ `cd diamond-finder && python3 run.py all`

**Checking results?**
→ `open diamond-finder/data/reports/latest.html`

---

**Main project:** `/Users/pjump/Desktop/projects/rough-quarters/`

**Discovery engine:** `/Users/pjump/Desktop/projects/rough-quarters/diamond-finder/` ← **WE BUILD HERE**
