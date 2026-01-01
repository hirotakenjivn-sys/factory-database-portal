-- ================================================
-- PRESS機のマスタデータ登録
-- machine_listテーブルにPRESS機を追加
-- 新スキーマ: machine_type_id (外部キー)
-- ================================================

SET NAMES utf8mb4;

-- 既存のPRESS機を削除（重複回避）
DELETE FROM `machine_list`
WHERE `machine_no` IN (
  'PRESS-001', 'PRESS-002', 'PRESS-003', 'PRESS-004',
  'PRESS-005', 'PRESS-006', 'PRESS-007', 'PRESS-008',
  'PRESS-S001', 'PRESS-S002', 'PRESS-S003', 'PRESS-S004'
);

-- PRESS機の登録（factory_id=1: Main Factory）
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-001', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-002', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-003', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-004', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-005', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-006', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-007', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-008', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';

-- 小型PRESS機の登録
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-S001', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-S002', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-S003', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'PRESS-S004', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';

-- 確認用クエリ
SELECT mt.machine_type_name, COUNT(*) as count
FROM machine_list ml
JOIN machine_types mt ON ml.machine_type_id = mt.machine_type_id
GROUP BY mt.machine_type_name;
