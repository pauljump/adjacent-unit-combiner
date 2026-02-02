# Project Consolidation & Rename Proposal

## What We Thought We Were Building

**Original Idea (IDEA-155):** "Adjacent Unit Combiner"
- Find two units for sale you can combine
- ONE specific arbitrage opportunity
- Manual curation of listings
- 2-week MVP

## What We Actually Built

**Reality (IDEA-155-v2):** "Home Intelligence Engine"
- Autonomous discovery system
- 571,476 buildings analyzed (not just listings)
- 6+ search strategies (adjacent units is just ONE)
- 157 diamonds cataloged
- Self-improving, always searching
- Quality of life focused

**The Evolution:**
```
Week 1: Adjacent units → Found 133 pairs
Week 2: "What else is a diamond?" → Added testimonials, maintenance
Week 3: BREAKTHROUGH → Data-driven discovery from 571K buildings
        From 26 hardcoded → 500 candidates → 100 processed → 157 cataloged
```

---

## Current Directory Structure

```
adjacent-unit-combiner/                  ← MISLEADING NAME
├── diamond-finder/                      ← ACTUAL SYSTEM
│   ├── strategies/                      ← 6 live strategies
│   │   ├── adjacent_units.py            ← Original idea (1 of 6)
│   │   ├── discover_great_buildings.py  ← NEW: 571K building query
│   │   ├── building_testimonials.py     ← Reddit social proof
│   │   ├── well_maintained_buildings.py ← HPD violations
│   │   ├── realtor_listings_live.py     ← 7K current listings
│   │   └── long_tenure_simple.py        ← ACRIS property records
│   ├── data/
│   │   └── diamonds.db                  ← 157 diamonds cataloged
│   └── run.py                           ← Main orchestrator
├── experiments/                         ← Data sources
│   ├── manhattan_all_listings.csv       ← 7,214 listings
│   └── brooklyn_all_listings.csv        ← 21M Brooklyn
├── IDEA-CARD.md                        ← Original concept (outdated)
└── IDEA-CARD-v2.md                     ← What we actually built (new)
```

---

## The Problem

**Directory name:** `adjacent-unit-combiner`
- Suggests it ONLY does adjacent units
- That's just 1 of 6 strategies now
- Misleading for what we built

**Reality:** Multi-strategy autonomous home discovery engine

---

## Rename Proposals

### Option 1: `home-intelligence` ⭐ RECOMMENDED

**Why:**
- Captures the data/intelligence aspect
- Not tied to one strategy
- Room to grow (any discovery method)
- Professional, scalable

**Full path:** `/Users/pjump/Desktop/projects/home-intelligence/`

**Rename:**
```bash
cd /Users/pjump/Desktop/projects
mv adjacent-unit-combiner home-intelligence
```

---

### Option 2: `diamond-homes`

**Why:**
- "Diamonds in the rough" is the core metaphor
- Aligns with `/diamond-finder/` subdirectory
- Easy to understand

**Full path:** `/Users/pjump/Desktop/projects/diamond-homes/`

---

### Option 3: `apartment-intelligence`

**Why:**
- More specific than "home"
- Intelligence = data-driven
- Scales to any apartment discovery method

**Full path:** `/Users/pjump/Desktop/projects/apartment-intelligence/`

---

### Option 4: `exceptional-homes`

**Why:**
- Focus on quality, not price
- "Exceptional" = the core filter
- Aspirational naming

**Full path:** `/Users/pjump/Desktop/projects/exceptional-homes/`

---

## Recommended Structure After Rename

```
home-intelligence/                       ← NEW NAME
├── README.md                            ← Update: "Home Intelligence Engine"
├── IDEA-CARD.md                        ← Replace with v2 content
├── discovery-engine/                   ← Rename from "diamond-finder"
│   ├── strategies/                     ← Keep as-is
│   ├── data/                          ← Keep as-is
│   └── run.py                         ← Keep as-is
├── data-sources/                       ← Rename from "experiments"
│   ├── realtor/
│   │   ├── manhattan_all_listings.csv
│   │   └── brooklyn_all_listings.csv
│   └── vayo/                          ← Link to Vayo DB
└── docs/
    ├── SCALING_SUCCESS.md
    ├── DATA_SOURCES_FOUND.md
    └── DATA_EXPANSION_ROADMAP.md
```

---

## What Gets Updated

### 1. **Directory Name**
`adjacent-unit-combiner` → `home-intelligence`

### 2. **README.md**
Replace with concept from IDEA-CARD-v2:
- "Home Intelligence Engine"
- "Discovers exceptional homes from 571K buildings"
- Link to strategies, data sources, roadmap

### 3. **IDEA-CARD.md**
Replace old content with v2:
- Show the evolution (adjacent units → full engine)
- Current stats (157 diamonds, 6 strategies)
- Vision achieved

### 4. **Subdirectory Names** (optional)
- `diamond-finder/` → `discovery-engine/`
- `experiments/` → `data-sources/`

---

## Migration Steps

```bash
# 1. Rename main directory
cd /Users/pjump/Desktop/projects
mv adjacent-unit-combiner home-intelligence

# 2. Update README
cd home-intelligence
# (Replace README.md with new content)

# 3. Replace IDEA-CARD with v2
mv IDEA-CARD.md IDEA-CARD-v1-original.md
mv IDEA-CARD-v2.md IDEA-CARD.md

# 4. Optional: Rename subdirectories
mv diamond-finder discovery-engine
mv experiments data-sources

# 5. Update git remote (if needed)
# git remote set-url origin <new-url>
```

---

## My Recommendation

**Directory:** `home-intelligence`

**Why:**
1. ✅ Accurate (it IS intelligence-driven)
2. ✅ Scalable (can add any discovery method)
3. ✅ Professional naming
4. ✅ Not tied to one strategy
5. ✅ Matches what we built (data → insights → diamonds)

**Keep simple:**
- Just rename parent directory
- Update README.md
- Replace IDEA-CARD.md
- Everything else works as-is

**Result:**
Clear, accurate naming that represents the autonomous multi-strategy discovery engine we actually built.

---

## What This Represents

**Not:** A single-purpose adjacent unit finder
**Actually:** An autonomous apartment discovery intelligence system that:
- Analyzes 571K+ buildings
- Uses 6+ strategies (and growing)
- Cross-validates signals
- Catalogs diamonds (157 and growing)
- Finds availability in real-time (14 units now)
- Costs $0/month
- Runs forever

**The vision:** "Always searching, always finding new ways, always discovering"

**✅ ACHIEVED** - just needs a name that reflects it.

---

**Your call:** Which name resonates?
