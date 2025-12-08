-- Migration: Add admin employee record
-- This script adds an employee record for the 'admin' user to enable trace registration

SET NAMES utf8mb4;

-- ================================================
-- Add admin employee if not exists
-- ================================================

-- Check if admin employee already exists, if not, insert it
INSERT INTO `employees` (`employee_no`, `name`, `is_active`, `user`, `timestamp`)
SELECT 'admin', 'admin', TRUE, 'system', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM `employees`
    WHERE `employee_no` = 'admin' OR `name` = 'admin'
);

-- Verify the insertion
SELECT
    employee_id,
    employee_no,
    name,
    is_active,
    timestamp
FROM `employees`
WHERE employee_no = 'admin' OR name = 'admin';

-- Migration complete!
-- The admin user can now register traces successfully.
