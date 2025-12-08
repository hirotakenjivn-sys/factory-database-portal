-- 各製品の工程数と最後の工程を確認
SELECT
    p.product_id,
    prod.product_code,
    COUNT(*) as process_count,
    MAX(p.process_no) as max_process_no,
    GROUP_CONCAT(p.process_name ORDER BY p.process_no SEPARATOR ' → ') as process_flow
FROM processes p
JOIN products prod ON p.product_id = prod.product_id
WHERE prod.is_active = TRUE
GROUP BY p.product_id, prod.product_code
ORDER BY p.product_id
LIMIT 30;

-- PACKINGが既に存在するか確認
SELECT COUNT(*) as packing_count
FROM processes
WHERE process_name = 'PACKING';

-- process_name_typesにPACKINGが存在するか確認
SELECT * FROM process_name_types WHERE process_name = 'PACKING';
