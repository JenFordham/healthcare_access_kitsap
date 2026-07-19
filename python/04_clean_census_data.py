"""
===============================================================================
04_clean_census_data.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Cleans the ACS demographic dataset, replaces Census missing-value codes,
    removes tiny or special-use ZCTAs from community-level analysis, and
    recalculates demographic rates.

Inputs:
    - data/cleaned/kitsap_census_demographics.csv

Outputs:
    - data/cleaned/kitsap_census_cleaned.csv

Key transformations:
    - Replaces Census missing-value placeholders with null values
    - Excludes ZCTAs with fewer than 500 residents
    - Recalculates poverty, senior-population, and uninsured rates
    - Standardizes ZIP formatting
===============================================================================
"""
import pandas as pd
from pathlib import Path

input_path = Path("data/cleaned/kitsap_census_demographics.csv")
output_path = Path("data/cleaned/kitsap_census_cleaned.csv")

census = pd.read_csv(input_path, dtype={"ZIP": str})

# Census missing-value placeholders
missing_codes = [-666666666, -888888888, -999999999]
census = census.replace(missing_codes, pd.NA)

# Remove tiny/special-use ZIPs for community-level analysis
census = census[census["Total_Population"] >= 500].copy()

# Remove ZCTAs outside the Kitsap County project scope
excluded_zips = {"98320"}
census = census[~census["ZIP"].isin(excluded_zips)].copy()

# Recalculate rates after cleaning
census["Percent_65_Plus"] = (
    census["Population_65_Plus"] / census["Total_Population"] * 100
)

census["Poverty_Rate"] = (
    census["Population_Below_Poverty"] / census["Total_Population"] * 100
)

census["Uninsured_Rate_Under_65"] = (
    census["Uninsured_Under_65"] / census["Total_Population"] * 100
)

# Round rates for readability
rate_cols = ["Percent_65_Plus", "Poverty_Rate", "Uninsured_Rate_Under_65"]
census[rate_cols] = census[rate_cols].round(2)

# Sort by ZIP
census = census.sort_values("ZIP")

census.to_csv(output_path, index=False)

print("Census data cleaned!")
print(f"Records: {len(census)}")
print(f"Saved to: {output_path}")

print("\nCleaned Census ZIPs:")
print(census[["ZIP", "Total_Population", "Median_Age", "Median_Household_Income"]])

