-- ================================================
-- Machine List (機械リスト) - 30機
-- ================================================
-- Main Factory: 20機, Sub Factory: 10機
-- machine_type: PRESS, TAP, BARREL

INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type`, `user`) VALUES
-- Main Factory (factory_id = 1) - PRESS machines
(1, 'PRESS-001', 'PRESS', 'admin'),
(1, 'PRESS-002', 'PRESS', 'admin'),
(1, 'PRESS-003', 'PRESS', 'admin'),
(1, 'PRESS-004', 'PRESS', 'admin'),
(1, 'PRESS-005', 'PRESS', 'admin'),
(1, 'PRESS-006', 'PRESS', 'admin'),
(1, 'PRESS-007', 'PRESS', 'admin'),
(1, 'PRESS-008', 'PRESS', 'admin'),

-- Main Factory - TAP machines
(1, 'TAP-001', 'TAP', 'admin'),
(1, 'TAP-002', 'TAP', 'admin'),
(1, 'TAP-003', 'TAP', 'admin'),
(1, 'TAP-004', 'TAP', 'admin'),
(1, 'TAP-005', 'TAP', 'admin'),
(1, 'TAP-006', 'TAP', 'admin'),

-- Main Factory - BARREL machines
(1, 'BARREL-001', 'BARREL', 'admin'),
(1, 'BARREL-002', 'BARREL', 'admin'),
(1, 'BARREL-003', 'BARREL', 'admin'),
(1, 'BARREL-004', 'BARREL', 'admin'),
(1, 'BARREL-005', 'BARREL', 'admin'),
(1, 'BARREL-006', 'BARREL', 'admin'),

-- Sub Factory (factory_id = 2) - PRESS machines
(2, 'PRESS-S001', 'PRESS', 'admin'),
(2, 'PRESS-S002', 'PRESS', 'admin'),
(2, 'PRESS-S003', 'PRESS', 'admin'),
(2, 'PRESS-S004', 'PRESS', 'admin'),

-- Sub Factory - TAP machines
(2, 'TAP-S001', 'TAP', 'admin'),
(2, 'TAP-S002', 'TAP', 'admin'),
(2, 'TAP-S003', 'TAP', 'admin'),

-- Sub Factory - BARREL machines
(2, 'BARREL-S001', 'BARREL', 'admin'),
(2, 'BARREL-S002', 'BARREL', 'admin'),
(2, 'BARREL-S003', 'BARREL', 'admin');

-- 合計30機
-- Main Factory: PRESS 8機, TAP 6機, BARREL 6機 = 20機
-- Sub Factory: PRESS 4機, TAP 3機, BARREL 3機 = 10機
