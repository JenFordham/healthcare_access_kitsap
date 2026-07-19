"""
===============================================================================
06_quality_assurance.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Performs quality-assurance checks on the cleaned provider and Census
    datasets before analysis and visualization.

Inputs:
    - data/cleaned/kitsap_provider_master.csv
    - data/cleaned/kitsap_census_cleaned.csv

Outputs:
    - Console-based quality-assurance report

Checks performed:
    - Provider ZIP and Census ZCTA alignment
    - Provider ZIPs without Census records
    - Census ZCTAs without represented facilities
    - Duplicate facilities
    - Missing provider ZIP codes
    - Facility totals by ZIP
===============================================================================
"""
import pandas as pd

providers = pd.read_csv(
    "data/cleaned/kitsap_provider_master.csv",
    dtype={"ZIP": str}
)

census = pd.read_csv(
    "data/cleaned/kitsap_census_cleaned.csv",
    dtype={"ZIP": str}
)

print("=" * 60)
print("QUALITY ASSURANCE REPORT")
print("=" * 60)

# -----------------------------
# Provider ZIPs
# -----------------------------
print("\nProvider ZIPs")
print(sorted(providers["ZIP"].unique()))

# -----------------------------
# Census ZIPs
# -----------------------------
print("\nCensus ZIPs")
print(sorted(census["ZIP"].unique()))

# -----------------------------
# ZIPs with providers but no Census record
# -----------------------------
provider_only = sorted(set(providers["ZIP"]) - set(census["ZIP"]))

print("\nProvider ZIPs NOT in Census:")
print(provider_only)

# -----------------------------
# Census ZIPs with no providers
# -----------------------------
census_only = sorted(set(census["ZIP"]) - set(providers["ZIP"]))

print("\nCensus ZIPs with NO providers:")
print(census_only)

# -----------------------------
# Duplicate facilities
# -----------------------------
duplicates = providers.duplicated(
    subset=["NAME", "ADDRESS"]
).sum()

print(f"\nDuplicate facilities: {duplicates}")

# -----------------------------
# Missing ZIPs
# -----------------------------
missing_zip = providers["ZIP"].isna().sum()

print(f"Missing provider ZIPs: {missing_zip}")

# -----------------------------
# Facilities by ZIP
# -----------------------------
print("\nFacilities by ZIP")
print(providers.groupby("ZIP").size().sort_values(ascending=False))