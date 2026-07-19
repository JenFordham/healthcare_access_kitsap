-- =====================================================
-- Healthcare Access Equity Analysis
-- Kitsap County, Washington
--
-- Purpose:
--     Answers public-health stakeholder questions concerning the distribution
--     of licensed healthcare resources, community socioeconomic need, and the
--     relative alignment between healthcare supply and measured need.
--
-- Database:
--     data/cleaned/Healthcare_Access.db
--
-- Tables:
--     providers
--         One record per licensed clinic or hospital facility.
--
--     census
--         One record per included ZIP Code Tabulation Area.
--
--     access_metrics
--         One record per ZCTA containing demographic and healthcare-supply
--         measures.
--
--     equity_metrics
--         One record per ZCTA containing standardized component indices,
--         Healthcare Access Priority Scores, and relative priority rankings.
--
--     sensitivity_analysis
--         One record per ZCTA comparing priority rankings with and without
--         hospital beds in the Supply Index.
--
-- Analytical scope:
--     The healthcare resource inventory is limited to the Washington State
--     Department of Health clinic and hospital datasets selected for this
--     project. Results should not be interpreted as a complete inventory of
--     every healthcare provider or service available to Kitsap residents.
--
-- Primary business questions:
--     1. Where are licensed clinics and hospitals concentrated?
--     2. How does healthcare supply vary across Kitsap ZCTAs?
--     3. Which communities exhibit greater socioeconomic need?
--     4. Where may community need be less aligned with measured supply?
--     5. How stable are the priority rankings when assumptions are changed?
--
-- Author:
--     Jen Fordham
-- =====================================================

-- =====================================================
-- Query 01: Facilities by ZIP Code
--
-- Business question:
--     Where are licensed clinics and hospitals concentrated across the
--     included Kitsap County ZIP Code Tabulation Areas?
--
-- Grain:
--     One result row per ZIP.
--
-- Source table:
--     providers
-- =====================================================

SELECT
    ZIP,
    COUNT(*) AS Total_Facilities,
    SUM(CASE WHEN FACILITY_CATEGORY = 'Clinic' THEN 1 ELSE 0 END) AS Clinics,
    SUM(CASE WHEN FACILITY_CATEGORY = 'Hospital' THEN 1 ELSE 0 END) AS Hospitals
FROM providers
GROUP BY ZIP
ORDER BY Total_Facilities DESC;


-- =====================================================
-- 2. Facilities by City
-- =====================================================

SELECT
    CITY,
    COUNT(*) AS Total_Facilities,
    SUM(CASE WHEN FACILITY_CATEGORY = 'Clinic' THEN 1 ELSE 0 END) AS Clinics,
    SUM(CASE WHEN FACILITY_CATEGORY = 'Hospital' THEN 1 ELSE 0 END) AS Hospitals
FROM providers
GROUP BY CITY
ORDER BY Total_Facilities DESC;


-- =====================================================
-- 3. Total Provider Workforce by City
-- =====================================================

SELECT
    CITY,
    COUNT(*) AS Total_Facilities,
    SUM(PROVIDERS) AS Total_Providers,
    ROUND(AVG(PROVIDERS),2) AS Avg_Providers_Per_Facility
FROM providers
GROUP BY CITY
ORDER BY Total_Providers DESC;


-- =====================================================
-- 4. Provider Availability by ZIP
-- =====================================================

SELECT
    ZIP,
    Total_Providers,
    Providers_per_10k,
    Total_Population
FROM access_metrics
ORDER BY Providers_per_10k DESC;


-- =====================================================
-- 5. Communities with Higher Poverty &
--    Lower Provider Availability
-- =====================================================

SELECT
    c.ZIP,
    c.Poverty_Rate,
    a.Providers_per_10k,
    c.Total_Population
FROM census AS c
JOIN access_metrics AS a
    ON c.ZIP = a.ZIP
WHERE
    c.Poverty_Rate >
        (SELECT AVG(Poverty_Rate)
         FROM census)
AND
    a.Providers_per_10k <
        (SELECT AVG(Providers_per_10k)
         FROM access_metrics)
ORDER BY c.Poverty_Rate DESC;


-- =====================================================
-- 6. High Population ZIP Codes with
--    Highest Provider Availability
-- =====================================================

SELECT
    ZIP,
    Total_Population,
    Total_Providers,
    Providers_per_10k
FROM access_metrics
WHERE Total_Population >
    (SELECT AVG(Total_Population)
     FROM access_metrics)
ORDER BY Providers_per_10k DESC;


-- =====================================================
-- 7. Provider Availability Classification
-- =====================================================

SELECT
    ZIP,
    Providers_per_10k,

    CASE
        WHEN Providers_per_10k >= 10 THEN 'High'
        WHEN Providers_per_10k >= 5 THEN 'Moderate'
        ELSE 'Low'
    END AS Provider_Access

FROM access_metrics
ORDER BY Providers_per_10k DESC;


-- =====================================================
-- 8. High Provider Availability +
--    Low Poverty
-- =====================================================

