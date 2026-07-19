"""
===============================================================================
10_geospatial_analysis.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Creates a visualization-ready geospatial layer for the 18 ZIP Code
    Tabulation Areas included in the Healthcare Access Equity Analysis.

Inputs:
    - data/raw/tl_2025_us_zcta520/tl_2025_us_zcta520.shp
    - data/cleaned/kitsap_healthcare_equity_metrics.csv

Outputs:
    - data/cleaned/kitsap_priority_map.geojson
    - Console-based geospatial QA summary

Processing steps:
    - Loads official 2025 Census ZCTA boundaries
    - Filters to the 18 project ZCTAs
    - Joins healthcare access metrics to the boundary polygons
    - Validates complete geographic and analytical coverage
    - Reprojects the layer to WGS 84 for web mapping
    - Exports a GeoJSON file for Power BI
===============================================================================
"""
from pathlib import Path

import geopandas as gpd
import pandas as pd

# --------------------------------------------------
# File paths
# --------------------------------------------------
zcta_path = Path(
    "data/raw/tl_2025_us_zcta520/tl_2025_us_zcta520.shp"
)

metrics_path = Path(
    "data/cleaned/kitsap_healthcare_equity_metrics.csv"
)

output_path = Path(
    "data/cleaned/kitsap_priority_map.geojson"
)

# --------------------------------------------------
# Project ZCTAs
# --------------------------------------------------
kitsap_zctas = [
    "98110",
    "98310",
    "98311",
    "98312",
    "98314",
    "98315",
    "98329",
    "98337",
    "98340",
    "98342",
    "98346",
    "98359",
    "98366",
    "98367",
    "98370",
    "98380",
    "98383",
    "98392",
]

# --------------------------------------------------
# Validate input files
# --------------------------------------------------
if not zcta_path.exists():
    raise FileNotFoundError(
        f"ZCTA shapefile not found: {zcta_path}"
    )

if not metrics_path.exists():
    raise FileNotFoundError(
        f"Healthcare equity metrics file not found: "
        f"{metrics_path}"
    )

# --------------------------------------------------
# Load national ZCTA boundaries
# --------------------------------------------------
print("Loading 2025 Census ZCTA boundaries...")

zctas = gpd.read_file(zcta_path)

zip_columns = [
    col for col in zctas.columns
    if "ZCTA5CE" in col.upper()
]

print("Possible ZCTA columns:", zip_columns)

for col in zip_columns:
    match = zctas[
        zctas[col].astype(str) == "98110"
    ]

    if not match.empty:
        print(f"\n98110 found in column: {col}")
        print(match)

print(f"National ZCTA records loaded: {len(zctas):,}")

# --------------------------------------------------
# Identify the ZCTA field
# --------------------------------------------------
zcta_column_candidates = [
    "ZCTA5CE20",
    "GEOID20",
    "GEOID",
]

zcta_column = next(
    (
        column
        for column in zcta_column_candidates
        if column in zctas.columns
    ),
    None,
)

if zcta_column is None:
    raise ValueError(
        "A recognized ZCTA identifier column was not found. "
        f"Available columns: {zctas.columns.tolist()}"
    )

zctas[zcta_column] = (
    zctas[zcta_column]
    .astype(str)
    .str.zfill(5)
)

# --------------------------------------------------
# Filter to project ZCTAs
# --------------------------------------------------
kitsap_boundaries = zctas[
    zctas[zcta_column].isin(kitsap_zctas)
].copy()

found_zctas = set(
    kitsap_boundaries[zcta_column]
)

missing_boundaries = sorted(
    set(kitsap_zctas) - found_zctas
)

unexpected_boundaries = sorted(
    found_zctas - set(kitsap_zctas)
)

if missing_boundaries:
    raise ValueError(
        f"Missing ZCTA boundaries: {missing_boundaries}"
    )

if unexpected_boundaries:
    raise ValueError(
        f"Unexpected ZCTA boundaries: "
        f"{unexpected_boundaries}"
    )

if len(kitsap_boundaries) != len(kitsap_zctas):
    raise ValueError(
        "The number of filtered boundary records does not "
        "match the expected 18 project ZCTAs."
    )

# --------------------------------------------------
# Load healthcare equity metrics
# --------------------------------------------------
print("Loading healthcare equity metrics...")

metrics = pd.read_csv(
    metrics_path,
    dtype={"ZIP": str},
)

metrics["ZIP"] = (
    metrics["ZIP"]
    .astype(str)
    .str.zfill(5)
)

