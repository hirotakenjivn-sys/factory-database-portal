-- ================================================
-- すべてのPRESS工程にPRESS機とSPMを追加
-- cycle_time: 4～100個/分（ランダム）
-- ================================================

-- 既存のSPMデータをクリア
DELETE FROM spm;

-- すべてのPRESS工程（PRESS, PRESS 1/2, PRESS 1/3など）に対してSPMデータを投入
-- 各工程に1～3台のPRESS機をランダムに割り当て
INSERT INTO `spm` (`product_id`, `process_name`, `press_no`, `cycle_time`, `user`)
SELECT
    p.product_id,
    p.process_name,
    -- product_idとprocess_noの組み合わせでPRESS機を決定
    CASE ((p.product_id * 7 + p.process_no) % 12)
        WHEN 0 THEN 'PRESS-001'
        WHEN 1 THEN 'PRESS-002'
        WHEN 2 THEN 'PRESS-003'
        WHEN 3 THEN 'PRESS-004'
        WHEN 4 THEN 'PRESS-005'
        WHEN 5 THEN 'PRESS-006'
        WHEN 6 THEN 'PRESS-007'
        WHEN 7 THEN 'PRESS-008'
        WHEN 8 THEN 'PRESS-S001'
        WHEN 9 THEN 'PRESS-S002'
        WHEN 10 THEN 'PRESS-S003'
        ELSE 'PRESS-S004'
    END as press_no,
    -- cycle_time: 4～100個/分の範囲でランダム生成
    FLOOR(4 + (RAND() * 96)) as cycle_time,
    'admin' as user
FROM processes p
WHERE p.process_name LIKE 'PRESS%'
ORDER BY p.product_id, p.process_no;

-- 一部の工程に2台目のPRESS機を追加（約30%の工程）
INSERT INTO `spm` (`product_id`, `process_name`, `press_no`, `cycle_time`, `user`)
SELECT
    p.product_id,
    p.process_name,
    -- 異なるPRESS機を割り当て
    CASE ((p.product_id * 11 + p.process_no * 3) % 12)
        WHEN 0 THEN 'PRESS-002'
        WHEN 1 THEN 'PRESS-003'
        WHEN 2 THEN 'PRESS-004'
        WHEN 3 THEN 'PRESS-005'
        WHEN 4 THEN 'PRESS-006'
        WHEN 5 THEN 'PRESS-007'
        WHEN 6 THEN 'PRESS-008'
        WHEN 7 THEN 'PRESS-S001'
        WHEN 8 THEN 'PRESS-S002'
        WHEN 9 THEN 'PRESS-S003'
        WHEN 10 THEN 'PRESS-S004'
        ELSE 'PRESS-001'
    END as press_no,
    FLOOR(4 + (RAND() * 96)) as cycle_time,
    'admin' as user
FROM processes p
WHERE p.process_name LIKE 'PRESS%'
    AND (p.product_id % 3 = 0)  -- 約30%の工程
ORDER BY p.product_id, p.process_no;

-- 一部の工程に3台目のPRESS機を追加（約15%の工程）
INSERT INTO `spm` (`product_id`, `process_name`, `press_no`, `cycle_time`, `user`)
SELECT
    p.product_id,
    p.process_name,
    -- さらに異なるPRESS機を割り当て
    CASE ((p.product_id * 13 + p.process_no * 5) % 12)
        WHEN 0 THEN 'PRESS-003'
        WHEN 1 THEN 'PRESS-004'
        WHEN 2 THEN 'PRESS-005'
        WHEN 3 THEN 'PRESS-006'
        WHEN 4 THEN 'PRESS-007'
        WHEN 5 THEN 'PRESS-008'
        WHEN 6 THEN 'PRESS-S001'
        WHEN 7 THEN 'PRESS-S002'
        WHEN 8 THEN 'PRESS-S003'
        WHEN 9 THEN 'PRESS-S004'
        WHEN 10 THEN 'PRESS-001'
        ELSE 'PRESS-002'
    END as press_no,
    FLOOR(4 + (RAND() * 96)) as cycle_time,
    'admin' as user
FROM processes p
WHERE p.process_name LIKE 'PRESS%'
    AND (p.product_id % 7 = 0)  -- 約15%の工程
ORDER BY p.product_id, p.process_no;

-- ================================================
-- 結果を確認
-- ================================================

-- SPMレコード数の確認
SELECT 'Total SPM records:' as status, COUNT(*) as count FROM spm;

-- PRESS工程数の確認
SELECT 'Total PRESS processes:' as status, COUNT(*) as count
FROM processes
WHERE process_name LIKE 'PRESS%';

-- PRESS機ごとの割り当て数
SELECT 'PRESS machines assignment:' as status;
SELECT press_no, COUNT(*) as assigned_count
FROM spm
GROUP BY press_no
ORDER BY press_no;

-- cycle_timeの統計
SELECT 'Cycle time statistics (units/min):' as status;
SELECT
    MIN(cycle_time) as min_spm,
    MAX(cycle_time) as max_spm,
    ROUND(AVG(cycle_time), 2) as avg_spm,
    COUNT(*) as total_records
FROM spm;

-- サンプルデータを表示（各製品の最初のPRESS工程）
SELECT 'Sample SPM data:' as status;
SELECT
    s.product_id,
    pr.product_code,
    s.process_name,
    s.press_no,
    s.cycle_time,
    ml.machine_type
FROM spm s
JOIN products pr ON s.product_id = pr.product_id
LEFT JOIN machine_list ml ON s.press_no = ml.machine_no
ORDER BY s.product_id, s.process_name, s.press_no
LIMIT 30;

-- machine_listに存在しないpress_noをチェック（結果が0件であること）
SELECT 'Invalid press_no (should be empty):' as status;
SELECT DISTINCT s.press_no
FROM spm s
LEFT JOIN machine_list ml ON s.press_no = ml.machine_no
WHERE ml.machine_list_id IS NULL;

-- 各工程に割り当てられたPRESS機の数を確認
SELECT 'Machines per process (sample):' as status;
SELECT
    product_id,
    process_name,
    COUNT(*) as machine_count,
    GROUP_CONCAT(press_no ORDER BY press_no) as machines
FROM spm
GROUP BY product_id, process_name
ORDER BY product_id, process_name
LIMIT 20;
