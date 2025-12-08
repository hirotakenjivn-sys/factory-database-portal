-- Update processes for products 1-10 with correct SPM/DAY fields
-- SPM工程（PRESS）：rough_cycletime（秒/個）と setup_time（分）
-- DAY工程（その他）：rough_cycletime（日数）と production_limit（個数）

SET NAMES utf8mb4;

-- 製品1-10の既存processesを削除
DELETE FROM `processes` WHERE `product_id` IN (1,2,3,4,5,6,7,8,9,10);

-- 新しいprocessesデータを挿入
INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `setup_time`, `user`) VALUES
-- 製品1: PRESS工程(SPM) + DAY工程の組み合わせ
(1, 1, 'PRESS 1/4', 120.5, NULL, 45.0, 'admin'),
(1, 2, 'PRESS 2/4', 135.2, NULL, 50.5, 'admin'),
(1, 3, 'TAPPING', 2.0, 5000, NULL, 'admin'),
(1, 4, 'INSPECTION', 1.0, 10000, NULL, 'admin'),
-- 製品2: DAY工程のみ
(2, 1, 'WELDING', 3.5, 8000, NULL, 'admin'),
(2, 2, 'ASSEMBLY', 2.0, 6000, NULL, 'admin'),
(2, 3, 'COATING', 5.0, 20000, NULL, 'admin'),
-- 製品3: PRESS工程(SPM)中心
(3, 1, 'PRESS 1/2', 98.75, NULL, 30.0, 'admin'),
(3, 2, 'PRESS 2/2', 110.3, NULL, 35.0, 'admin'),
-- 製品4: 混合
(4, 1, 'PLATING', 4.0, 15000, NULL, 'admin'),
(4, 2, 'INSPECTION', 1.5, 12000, NULL, 'admin'),
(4, 3, 'PRESS 3/3', 145.8, NULL, 55.0, 'admin'),
-- 製品5: DAY工程のみ
(5, 1, 'HEAT_TREATMENT', 7.0, 25000, NULL, 'admin'),
(5, 2, 'POLISHING', 3.0, 10000, NULL, 'admin'),
(5, 3, 'ANODIZING', 4.5, 18000, NULL, 'admin'),
-- 製品6～10: 追加の多様なサンプル
(6, 1, 'PAINTING', 2.5, 8000, NULL, 'admin'),
(6, 2, 'WELDING', 3.0, 7000, NULL, 'admin'),
(6, 3, 'ASSEMBLY', 1.5, 5000, NULL, 'admin'),
(7, 1, 'PRESS 1/3', 88.5, NULL, 28.0, 'admin'),
(7, 2, 'PRESS 2/3', 92.3, NULL, 30.0, 'admin'),
(7, 3, 'PRESS 3/3', 95.7, NULL, 32.0, 'admin'),
(8, 1, 'TAPPING', 1.5, 4000, NULL, 'admin'),
(8, 2, 'COATING', 6.0, 22000, NULL, 'admin'),
(9, 1, 'PAINTING', 3.5, 12000, NULL, 'admin'),
(9, 2, 'WELDING', 2.5, 7500, NULL, 'admin'),
(10, 1, 'ASSEMBLY', 2.0, 6500, NULL, 'admin'),
(10, 2, 'INSPECTION', 1.0, 15000, NULL, 'admin'),
(10, 3, 'PLATING', 5.5, 20000, NULL, 'admin');