SELECT
    ZIP,
    Providers_per_10k,
    Poverty_Rate,

    CASE
        WHEN Providers_per_10k >= 10 THEN 'High'
        WHEN Providers_per_10k >= 5 THEN 'Moderate'
        ELSE 'Low'
    END AS Provider_Access

FROM access_metrics

WHERE
    Providers_per_10k >= 10
AND
    Poverty_Rate < 8

ORDER BY Providers_per_10k DESC;


-- =====================================================
-- 9. Rank ZIP Codes by Provider Availability
-- =====================================================

SELECT
    ZIP,
    Providers_per_10k,

    RANK() OVER (
        ORDER BY Providers_per_10k DESC
    ) AS Provider_Rank,

    DENSE_RANK() OVER (
        ORDER BY Providers_per_10k DESC
    ) AS Dense_Provider_Rank,

    ROW_NUMBER() OVER (
        ORDER BY Providers_per_10k DESC
    ) AS Provider_Row_Number

FROM access_metrics
ORDER BY Provider_Rank;


-- =====================================================
-- 10. Rank ZIP Codes by Poverty Rate
-- =====================================================

SELECT
    ZIP,
    Poverty_Rate,

    RANK() OVER (
        ORDER BY Poverty_Rate DESC
    ) AS Poverty_Rank

FROM access_metrics
ORDER BY Poverty_Rank;

-- =====================================================
-- 11. Healthcare Supply by ZIP
-- =====================================================

SELECT
    ZIP,
    Providers_per_10k,
    Physicians_per_10k,
    Clinics,
    Clinics_per_10k,
    Hospital_Beds,
    Hospital_Beds_per_10k
FROM access_metrics
ORDER BY Providers_per_10k DESC;

-- =====================================================
-- 12. ZIP Codes with No Facilities in the Selected Data
-- =====================================================

SELECT
    ZIP,
    Total_Population,
    Poverty_Rate,
    Uninsured_Rate_Under_65
FROM access_metrics
WHERE Total_Facilities = 0
ORDER BY Total_Population DESC;

-- =====================================================
-- 13. Hospital Capacity by ZIP
-- =====================================================

SELECT
    ZIP,
    Hospitals,
    Hospital_Beds,
    Hospital_Beds_per_10k,
    Total_Population
FROM access_metrics
WHERE Hospitals > 0
ORDER BY Hospital_Beds_per_10k DESC;

-- =====================================================
-- 14. Clinic Availability by ZIP
-- =====================================================

SELECT
    ZIP,
    Clinics,
    Clinics_per_10k,
    Total_Population
FROM access_metrics
ORDER BY Clinics_per_10k DESC;

-- =====================================================
-- 15. Community Need Indicators
-- =====================================================

SELECT
    ZIP,
    Total_Population,
    Poverty_Rate,
    Uninsured_Rate_Under_65,
    Median_Household_Income
FROM access_metrics
ORDER BY Poverty_Rate DESC;

-- =====================================================
-- 16. Highest Population ZIP Codes
-- =====================================================

SELECT
    ZIP,
    Total_Population,
    Providers_per_10k,
    Physicians_per_10k,
    Clinics_per_10k,
    Hospital_Beds_per_10k
FROM access_metrics
ORDER BY Total_Population DESC;

-- =====================================================
-- Query 17: Healthcare Access Priority Ranking
--
-- Business question:
--     Which ZIP codes demonstrate the greatest measured community need
--     relative to licensed healthcare supply?
--
-- Grain:
--     One result row per ZIP.
--
-- Source table:
--     equity_metrics
--
-- Interpretation:
--     Higher scores and lower rank numbers indicate greater preliminary
--     priority for further assessment. Rankings are relative to the 18 ZCTAs
--     included in this analysis and are not official shortage designations.
-- =====================================================

SELECT
    ZIP,
    Providers_per_10k,
    Physicians_per_10k,
    Clinics_per_10k,
    Hospital_Beds_per_10k,
    Poverty_Rate,
    Uninsured_Rate_Under_65,
    Total_Population,
    Supply_Index,
    Need_Index,
    Healthcare_Access_Priority_Score,
    Priority_Rank,
    Relative_Priority_Level
FROM equity_metrics
ORDER BY Priority_Rank;

-- =====================================================
-- 18. Higher Relative Priority ZIP Codes
-- =====================================================

SELECT
    ZIP,
    Healthcare_Access_Priority_Score,
    Priority_Rank,
    Providers_per_10k,
    Clinics_per_10k,
    Poverty_Rate,
    Uninsured_Rate_Under_65,
    Total_Population
FROM equity_metrics
WHERE Relative_Priority_Level = 'Higher'
ORDER BY Priority_Rank;

-- =====================================================
-- 19. Sensitivity Analysis
-- =====================================================

SELECT
    ZIP,
    Priority_Rank_With_Beds,
    Priority_Rank_Without_Beds,
    Rank_Change,
    Rank_Stability
FROM sensitivity_analysis
ORDER BY Priority_Rank_With_Beds;