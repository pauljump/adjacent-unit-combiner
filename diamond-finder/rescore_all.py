"""
Re-score all diamonds in the database with the current scoring logic
"""
import sqlite3
from core.models import Diamond
from core.database import DiamondDatabase
from core.scorer_quality_of_life import score_diamond_qol

db = DiamondDatabase()

print("Re-scoring all diamonds in database...")
print("=" * 60)

# Get all diamonds
conn = sqlite3.connect('data/diamonds.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT id, address, unit, listing_type, price, bedrooms, sqft, photos, why_special,
           social_mentions, tenure_years, is_available, listing_url, found_by_strategies, score
    FROM diamonds
''')

rows = cursor.fetchall()
print(f"Found {len(rows)} diamonds to re-score\n")

updated_count = 0
for row in rows:
    # Reconstruct diamond from database row
    diamond = Diamond(
        address=row[1],
        unit=row[2] or "",
        listing_type=row[3] or "unknown",
        price=row[4] or 0,
        is_available=bool(row[11])
    )
    diamond.id = row[0]
    diamond.bedrooms = row[5]
    diamond.sqft = row[6]
    diamond.photos = eval(row[7]) if row[7] else []
    diamond.why_special = eval(row[8]) if row[8] else []
    diamond.social_mentions = row[9] or 0
    diamond.tenure_years = row[10]
    diamond.url = row[12]
    diamond.found_by_strategies = eval(row[13]) if row[13] else []

    old_score = row[14]

    # Re-score
    score_diamond_qol(diamond)

    # Save if changed
    if abs(diamond.score - old_score) > 0.1:  # Allow for floating point differences
        db.save_diamond(diamond)
        print(f"✓ {diamond.address}: {old_score} → {diamond.score}")
        updated_count += 1

conn.close()

print(f"\n✅ Re-scored {len(rows)} diamonds ({updated_count} changed)")
