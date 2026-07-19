"""
===============================================================================
05_merge_data.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Aggregates healthcare resources by ZIP Code and combines them with ACS
    demographic data to create the primary analysis table.

Inputs:
    - data/cleaned/kitsap_provider_master.csv
    - data/cleaned/kitsap_census_cleaned.csv

Outputs:
    - data/cleaned/kitsap_access_metrics.csv

Key calculated measures:
    - Facilities per 10,000 residents
    - Clinics per 10,000 residents
    - Providers per 10,000 residents
    - Physicians per 10,000 residents
    - Hospital beds per 10,000 residents
===============================================================================
"""
import pandas as pd
from pathlib import Path


provider_path = Path("data/cleaned/kitsap_provider_master.csv")
census_path = Path("data/cleaned/kitsap_census_cleaned.csv")
output_path = Path("data/cleaned/kitsap_access_metrics.csv")

providers = pd.read_csv(provider_path, dtype={"ZIP": str})
census = pd.read_csv(census_path, dtype={"ZIP": str})

# Aggregate provider data by ZIP
provider_summary = (
    providers
    .groupby("ZIP")
    .agg(
        Total_Facilities=("FACILITY_ID", "count"),
        Clinics=("FACILITY_CATEGORY", lambda x: (x == "Clinic").sum()),
        Hospitals=("FACILITY_CATEGORY", lambda x: (x == "Hospital").sum()),
        Total_Providers=("PROVIDERS", "sum"),
        Total_Physicians=("PHYSICIANS", "sum"),
        Family_Practice_GP=("FP_GP", "sum"),
        Internal_Medicine=("IM", "sum"),
        Pediatrics=("PEDS", "sum"),
        OB_GYN=("OB_GYN", "sum"),
        Physician_Assistants=("PA", "sum"),
        Nurse_Practitioners=("NP", "sum"),
        Licensed_Midwives=("LMW", "sum"),
        Hospital_Beds=("HOSPITAL_BEDS", "sum")
    )
    .reset_index()
)

# Merge with Census data
access = census.merge(provider_summary, on="ZIP", how="left")

# Replace ZIPs with no providers with 0
provider_cols = [
    "Total_Facilities", "Clinics", "Hospitals", "Total_Providers",
    "Total_Physicians", "Family_Practice_GP", "Internal_Medicine",
    "Pediatrics", "OB_GYN", "Physician_Assistants",
    "Nurse_Practitioners", "Licensed_Midwives", "Hospital_Beds"
]

access[provider_cols] = access[provider_cols].fillna(0)

# Access metrics per 10,000 residents
access["Facilities_per_10k"] = access["Total_Facilities"] / access["Total_Population"] * 10000
access["Clinics_per_10k"] = access["Clinics"] / access["Total_Population"] * 10000
access["Providers_per_10k"] = access["Total_Providers"] / access["Total_Population"] * 10000
access["Physicians_per_10k"] = access["Total_Physicians"] / access["Total_Population"] * 10000
access["Hospital_Beds_per_10k"] = access["Hospital_Beds"] / access["Total_Population"] * 10000

# Round metrics
rate_cols = [
    "Facilities_per_10k", "Clinics_per_10k", "Providers_per_10k",
    "Physicians_per_10k", "Hospital_Beds_per_10k"
]
access[rate_cols] = access[rate_cols].round(2)

# Sort for easy review
access = access.sort_values("Providers_per_10k", ascending=False)

access.to_csv(output_path, index=False)

print("Access metrics table created!")
print(f"Records: {len(access)}")
print(f"Saved to: {output_path}")

print("\nTop ZIPs by providers per 10k:")
print(access[["ZIP", "Total_Population", "Total_Providers", "Providers_per_10k"]].head(10))

print("\nLowest ZIPs by providers per 10k:")
print(access[["ZIP", "Total_Population", "Total_Providers", "Providers_per_10k"]].tail(10))