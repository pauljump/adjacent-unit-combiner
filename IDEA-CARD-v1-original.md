---
id: IDEA-155
collection: concepts
legacy_ids:
- IDEA-155
directory: adjacent-unit-combiner
title: Adjacent Unit Combiner
type: Service
status: concept
confidence: Medium
one_liner: NYC real estate search that finds two adjacent for-sale units that can be combined into one larger apartment
primary_user: NYC apartment buyers looking for larger spaces
buyer: Buyers seeking 2BR+ equivalent apartments, renovators, investors
distribution_wedge: NYC real estate forums, broker referrals, luxury buyer networks
revenue_model: Commission on successful purchases or subscription for alerts
time_to_signal_days: 30
related:
- IDEA-060_off-market-apartment-hunter
- IDEA-133_off-market-supply-network-zillow-killer-wedge
---

# Adjacent Unit Combiner

**Find two small units for sale → Combine into one larger home**

## The Problem

NYC real estate pain:
- Large apartments are expensive or rare
- Two small adjacent units are often cheaper than one large unit
- No way to search for "adjacent units both for sale"
- Buyers manually cross-reference floor plans and listings
- Opportunity windows close fast (units sell separately)

**You want:** "Show me two studios/1BRs in the same building, both for sale, that share a wall"

## The Solution

Intelligent adjacency matching:
1. Ingest NYC for-sale listings (StreetEasy, Zillow, etc.)
2. Group by building address
3. Infer adjacency from unit numbers and floor plans:
   - Horizontal: 3A + 3B (same floor, sequential units)
   - Vertical: 3A + 4A (same stack, consecutive floors)
   - Diagonal: 3A + 4B (corner units that share ceiling/wall)
4. Alert when both units are for sale simultaneously
5. Show combined value vs. comparable large units

```
Example Match:
Building: 123 West 72nd St
Unit 1: 5C - Studio, $450k, 500 sqft
Unit 2: 5D - 1BR, $550k, 600 sqft
Combined: 1,100 sqft (equivalent to $1.2M+ 2BR)
Savings: ~$200k + renovation cost
```

## Why Now?

- NYC inventory data is accessible via APIs (StreetEasy, ACRIS)
- Building floor plans often publicly available (DOB filings, prior listings)
- Remote work increased demand for space vs. location
- Renovation-friendly buildings (co-op approvals loosening)
- AI/ML can infer adjacency from fuzzy data (unit naming patterns, photos)

## User Types

**Primary Users:**
1. **Growing families** - need 2BR+ but priced out
2. **Renovators** - willing to combine units as project
3. **Investors** - buy cheap, combine, sell/rent at premium

**Example persona:**
- Couple with baby in UWS 1BR
- Budget: $1M max
- Want 2BR (market rate: $1.2M+)
- Willing to renovate if savings >$150k

## Key Workflow

1. User sets preferences:
   - Neighborhoods (UWS, UES, Brooklyn Heights)
   - Budget: $1M total
   - Min combined size: 1,000 sqft
   - Unit types: Studios + 1BRs

2. System searches:
   - Pull all for-sale units in target buildings
   - Identify adjacent pairs using heuristics:
     - Unit number patterns (3A/3B, 12/12A, 501/502)
     - Floor plan analysis (shared walls)
     - Historical listings (same floor layout)

3. Alert on matches:
   - Email/SMS when new adjacent pair appears
   - Show combined layout mockup
   - Calculate total cost (purchase + renovation estimate)

4. Comparison view:
   - Combined unit specs vs. market comps
   - Estimated renovation cost (wall removal, kitchen/bath)
   - Potential resale/rental value post-combination

5. Action:
   - Connect with broker for dual showing
   - Refer to architect for feasibility study
   - Coordinate dual offers (contingent on both)

## Adjacency Inference Logic

**High Confidence (90%+ accuracy):**
- Same floor + sequential letters (3A/3B, 5C/5D)
- Same floor + sequential numbers (401/402, 1205/1206)
- Vertical stack + same letter (3A/4A, 12C/13C)

**Medium Confidence (70% accuracy):**
- Corner units diagonal (3A/4B if both corners)
- Floor plan analysis (wall positions in photos/PDFs)
- Building layout patterns (pre-war 6-unit floors)

**Low Confidence (50% accuracy):**
- Fuzzy unit naming (Studio A vs. 1BR B)
- Large buildings with irregular layouts
- New construction with custom floorplans

