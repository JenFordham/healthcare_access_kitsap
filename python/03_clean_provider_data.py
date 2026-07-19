"""
===============================================================================
03_clean_provider_data.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Cleans and standardizes Washington State clinic and hospital records,
    filters the data to the Kitsap County project scope, aligns the two source
    schemas, and creates one provider master table.

Inputs:
    - data/Raw/Clinics.gdb
    - data/Raw/Hospitals.gdb

Outputs:
    - data/cleaned/kitsap_provider_master.csv

Key transformations:
    - Standardizes ZIP codes and text fields
    - Converts provider measures to numeric values
    - Removes a known incorrectly coded Forks clinic record
    - Assigns Clinic and Hospital facility categories
    - Combines clinic and hospital records
===============================================================================
"""
import geopandas as gpd
import pandas as pd
from pathlib import Path

# -----------------------------
# File paths
# -----------------------------
clinic_path = r"data/Raw/Clinics.gdb"
hospital_path = r"data/Raw/Hospitals.gdb"
output_path = Path("data/cleaned")
output_path.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Kitsap ZIP Codes
# -----------------------------
kitsap_zips = [
    "98110", "98310", "98311", "98312", "98314", "98315",
    "98320", "98322", "98329", "98337", "98340",
    "98342", "98345", "98346", "98353", "98359",
    "98364", "98366", "98367", "98370", "98380",
    "98383", "98384", "98392"
]

# -----------------------------
# Load raw data
# -----------------------------
clinics = gpd.read_file(clinic_path, layer="Clinics")
hospitals = gpd.read_file(hospital_path, layer="Hospitals")

# -----------------------------
# Clean clinics
# -----------------------------
clinics["ZIP"] = clinics["ZIP"].astype(str).str[:5]
clinics = clinics[clinics["ZIP"].isin(kitsap_zips)].copy()

# Remove known data quality issue:
# Forks Women's Clinic has city=Forks but ZIP=98311.
clinics = clinics[clinics["CITY"].str.upper() != "FORKS"].copy()

clinic_cols = [
    "NAME", "ADDRESS", "CITY", "ZIP", "TYPECARE", "TYPE",
    "PROVIDERS", "PHYSICIANS", "FP_GP", "IM", "PEDS",
    "OB_GYN", "PA", "NP", "LMW", "POINT_X", "POINT_Y", "geometry"
]

clinics = clinics[clinic_cols].copy()

# Standardize text fields
text_cols = ["NAME", "ADDRESS", "CITY", "ZIP", "TYPECARE", "TYPE"]
for col in text_cols:
    clinics[col] = clinics[col].astype(str).str.strip()

# Replace blanks with Unknown
for col in ["TYPECARE", "TYPE"]:
    clinics[col] = clinics[col].replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})

# Convert provider count fields to numeric
provider_cols = ["PROVIDERS", "PHYSICIANS", "FP_GP", "IM", "PEDS", "OB_GYN", "PA", "NP", "LMW"]
for col in provider_cols:
    clinics[col] = pd.to_numeric(clinics[col], errors="coerce").fillna(0)

# Add facility type
clinics["FACILITY_CATEGORY"] = "Clinic"
clinics["HOSPITAL_BEDS"] = 0
clinics["ICU_AVAILABLE"] = "No"
clinics["ACUTE_CARE"] = "No"
clinics["CRITICAL_ACCESS"] = "No"

# -----------------------------
# Clean hospitals
# -----------------------------
hospitals["ZIP"] = hospitals["ZIP"].astype(str).str[:5]
hospitals = hospitals[hospitals["ZIP"].isin(kitsap_zips)].copy()

hospital_cols = [
    "NAME", "ADDRESS", "CITY", "ZIP", "Beds_Total",
    "ACUTE", "ICU", "CAH", "geometry"
]

hospitals = hospitals[hospital_cols].copy()

# Standardize text
for col in ["NAME", "ADDRESS", "CITY", "ZIP", "ACUTE", "ICU", "CAH"]:
    hospitals[col] = hospitals[col].astype(str).str.strip()

hospitals["Beds_Total"] = pd.to_numeric(hospitals["Beds_Total"], errors="coerce").fillna(0)

# Align hospital columns with clinic structure
hospitals["TYPECARE"] = "Hospital"
hospitals["TYPE"] = "Hospital"
hospitals["PROVIDERS"] = 0
hospitals["PHYSICIANS"] = 0
hospitals["FP_GP"] = 0
hospitals["IM"] = 0
hospitals["PEDS"] = 0
hospitals["OB_GYN"] = 0
hospitals["PA"] = 0
hospitals["NP"] = 0
hospitals["LMW"] = 0
hospitals["POINT_X"] = hospitals.geometry.x
hospitals["POINT_Y"] = hospitals.geometry.y
hospitals["FACILITY_CATEGORY"] = "Hospital"
hospitals["HOSPITAL_BEDS"] = hospitals["Beds_Total"]
hospitals["ICU_AVAILABLE"] = hospitals["ICU"]
hospitals["ACUTE_CARE"] = hospitals["ACUTE"]
hospitals["CRITICAL_ACCESS"] = hospitals["CAH"]

hospitals = hospitals.drop(columns=["Beds_Total", "ACUTE", "ICU", "CAH"])

# -----------------------------
# Combine datasets
# -----------------------------
provider_master = pd.concat([clinics, hospitals], ignore_index=True)

# Add unique ID
provider_master.insert(
    0,
    "FACILITY_ID",
    range(1, len(provider_master) + 1)
)

# Export CSV for SQL and Power BI
csv_output = output_path / "kitsap_provider_master.csv"
provider_master.drop(columns="geometry").to_csv(csv_output, index=False)

print("Provider master table created!")
print(f"Records: {len(provider_master)}")
print(f"Clinics: {(provider_master['FACILITY_CATEGORY'] == 'Clinic').sum()}")
print(f"Hospitals: {(provider_master['FACILITY_CATEGORY'] == 'Hospital').sum()}")
print(f"Saved to: {csv_output}")

print("\nFacilities by city:")
print(provider_master["CITY"].value_counts())

print("\nFacilities by category:")
print(provider_master["FACILITY_CATEGORY"].value_counts())