#!/usr/bin/env python3
"""
Fetch NYC open data for real estate analysis.
Uses NYC Open Data Socrata API (free, no auth required).
"""

import requests
import json
from typing import List, Dict


class NYCDataFetcher:
    """Fetch data from NYC Open Data portal"""

    DATASETS = {
        "rolling_sales": "usep-8jbt",  # NYC Citywide Rolling Calendar Sales
        "pluto": "64uk-42ks",  # Primary Land Use Tax Lot Output
        "property_valuation": "yjxr-fw8i",  # Property Valuation and Assessment
    }

    BASE_URL = "https://data.cityofnewyork.us/resource"

    def fetch_rolling_sales(self, limit: int = 1000, borough: str = "Manhattan") -> List[Dict]:
        """
        Fetch recent property sales from NYC Rolling Sales dataset.

        Note: This shows what HAS SOLD, not what's currently for sale.
        """
        dataset_id = self.DATASETS["rolling_sales"]
        url = f"{self.BASE_URL}/{dataset_id}.json"

        params = {
            "$limit": limit,
            "$where": f"borough='{borough.upper()}'",
            "$order": "sale_date DESC"
        }

        print(f"Fetching {limit} recent sales in {borough}...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        print(f"Fetched {len(data)} sales records")
        return data

    def fetch_pluto_data(self, limit: int = 1000, borough: str = "MN") -> List[Dict]:
        """
        Fetch building/lot data from PLUTO.

        Contains: lot size, building class, units, year built, etc.
        Borough codes: MN=Manhattan, BK=Brooklyn, QN=Queens, BX=Bronx, SI=Staten Island
        """
        dataset_id = self.DATASETS["pluto"]
        url = f"{self.BASE_URL}/{dataset_id}.json"

        params = {
            "$limit": limit,
            "$where": f"borough='{borough}'",
        }

        print(f"Fetching PLUTO data for {limit} properties in {borough}...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        print(f"Fetched {len(data)} PLUTO records")
        return data


def main():
    fetcher = NYCDataFetcher()

    # Fetch recent Manhattan sales
    print("=" * 80)
    print("FETCHING NYC OPEN DATA")
    print("=" * 80)
    print()

    sales = fetcher.fetch_rolling_sales(limit=100, borough="Manhattan")

    # Save to file
    output_file = "experiments/nyc_rolling_sales_sample.json"
    with open(output_file, 'w') as f:
        json.dump(sales, f, indent=2)
    print(f"Saved to {output_file}\n")

    # Show sample
    if sales:
        print("Sample sale record:")
        print("-" * 80)
        sample = sales[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")
        print()

    # Analyze what's available
    print("=" * 80)
    print("DATA ANALYSIS")
    print("=" * 80)
    print()

    if sales:
        # Check which fields we have
        fields = sales[0].keys()
        print(f"Available fields ({len(fields)}):")
        for field in sorted(fields):
            print(f"  - {field}")
        print()

        # Check for unit numbers
        units_found = [s for s in sales if 'apartment_number' in s and s.get('apartment_number')]
        print(f"Records with apartment numbers: {len(units_found)}/{len(sales)}")

        if units_found:
            print("\nSample apartments:")
            for sale in units_found[:5]:
                addr = sale.get('address', 'N/A')
                unit = sale.get('apartment_number', 'N/A')
                price = sale.get('sale_price', 'N/A')
                date = sale.get('sale_date', 'N/A')
                print(f"  {addr} #{unit} - ${price} on {date}")


if __name__ == '__main__':
    main()
