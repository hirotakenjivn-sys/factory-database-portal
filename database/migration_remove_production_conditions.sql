-- Migration: Remove production_conditions table and simplify trace tables
-- This script migrates data from production_conditions into stamp_traces and outsource_traces directly

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ================================================
-- Step 1: Add new columns to stamp_traces
-- ================================================
ALTER TABLE `stamp_traces`
  ADD COLUMN `lot_id` INT NULL AFTER `production_condition_id`,
  ADD COLUMN `process_id` INT NULL AFTER `lot_id`,
  ADD COLUMN `po_id` INT NULL AFTER `process_id`;

-- ================================================
-- Step 2: Add new columns to outsource_traces
-- ================================================
ALTER TABLE `outsource_traces`
  ADD COLUMN `lot_id` INT NULL AFTER `production_condition_id`,
  ADD COLUMN `process_id` INT NULL AFTER `lot_id`,
  ADD COLUMN `po_id` INT NULL AFTER `process_id`;

-- ================================================
-- Step 3: Migrate data from production_conditions to stamp_traces
-- ================================================
UPDATE `stamp_traces` st
INNER JOIN `production_conditions` pc ON st.production_condition_id = pc.production_condition_id
SET
  st.lot_id = pc.lot_id,
  st.process_id = pc.process_id,
  st.po_id = pc.po_id;

-- ================================================
-- Step 4: Migrate data from production_conditions to outsource_traces
-- ================================================
UPDATE `outsource_traces` ot
INNER JOIN `production_conditions` pc ON ot.production_condition_id = pc.production_condition_id
SET
  ot.lot_id = pc.lot_id,
  ot.process_id = pc.process_id,
  ot.po_id = pc.po_id;

-- ================================================
-- Step 5: Verify data migration (optional check)
-- ================================================
-- Uncomment to verify all records have been migrated
-- SELECT COUNT(*) FROM stamp_traces WHERE lot_id IS NULL OR process_id IS NULL;
-- SELECT COUNT(*) FROM outsource_traces WHERE lot_id IS NULL OR process_id IS NULL;

-- ================================================
-- Step 6: Drop foreign key constraints on production_condition_id
-- ================================================
ALTER TABLE `stamp_traces`
  DROP FOREIGN KEY `stamp_traces_ibfk_1`;

ALTER TABLE `outsource_traces`
  DROP FOREIGN KEY `outsource_traces_ibfk_1`;

-- ================================================
-- Step 7: Drop production_condition_id columns
-- ================================================
ALTER TABLE `stamp_traces`
  DROP COLUMN `production_condition_id`;

ALTER TABLE `outsource_traces`
  DROP COLUMN `production_condition_id`;

-- ================================================
-- Step 8: Make new columns NOT NULL (now that data is migrated)
-- ================================================
ALTER TABLE `stamp_traces`
  MODIFY COLUMN `lot_id` INT NOT NULL,
  MODIFY COLUMN `process_id` INT NOT NULL;

ALTER TABLE `outsource_traces`
  MODIFY COLUMN `lot_id` INT NOT NULL,
  MODIFY COLUMN `process_id` INT NOT NULL;

-- ================================================
-- Step 9: Add foreign key constraints for new columns
-- ================================================
ALTER TABLE `stamp_traces`
  ADD CONSTRAINT `fk_stamp_traces_lot` FOREIGN KEY (`lot_id`) REFERENCES `lot`(`lot_id`),
  ADD CONSTRAINT `fk_stamp_traces_process` FOREIGN KEY (`process_id`) REFERENCES `processes`(`process_id`),
  ADD CONSTRAINT `fk_stamp_traces_po` FOREIGN KEY (`po_id`) REFERENCES `po`(`po_id`);

ALTER TABLE `outsource_traces`
  ADD CONSTRAINT `fk_outsource_traces_lot` FOREIGN KEY (`lot_id`) REFERENCES `lot`(`lot_id`),
  ADD CONSTRAINT `fk_outsource_traces_process` FOREIGN KEY (`process_id`) REFERENCES `processes`(`process_id`),
  ADD CONSTRAINT `fk_outsource_traces_po` FOREIGN KEY (`po_id`) REFERENCES `po`(`po_id`);

-- ================================================
-- Step 10: Add indexes for better query performance
-- ================================================
ALTER TABLE `stamp_traces`
  ADD INDEX `idx_stamp_traces_lot` (`lot_id`),
  ADD INDEX `idx_stamp_traces_process` (`process_id`),
  ADD INDEX `idx_stamp_traces_po` (`po_id`);

ALTER TABLE `outsource_traces`
  ADD INDEX `idx_outsource_traces_lot` (`lot_id`),
  ADD INDEX `idx_outsource_traces_process` (`process_id`),
  ADD INDEX `idx_outsource_traces_po` (`po_id`);

-- ================================================
-- Step 11: Drop production_conditions table
-- ================================================
DROP TABLE IF EXISTS `production_conditions`;

SET FOREIGN_KEY_CHECKS = 1;

-- Migration complete!
-- The database structure is now simplified with trace tables directly referencing lot, process, and po.
