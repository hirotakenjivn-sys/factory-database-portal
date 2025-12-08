-- ================================================
-- Update machine_list to add machine_type
-- ================================================

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

-- 確認用クエリ
SELECT machine_type, COUNT(*) as count
FROM machine_list
GROUP BY machine_type;
