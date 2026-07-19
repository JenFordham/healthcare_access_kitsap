"""
===============================================================================
07_create_database.py
Healthcare Access Equity Analysis — Kitsap County, Washington

Purpose:
    Loads the cleaned and derived project datasets into a SQLite database for
    SQL analysis and downstream reporting.

Inputs:
    - data/cleaned/kitsap_provider_master.csv
    - data/cleaned/kitsap_census_cleaned.csv
    - data/cleaned/kitsap_access_metrics.csv
    - data/cleaned/kitsap_healthcare_equity_metrics.csv
    - data/cleaned/kitsap_sensitivity_analysis.csv

Outputs:
    - data/cleaned/Healthcare_Access.db

Database tables:
    - providers
    - census
    - access_metrics
    - equity_metrics
    - sensitivity_analysis
===============================================================================
"""
import sqlite3
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# File paths
# --------------------------------------------------
provider_file = Path("data/cleaned/kitsap_provider_master.csv")
census_file = Path("data/cleaned/kitsap_census_cleaned.csv")
access_file = Path("data/cleaned/kitsap_access_metrics.csv")
equity_file = Path(
    "data/cleaned/kitsap_healthcare_equity_metrics.csv"
)
sensitivity_file = Path(
    "data/cleaned/kitsap_sensitivity_analysis.csv"
)

db_file = Path("data/cleaned/Healthcare_Access.db")

# --------------------------------------------------
# Read CSV files
# --------------------------------------------------
providers = pd.read_csv(
    provider_file,
    dtype={"ZIP": str}
)

census = pd.read_csv(
    census_file,
    dtype={"ZIP": str}
)

access = pd.read_csv(
    access_file,
    dtype={"ZIP": str}
)

equity = pd.read_csv(
    equity_file,
    dtype={"ZIP": str}
)

sensitivity = pd.read_csv(
    sensitivity_file,
    dtype={"ZIP": str}
)

# --------------------------------------------------
# Create SQLite database connection
# --------------------------------------------------
conn = sqlite3.connect(db_file)

# --------------------------------------------------
# Write tables to database
# --------------------------------------------------
providers.to_sql(
    "providers",
    conn,
    if_exists="replace",
    index=False
)

census.to_sql(
    "census",
    conn,
    if_exists="replace",
    index=False
)

access.to_sql(
    "access_metrics",
    conn,
    if_exists="replace",
    index=False
)

equity.to_sql(
    "equity_metrics",
    conn,
    if_exists="replace",
    index=False
)

sensitivity.to_sql(
    "sensitivity_analysis",
    conn,
    if_exists="replace",
    index=False
)

# --------------------------------------------------
# Verify tables
# --------------------------------------------------
cursor = conn.cursor()

tables = cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
    """
).fetchall()

print("=" * 50)
print("DATABASE CREATED")
print("=" * 50)

print("\nTables:")
for table in tables:
    print(f"• {table[0]}")

# --------------------------------------------------
# Verify row counts
# --------------------------------------------------
table_names = [
    "providers",
    "census",
    "access_metrics",
    "equity_metrics",
    "sensitivity_analysis",
]

print("\nRow counts:")
for table in table_names:
    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count} rows")

# --------------------------------------------------
# Close connection
# --------------------------------------------------
conn.close()

print(f"\nDatabase saved to:\n{db_file}")