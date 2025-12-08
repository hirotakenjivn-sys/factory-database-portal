-- ================================================
-- 今週のプレス計画に関わるテーブルデータ確認
-- ================================================

-- 1. machine_list (機械リスト) - PRESS機械のみ
SELECT '=== 1. PRESS機械リスト ===' AS '';
SELECT
    machine_list_id,
    factory_id,
    machine_no,
    machine_type,
    user,
    timestamp
FROM machine_list
WHERE machine_type = 'PRESS'
ORDER BY machine_no;

-- 2. products (製品マスタ) - 有効な製品のみ、最初の20件
SELECT '' AS '';
SELECT '=== 2. 製品マスタ（有効、先頭20件） ===' AS '';
SELECT
    product_id,
    product_code,
    customer_id,
    is_active,
    user,
    timestamp
FROM products
WHERE is_active = TRUE
ORDER BY product_id
LIMIT 20;

-- 3. customers (顧客マスタ) - 有効な顧客のみ、最初の20件
SELECT '' AS '';
SELECT '=== 3. 顧客マスタ（有効、先頭20件） ===' AS '';
SELECT
    customer_id,
    customer_name,
    is_active,
    user,
    timestamp
FROM customers
WHERE is_active = TRUE
ORDER BY customer_id
LIMIT 20;

-- 4. po (発注) - 未配送POのみ、最初の30件
SELECT '' AS '';
SELECT '=== 4. 未配送PO（先頭30件） ===' AS '';
SELECT
    po_id,
    po_number,
    product_id,
    delivery_date,
    date_receive_po,
    po_quantity,
    is_delivered,
    user,
    timestamp
FROM po
WHERE is_delivered = FALSE
ORDER BY delivery_date, product_id
LIMIT 30;

-- 5. processes (工程) - PRESS工程のみ、最初の50件
SELECT '' AS '';
SELECT '=== 5. PRESS工程（先頭50件） ===' AS '';
SELECT
    process_id,
    product_id,
    process_no,
    process_name,
    rough_cycletime,
    setup_time,
    production_limit,
    user,
    timestamp
FROM processes
WHERE process_name LIKE '%PRESS%'
ORDER BY product_id, process_no
LIMIT 50;

-- 6. process_name_types (工程名マスタ) - PRESS関連のみ
SELECT '' AS '';
SELECT '=== 6. 工程名マスタ（PRESS関連） ===' AS '';
SELECT
    process_name_id,
    process_name,
    day_or_spm,
    CASE
        WHEN day_or_spm = TRUE THEN 'SPM'
        WHEN day_or_spm = FALSE THEN 'DAY'
        ELSE 'NULL'
    END AS type_label,
    user,
    timestamp
FROM process_name_types
WHERE process_name LIKE '%PRESS%'
ORDER BY process_name;

-- 7. calendar (カレンダー) - 今後の休日、最初の30件
SELECT '' AS '';
SELECT '=== 7. カレンダー（今後の休日、先頭30件） ===' AS '';
SELECT
    c.calendar_id,
    c.date_holiday,
    ht.date_type AS holiday_type,
    c.user,
    c.timestamp
FROM calendar c
LEFT JOIN holiday_types ht ON c.holiday_type_id = ht.holiday_type_id
WHERE c.date_holiday >= CURDATE()
ORDER BY c.date_holiday
LIMIT 30;

-- データ件数サマリー
SELECT '' AS '';
SELECT '=== データ件数サマリー ===' AS '';
SELECT 'PRESS機械数' AS category, COUNT(*) AS count FROM machine_list WHERE machine_type = 'PRESS'
UNION ALL
SELECT '有効製品数', COUNT(*) FROM products WHERE is_active = TRUE
UNION ALL
SELECT '有効顧客数', COUNT(*) FROM customers WHERE is_active = TRUE
UNION ALL
SELECT '未配送PO数', COUNT(*) FROM po WHERE is_delivered = FALSE
UNION ALL
SELECT 'PRESS工程数', COUNT(*) FROM processes WHERE process_name LIKE '%PRESS%'
UNION ALL
SELECT 'PRESS工程名タイプ数', COUNT(*) FROM process_name_types WHERE process_name LIKE '%PRESS%'
UNION ALL
SELECT '今後の休日数', COUNT(*) FROM calendar WHERE date_holiday >= CURDATE();
