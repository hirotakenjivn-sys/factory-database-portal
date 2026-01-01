-- Machine List Only
-- Factory Database Portal
-- 新スキーマ: machine_type_id (外部キー)

SET NAMES utf8mb4;

-- ================================================
-- Machine List (機械リスト) - 20 records
-- ================================================
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0001', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0002', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0003', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0004', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0005', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0006', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0007', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0008', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0009', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0010', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0011', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0012', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0013', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0014', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0015', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0016', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0017', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0018', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'M-0019', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'M-0020', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
