CREATE VIEW IF NOT EXISTS test AS
SELECT
    quote(local_authority) AS stored_value,
    LENGTH(local_authority) AS length,
    COUNT(*) AS rows
FROM work_orders
WHERE local_authority LIKE 'Brisbane%'
GROUP BY local_authority;