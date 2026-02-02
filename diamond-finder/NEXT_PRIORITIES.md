# What We're Doing to Find MORE Diamond Homes

**Current State:** 157 diamonds cataloged, but only 14 available units

**The Gap:** We're finding BUILDINGS (100 discovered), not drilling into UNITS within them

---

## 🎯 Immediate Priorities (This Week)

### 1. **Expand Realtor Matching to ALL Discovered Buildings** ⭐ TOP PRIORITY

**Current:**
- Only matching Realtor.com listings to 13 hardcoded buildings
- Found 3 units in Ansonia

**Should be:**
- Match against ALL 100 discovered buildings
- Potential: 100 buildings × 7,214 listings = hundreds of available units

**Action:**
```python
# strategies/realtor_listings_live.py
# Instead of: hardcoded_buildings = ["The Ansonia", ...]
# Do: Query diamond database for ALL discovered buildings
# Match Realtor listings to those addresses
```

**Impact:** Could find 50-100+ available units immediately (vs 14 now)

---

### 2. **Add Unit-Level Rental History** ⭐ HIGH VALUE

**What we're missing:**
- "Which specific UNITS in this building are diamonds?"
- Rental turnover data
- Price history per unit

**Data sources we already have:**
- Vayo database has `current_rents` table (not using it yet!)
- StreetEasy rental archives
- Zillow rental history

**What this unlocks:**
- "Unit 12C rented for $8k/mo for 10 years straight = people love it"
- "Unit 4D has 50% tenant turnover = something's wrong"
- Identify best units WITHIN great buildings

**Action:** Query Vayo's rental tables for unit-level data

---

### 3. **Reddit Unit-Specific Testimonials**

**Current:** Only finding building-level mentions
- "The Dakota is great" ✓
- "I lived in Dakota unit 8D and loved it" ✗ (not extracting unit #)

**Should extract:**
- Specific unit numbers from testimonials
- "Lived in 3C for 10 years, corner unit with best light"

**Impact:** Find specific diamond units, not just buildings

---

### 4. **Building → Unit Inheritance Scoring**

**Current:** Buildings get scored, but units inside don't inherit that score

**Should be:**
- San Remo scores 47/100 (great building)
- ALL units in San Remo should START at 47/100 base score
- Then ADD unit-specific signals (corner, high floor, outdoor space)

**Result:** Units in great buildings get properly surfaced

---

## 🚀 This Month

### 5. **StreetEasy Historical Scraping**

**What we get:**
- 10+ years of listing history
- See which units listed multiple times (turnover = bad signal)
- Find units that NEVER list (owned forever = diamond)
- Price history per unit

**Action:** Build scraper (we have examples in Vayo project)

---

### 6. **Floor Plan Analysis for Unit Features**

**Data source:** NYC DOB, historical listings

**What to extract:**
- Corner units (multiple exposures)
- High floor units
- Outdoor space (terrace, balcony)
- Through-floor potential
- Sun exposure (south/east facing)

**Impact:** Auto-identify best units in each building geometrically

---

### 7. **Expand to Brooklyn, Queens**

**Current:** Only Manhattan (571K buildings, but filtered to ~500 Manhattan pre-war)

**Should add:**
- Brooklyn pre-war gems (Park Slope, Brooklyn Heights)
- Queens co-ops (Forest Hills, Rego Park)

**Impact:** 3x the potential diamonds

---

## 🔄 Always Running

### 8. **Daily Automated Discovery**

**Setup cron:**
```bash
# Run at 3am daily
0 3 * * * cd /path/to/rough-quarters/diamond-finder && python3 run.py daily

# Generate digest at 7am
0 7 * * * cd /path/to/rough-quarters/diamond-finder && python3 run.py digest
```

**Result:** Wake up to new diamonds every morning

---

### 9. **Strategy Performance Tuning**

**Current:** 20 strategies defined, but many not finding anything

**Should:**
- Deprecate strategies with 0 finds in 30 days
- Double down on high-performers
- A/B test scoring algorithms

---

### 10. **Cross-Reference More Data Sources**

**We have but aren't using:**
- Energy benchmarking (NYC Local Law 84)
- Landmark designation status
- Co-op vs condo (affects combination feasibility)
- School districts (if expanding to families)

---

## 📊 Metrics to Track

**Discovery funnel:**
```
571,476 buildings in NYC
    ↓ Filter: Pre-war + low complaints
500 candidates
    ↓ Process top 100
100 buildings discovered
    ↓ Find units in those buildings
??? specific units ← MISSING STEP
    ↓ Filter: Available now
14 available units

GOAL: Get ??? to 500+ specific units
Then 14 available → 50+ available
```

---

## 🎯 The Core Problem We're Solving

**Current bottleneck:**
1. ✅ We find great BUILDINGS (100 discovered)
2. ❌ We don't drill into UNITS within those buildings
3. ❌ Only 14 available units (all from ONE building - Ansonia)

**Solution:**
1. Match Realtor listings to ALL 100 buildings (not just 13)
2. Add unit-level data (rental history, floor plans)
3. Inherit building scores to units
4. Extract unit numbers from testimonials

**Result:**
- From 14 available units → 50-100+ available units
- From "great buildings" → "specific great apartments"
- From building-level diamonds → unit-level diamonds

---

## What to Build First?

**My recommendation for next 2 hours:**

### Priority #1: Expand Realtor Matching
- Update `realtor_listings_live.py` to query ALL discovered buildings
- Should find 50+ available units immediately

### Priority #2: Query Vayo Rental Data
- Explore `current_rents` table
- Find unit-level rental history
- Identify which units have stable tenants (diamond signal)

### Priority #3: Building → Unit Score Inheritance
- Units in great buildings should inherit building score
- Add unit-specific bonuses (corner, high floor, etc.)

**Time to impact:**
- Priority #1: 30 minutes → 3x more available units
- Priority #2: 1 hour → unit-level intelligence
- Priority #3: 30 minutes → better unit scoring

**Want me to start with Priority #1?** (Expand Realtor matching to all 100 discovered buildings)
