# Data Dictionary
## Healthcare Access Equity Analysis for Kitsap County, Washington

This document defines the fields used throughout the project. The analysis combines licensed healthcare facility data from the Washington State Department of Health with demographic data from the 2022 U.S. Census American Community Survey (ACS).

---

# Table: providers

One record represents one licensed healthcare facility.

| Field | Description | Source |
|-------|-------------|--------|
| FACILITY_ID | Unique identifier assigned during data preparation | Calculated |
| NAME | Facility name | WA DOH |
| FACILITY_CATEGORY | Clinic or Hospital | Calculated |
| TYPECARE | Primary care type (Primary, Dental, Mental Health, etc.) | WA DOH |
| TYPE | Facility ownership/type (Private, FQHC, HMO, Tribal, etc.) | WA DOH |
| ADDRESS | Facility street address | WA DOH |
| CITY | Facility city | WA DOH |
| ZIP | Facility ZIP code | WA DOH |
| PROVIDERS | Number of healthcare providers at the facility | WA DOH |
| PHYSICIANS | Number of physicians at the facility | WA DOH |
| FP_GP | Family Practice / General Practice providers | WA DOH |
| IM | Internal Medicine providers | WA DOH |
| PEDS | Pediatric providers | WA DOH |
| OB_GYN | Obstetrics & Gynecology providers | WA DOH |
| PA | Physician Assistants | WA DOH |
| NP | Nurse Practitioners | WA DOH |
| LMW | Licensed Midwives | WA DOH |

---

# Table: census

One record represents one ZIP Code Tabulation Area (ZCTA).

| Field | Description | Source |
|-------|-------------|--------|
| ZIP | ZIP Code Tabulation Area | U.S. Census ACS |
| Geography | Census geographic identifier | U.S. Census ACS |
| Total_Population | Estimated total population | U.S. Census ACS |
| Median_Age | Median age of residents | U.S. Census ACS |
| Median_Household_Income | Median household income (USD) | U.S. Census ACS |
| Population_Below_Poverty | Number of residents below the federal poverty level | U.S. Census ACS |
| Poverty_Rate | Percentage of residents below the federal poverty level | Calculated |
| Uninsured_Under_65 | Number of uninsured residents under age 65 | U.S. Census ACS |
| Uninsured_Rate_Under_65 | Percentage of uninsured residents under age 65 | Calculated |

---

# Table: access_metrics

One record represents one Kitsap County ZIP Code Tabulation Area (ZCTA).

| Field | Description | Source |
|-------|-------------|--------|
| ZIP | ZIP Code Tabulation Area | Calculated |
| Total_Population | Total population | Census |
| Median_Age | Median age | Census |
| Median_Household_Income | Median household income | Census |
| Poverty_Rate | Poverty rate (%) | Census |
| Uninsured_Rate_Under_65 | Uninsured rate (%) | Census |
| Clinics | Number of licensed clinics | Calculated |
| Hospitals | Number of licensed hospitals | Calculated |
| Total_Facilities | Total licensed healthcare facilities | Calculated |
| Total_Providers | Total healthcare providers | Calculated |
| Total_Physicians | Total physicians | Calculated |
| Hospital_Beds | Total licensed hospital beds | Calculated |
| Providers_per_10k | Providers per 10,000 residents | Calculated |
| Physicians_per_10k | Physicians per 10,000 residents | Calculated |
| Hospital_Beds_per_10k | Hospital beds per 10,000 residents | Calculated |

---

# Data Sources

- **Washington State Department of Health (DOH)** — Licensed Clinics and Hospitals datasets
- **U.S. Census Bureau** — 2022 American Community Survey (ACS) 5-Year Estimates

---

# Notes

- The analysis is limited to licensed clinics and hospitals included in the Washington State Department of Health datasets used for this project.
- ZIP codes are represented using Census ZIP Code Tabulation Areas (ZCTAs).
- Healthcare facilities may serve residents outside their own ZIP code; therefore, provider availability metrics should be interpreted as indicators of geographic access rather than direct measures of healthcare utilization.