**Verification:**
- Pull DOB alteration permits (prior combinations)
- Check building floor plans (NYC DOB, co-op docs)
- Broker confirmation (share findings for validation)

## Differentiation

**vs Manual search (StreetEasy):**
- Manual: Check each listing, guess adjacency
- AUC: Auto-detect pairs, calculate savings

**vs Broker networks:**
- Brokers: Know their own listings
- AUC: Cross-brokerage matching citywide

**vs Zillow/StreetEasy:**
- Zillow: Single-unit search
- AUC: Multi-unit combination opportunities

**Unique Value:**
- Only tool focused on unit combination arbitrage
- Automated adjacency detection (not manual)
- Total cost modeling (purchase + reno + opportunity)

## MVP Scope

**Phase 1 (Month 1):**
- Scrape StreetEasy for Manhattan listings
- Simple adjacency rules (same floor sequential units)
- Email alerts for new matches
- No floor plan analysis (text-based only)
- Manual verification workflow

**Phase 2 (Month 2):**
- Add Brooklyn, Queens neighborhoods
- Floor plan image analysis (computer vision)
- Cost calculator (purchase + renovation estimate)
- Broker referral network (earn commission)
- User dashboard (saved searches, match history)

**Phase 3 (Month 3):**
- Building permit analysis (DOB data integration)
- Co-op/condo approval difficulty scoring
- Architectural feasibility API (structural walls)
- Financing guidance (dual mortgage vs. construction loan)
- Resale/rental value projections

**Out of Scope (v1):**
- Nationwide coverage (NYC only)
- Off-market listings (for-sale only)
- Purchase transaction platform
- Contractor marketplace

## Technical Approach

**Stack:**
- **Scraper:** Playwright/Puppeteer (StreetEasy, Zillow)
- **Database:** PostgreSQL (listings, buildings, matches)
- **Adjacency Engine:** Python (heuristics + ML)
- **Floor Plan CV:** OpenCV / Claude Vision API
- **Frontend:** Next.js (search interface, alerts)
- **Notifications:** SendGrid (email), Twilio (SMS)

**Data Pipeline:**
```
StreetEasy API → Listings Table
                ↓
         Building Grouping
                ↓
         Adjacency Matcher (rules + ML)
                ↓
         Match Candidates Table
                ↓
         User Alert Engine
```

**Adjacency Algorithm:**
```python
def find_adjacent_pairs(listings):
    # Group by building address
    building_groups = group_by(listings, 'address')

    for building, units in building_groups:
        for unit_a in units:
            for unit_b in units:
                if is_adjacent(unit_a, unit_b):
                    confidence = calculate_confidence(unit_a, unit_b)
                    yield Match(unit_a, unit_b, confidence)

def is_adjacent(a, b):
    # Horizontal: same floor, sequential units
    if a.floor == b.floor and abs(unit_num(a) - unit_num(b)) == 1:
        return True

    # Vertical: consecutive floors, same unit letter
    if abs(a.floor - b.floor) == 1 and a.unit_letter == b.unit_letter:
        return True

    # Floor plan analysis (if available)
    if share_wall_in_floorplan(a.floorplan_url, b.floorplan_url):
        return True

    return False
```

## Monetization

**Model 1: Commission (Broker Referral)**
- Refer matched buyers to partner brokers
- Earn 25% of broker commission (0.75% of sale price)
- Example: $1M combined purchase → $30k commission → $7.5k to platform

**Model 2: Subscription**
- Free: 5 matches/month, email alerts
- Pro ($29/mo): Unlimited matches, SMS alerts, cost calculator
- Premium ($99/mo): Concierge service, architect/broker intros, priority access

**Model 3: Transaction Fee**
- Charge buyer 0.5% of total purchase if deal closes
- Example: $1M purchase → $5k fee
- Only charge if both units purchased together

**Initial Focus:** Start with commission model (no upfront cost to users)

## Success Metrics

**Week 1:**
- 100 buildings indexed
- 10 adjacent pairs identified
- 5 user signups

**Month 1:**
- 1,000 buildings indexed (Manhattan)
- 50 adjacent pairs identified
- 100 active users
- 10 serious buyer leads

**Month 3:**
- 5,000 buildings indexed (Manhattan + Brooklyn)
- 200+ adjacent pairs in database
- 500 active users
- 3 successful dual purchases (closed deals)
- $20k+ in commission revenue

