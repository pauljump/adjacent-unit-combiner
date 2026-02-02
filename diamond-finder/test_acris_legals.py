"""
Test ACRIS Real Property Legals dataset to get addresses
"""
import os
from sodapy import Socrata
import json

app_token = os.getenv('NYC_OPEN_DATA_KEY')
client = Socrata("data.cityofnewyork.us", app_token, timeout=60)

print("Fetching sample ACRIS Real Property Legals records...")
print("(This dataset has the addresses)")

results = client.get(
    "8h5j-fqxa",  # ACRIS Real Property Legals
    limit=5,
    order=":id"
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
