"""
===============================================================================
09_sensitivity_analysis.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Evaluates whether the Healthcare Access Priority rankings are overly
    influenced by hospital-bed availability.

Inputs:
    - data/cleaned/kitsap_healthcare_equity_metrics.csv

Outputs:
    - data/cleaned/kitsap_sensitivity_analysis.csv
    - Console-based model-stability summary

Models compared:
    Model A — With hospital beds
        - Providers per 10,000: 50%
        - Clinics per 10,000: 30%
        - Hospital beds per 10,000: 20%

    Model B — Without hospital beds
        - Providers per 10,000: 60%
        - Clinics per 10,000: 40%

Evaluation measures:
    - Rank change by ZIP
    - Average and maximum absolute rank change
    - Number of unchanged ZIP rankings
    - Overlap among the five highest-priority ZIPs
===============================================================================
"""
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# File paths
# --------------------------------------------------
input_path = Path(
    "data/cleaned/kitsap_healthcare_equity_metrics.csv"
)

output_path = Path(
    "data/cleaned/kitsap_sensitivity_analysis.csv"
)

# --------------------------------------------------
# Load equity metrics
# --------------------------------------------------
df = pd.read_csv(input_path, dtype={"ZIP": str})

# --------------------------------------------------
# Validate required standardized columns
# --------------------------------------------------
required_columns = [
    "ZIP",
    "Providers_per_10k_Z",
    "Clinics_per_10k_Z",
    "Hospital_Beds_per_10k_Z",
    "Need_Index",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# --------------------------------------------------
# Model A: Current weighted model
#
# Supply:
#   50% Providers per 10k
#   30% Clinics per 10k
#   20% Hospital beds per 10k
#
# Need:
#   Existing Need_Index from script 08
# --------------------------------------------------
df["Supply_Index_With_Beds"] = (
    df["Providers_per_10k_Z"] * 0.50
    + df["Clinics_per_10k_Z"] * 0.30
    + df["Hospital_Beds_per_10k_Z"] * 0.20
)

df["Priority_Score_With_Beds"] = (
    df["Need_Index"]
    - df["Supply_Index_With_Beds"]
)

df["Priority_Rank_With_Beds"] = (
    df["Priority_Score_With_Beds"]
    .rank(method="min", ascending=False)
    .astype(int)
)

# --------------------------------------------------
# Model B: Sensitivity model without hospital beds
#
# Supply:
#   60% Providers per 10k
#   40% Clinics per 10k
#
# Need:
#   Same Need_Index as Model A
# --------------------------------------------------
df["Supply_Index_Without_Beds"] = (
    df["Providers_per_10k_Z"] * 0.60
    + df["Clinics_per_10k_Z"] * 0.40
)

df["Priority_Score_Without_Beds"] = (
    df["Need_Index"]
    - df["Supply_Index_Without_Beds"]
)

df["Priority_Rank_Without_Beds"] = (
    df["Priority_Score_Without_Beds"]
    .rank(method="min", ascending=False)
    .astype(int)
)

# --------------------------------------------------
# Compare the two models
#
# Positive Rank_Change:
# ZIP becomes lower priority when beds are removed
#
# Negative Rank_Change:
# ZIP becomes higher priority when beds are removed
# --------------------------------------------------
df["Rank_Change"] = (
    df["Priority_Rank_Without_Beds"]
    - df["Priority_Rank_With_Beds"]
)

df["Absolute_Rank_Change"] = (
    df["Rank_Change"].abs()
)

# --------------------------------------------------
# Create a simple stability label
# --------------------------------------------------
def classify_stability(change: int) -> str:
    if change == 0:
        return "No Change"
    if abs(change) == 1:
        return "Minimal Change"
    if abs(change) <= 3:
        return "Moderate Change"
    return "Large Change"


df["Rank_Stability"] = (
    df["Rank_Change"]
    .apply(classify_stability)
)

# --------------------------------------------------
# Round calculated fields
# --------------------------------------------------
score_columns = [
    "Supply_Index_With_Beds",
    "Priority_Score_With_Beds",
    "Supply_Index_Without_Beds",
    "Priority_Score_Without_Beds",
]

df[score_columns] = df[score_columns].round(3)

# --------------------------------------------------
# Select final comparison columns
# --------------------------------------------------
comparison = df[
    [
        "ZIP",
        "Priority_Score_With_Beds",
        "Priority_Rank_With_Beds",
        "Priority_Score_Without_Beds",
        "Priority_Rank_Without_Beds",
        "Rank_Change",
        "Absolute_Rank_Change",
        "Rank_Stability",
    ]
].copy()

comparison = comparison.sort_values(
    [
        "Priority_Rank_With_Beds",
        "ZIP",
    ]
)

# --------------------------------------------------
# Summary statistics
# --------------------------------------------------
average_rank_change = (
    comparison["Absolute_Rank_Change"].mean()
)

maximum_rank_change = (
    comparison["Absolute_Rank_Change"].max()
)

unchanged_count = (
    comparison["Rank_Change"] == 0
).sum()

top_five_with_beds = set(
    comparison
    .nsmallest(5, "Priority_Rank_With_Beds")["ZIP"]
)

top_five_without_beds = set(
    comparison
    .nsmallest(5, "Priority_Rank_Without_Beds")["ZIP"]
)

top_five_overlap = len(
    top_five_with_beds
    & top_five_without_beds
)

# --------------------------------------------------
# Export
# --------------------------------------------------
comparison.to_csv(output_path, index=False)

print("=" * 65)
print("SENSITIVITY ANALYSIS COMPLETE")
print("=" * 65)

print(f"\nRecords: {len(comparison)}")
print(f"Saved to: {output_path}")

print("\nModel comparison:")
print(comparison.to_string(index=False))

print("\nSummary:")
print(
    f"Average absolute rank change: "
    f"{average_rank_change:.2f}"
)

print(
    f"Maximum absolute rank change: "
    f"{maximum_rank_change}"
)

print(
    f"ZIP codes with no rank change: "
    f"{unchanged_count} of {len(comparison)}"
)

print(
    f"Top-five overlap between models: "
    f"{top_five_overlap} of 5"
)