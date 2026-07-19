"""
===============================================================================
02_get_census_data.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Retrieves ZIP Code Tabulation Area demographic estimates from the
    U.S. Census Bureau 2022 American Community Survey 5-Year API.

    Calculates population age 65+, poverty, and uninsured-under-65 measures
    needed for the healthcare access analysis.

Inputs:
    - U.S. Census Bureau ACS API
    - Census API key supplied through the project configuration

Outputs:
    - data/cleaned/kitsap_census_demographics.csv

Primary tools:
    - Requests
    - pandas
===============================================================================
"""
import requests
import pandas as pd

# ACS 5-year data from U.S. Census API
base_url = "https://api.census.gov/data/2022/acs/acs5"

# Variables we want
variables = {
    "NAME": "Geography",
    "B01003_001E": "Total_Population",
    "B01002_001E": "Median_Age",
    "B19013_001E": "Median_Household_Income",
    "B17001_002E": "Population_Below_Poverty",
    "B27010_002E": "Population_Under_19",
    "B27010_017E": "Uninsured_Under_19",
    "B27010_018E": "Population_19_34",
    "B27010_033E": "Uninsured_19_34",
    "B27010_034E": "Population_35_64",
    "B27010_050E": "Uninsured_35_64",
    "B01001_020E": "Female_65_66",
    "B01001_021E": "Female_67_69",
    "B01001_022E": "Female_70_74",
    "B01001_023E": "Female_75_79",
    "B01001_024E": "Female_80_84",
    "B01001_025E": "Female_85_Plus",
    "B01001_044E": "Male_65_66",
    "B01001_045E": "Male_67_69",
    "B01001_046E": "Male_70_74",
    "B01001_047E": "Male_75_79",
    "B01001_048E": "Male_80_84",
    "B01001_049E": "Male_85_Plus",
}

params = {
    "get": ",".join(variables.keys()),
    "for": "zip code tabulation area:*",
    "key": "ccbf19bf968fac9823b1bcabe26efc9901557c46"
}

response = requests.get(base_url, params=params)
response.raise_for_status()

data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data[1:], columns=data[0])

# Rename columns
df = df.rename(columns=variables)
df = df.rename(columns={"zip code tabulation area": "ZIP"})

# Kitsap ZIP codes
kitsap_zips = [
    "98110", "98310", "98311", "98312", "98314", "98315",
    "98320", "98322", "98329", "98337", "98340",
    "98342", "98345", "98346", "98353", "98359",
    "98364", "98366", "98367", "98370", "98380",
    "98383", "98384", "98392"
]

df = df[df["ZIP"].isin(kitsap_zips)]

# Convert numeric columns
numeric_cols = [col for col in df.columns if col not in ["Geography", "state", "ZIP"]]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

df["Population_Under_65"] = (
    df["Population_Under_19"]
    + df["Population_19_34"]
    + df["Population_35_64"]
)

df["Uninsured_Under_65"] = (
    df["Uninsured_Under_19"]
    + df["Uninsured_19_34"]
    + df["Uninsured_35_64"]
)

df["Uninsured_Rate_Under_65"] = (
    df["Uninsured_Under_65"]
    / df["Population_Under_65"]
    * 100
)

# Create age 65+ field
senior_cols = [
    "Female_65_66", "Female_67_69", "Female_70_74",
    "Female_75_79", "Female_80_84", "Female_85_Plus",
    "Male_65_66", "Male_67_69", "Male_70_74",
    "Male_75_79", "Male_80_84", "Male_85_Plus"
]

df["Population_65_Plus"] = df[senior_cols].sum(axis=1)
df["Percent_65_Plus"] = df["Population_65_Plus"] / df["Total_Population"] * 100
df["Poverty_Rate"] = df["Population_Below_Poverty"] / df["Total_Population"] * 100
df["Uninsured_Rate_Under_65"] = df["Uninsured_Under_65"] / df["Total_Population"] * 100

# Keep final columns
final_df = df[
    [
        "ZIP",
        "Geography",
        "Total_Population",
        "Median_Age",
        "Median_Household_Income",
        "Population_65_Plus",
        "Percent_65_Plus",
        "Population_Below_Poverty",
        "Poverty_Rate",
        "Population_Under_65",
        "Uninsured_Under_65",
        "Uninsured_Rate_Under_65",
    ]
]

print(final_df)

# Export
final_df.to_csv("data/cleaned/kitsap_census_demographics.csv", index=False)

print("\nSaved to data/cleaned/kitsap_census_demographics.csv")