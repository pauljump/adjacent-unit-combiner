# Data Expansion Roadmap - What We're Still Missing

## ✅ What We Have (Starting Point)

### Current Data Sources
1. **Reddit Testimonials** - 19 buildings, 88+ mentions
2. **NYC HPD Violations** - Building maintenance quality
3. **NYC ACRIS** - 16M property transfers (via Vayo)
4. **Realtor.com Listings** - 7,214 current Manhattan listings
5. **Vayo Database** - 571K buildings, 26M complaints

### What This Gives Us
- ✅ Great buildings identified
- ✅ Building-level quality signals
- ✅ Current availability (some units)
- ✅ Maintenance records
- ✅ Property transfer history

---

## ❌ What We're Missing (Expansion Targets)

### 1. **Unit-Level Rental History** 🎯 HIGH PRIORITY

**What:** Historical rents for specific units over time

**Why Important:**
- See if rent stayed stable (long tenure signal)
- Identify rent-stabilized units
- Spot sudden spikes (bad landlord)
- Track unit turnover rate

**Potential Sources:**
- **StreetEasy Historical** - Has "price history" but need to scrape archives
- **Zillow Rental History** - API might have this
- **NYC DHCR** - Rent stabilization database (Vayo has scraper for this)
- **Vayo Database** - Check if `current_rents` table has historical data

**Implementation:**
```python
# Check what's in Vayo's rent data
SELECT building_id, unit_number, rent_amount, effective_date
FROM current_rents
WHERE building_id = 'The Dakota'
ORDER BY unit_number, effective_date;
```

---

### 2. **Tenant Turnover Data** 🎯 HIGH PRIORITY

**What:** How often units change hands

**Why Important:**
- Low turnover = people love living there
- High turnover = red flag
- Correlates with our "long tenure" signal

**Potential Sources:**
- **NYC DOB Change of Occupancy** - Filed when new tenant moves in
- **USPS Change of Address** - Public records (expensive)
- **Utility Connection Records** - Con Ed, National Grid (probably restricted)
- **Infer from ACRIS** - Property sales show ownership turnover

**Implementation:**
```python
# Use ACRIS to infer turnover
# If same owner for 20+ years = low turnover
SELECT property_address, COUNT(*) as transfers,
       MIN(recorded_date) as first_sale,
       MAX(recorded_date) as last_sale
FROM acris_master
GROUP BY property_address
HAVING COUNT(*) <= 2;  # Low turnover
```

---

### 3. **Building Amenity Changes Over Time**

**What:** When buildings added/removed amenities

**Why Important:**
- Gym added 5 years ago = improving building
- Doorman removed = declining building
- Correlates with quality of life

**Potential Sources:**
- **StreetEasy Building Pages** - Track amenity lists over time
- **DOB Alteration Permits** - Vayo has `dob_permits` table
- **Certificate of Occupancy Updates** - Vayo has `certificates_of_occupancy`

**Implementation:**
```python
# Check DOB permits for amenity additions
SELECT address, work_type, description, filing_date
FROM dob_permits
WHERE description LIKE '%gym%'
   OR description LIKE '%roof%'
   OR description LIKE '%lobby%'
ORDER BY filing_date DESC;
```

---

### 4. **Actual Resident Reviews** 🎯 MEDIUM PRIORITY

**What:** Reviews from people who lived in specific units

**Why Important:**
- More valuable than building-level reviews
- "Unit 4B has the best light" = actionable
- "Avoid 2nd floor, noisy" = useful

**Potential Sources:**
- **StreetEasy Reviews** - Building + sometimes unit-specific
- **ApartmentRatings.com** - Unit-level reviews
- **Google Maps Reviews** - Some mention units
- **Reddit/Yelp** - Mine for unit-specific mentions

**Implementation:**
```python
# Scrape StreetEasy building review pages
# Extract mentions of specific units
# Store: building, unit, rating, review_text, date
```

---

### 5. **Natural Light / Sun Exposure Data** 🎯 MEDIUM PRIORITY

**What:** Which units get morning sun, afternoon sun, etc.

**Why Important:**
- HUGE quality of life factor
- "Morning sun, south-facing" = premium
- Can infer from unit orientation + building position

