-- ================================================
-- マイグレーション: machine_listテーブルにmachine_typeカラムを追加
-- ================================================

-- machine_typeカラムを追加（PRESS、TAP、BARRELの3種類）
ALTER TABLE `machine_list`
ADD COLUMN `machine_type` ENUM('PRESS', 'TAP', 'BARREL') NULL COMMENT '機械種類' AFTER `machine_no`;

-- 既存レコードにはデフォルト値を設定（必要に応じて）
-- UPDATE `machine_list` SET `machine_type` = 'PRESS' WHERE `machine_type` IS NULL;

-- インデックスを追加（検索性能向上）
ALTER TABLE `machine_list`
ADD INDEX `idx_machine_type` (`machine_type`);