required_columns = [
    "ZIP",
    "Total_Population",
    "Total_Providers",
    "Hospital_Beds",
    "Providers_per_10k",
    "Poverty_Rate",
    "Uninsured_Rate_Under_65",
    "Supply_Index",
    "Need_Index",
    "Healthcare_Access_Priority_Score",
    "Priority_Score",
    "Priority_Rank",
    "Relative_Priority_Level",
]

missing_columns = [
    column
    for column in required_columns
    if column not in metrics.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required metrics columns: "
        f"{missing_columns}"
    )

duplicate_metric_zips = metrics[
    metrics["ZIP"].duplicated(keep=False)
]["ZIP"].unique()

if len(duplicate_metric_zips) > 0:
    raise ValueError(
        "Duplicate ZIP records found in healthcare equity "
        f"metrics: {duplicate_metric_zips.tolist()}"
    )

metrics = metrics[
    required_columns
].copy()

# --------------------------------------------------
# Prepare boundary identifier
# --------------------------------------------------
kitsap_boundaries = kitsap_boundaries.rename(
    columns={zcta_column: "ZIP"}
)

kitsap_boundaries = kitsap_boundaries[
    [
        "ZIP",
        "geometry",
    ]
].copy()

# --------------------------------------------------
# Join metrics to geographic boundaries
# --------------------------------------------------
priority_map = kitsap_boundaries.merge(
    metrics,
    on="ZIP",
    how="left",
    validate="one_to_one",
)

missing_metrics = priority_map[
    priority_map["Priority_Score"].isna()
]["ZIP"].tolist()

if missing_metrics:
    raise ValueError(
        "Healthcare metrics were not matched for these "
        f"ZCTAs: {missing_metrics}"
    )

if len(priority_map) != len(kitsap_zctas):
    raise ValueError(
        "The completed geospatial layer does not contain "
        "the expected 18 records."
    )

# --------------------------------------------------
# Validate geometries
# --------------------------------------------------
empty_geometries = priority_map[
    priority_map.geometry.is_empty
]["ZIP"].tolist()

missing_geometries = priority_map[
    priority_map.geometry.isna()
]["ZIP"].tolist()

if empty_geometries:
    raise ValueError(
        f"Empty geometries found for: {empty_geometries}"
    )

if missing_geometries:
    raise ValueError(
        f"Missing geometries found for: "
        f"{missing_geometries}"
    )

invalid_geometry_count = (
    ~priority_map.geometry.is_valid
).sum()

if invalid_geometry_count > 0:
    print(
        f"Repairing {invalid_geometry_count} invalid "
        "geometries..."
    )

    priority_map["geometry"] = (
        priority_map.geometry.make_valid()
    )

# --------------------------------------------------
# Reproject for web mapping
# --------------------------------------------------
priority_map = priority_map.to_crs(
    epsg=4326
)

# --------------------------------------------------
# Sort by priority rank
# --------------------------------------------------
priority_map = priority_map.sort_values(
    [
        "Priority_Rank",
        "ZIP",
    ]
)

# --------------------------------------------------
# Export GeoJSON
# --------------------------------------------------
output_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

priority_map.to_file(
    output_path,
    driver="GeoJSON",
)

# --------------------------------------------------
# Summary statistics
# --------------------------------------------------
priority_level_counts = (
    priority_map["Relative_Priority_Level"]
    .value_counts()
    .reindex(
        [
            "Higher",
            "Moderate",
            "Lower",
        ],
        fill_value=0,
    )
)

top_priority_row = (
    priority_map
    .sort_values("Priority_Rank")
    .iloc[0]
)

# --------------------------------------------------
# Console summary
# --------------------------------------------------
print("=" * 65)
print("GEOSPATIAL ANALYSIS COMPLETE")
print("=" * 65)

print(
    f"\nNational ZCTA records: "
    f"{len(zctas):,}"
)

print(
    f"Project ZCTA boundaries: "
    f"{len(kitsap_boundaries)}"
)

print(
    f"Healthcare metric records: "
    f"{len(metrics)}"
)

print(
    f"Successful geographic joins: "
    f"{len(priority_map)} of {len(kitsap_zctas)}"
)

print("\nPriority levels:")

for priority_level, count in priority_level_counts.items():
    print(
        f"{priority_level}: {count}"
    )

print("\nTop-priority area:")

print(
    f"ZIP: {top_priority_row['ZIP']}"
)

print(
    f"Priority score: "
    f"{top_priority_row['Priority_Score']}"
)

print(
    f"Priority rank: "
    f"{top_priority_row['Priority_Rank']}"
)

print(
    f"\nCoordinate reference system: "
    f"{priority_map.crs}"
)

print(
    f"Saved to: {output_path}"
)

print("\nReady for Power BI mapping.")

print(
    zctas[
        zctas["ZCTA5CE20"] == "98110"
    ]
)

print(zctas.columns.tolist())

