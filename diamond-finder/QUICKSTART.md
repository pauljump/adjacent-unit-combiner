# Diamond Finder - Quick Start

## What You Just Got

A self-contained apartment discovery system that runs locally on your machine, finds exceptional opportunities, and delivers them to you in a beautiful daily digest.

## Running It Right Now

```bash
cd diamond-finder
python3 run.py all
```

This will:
1. ✅ Run all search strategies
2. ✅ Score and rank findings
3. ✅ Save to database
4. ✅ Generate HTML report
5. ✅ Open in your browser

## What You'll See

A beautiful HTML page showing:
- **Top diamonds** scored 80-100
- **Why each is special** (price premium, unique features, etc.)
- **Full details** (price, beds, sqft)
- **Discovery metadata** (which strategies found it, photos available)

## Daily Workflow

### Option 1: Manual (Start Here)

Run whenever you want to check for new diamonds:

```bash
cd diamond-finder
python3 run.py all
open data/reports/latest.html
```

### Option 2: Automated (Recommended)

Set up cron to run automatically:

```bash
# Edit crontab
crontab -e

# Add these lines:
0 3 * * * cd /Users/pjump/Desktop/projects/adjacent-unit-combiner/diamond-finder && /usr/local/bin/python3 run.py daily
0 7 * * * cd /Users/pjump/Desktop/projects/adjacent-unit-combiner/diamond-finder && /usr/local/bin/python3 run.py digest
```

Now it runs every day:
- 3am: Search for diamonds
- 7am: Generate digest

Check `data/reports/latest.html` every morning.

## Commands Reference

```bash
# Run everything (search + digest + stats)
python3 run.py all

# Just search for diamonds
python3 run.py daily

# Just generate digest from existing data
python3 run.py digest

# View strategy performance
python3 run.py stats

# Self-improvement (coming in Phase 2)
python3 run.py evolve
```

## Customization

Edit `config.yaml`:

```yaml
preferences:
  neighborhoods: ["Upper West Side", "SoHo", "Tribeca"]
  budget_max: 5000000
  budget_min: 500000
  bedrooms_min: 2
  interested_in: ["sale", "rental"]

delivery:
  max_per_day: 5  # Top 5 diamonds

scoring:
  min_score: 80  # Only show 80+ scores
```

## Current Strategies

**Active (2):**
1. **Adjacent Units Combiner** - Finds opportunities to buy and combine adjacent apartments
2. **Mock Finder** - Generates test data (will be replaced with real strategies)

**Coming in Phase 2:**
- Price Anomaly Hunter
- Long Tenure Tracker
- Rent-Stabilized Finder
- Estate Sale Monitor
- Social Media Listener
- Owner-Occupied Rental Finder
- And more... (system will generate new strategies automatically)

## Data Storage

Everything is stored in `data/diamonds.db` (SQLite):
- All diamonds ever found
- Strategy performance history
- Completely local (your data stays private)

## What's Next?

### Phase 2: Intelligence (Coming Soon)

- **LLM Strategy Generation**: System invents new search strategies weekly
- **Real Data Sources**: StreetEasy, ACRIS, Reddit, Zillow integration
- **Auto-Enrichment**: Scrapes photos, floor plans, social mentions
- **Learning Loop**: Deprecates bad strategies, refines good ones
- **Email Delivery**: Morning digest in your inbox

### Your Part

1. **Run it regularly** to build your database
2. **Review the digests** to understand what it finds
3. **Adjust config** to match your taste
4. **Wait for Phase 2** for autonomous evolution

## Cost

**Current (Phase 1):** $0/month (runs locally, no API calls)

**Phase 2:** ~$15-20/month for LLM API calls

## Philosophy

This system is designed to be:

- **Set and forget**: Runs on its own
- **Creative**: Finds opportunities you'd never think to look for
- **Learning**: Gets better over time
- **Private**: Your data stays local
- **Transparent**: You see exactly what it's doing

The goal: Wake up to exceptional apartments you didn't know existed.

## Need Help?

Check the full `README.md` for detailed documentation.

## Example Output

Your digest will look like:

```
💎 #1. 180 East 79th Street, Unit 14A - Score: 90/100
    FOR SALE: $8,300,000 (3 bed, 2,594 sqft)

    Why This Is Special:
    → Owner held for 47 years (extreme tenure)
    → Through-floor duplex with private elevator
    → Sold $3,200/sqft when building averages $1,800/sqft
    → Original 1920s pre-war details preserved
    → Sold off-market, never publicly listed

    📸 68 photos | 🔍 Found by: mock_finder
    [View Listing →]
```

Enjoy discovering diamonds! 💎
