"""
Quick test to see what fields ACRIS actually returns
"""
import os
from sodapy import Socrata
import json

app_token = os.getenv('NYC_OPEN_DATA_KEY')
client = Socrata("data.cityofnewyork.us", app_token, timeout=60)

print("Fetching sample ACRIS records...")
results = client.get(
    "bnx9-e6tj",  # ACRIS Real Property Master
    limit=5,
    order="document_date DESC"
)

print(f"\nGot {len(results)} records\n")
print("=" * 80)

for i, record in enumerate(results, 1):
    print(f"\nRECORD {i}:")
    print(json.dumps(record, indent=2))
    print("=" * 80)

print("\n\nAVAILABLE FIELDS:")
if results:
    fields = sorted(results[0].keys())
    for field in fields:
        print(f"  - {field}")
