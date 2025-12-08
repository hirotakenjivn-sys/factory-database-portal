-- ================================================
-- PRESS機のマスタデータ登録
-- machine_listテーブルにPRESS機を追加
-- ================================================

-- 既存のmachine_listにmachine_typeを設定（まだ設定されていない場合）
-- PRESSマシン（M-0001 ～ M-0070）
UPDATE `machine_list` SET `machine_type` = 'PRESS'
WHERE `machine_no` REGEXP '^M-00[0-6][0-9]$' OR `machine_no` = 'M-0070';

-- TAPマシン（M-0071 ～ M-0130）
UPDATE `machine_list` SET `machine_type` = 'TAP'
WHERE `machine_no` REGEXP '^M-00(7[1-9]|[89][0-9])$'
   OR `machine_no` REGEXP '^M-01[0-2][0-9]$'
   OR `machine_no` = 'M-0130';

-- BARRELマシン（M-0131 ～ M-0200）
UPDATE `machine_list` SET `machine_type` = 'BARREL'
WHERE `machine_no` REGEXP '^M-01[3-9][0-9]$'
   OR `machine_no` = 'M-0200';

-- ================================================
-- SPM工程用PRESS機の追加
-- press_no として参照されるPRESS機を登録
-- ================================================

-- 既存のPRESS機を削除（重複回避）
DELETE FROM `machine_list`
WHERE `machine_no` IN (
  'PRESS-001', 'PRESS-002', 'PRESS-003', 'PRESS-004',
  'PRESS-005', 'PRESS-006', 'PRESS-007', 'PRESS-008',
  'PRESS-S001', 'PRESS-S002', 'PRESS-S003', 'PRESS-S004'
);

-- PRESS機の登録（factory_id=1: Main Factory）
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type`, `user`) VALUES
(1, 'PRESS-001', 'PRESS', 'admin'),
(1, 'PRESS-002', 'PRESS', 'admin'),
(1, 'PRESS-003', 'PRESS', 'admin'),
(1, 'PRESS-004', 'PRESS', 'admin'),
(1, 'PRESS-005', 'PRESS', 'admin'),
(1, 'PRESS-006', 'PRESS', 'admin'),
(1, 'PRESS-007', 'PRESS', 'admin'),
(1, 'PRESS-008', 'PRESS', 'admin');

-- 小型PRESS機の登録（PRESS-S001～PRESS-S004）
INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type`, `user`) VALUES
(1, 'PRESS-S001', 'PRESS', 'admin'),
(1, 'PRESS-S002', 'PRESS', 'admin'),
(1, 'PRESS-S003', 'PRESS', 'admin'),
(1, 'PRESS-S004', 'PRESS', 'admin');

-- ================================================
-- 確認用クエリ
-- ================================================

-- machine_typeごとの集計
SELECT machine_type, COUNT(*) as count
FROM machine_list
GROUP BY machine_type
ORDER BY machine_type;

-- PRESS機の一覧
SELECT machine_list_id, factory_id, machine_no, machine_type, user
FROM machine_list
WHERE machine_type = 'PRESS'
ORDER BY machine_no;
