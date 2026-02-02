"""
Test NYC DOF Rolling Sales dataset - much simpler than ACRIS
This has actual sale prices, dates, and addresses in one place
"""
import os
from sodapy import Socrata
import json

app_token = os.getenv('NYC_OPEN_DATA_KEY')
client = Socrata("data.cityofnewyork.us", app_token, timeout=60)

print("Fetching NYC Rolling Sales data...")
print("(Manhattan residential sales)")

# Rolling Sales dataset: usep-8vv4
results = client.get(
    "usep-8vv4",  # DOF: Condominium Comparable Rental Income - Manhattan
    limit=10,
)

print(f"\nGot {len(results)} records\n")

if results:
    print("SAMPLE RECORD:")
    print(json.dumps(results[0], indent=2))

    print("\n\nAVAILABLE FIELDS:")
    fields = sorted(results[0].keys())
    for field in fields:
        print(f"  - {field}")
