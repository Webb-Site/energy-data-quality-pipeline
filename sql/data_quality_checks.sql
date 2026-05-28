-- Check 1: Duplicate customers
SELECT customer_id, COUNT(*) AS record_count
FROM clean_customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check 2: Negative usage should not exist after cleaning
SELECT *
FROM clean_meter_readings
WHERE kwh_used < 0;

-- Check 3: Missing tariff rates should not exist after cleaning
SELECT *
FROM clean_tariffs
WHERE unit_rate IS NULL OR unit_rate <= 0;

-- Check 4: Monthly usage records with missing estimated cost
SELECT *
FROM monthly_usage_summary
WHERE estimated_cost IS NULL;

-- Check 5: Customer usage by month
SELECT
    reading_month,
    COUNT(DISTINCT customer_id) AS customers,
    SUM(total_kwh) AS total_kwh,
    SUM(estimated_cost) AS total_estimated_cost
FROM monthly_usage_summary
GROUP BY reading_month
ORDER BY reading_month;