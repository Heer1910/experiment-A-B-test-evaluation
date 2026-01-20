-- Segment Breakdowns for Experiment Analysis
-- Compute CTR and CVR by variant and segment

-- 1. Overall metrics by variant (eligible users only)
SELECT 
    variant,
    COUNT(*) as n_users,
    SUM(CASE WHEN clicked THEN 1 ELSE 0 END) as n_clicks,
    AVG(CASE WHEN clicked THEN 1.0 ELSE 0.0 END) as ctr,
    SUM(CASE WHEN converted THEN 1 ELSE 0 END) as n_conversions,
    AVG(CASE WHEN converted THEN 1.0 ELSE 0.0 END) as cvr
FROM experiment_users
WHERE eligible = TRUE
GROUP BY variant
ORDER BY variant;

-- 2. Metrics by device category and variant
SELECT 
    device_category,
    variant,
    COUNT(*) as n_users,
    AVG(CASE WHEN clicked THEN 1.0 ELSE 0.0 END) as ctr,
    AVG(CASE WHEN converted THEN 1.0 ELSE 0.0 END) as cvr
FROM experiment_users
WHERE eligible = TRUE
GROUP BY device_category, variant
ORDER BY device_category, variant;

-- 3. Metrics by country and variant (top countries only)
SELECT 
    country,
    variant,
    COUNT(*) as n_users,
    AVG(CASE WHEN clicked THEN 1.0 ELSE 0.0 END) as ctr,
    AVG(CASE WHEN converted THEN 1.0 ELSE 0.0 END) as cvr
FROM experiment_users
WHERE eligible = TRUE
  AND country IN ('US', 'IN', 'CA')
GROUP BY country, variant
ORDER BY country, variant;

-- 4. Lift calculation by device (for visualization)
WITH device_metrics AS (
    SELECT 
        device_category,
        variant,
        AVG(CASE WHEN converted THEN 1.0 ELSE 0.0 END) as cvr
    FROM experiment_users
    WHERE eligible = TRUE
    GROUP BY device_category, variant
),
control_cvr AS (
    SELECT device_category, cvr as control_cvr
    FROM device_metrics
    WHERE variant = 'control'
),
treatment_cvr AS (
    SELECT device_category, cvr as treatment_cvr
    FROM device_metrics
    WHERE variant = 'treatment'
)
SELECT 
    c.device_category,
    c.control_cvr,
    t.treatment_cvr,
    t.treatment_cvr - c.control_cvr as absolute_lift,
    (t.treatment_cvr - c.control_cvr) * 100.0 / c.control_cvr as relative_lift_pct
FROM control_cvr c
JOIN treatment_cvr t ON c.device_category = t.device_category
ORDER BY c.device_category;

-- 5. Guardrail metrics by variant
SELECT 
    variant,
    AVG(CASE WHEN bounce THEN 1.0 ELSE 0.0 END) as bounce_rate,
    AVG(session_duration_sec) as avg_session_duration_sec,
    AVG(sessions) as avg_sessions
FROM experiment_users
WHERE eligible = TRUE
GROUP BY variant
ORDER BY variant;
