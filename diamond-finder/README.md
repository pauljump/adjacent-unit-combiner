# Diamond Finder

An autonomous system that continuously discovers exceptional apartment opportunities ("diamonds") using multiple search strategies.

## The Vision

This system is designed to run forever on your local machine, constantly:
- **Finding** exceptional apartments using multiple creative search strategies
- **Scoring** each find based on objective signals (price, tenure, scarcity, etc.)
- **Learning** which strategies work best
- **Evolving** by generating new search strategies over time
- **Delivering** a daily digest of the best finds

## Current Status: Phase 1 (Core System)

✅ **Working:**
- Core framework (database, scoring, execution)
- 2 seed strategies (adjacent units, mock finder)
- Automated scoring system
- Beautiful HTML digest reports
- Command-line orchestration

🚧 **Coming in Phase 2:**
- LLM-powered strategy generation
- Real data source integrations (StreetEasy, ACRIS, etc.)
- Automated enrichment (photo scraping, floor plans)
- Email delivery
- Self-improvement loop

## Quick Start

### 1. Install Dependencies

```bash
cd diamond-finder
pip install -r requirements.txt
```

### 2. Run Your First Search

```bash
# Run all strategies and generate digest
python run.py all
```

This will:
- Execute all search strategies
- Find and score diamond candidates
- Save to database
- Generate an HTML report
- Open it in your browser

### 3. View Results

The system will open `data/reports/latest.html` in your browser showing your top diamonds.

## Commands

```bash
# Run daily search (execute all strategies)
python run.py daily

# Generate digest from existing data
python run.py digest

# View strategy performance stats
python run.py stats

# Self-improvement (Phase 2 - coming soon)
python run.py evolve

# Run everything (search + digest + stats)
python run.py all
```

## Configuration

Edit `config.yaml` to customize:

```yaml
preferences:
  neighborhoods: ["Upper West Side", "SoHo", ...]
  budget_max: 5000000
  budget_min: 500000
  bedrooms_min: 2
  interested_in: ["sale", "rental"]

delivery:
  method: "html"  # or "email" or "both"
  max_per_day: 5

scoring:
  min_score: 80  # Only show diamonds scoring 80+
```

## How It Works

### 1. Search Strategies

Each strategy implements a different method for finding diamonds:

- **Adjacent Units**: Finds opportunities to combine adjacent apartments
- **Mock Finder**: Test data generator (will be replaced with real strategies)

Future strategies (Phase 2):
- Price Anomaly Hunter
- Long Tenure Tracker
- Rent-Stabilized Finder
- Estate Sale Monitor
- Social Listening
- And more...

### 2. Scoring System

Each diamond is scored 0-100 based on:

- **Price Premium** (0-25 pts): How much above market it sold for
- **Tenure** (0-25 pts): How long previous owner held it
- **Photos/Evidence** (0-15 pts): Quality of documentation
- **Social Proof** (0-10 pts): Mentions in forums, blogs, etc.
- **Scarcity Signals** (0-25 pts): Unique features (terrace, views, etc.)
- **Consensus Bonus** (0-10 pts): Multiple strategies found it

### 3. Daily Digest

Every day, the system:
1. Runs all active strategies
2. Scores all findings
3. Deduplicates (same apartment found by multiple strategies)
4. Selects top N (configurable)
5. Generates beautiful HTML report

### 4. Self-Improvement (Phase 2)

The system learns which strategies perform best:
- Tracks which strategies find high-scoring diamonds
- Generates new strategies using LLM
- Deprecates low-performing strategies
- Continuously evolves without human intervention

## Running Continuously

### Option 1: Cron (Recommended)

Add to your crontab:

```bash
# Run daily at 3am
0 3 * * * cd /path/to/diamond-finder && python run.py daily

# Generate digest at 7am
0 7 * * * cd /path/to/diamond-finder && python run.py digest

# Evolve strategies weekly (Sunday at 2am)
0 2 * * 0 cd /path/to/diamond-finder && python run.py evolve
```

### Option 2: Manual

Just run whenever you want:

```bash
python run.py all
```

## Database

All diamonds are stored in `data/diamonds.db` (SQLite).

- Persistent across runs
- Deduplicates automatically
- Tracks discovery history
- Stores strategy performance

## Project Structure

```
diamond-finder/
├── run.py                 # Main orchestrator
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
├── strategies/            # Search strategies
│   ├── adjacent_units.py
│   └── mock_finder.py
├── core/                  # Core framework
│   ├── models.py          # Data models
│   ├── database.py        # Database operations
│   ├── scorer.py          # Scoring system
│   ├── executor.py        # Strategy execution
│   ├── reporter.py        # HTML generation
│   └── strategy_base.py   # Base strategy class
└── data/
    ├── diamonds.db        # SQLite database
    └── reports/           # HTML reports
        └── latest.html
```

## Adding New Strategies

1. Create a new file in `strategies/`
2. Inherit from `SearchStrategy`
3. Implement the `search()` method
4. Import it in `strategies/__init__.py`

Example:

```python
from core.strategy_base import SearchStrategy
from core.models import Diamond

class MyStrategy(SearchStrategy):
    def __init__(self):
        super().__init__(
            name="my_strategy",
            description="What this strategy does"
        )

    def search(self) -> List[Diamond]:
        diamonds = []

        # Your search logic here
        diamond = self._create_diamond(
            address="123 Main St",
            unit="5A",
            listing_type="sale",
            price=1000000,
            why_special=["Reason 1", "Reason 2"]
        )

        diamonds.append(diamond)
        return diamonds
```

## Cost Estimate

**Phase 1 (Current):**
- $0/month (runs locally, no API calls)

**Phase 2 (With LLM):**
- ~$15-20/month for LLM API calls
  - Strategy generation: ~$5/month
  - Data enrichment: ~$10/month
  - Monitoring: ~$5/month

## Next Steps

1. **Run it**: `python run.py all`
2. **Review the digest**: Check what it found
3. **Customize config**: Adjust to your preferences
4. **Wait for Phase 2**: LLM-powered evolution coming soon

## Philosophy

This system embodies:
- **Autonomous**: Set it and forget it
- **Creative**: Invents new ways to find opportunities
- **Learning**: Gets better over time
- **Local**: Your data stays on your machine
- **Transparent**: See exactly what it's doing

The goal: Wake up each day to a curated list of exceptional apartments you'd never have found manually.
