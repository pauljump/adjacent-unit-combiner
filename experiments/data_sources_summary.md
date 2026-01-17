# NYC Real Estate Data Sources

## Free & Open Source

### 1. NYC Open Data (Socrata API)
**Access:** https://data.cityofnewyork.us (no auth required)

#### Rolling Sales (`usep-8jbt`)
- **What:** Completed property sales transactions
- **Fields:** address, sale_price, sale_date, sqft, units, etc.
- **Limitation:** Shows what SOLD, not what's currently for sale
- **Unit data:** Some records include unit numbers in address field

#### PLUTO (`64uk-42ks`)
- **What:** Building/lot characteristics
- **Fields:** total units, building class, lot size, year built
- **Use case:** Understand building structure

#### Property Valuation (`yjxr-fw8i`)
- **What:** Tax assessments
- **Fields:** assessed value, exemptions
- **Use case:** Proxy for market value

### 2. ACRIS (NYC Property Records)
- **What:** Deeds, mortgages, liens
- **Access:** https://www.nyc.gov/site/finance/property/acris.page
- **Limitation:** Historical transactions, not current listings

## The Challenge: Current For-Sale Listings

None of the public datasets show **current for-sale listings**.

### Options:

1. **Web scraping** (StreetEasy, Zillow)
   - Pros: Real-time listing data
   - Cons: Terms of service violations, bot detection, legal risk

2. **Playwright/Selenium automation**
   - Pros: Bypasses basic blocks
   - Cons: Slow, fragile, still grey area legally

3. **Paid APIs**
   - RapidAPI Real Estate APIs ($$$)
   - Zillow/Redfin partnerships ($$$$)

4. **Hybrid approach** (recommended for MVP)
   - Use NYC Open Data to identify buildings with recent sales
   - Manually verify current listings on StreetEasy
   - Build database of building patterns
   - Alert when new units appear in target buildings

## Recommendation for IDEA-155

**Phase 1:** Use NYC Rolling Sales to analyze historical patterns
- Which buildings have had multiple unit sales?
- What unit combinations sold together?
- Validate that adjacent pairs exist and sell

**Phase 2:** Manual listing monitoring
- Track 50-100 target buildings
- Check StreetEasy daily for new listings
- Identify adjacent pairs manually
- Validate economic model

**Phase 3:** Automated scraping (if Phase 2 shows demand)
- Build Playwright scraper
- Accept legal risk or negotiate API access
- Scale to full automation
