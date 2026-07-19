"""
===============================================================================
08_build_equity_index.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Creates a preliminary Healthcare Access Priority Score that compares
    standardized healthcare supply indicators with standardized measures of
    community need.

Inputs:
    - data/cleaned/kitsap_access_metrics.csv

Outputs:
    - data/cleaned/kitsap_healthcare_equity_metrics.csv

Supply Index weights:
    - Providers per 10,000 residents: 50%
    - Clinics per 10,000 residents: 30%
    - Hospital beds per 10,000 residents: 20%

Need Index weights:
    - Poverty rate: 50%
    - Uninsured rate among residents under age 65: 30%
    - Total population: 20%

Scoring:
    Healthcare Access Priority Score = Need Index - Supply Index

Interpretation:
    Higher scores indicate greater measured community need relative to the
    licensed healthcare resources represented in the selected datasets.

Important limitation:
    This score is a preliminary prioritization tool and is not an official
    healthcare-shortage or underserved-area designation.
===============================================================================
"""
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# File paths
# --------------------------------------------------
input_path = Path("data/cleaned/kitsap_access_metrics.csv")
output_path = Path("data/cleaned/kitsap_healthcare_equity_metrics.csv")

# --------------------------------------------------
# Load data
# --------------------------------------------------
df = pd.read_csv(input_path, dtype={"ZIP": str})

# --------------------------------------------------
# Validate required columns
# --------------------------------------------------
required_columns = [
    "ZIP",
    "Total_Population",
    "Poverty_Rate",
    "Uninsured_Rate_Under_65",
    "Providers_per_10k",
    "Physicians_per_10k",
    "Clinics_per_10k",
    "Hospital_Beds_per_10k",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# --------------------------------------------------
# Z-score standardization
# A value of 0 = county ZIP average
# Positive values = above average
# Negative values = below average
# --------------------------------------------------
def z_score(series: pd.Series) -> pd.Series:
    standard_deviation = series.std(ddof=0)

    if standard_deviation == 0:
        return pd.Series(0.0, index=series.index)

    return (series - series.mean()) / standard_deviation


# Supply measures: higher values indicate greater supply
supply_metrics = [
    "Providers_per_10k",
    "Physicians_per_10k",
    "Clinics_per_10k",
    "Hospital_Beds_per_10k",
]

# Need measures: higher values indicate greater community need
need_metrics = [
    "Poverty_Rate",
    "Uninsured_Rate_Under_65",
    "Total_Population",
]

# Create standardized columns
for metric in supply_metrics + need_metrics:
    df[f"{metric}_Z"] = z_score(df[metric])

# --------------------------------------------------
# Create weighted component indices
#
# Supply Index
#   50% Providers per 10k
#   30% Clinics per 10k
#   20% Hospital Beds per 10k
#
# Need Index
#   50% Poverty Rate
#   30% Uninsured Rate
#   20% Population
# --------------------------------------------------
df["Supply_Index"] = (
    df["Providers_per_10k_Z"] * 0.50 +
    df["Clinics_per_10k_Z"] * 0.30 +
    df["Hospital_Beds_per_10k_Z"] * 0.20
)

df["Need_Index"] = (
    df["Poverty_Rate_Z"] * 0.50 +
    df["Uninsured_Rate_Under_65_Z"] * 0.30 +
    df["Total_Population_Z"] * 0.20
)

# --------------------------------------------------
# Create final assessment scores
#
# Higher Healthcare_Access_Priority_Score:
# greater population need relative to healthcare supply
#
# Higher Equity_Balance:
# stronger supply relative to population need
# --------------------------------------------------
df["Healthcare_Access_Priority_Score"] = (
    df["Need_Index"] - df["Supply_Index"]
)

df["Equity_Balance"] = (
    df["Supply_Index"] - df["Need_Index"]
)

# --------------------------------------------------
# Normalize Priority Score to 0–100 for reporting
# --------------------------------------------------

min_score = df["Healthcare_Access_Priority_Score"].min()
max_score = df["Healthcare_Access_Priority_Score"].max()

df["Priority_Score"] = (
    (
        df["Healthcare_Access_Priority_Score"] - min_score
    )
    / (max_score - min_score)
) * 100

df["Priority_Score"] = df["Priority_Score"].round(1)

# Rank highest potential priority first
df["Priority_Rank"] = (
    df["Healthcare_Access_Priority_Score"]
    .rank(method="min", ascending=False)
    .astype(int)
)

# Divide ZIPs into three relative priority groups
df["Relative_Priority_Level"] = pd.qcut(
    df["Healthcare_Access_Priority_Score"].rank(method="first"),
    q=3,
    labels=["Lower", "Moderate", "Higher"]
)

# Round calculated fields
calculated_columns = [
    column for column in df.columns
    if column.endswith("_Z")
] + [
    "Supply_Index",
    "Need_Index",
    "Healthcare_Access_Priority_Score",
    "Equity_Balance",
]

df[calculated_columns] = df[calculated_columns].round(3)

# Sort highest potential priority first
df = df.sort_values(
    ["Priority_Rank", "ZIP"]
)

# --------------------------------------------------
# Export
# --------------------------------------------------
df.to_csv(output_path, index=False)

print("=" * 60)
print("HEALTHCARE EQUITY METRICS CREATED")
print("=" * 60)

print(f"\nRecords: {len(df)}")
print(f"Saved to: {output_path}")

print("\nZIP codes ranked by potential priority:")
print(
    df[
        [
            "ZIP",
            "Providers_per_10k",
            "Physicians_per_10k",
            "Clinics_per_10k",
            "Hospital_Beds_per_10k",
            "Poverty_Rate",
            "Uninsured_Rate_Under_65",
            "Total_Population",
            "Supply_Index",
            "Need_Index",
            "Healthcare_Access_Priority_Score",
            "Priority_Rank",
            "Relative_Priority_Level",
        ]
    ].to_string(index=False)
)