-- ================================================
-- Machine List (機械リスト) - 30機
-- ================================================
-- Main Factory: 20機, Sub Factory: 10機
-- 新スキーマ: machine_type_id (外部キー)

SET NAMES utf8mb4;

-- Main Factory (factory_id = 1) - PRESS machines
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

-- Main Factory - TAP machines
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'TAP-001', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'TAP-002', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'TAP-003', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'TAP-004', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'TAP-005', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'TAP-006', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';

-- Main Factory - BARREL machines
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'BARREL-001', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'BARREL-002', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'BARREL-003', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'BARREL-004', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'BARREL-005', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 1, 'BARREL-006', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';

-- Sub Factory (factory_id = 2) - PRESS machines
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'PRESS-S001', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'PRESS-S002', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'PRESS-S003', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'PRESS-S004', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';

-- Sub Factory - TAP machines
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'TAP-S001', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'TAP-S002', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'TAP-S003', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'TAP';

-- Sub Factory - BARREL machines
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'BARREL-S001', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'BARREL-S002', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT 2, 'BARREL-S003', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'BARREL';

-- 合計30機
-- Main Factory: PRESS 8機, TAP 6機, BARREL 6機 = 20機
-- Sub Factory: PRESS 4機, TAP 3機, BARREL 3機 = 10機
