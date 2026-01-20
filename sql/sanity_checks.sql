-- Sanity Checks for Experiment Data
-- Run these queries to validate data quality before analysis

-- 1. Overall counts by variant
SELECT 
    variant,
    COUNT(*) as n_users,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as pct_of_total
FROM experiment_users
GROUP BY variant
ORDER BY variant;

-- 2. Eligibility breakdown
SELECT 
    eligible,
    variant,
    COUNT(*) as n_users
FROM experiment_users
GROUP BY eligible, variant
ORDER BY eligible DESC, variant;

-- 3. Device distribution by variant (check for balance)
SELECT 
    device_category,
    variant,
    COUNT(*) as n_users,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY variant) as pct_within_variant
FROM experiment_users
GROUP BY device_category, variant
ORDER BY device_category, variant;

-- 4. Country distribution by variant (check for balance)
SELECT 
    country,
    variant,
    COUNT(*) as n_users
FROM experiment_users
WHERE country IN ('US', 'IN', 'CA')  -- Top 3 countries
GROUP BY country, variant
ORDER BY country, variant;

-- 5. Sample Ratio Check
WITH variant_counts AS (
    SELECT 
        variant,
        COUNT(*) as n
    FROM experiment_users
    GROUP BY variant
),
expected AS (
    SELECT 
        SUM(n) * 0.5 as expected_control,
        SUM(n) * 0.5 as expected_treatment
    FROM variant_counts
)
SELECT 
    v.variant,
    v.n as observed,
    CASE 
        WHEN v.variant = 'control' THEN e.expected_control
        ELSE e.expected_treatment
    END as expected,
    v.n - CASE 
        WHEN v.variant = 'control' THEN e.expected_control
        ELSE e.expected_treatment
    END as difference,
    (v.n - CASE 
        WHEN v.variant = 'control' THEN e.expected_control
        ELSE e.expected_treatment
    END) * 100.0 / CASE 
        WHEN v.variant = 'control' THEN e.expected_control
        ELSE e.expected_treatment
    END as pct_difference
FROM variant_counts v
CROSS JOIN expected e
ORDER BY v.variant;

-- 6. Contamination check (should return 0 rows)
SELECT 
    user_id,
    COUNT(DISTINCT variant) as n_variants
FROM experiment_users
GROUP BY user_id
HAVING COUNT(DISTINCT variant) > 1;
