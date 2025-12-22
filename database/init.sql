-- Factory Database Portal
-- Database Initialization Script
-- MySQL 8.0.32

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Set timezone to Vietnam (UTC+7)
SET time_zone = '+07:00';

-- ================================================
-- 1. customers (顧客マスタ)
-- ================================================
DROP TABLE IF EXISTS `customers`;
CREATE TABLE `customers` (
  `customer_id` INT AUTO_INCREMENT PRIMARY KEY,
  `customer_name` VARCHAR(255) NOT NULL,
  `is_active` BOOLEAN DEFAULT TRUE,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  INDEX `idx_customer_name` (`customer_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 2. products (製品マスタ)
-- ================================================
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `product_id` INT AUTO_INCREMENT PRIMARY KEY,
  `product_code` VARCHAR(100) NOT NULL,
  `customer_id` INT NOT NULL,
  `is_active` BOOLEAN DEFAULT TRUE,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`customer_id`) REFERENCES `customers`(`customer_id`),
  INDEX `idx_products_customer` (`customer_id`),
  INDEX `idx_products_code` (`product_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 3. process_name_types (工程名マスタ)
-- ================================================
DROP TABLE IF EXISTS `process_name_types`;
CREATE TABLE `process_name_types` (
  `process_name_id` INT AUTO_INCREMENT PRIMARY KEY,
  `process_name` VARCHAR(100) NOT NULL,
  `day_or_spm` BOOLEAN COMMENT 'TRUE: SPM, FALSE: DAY',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 4. processes (工程)
-- ================================================
DROP TABLE IF EXISTS `processes`;
CREATE TABLE `processes` (
  `process_id` INT AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL,
  `process_no` INT NOT NULL,
  `process_name_id` INT NOT NULL,
  `rough_cycletime` DECIMAL(10, 2),
  `setup_time` DECIMAL(10, 2) COMMENT '段取時間（分）',
  `production_limit` INT COMMENT '生産可能限界',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
  FOREIGN KEY (`process_name_id`) REFERENCES `process_name_types`(`process_name_id`),
  INDEX `idx_processes_product` (`product_id`),
  UNIQUE KEY `uk_product_process` (`product_id`, `process_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 5. factories (工場マスタ)
-- ================================================
DROP TABLE IF EXISTS `factories`;
CREATE TABLE `factories` (
  `factory_id` INT AUTO_INCREMENT PRIMARY KEY,
  `factory_name` VARCHAR(255) NOT NULL,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 6. machine_list (機械リスト)
-- ================================================
DROP TABLE IF EXISTS `machine_list`;
CREATE TABLE `machine_list` (
  `machine_list_id` INT AUTO_INCREMENT PRIMARY KEY,
  `factory_id` INT NOT NULL,
  `machine_no` VARCHAR(100) NOT NULL,
  `machine_type` ENUM('PRESS', 'TAP', 'BARREL') NULL COMMENT '機械種類',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`factory_id`) REFERENCES `factories`(`factory_id`),
  INDEX `idx_machine_type` (`machine_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 7. maintain_machines (機械メンテナンス)
-- ================================================
DROP TABLE IF EXISTS `maintain_machines`;
CREATE TABLE `maintain_machines` (
  `maintain_machine_id` INT AUTO_INCREMENT PRIMARY KEY,
  `machine_list_id` INT NOT NULL,
  `date` DATE NOT NULL,
  `time_from` TIME,
  `time_to` TIME,
  `note` TEXT,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`machine_list_id`) REFERENCES `machine_list`(`machine_list_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 8. broken_mold (金型故障)
-- ================================================
DROP TABLE IF EXISTS `broken_mold_history`;
DROP TABLE IF EXISTS `broken_mold_mold`;
DROP TABLE IF EXISTS `broken_mold_stamp`;
DROP TABLE IF EXISTS `broken_mold`;

CREATE TABLE `broken_mold_stamp` (
  `broken_mold_stamp_id` INT AUTO_INCREMENT PRIMARY KEY,
  `process_id` INT NOT NULL,
  `reason` TEXT,
  `date_broken_time` DATETIME,
  `date_hope_repaired` DATE,
  `note` TEXT,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`process_id`) REFERENCES `processes`(`process_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `broken_mold_mold` (
  `broken_mold_mold_id` INT AUTO_INCREMENT PRIMARY KEY,
  `broken_mold_stamp_id` INT NOT NULL,
  `date_schedule_repaired` DATE,
  `note` TEXT,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`broken_mold_stamp_id`) REFERENCES `broken_mold_stamp`(`broken_mold_stamp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `broken_mold_history` (
  `broken_mold_history_id` INT AUTO_INCREMENT PRIMARY KEY,
  `broken_mold_mold_id` INT NOT NULL,
  `way_repair` TEXT,
  `repairman` VARCHAR(100),
  `cause` TEXT,
  `actual_repaired_date` DATE,
  `quantity` INT,
  `note` TEXT,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`broken_mold_mold_id`) REFERENCES `broken_mold_mold`(`broken_mold_mold_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 9. using_machine (使用機械)
-- ================================================
DROP TABLE IF EXISTS `using_machine`;
CREATE TABLE `using_machine` (
  `using_machine_id` INT AUTO_INCREMENT PRIMARY KEY,
  `process_id` INT NOT NULL,
  `machine` VARCHAR(100),
  `priority` INT,
  `exact_cycletime` DECIMAL(10, 2),
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`process_id`) REFERENCES `processes`(`process_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 10. working_hours (稼働時間)
-- ================================================
DROP TABLE IF EXISTS `working_hours`;
CREATE TABLE `working_hours` (
  `working_hours_id` INT AUTO_INCREMENT PRIMARY KEY,
  `factory_id` INT NOT NULL,
  `hours` DECIMAL(5, 2) NOT NULL,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`factory_id`) REFERENCES `factories`(`factory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 11. holiday_types (休日種別マスタ)
-- ================================================
DROP TABLE IF EXISTS `holiday_types`;
CREATE TABLE `holiday_types` (
  `holiday_type_id` INT AUTO_INCREMENT PRIMARY KEY,
  `date_type` VARCHAR(50) NOT NULL COMMENT '例: 祝日, 会社休日, 土日'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 12. calendar (カレンダー)
-- ================================================
DROP TABLE IF EXISTS `calendar`;
CREATE TABLE `calendar` (
  `calendar_id` INT AUTO_INCREMENT PRIMARY KEY,
  `date_holiday` DATE NOT NULL UNIQUE,
  `holiday_type_id` INT NOT NULL,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`holiday_type_id`) REFERENCES `holiday_types`(`holiday_type_id`),
  INDEX `idx_calendar_date` (`date_holiday`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 13. material_rates (材料レート)
-- ================================================
DROP TABLE IF EXISTS `material_rates`;
CREATE TABLE `material_rates` (
  `material_rate_id` INT AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL,
  `thickness` DECIMAL(10, 2),
  `width` DECIMAL(10, 2),
  `pitch` DECIMAL(10, 2),
  `h` DECIMAL(10, 2),
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 13a. spm (SPM設定)
-- ================================================
DROP TABLE IF EXISTS `spm`;
CREATE TABLE `spm` (
  `spm_id` INT AUTO_INCREMENT PRIMARY KEY,
  `process_id` INT NOT NULL,
  `machine_list_id` INT NOT NULL,
  `cycle_time` DECIMAL(10, 2) NOT NULL,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`process_id`) REFERENCES `processes`(`process_id`),
  FOREIGN KEY (`machine_list_id`) REFERENCES `machine_list`(`machine_list_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 14. lot (ロット)
-- ================================================
DROP TABLE IF EXISTS `lot`;
CREATE TABLE `lot` (
  `lot_id` INT AUTO_INCREMENT PRIMARY KEY,
  `lot_number` VARCHAR(100) NOT NULL UNIQUE,
  `product_id` INT NOT NULL,
  `date_created` DATE NOT NULL,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
  INDEX `idx_lot_number` (`lot_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 15. po (発注)
-- ================================================
DROP TABLE IF EXISTS `po`;
CREATE TABLE `po` (
  `po_id` INT AUTO_INCREMENT PRIMARY KEY,
  `po_number` VARCHAR(100) NOT NULL,
  `product_id` INT NOT NULL,
  `delivery_date` DATE NOT NULL,
  `date_receive_po` DATE NOT NULL,
  `po_quantity` INT NOT NULL,
  `is_delivered` BOOLEAN DEFAULT FALSE COMMENT '配送済みフラグ',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
  INDEX `idx_po_product` (`product_id`),
  INDEX `idx_po_delivery` (`delivery_date`),
  INDEX `idx_po_is_delivered` (`is_delivered`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 15-1. deleted_po (削除されたPO)
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
  `is_delivered` BOOLEAN DEFAULT FALSE,
  `original_timestamp` DATETIME COMMENT '元の登録日時',
  `original_user` VARCHAR(100) COMMENT '元の登録ユーザー',
  `deleted_timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '削除日時',
  `deleted_by_user` VARCHAR(100) COMMENT '削除実行ユーザー',
  INDEX `idx_deleted_po_original` (`po_id`),
  INDEX `idx_deleted_po_deleted_timestamp` (`deleted_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 16. finished_products (完成品)
-- ================================================


-- ================================================
-- 17. employees (従業員マスタ)
-- ================================================
DROP TABLE IF EXISTS `employees`;
CREATE TABLE `employees` (
  `employee_id` INT AUTO_INCREMENT PRIMARY KEY,
  `employee_no` VARCHAR(50) NOT NULL UNIQUE,
  `name` VARCHAR(255) NOT NULL,
  `is_active` BOOLEAN DEFAULT TRUE,
  `password_hash` VARCHAR(255),
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 18. suppliers (サプライヤーマスタ)
-- ================================================
DROP TABLE IF EXISTS `suppliers`;
CREATE TABLE `suppliers` (
  `supplier_id` INT AUTO_INCREMENT PRIMARY KEY,
  `supplier_name` VARCHAR(255) NOT NULL,
  `supplier_business` VARCHAR(255),
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 19. stamp_traces (内製トレース)
-- ================================================
DROP TABLE IF EXISTS `stamp_traces`;
CREATE TABLE `stamp_traces` (
  `stamp_trace_id` INT AUTO_INCREMENT PRIMARY KEY,
  `lot_id` INT NOT NULL,
  `process_id` INT NOT NULL,
  `po_id` INT NULL COMMENT 'POに紐づかない作業の場合はNULL',
  `employee_id` INT NOT NULL,
  `ok_quantity` INT NOT NULL,
  `ng_quantity` INT NOT NULL,
  `result` VARCHAR(50) COMMENT 'pass, fail, rework',
  `date` DATE NOT NULL,
  `note` TEXT,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`lot_id`) REFERENCES `lot`(`lot_id`),
  FOREIGN KEY (`process_id`) REFERENCES `processes`(`process_id`),
  FOREIGN KEY (`po_id`) REFERENCES `po`(`po_id`),
  FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`),
  INDEX `idx_stamp_traces_date` (`date`),
  INDEX `idx_stamp_traces_lot` (`lot_id`),
  INDEX `idx_stamp_traces_process` (`process_id`),
  INDEX `idx_stamp_traces_po` (`po_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 20. outsource_traces (外注トレース)
-- ================================================
DROP TABLE IF EXISTS `outsource_traces`;
CREATE TABLE `outsource_traces` (
  `outsource_trace_id` INT AUTO_INCREMENT PRIMARY KEY,
  `lot_id` INT NOT NULL,
  `process_id` INT NOT NULL,
  `po_id` INT NULL COMMENT 'POに紐づかない作業の場合はNULL',
  `supplier_id` INT NOT NULL,
  `ok_quantity` INT NOT NULL,
  `ng_quantity` INT NOT NULL,
  `date` DATE NOT NULL,
  `note` TEXT,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100),
  FOREIGN KEY (`lot_id`) REFERENCES `lot`(`lot_id`),
  FOREIGN KEY (`process_id`) REFERENCES `processes`(`process_id`),
  FOREIGN KEY (`po_id`) REFERENCES `po`(`po_id`),
  FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`supplier_id`),
  INDEX `idx_outsource_traces_date` (`date`),
  INDEX `idx_outsource_traces_lot` (`lot_id`),
  INDEX `idx_outsource_traces_process` (`process_id`),
  INDEX `idx_outsource_traces_po` (`po_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- 21. production_schedule (生産計画スケジュール)
-- ================================================
DROP TABLE IF EXISTS `production_schedule`;
CREATE TABLE `production_schedule` (
  `schedule_id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'スケジュールID（主キー）',
  `po_id` INT NOT NULL COMMENT 'PO ID',
  `process_id` INT NOT NULL COMMENT '工程ID',
  `machine_list_id` INT NULL COMMENT 'マシンID（PRESS機の場合のみ設定）',
  `planned_start_datetime` DATETIME NOT NULL COMMENT '開始予定日時',
  `planned_end_datetime` DATETIME NOT NULL COMMENT '終了予定日時',
  `po_quantity` INT NOT NULL COMMENT 'PO数量',
  `setup_time` DECIMAL(10,2) DEFAULT 0 COMMENT '段取時間（分）',
  `processing_time` DECIMAL(10,2) DEFAULT 0 COMMENT '加工時間（分）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  `user` VARCHAR(100) COMMENT '作成ユーザー',
  FOREIGN KEY (`po_id`) REFERENCES `po`(`po_id`) ON DELETE CASCADE,
  FOREIGN KEY (`process_id`) REFERENCES `processes`(`process_id`) ON DELETE CASCADE,
  FOREIGN KEY (`machine_list_id`) REFERENCES `machine_list`(`machine_list_id`) ON DELETE SET NULL,
  INDEX `idx_po_id` (`po_id`),
  INDEX `idx_process_id` (`process_id`),
  INDEX `idx_machine_list_id` (`machine_list_id`),
  INDEX `idx_planned_start` (`planned_start_datetime`),
  INDEX `idx_planned_end` (`planned_end_datetime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='生産計画スケジュール';

-- ================================================
-- 22. iot_button_events (ラズパイボタン押下ログ)
-- ================================================
DROP TABLE IF EXISTS `iot_button_events`;
CREATE TABLE `iot_button_events` (
  `event_id` INT AUTO_INCREMENT PRIMARY KEY,
  `button_name` VARCHAR(100) NOT NULL,
  `raspi_no` VARCHAR(100) NULL,
  `pressed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `note` TEXT,
  `user` VARCHAR(100) DEFAULT 'raspi'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

-- ================================================
-- 初期データ投入（デフォルトユーザー等）
-- ================================================

-- 休日種別
INSERT INTO `holiday_types` (`holiday_type_id`, `date_type`) VALUES
(1, '祝日'),
(2, '会社休日'),
(3, '土日');

-- デフォルト工場
INSERT INTO `factories` (`factory_id`, `factory_name`, `user`) VALUES
(1, 'Main Factory', 'system'),
(2, 'Sub Factory', 'system');
