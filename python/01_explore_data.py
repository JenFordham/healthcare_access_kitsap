"""
===============================================================================
01_explore_data.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Profiles the raw Washington State Department of Health clinic and hospital
    GIS datasets. Reviews layers, record counts, fields, care categories, and
    potential data-quality issues before cleaning.

Inputs:
    - data/raw/Clinics.gdb
    - data/raw/Hospitals.gdb

Outputs:
    - Console-based data profiling results
    - No source data is modified

Primary tools:
    - GeoPandas
===============================================================================
"""
import geopandas as gpd

# -----------------------------
# File paths
# -----------------------------
clinic_path = r"data/raw/Clinics.gdb"
hospital_path = r"data/raw/Hospitals.gdb"

# -----------------------------
# Load datasets
# -----------------------------
clinics = gpd.read_file(clinic_path, layer="Clinics")
hospitals = gpd.read_file(hospital_path, layer="Hospitals")

# -----------------------------
# Kitsap County ZIP Codes
# -----------------------------
kitsap_zips = [
    "98110","98310", "98311", "98312", "98314", 
    "98315", "98322", "98329", "98337", "98340",
    "98342", "98345", "98346", "98353", "98359",
    "98364", "98366", "98367", "98370", "98380",
    "98383", "98384", "98392"
]

# Convert ZIPs to text
clinics["ZIP"] = clinics["ZIP"].astype(str).str[:5]
hospitals["ZIP"] = hospitals["ZIP"].astype(str).str[:5]

# -----------------------------
# Filter to Kitsap County
# -----------------------------
kitsap_clinics = clinics[clinics["ZIP"].isin(kitsap_zips)]
kitsap_hospitals = hospitals[hospitals["ZIP"].isin(kitsap_zips)]

# -----------------------------
# Results
# -----------------------------
print("=" * 50)
print("KITSAP COUNTY HEALTHCARE FACILITIES")
print("=" * 50)

print(f"\nClinics: {len(kitsap_clinics)}")
print(f"Hospitals: {len(kitsap_hospitals)}")

print("\nClinic Cities")
print(kitsap_clinics["CITY"].value_counts())

print("\nHospital Cities")
print(kitsap_hospitals["CITY"].value_counts())

print("\nHospitals")
print(
    kitsap_hospitals[
        ["NAME", "CITY", "ZIP", "Beds_Total", "ACUTE", "ICU", "CAH"]
    ]
)

print("\nClinics not in expected Kitsap cities:")
unexpected = kitsap_clinics[
    ~kitsap_clinics["CITY"].isin([
        "Bremerton",
        "Silverdale",
        "Poulsbo",
        "Port Orchard",
        "Kingston",
        "Suquamish",
        "Bainbridge Island",
        "Manchester",
        "Seabeck",
        "Hansville",
        "Keyport",
        "Tracyton"
    ])
]

print(unexpected[["NAME", "ADDRESS", "CITY", "ZIP"]])

print("\n" + "=" * 50)
print("DATA COMPLETENESS")
print("=" * 50)

columns_to_check = [
    "TYPECARE",
    "TYPE",
    "OWNER",
    "PROVIDERS",
    "PHYSICIANS",
    "FP_GP",
    "IM",
    "PEDS",
    "OB_GYN",
    "PA",
    "NP",
    "LMW"
]

for col in columns_to_check:
    print(f"\n{col}")
    print(clinics[col].value_counts(dropna=False).head(10))