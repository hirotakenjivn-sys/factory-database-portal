-- Migration: Add is_delivered column to PO table and create DeletedPO table
-- Date: 2025-11-10
-- Description: PO配送管理機能の追加と削除PO管理機能の追加

SET NAMES utf8mb4;

-- ================================================
-- 1. POテーブルにis_deliveredカラムを追加
-- ================================================
ALTER TABLE `po`
ADD COLUMN `is_delivered` BOOLEAN NOT NULL DEFAULT FALSE AFTER `po_quantity`,
ADD INDEX `idx_po_delivered` (`is_delivered`);

-- 既存データはすべて未配送として設定
UPDATE `po` SET `is_delivered` = FALSE WHERE `is_delivered` IS NULL;

-- ================================================
-- 2. 削除されたPOテーブルの作成
-- ================================================
DROP TABLE IF EXISTS `deleted_po`;
CREATE TABLE `deleted_po` (
  `deleted_po_id` INT AUTO_INCREMENT PRIMARY KEY,
  `po_id` INT NOT NULL COMMENT '元のPO ID',
  `po_number` VARCHAR(100) NOT NULL,
  `product_id` INT NOT NULL,
  `delivery_date` DATE NOT NULL,
  `date_receive_po` DATE NOT NULL,
  `po_quantity` INT NOT NULL,
  `is_delivered` BOOLEAN NOT NULL,
  `original_timestamp` DATETIME NOT NULL COMMENT '元のPOのタイムスタンプ',
  `original_user` VARCHAR(100) COMMENT '元のPOの登録/更新ユーザー',
  `deleted_timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '削除日時',
  `deleted_by_user` VARCHAR(100) NOT NULL COMMENT '削除したユーザー',
  INDEX `idx_deleted_po_id` (`po_id`),
  INDEX `idx_deleted_po_timestamp` (`deleted_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='削除されたPOの履歴テーブル';

-- ================================================
-- Migration完了
-- ================================================
