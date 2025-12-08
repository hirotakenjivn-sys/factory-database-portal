-- Sample DAY Process Data
-- DAY工程のサンプルデータ
-- rough_cycletime: N日（生産期間）
-- production_limit: そのN日で生産できる数量

SET NAMES utf8mb4;

-- ========================================
-- Process Name Types（工程名マスタ）にDAY工程を追加
-- ========================================

INSERT INTO `process_name_types` (`process_name`, `day_or_spm`, `user`) VALUES
('PRESS', TRUE, 'admin'),
('PRESS 1/2', TRUE, 'admin'),
('PRESS 2/2', TRUE, 'admin'),
('PRESS 1/3', TRUE, 'admin'),
('PRESS 2/3', TRUE, 'admin'),
('PRESS 3/3', TRUE, 'admin'),
('PRESS 1/4', TRUE, 'admin'),
('PRESS 2/4', TRUE, 'admin'),
('PRESS 3/4', TRUE, 'admin'),
('PRESS 4/4', TRUE, 'admin'),
('PRESS 1/5', TRUE, 'admin'),
('PRESS 2/5', TRUE, 'admin'),
('PRESS 3/5', TRUE, 'admin'),
('PRESS 4/5', TRUE, 'admin'),
('PRESS 5/5', TRUE, 'admin'),
('TAPPING', FALSE, 'admin'),
('PLATING', FALSE, 'admin'),
('HEAT_TREATMENT', FALSE, 'admin'),
('WELDING', FALSE, 'admin'),
('ASSEMBLY', FALSE, 'admin'),
('INSPECTION', FALSE, 'admin'),
('PAINTING', FALSE, 'admin'),
('ANODIZING', FALSE, 'admin'),
('COATING', FALSE, 'admin'),
('POLISHING', FALSE, 'admin')
ON DUPLICATE KEY UPDATE
    day_or_spm = VALUES(day_or_spm),
    user = VALUES(user);

-- ========================================
-- Processes（工程）にDAY工程のサンプルを追加
-- ========================================

-- 製品1のDAY工程
-- TAPPING: 1日で2500個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (1, 5, 'TAPPING', 1, 2500, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'TAPPING',
    rough_cycletime = 1,
    production_limit = 2500;

-- PLATING: 5日で50000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (1, 6, 'PLATING', 5, 50000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'PLATING',
    rough_cycletime = 5,
    production_limit = 50000;

-- 製品2のDAY工程
-- HEAT_TREATMENT: 3日で10000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (2, 4, 'HEAT_TREATMENT', 3, 10000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'HEAT_TREATMENT',
    rough_cycletime = 3,
    production_limit = 10000;

-- ASSEMBLY: 2日で5000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (2, 5, 'ASSEMBLY', 2, 5000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'ASSEMBLY',
    rough_cycletime = 2,
    production_limit = 5000;

-- 製品3のDAY工程
-- PAINTING: 7日で30000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (3, 3, 'PAINTING', 7, 30000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'PAINTING',
    rough_cycletime = 7,
    production_limit = 30000;

-- ANODIZING: 4日で15000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (3, 4, 'ANODIZING', 4, 15000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'ANODIZING',
    rough_cycletime = 4,
    production_limit = 15000;

-- 製品4のDAY工程
-- COATING: 6日で25000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (4, 5, 'COATING', 6, 25000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'COATING',
    rough_cycletime = 6,
    production_limit = 25000;

-- TAPPING: 1日で3000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (4, 6, 'TAPPING', 1, 3000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'TAPPING',
    rough_cycletime = 1,
    production_limit = 3000;

-- 製品5のDAY工程
-- POLISHING: 2日で8000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (5, 4, 'POLISHING', 2, 8000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'POLISHING',
    rough_cycletime = 2,
    production_limit = 8000;

-- PLATING: 5日で40000個
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `user`)
VALUES (5, 5, 'PLATING', 5, 40000, 'admin')
ON DUPLICATE KEY UPDATE
    process_name = 'PLATING',
    rough_cycletime = 5,
    production_limit = 40000;

-- ========================================
-- 計算例の説明
-- ========================================
--
-- 例1: 製品1のTAPPING工程
-- - rough_cycletime = 1日
-- - production_limit = 2500個
-- - PO数量 = 5000個の場合
-- - 必要サイクル数 = CEILING(5000 / 2500) = 2
-- - 必要日数 = 2 * 1 = 2日
--
-- 例2: 製品1のPLATING工程
-- - rough_cycletime = 5日
-- - production_limit = 50000個
-- - PO数量 = 100000個の場合
-- - 必要サイクル数 = CEILING(100000 / 50000) = 2
-- - 必要日数 = 2 * 5 = 10日
--
-- 例3: 製品3のPAINTING工程
-- - rough_cycletime = 7日
-- - production_limit = 30000個
-- - PO数量 = 50000個の場合
-- - 必要サイクル数 = CEILING(50000 / 30000) = 2
-- - 必要日数 = 2 * 7 = 14日
--
