-- ================================================
-- すべての製品の工程の最後にPACKINGを追加
-- ================================================

-- 1. process_name_typesにPACKINGを追加（存在しない場合）
INSERT INTO process_name_types (process_name, day_or_spm, user)
SELECT 'PACKING', FALSE, 'admin'
WHERE NOT EXISTS (
    SELECT 1 FROM process_name_types WHERE process_name = 'PACKING'
);

-- 2. 各製品の最後にPACKING工程を追加
-- 既にPACKINGが最後の工程として存在する製品は除外
INSERT INTO processes (product_id, process_no, process_name, rough_cycletime, setup_time, production_limit, user)
SELECT
    p.product_id,
    p.max_process_no + 1 AS new_process_no,
    'PACKING' AS process_name,
    1.00 AS rough_cycletime,  -- 1日
    NULL AS setup_time,
    50000 AS production_limit,  -- 1日あたり50000個梱包可能（仮）
    'admin' AS user
FROM (
    SELECT
        product_id,
        MAX(process_no) AS max_process_no,
        MAX(CASE WHEN process_name = 'PACKING' THEN 1 ELSE 0 END) AS has_packing
    FROM processes
    GROUP BY product_id
) p
JOIN products prod ON p.product_id = prod.product_id
WHERE prod.is_active = TRUE
  AND p.has_packing = 0;  -- PACKINGがまだ存在しない製品のみ

-- 3. 追加された件数を確認
SELECT
    COUNT(*) AS added_packing_processes,
    'PACKING工程を追加しました' AS message
FROM processes
WHERE process_name = 'PACKING';

-- 4. サンプルで確認（先頭10製品の工程フロー）
SELECT
    p.product_id,
    prod.product_code,
    p.process_no,
    p.process_name,
    p.rough_cycletime,
    p.production_limit
FROM processes p
JOIN products prod ON p.product_id = prod.product_id
WHERE prod.is_active = TRUE
  AND p.product_id <= 10
ORDER BY p.product_id, p.process_no;
