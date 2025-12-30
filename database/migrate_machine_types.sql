USE factory_db;

-- 1. Create machine_types table
CREATE TABLE IF NOT EXISTS `machine_types` (
  `machine_type_id` INT AUTO_INCREMENT PRIMARY KEY,
  `machine_type_name` VARCHAR(50) NOT NULL UNIQUE,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Insert initial values
INSERT IGNORE INTO `machine_types` (`machine_type_name`, `user`) VALUES ('PRESS', 'admin');
INSERT IGNORE INTO `machine_types` (`machine_type_name`, `user`) VALUES ('TAP', 'admin');
INSERT IGNORE INTO `machine_types` (`machine_type_name`, `user`) VALUES ('BARREL', 'admin');

-- 3. Add machine_type_id column to machine_list
-- Check if column exists first (MySQL 8.0 doesn't have IF NOT EXISTS for ADD COLUMN in simple syntax, so we just add it. If it fails, it might exist)
-- We will assume it doesn't exist or handle it gracefully.
ALTER TABLE `machine_list` ADD COLUMN `machine_type_id` INT;

-- 4. Migrate data
UPDATE `machine_list` ml
JOIN `machine_types` mt ON ml.machine_type = mt.machine_type_name
SET ml.machine_type_id = mt.machine_type_id;

-- 5. Add Foreign Key
ALTER TABLE `machine_list` ADD CONSTRAINT `fk_machine_list_type` FOREIGN KEY (`machine_type_id`) REFERENCES `machine_types`(`machine_type_id`);

-- 6. Drop old column (Optional: You might want to keep it for a bit, but the plan said drop)
-- We will drop it to complete the refactor.
ALTER TABLE `machine_list` DROP COLUMN `machine_type`;