## Go-to-Market

**Launch Channels:**
1. **NYC real estate forums:**
   - StreetEasy forum posts
   - r/NYCapartments Reddit
   - Brownstoner comments

2. **Broker partnerships:**
   - Reach out to renovation-focused brokers
   - Offer exclusive match access
   - Revenue share model

3. **Content marketing:**
   - Blog: "How to save $200k on a 2BR in NYC"
   - Case studies of successful combinations
   - YouTube walkthroughs of combined units

4. **Paid ads:**
   - Google: "NYC 2 bedroom apartment under 1 million"
   - Facebook: Target NYC users searching real estate
   - Instagram: Before/after combination photos

**Wedge:**
- Lead with savings calculator: "See how much you could save"
- Free tool with upgrade path
- Viral: Users share matches with friends

## Risks & Mitigations

**Risk 1: False positives (units not actually adjacent)**
- **Mitigation:** Show confidence scores, require broker verification, manual review queue

**Risk 2: Co-op boards reject combination plans**
- **Mitigation:** Add co-op approval difficulty score, partner with architects for pre-checks

**Risk 3: Renovation costs exceed savings**
- **Mitigation:** Integrated cost calculator, contractor quotes, show net savings only

**Risk 4: Units sell separately before dual purchase**
- **Mitigation:** Real-time alerts, broker priority access, option to reserve both

**Risk 5: Data scraping legal issues**
- **Mitigation:** Use public APIs where available, respect robots.txt, license data if needed

## Riskiest Assumption

**"Buyers will actually pursue adjacent unit purchases instead of traditional large units"**

**Test (14 days):**
1. Manually identify 20 adjacent pairs in Manhattan
2. Post to r/NYCapartments with savings breakdown
3. Measure: Email signups, serious inquiries, broker contacts
4. Success criteria: 10+ serious leads, 2+ broker intros, 1 showing scheduled

**Follow-up tests:**
- A/B test messaging: "Save $200k" vs "Get more space"
- Survey users: What's ideal savings threshold to pursue? (50k, 100k, 200k?)
- Broker interviews: Do they see demand for this? Commission interest?

## Open Questions

1. What % of NYC buildings have adjacent units both for sale at same time? (Supply frequency)
2. Do co-op boards typically approve unit combinations? (Feasibility rate)
3. Average renovation cost for wall removal + kitchen/bath integration? (True cost)
4. How many buyers have capital for dual purchase + renovation? (Market size)
5. Should we help with financing (dual mortgage, construction loan)? (Scope expansion)

## Why This Wins

**Unique arbitrage:** No one else searching for this specific opportunity
**Quantifiable savings:** $100k-$300k vs buying equivalent large unit
**Timing advantage:** Alerts when both units available (rare windows)
**Data moat:** Building adjacency database + historical floor plans
**Network effects:** More users → more broker partners → more deal flow

This is Zillow for a specific, high-value wedge that doesn't exist yet.

## Competition

- **StreetEasy/Zillow:** Single-unit search only
- **Brokers:** Siloed to their own listings
- **RentHop/Naked Apartments:** Rental focus
- **PropertyShark:** Data tool, not buyer-facing
- **Compass Private Exclusives:** High-end only, no combination focus

**No one does:** Automated adjacent unit matching + combination opportunity alerts

## Next Steps

1. Build scraper for 100 Manhattan buildings (StreetEasy)
2. Implement basic adjacency rules (same floor, sequential units)
3. Create landing page with email signup
4. Post to r/NYCapartments with 5 real examples
5. Measure: Signups, broker interest, user feedback
6. If 20+ signups in week 1 → build dashboard
7. If broker interest → formalize referral program

## Example Match (Real Data)

**Building:** 315 West 86th Street, Manhattan
**Unit 1:** 4D - Studio, $475k, 450 sqft (listed 11/2024)
**Unit 2:** 4E - Studio, $495k, 500 sqft (listed 12/2024)

**Combined:**
- 950 sqft 2BR equivalent
- Total cost: $970k + $80k reno = $1.05M
- Market comp: 2BR in building = $1.3M+
- **Savings: $250k+**

**Adjacency confidence:** 95% (same floor, sequential units, pre-war building standard layout)

---

**Status:** Ready to validate
**Estimated MVP time:** 2 weeks (scraper + matching engine + landing page)
**First customer:** NYC apartment hunters on Reddit
