-- PRESS機械の確認
SELECT machine_list_id, machine_no, machine_type
FROM machine_list
WHERE machine_type = 'PRESS'
ORDER BY factory_id, machine_no;

-- PRESS工程を持つ製品と工程の確認
SELECT
    p.product_id,
    prod.product_code,
    p.process_id,
    p.process_no,
    p.process_name,
    p.rough_cycletime
FROM processes p
JOIN products prod ON p.product_id = prod.product_id
WHERE p.process_name LIKE '%PRESS%'
ORDER BY p.product_id, p.process_no;

-- 現在のspmデータ件数
SELECT COUNT(*) as current_spm_count FROM spm;
