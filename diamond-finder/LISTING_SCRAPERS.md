# Listing Scraper Research - GitHub Findings

**Goal:** Find actual available apartments in the buildings we've identified as great.

## GitHub Search Results

### StreetEasy Scrapers

1. **paetling/streeteasy_scraper** ⭐1
   - https://github.com/paetling/streeteasy_scraper
   - Scrapes and saves StreetEasy data for different searches

2. **nedhmn/streeteasy-scraper** ⭐1
   - https://github.com/nedhmn/streeteasy-scraper
   - More sophisticated: Dockerized, BrightData, FastAPI webhooks
   - Supports async scraping

3. **cschwartz1020/streeteasy-scraper** ⭐1
   - https://github.com/cschwartz1020/streeteasy-scraper
   - "Lazy implementation"

### Zillow API Libraries

1. **python-zillow** ⭐132
   - https://github.com/seme0021/python-zillow
   - Most popular Python wrapper for official Zillow API

2. **pyzillow** ⭐106
   - https://github.com/hanneshapke/pyzillow
   - Another Python Zillow API client

3. **actor-zillow-api-scraper** ⭐56
   - https://github.com/cermak-petr/actor-zillow-api-scraper
   - Apify actor for extracting data via Zillow's internal API

4. **househunt** ⭐49
   - https://github.com/althor880/househunt
   - Searches Redfin + combines with Zillow API

## Implementation Strategy

### Option 1: StreetEasy Scraper (NYC-specific)
**Pros:**
- NYC-focused (best for our use case)
- Most comprehensive NYC listings
- Has building names we can match against

**Cons:**
- Will get blocked by anti-scraping measures
- Need to use proxies/BrightData ($$$)
- Legally gray area

**Approach:**
```python
# For each building we love (The Dakota, etc.)
# Search StreetEasy for current listings in that building
# Match: "1 West 72nd Street" -> get units 3B, 5A, etc.
# Score each unit based on our quality-of-life criteria
```

### Option 2: Zillow Official API (Multi-city)
**Pros:**
- Official API (legal, stable)
- Won't get blocked
- Free tier available

**Cons:**
- Requires API key
- May have rate limits
- Less NYC-specific data than StreetEasy

**Approach:**
```python
from pyzillow import ZillowWrapper

# For each building address
# Query Zillow API for current listings
# Filter for rentals + sales
# Score units
```

### Option 3: NYC Open Data + Cross-reference
**Pros:**
- Free, official data
- No scraping needed
- Legal and stable

**Cons:**
- Doesn't show current availability
- Only shows historical sales/permits
- Need to combine with other sources

## Recommended Next Steps

1. **Short-term (NOW):**
   - Try Zillow API (python-zillow library)
   - Use free tier to test concept
   - For each of our 19 "great buildings", search current listings

2. **Medium-term:**
   - Look into StreetEasy's robots.txt and terms
   - Possibly use one of the GitHub scrapers as reference
   - Consider BrightData proxy service if needed

3. **Long-term:**
   - Build building-specific listing alerts
   - Monitor when units come available in our "great buildings"
   - Auto-score new listings

## Code Integration Plan

Create a new strategy: `strategies/building_listings_live.py`

```python
class BuildingListingsLiveStrategy(SearchStrategy):
    """
    For each building we've identified as great,
    find current available units via Zillow API.
    """

    def search(self):
        # Get our list of great buildings (from database)
        great_buildings = self.db.get_buildings_with_high_scores()

        # For each building, query Zillow
        for building in great_buildings:
            listings = zillow.search(building.address)

            # Create diamonds for available units
            for listing in listings:
                diamond = create_diamond(
                    address=listing.address,
                    unit=listing.unit,
                    price=listing.price,
                    why_special=[
                        f"In {building.name} (scored {building.score}/100)",
                        f"Building has {building.social_mentions} testimonials",
                        "CURRENTLY AVAILABLE"
                    ]
                )
```

## Legal/Ethical Considerations

- **Zillow API:** ✅ Fine to use (official)
- **StreetEasy Scraping:** ⚠️ Check robots.txt and terms
- **Public listings:** Generally OK to aggregate
- **Rate limiting:** Be respectful

## Cost Estimates

- Zillow API: Free tier (1000 calls/day)
- BrightData (if needed): ~$500/month for serious scraping
- Our current usage: $0 (all free sources)

---

**Status:** Research complete, ready to implement Zillow API integration.
