DROP VIEW IF EXISTS test;

DROP VIEW IF EXISTS maintenance_by_year;
CREATE VIEW maintenance_by_year AS
SELECT
    billing_year,
    COUNT(*) AS total_requests,
    ROUND(SUM(ytd_value), 2) AS expenditure,
    ROUND(AVG(ytd_value), 2) AS average_order
FROM work_orders
GROUP BY billing_year;

DROP VIEW IF EXISTS maintenance_by_authority;
CREATE VIEW maintenance_by_authority AS
SELECT
    local_authority,
    COUNT(*) AS work_orders,
    ROUND(SUM(ytd_value), 2) AS expenditure
FROM work_orders
WHERE local_authority IS NOT NULL
GROUP BY local_authority;

DROP VIEW IF EXISTS maintenance_by_type;
CREATE VIEW maintenance_by_type AS
SELECT
    wo_type,
    COUNT(*) AS work_orders,
    ROUND(SUM(ytd_value), 2) AS expenditure
FROM work_orders
WHERE wo_type IS NOT NULL
GROUP BY wo_type;

DROP VIEW IF EXISTS equipment_summary;
CREATE VIEW equipment_summary AS
SELECT
    equipment_classification,
    COUNT(*) AS work_orders,
    ROUND(SUM(ytd_value), 2) AS expenditure
FROM work_orders
WHERE equipment_classification IS NOT NULL
GROUP BY equipment_classification
ORDER BY expenditure DESC;

DROP VIEW IF EXISTS authority_performance;
CREATE VIEW authority_performance AS
SELECT
    local_authority,
    COUNT(*) AS work_orders,
    ROUND(SUM(ytd_value), 2) AS expenditure,
    ROUND(AVG(ytd_value), 2) AS average_work_order,
    MAX(ytd_value) AS largest_work_order
FROM work_orders
WHERE local_authority IS NOT NULL
GROUP BY local_authority
ORDER BY expenditure DESC;