**Potential Sources:**
- **NYC PLUTO** - Building footprints, orientations
- **Shadowmap.org API** - Sun position calculations
- **StreetEasy** - Sometimes mentions "south-facing"
- **Calculate from lat/lon** - Unit orientation + compass direction

**Implementation:**
```python
# Use building latitude/longitude + unit orientation
# Calculate sun exposure throughout year
# Score: morning sun (best), afternoon sun (worst in summer)
```

---

### 6. **Neighborhood Change Metrics**

**What:** Is the neighborhood improving or declining?

**Why Important:**
- Great building in improving area = double win
- Great building in declining area = risky

**Potential Sources:**
- **NYC Crime Stats** - Year-over-year trends
- **Business Permits** - New restaurants = improving
- **311 Complaints** - Vayo has 26M of these!
- **Zillow Home Values** - Neighborhood trends

**Implementation:**
```python
# Analyze 311 complaints trend
SELECT neighborhood,
       strftime('%Y', created_date) as year,
       COUNT(*) as complaints
FROM complaints
WHERE neighborhood IN ('Upper West Side', 'Upper East Side')
GROUP BY neighborhood, year
ORDER BY year DESC;
```

---

### 7. **Building Financial Health** 🎯 LOW PRIORITY (for diamonds)

**What:** HOA fees, assessments, financial stability

**Why Important:**
- Sudden assessment = financial trouble
- Low HOA fees = good value
- Mostly matters for buyers, less for renters

**Potential Sources:**
- **StreetEasy** - Lists HOA fees for condos
- **NYC Finance** - Building tax assessments
- **Public filings** - Co-op financial statements (rare)

---

### 8. **Unit-Specific Photos Over Time**

**What:** Photo history of specific units

**Why Important:**
- See if unit was renovated
- Compare quality across listings
- Identify "best" units in building

**Potential Sources:**
- **StreetEasy Archive** - Historical listing photos
- **Zillow** - Photo history
- **Archive.org** - Wayback machine for listing sites

---

### 9. **Broker/Agent Quality Data**

**What:** Which brokers represent the best units

**Why Important:**
- Top brokers handle top units
- Can prioritize based on agent reputation
- Network effect

**Potential Sources:**
- **Realtor.com CSV** - Has agent_name, broker_name
- **StreetEasy** - Agent transaction history
- **RealTrends** - Agent rankings

---

### 10. **Actual Tenant Demographics** (Ethical Gray Area)

**What:** Who lives in these buildings?

**Why Important:**
- Artists, professors = creative vibe
- Families = stable, quiet
- Young professionals = energy

**Potential Sources:**
- **Voter Registration** - Public but privacy concerns
- **LinkedIn** - Some people list their address
- **Infer from context** - Family-friendly amenities = families

**Note:** Tread carefully here ethically

---

## 🚀 Implementation Priority

### Phase 1 (This Week) - EASY WINS
1. ✅ Realtor.com CSV integration (DONE - just tested!)
2. **Vayo database exploration** - Check what rental history exists
3. **StreetEasy building amenities** - Scrape for our 19 great buildings
4. **ACRIS turnover analysis** - Use Vayo's 16M records

### Phase 2 (This Month) - MEDIUM EFFORT
5. **Unit-level reviews scraping** - ApartmentRatings, StreetEasy reviews
6. **Sun exposure calculations** - Use PLUTO + lat/lon
7. **Neighborhood trend analysis** - Mine Vayo's 26M complaint records
8. **Historical listing photos** - Archive.org + StreetEasy

### Phase 3 (Long-term) - HARD PROBLEMS
9. **Real-time rental price tracking** - Set up scrapers to run weekly
10. **Tenant turnover inference** - Complex data modeling
11. **Building financial health** - Harder to get data
12. **Predictive models** - ML on all the above

---

## 🎯 Next Steps

**Immediate:**
1. Add Realtor.com strategy to executor (5 minutes)
2. Query Vayo database to see what rental history exists (30 minutes)
3. Document findings (30 minutes)

**This Week:**
1. Build StreetEasy amenities scraper for our 19 buildings
2. Analyze ACRIS for turnover patterns
3. Create sun exposure calculator

**Keep expanding while using what we have!**
