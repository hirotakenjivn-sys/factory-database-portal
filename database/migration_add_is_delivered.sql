-- Migration: Add is_delivered column to po table and create deleted_po table
-- 既存のデータベースに対してこのマイグレーションを実行してください

USE factory_db;

-- poテーブルにis_deliveredカラムを追加（存在しない場合のみ）
ALTER TABLE `po`
ADD COLUMN IF NOT EXISTS `is_delivered` BOOLEAN DEFAULT FALSE COMMENT '配送済みフラグ' AFTER `po_quantity`,
ADD INDEX IF NOT EXISTS `idx_po_is_delivered` (`is_delivered`);

-- deleted_poテーブルを作成（存在しない場合のみ）
CREATE TABLE IF NOT EXISTS `deleted_po` (
  `deleted_po_id` INT AUTO_INCREMENT PRIMARY KEY,
  `po_id` INT NOT NULL COMMENT '元のPO ID',
  `po_number` VARCHAR(100) NOT NULL,
  `product_id` INT NOT NULL,
  `delivery_date` DATE NOT NULL,
  `date_receive_po` DATE NOT NULL,
  `po_quantity` INT NOT NULL,
  `is_delivered` BOOLEAN DEFAULT FALSE,
  `original_timestamp` DATETIME COMMENT '元の登録日時',
  `original_user` VARCHAR(100) COMMENT '元の登録ユーザー',
  `deleted_timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '削除日時',
  `deleted_by_user` VARCHAR(100) COMMENT '削除実行ユーザー',
  INDEX `idx_deleted_po_original` (`po_id`),
  INDEX `idx_deleted_po_deleted_timestamp` (`deleted_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 既存のpoレコードにis_deliveredのデフォルト値を設定
UPDATE `po` SET `is_delivered` = FALSE WHERE `is_delivered` IS NULL;
