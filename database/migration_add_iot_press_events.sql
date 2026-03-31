-- マイグレーション: iot_press_events テーブル追加
-- プレスショットイベント (Press-raspi互換)

CREATE TABLE IF NOT EXISTS `iot_press_events` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `ts_ms` BIGINT NOT NULL,
  `raspi_no` VARCHAR(50) NOT NULL DEFAULT 'unknown',
  INDEX `idx_iot_press_ts_ms` (`ts_ms`),
  INDEX `idx_iot_press_raspi_no` (`raspi_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='プレスショットイベント (Press-raspi互換)';
