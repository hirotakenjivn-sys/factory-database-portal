-- ================================================
-- 重複データのクリーンアップ
-- すべてのマスタデータを削除して再投入準備
-- ================================================

SET NAMES utf8mb4;
USE factory_db;

-- 外部キー制約を一時的に無効化
SET FOREIGN_KEY_CHECKS = 0;

-- ========== 全データ削除 ==========

-- machine_list を削除
DELETE FROM machine_list;
ALTER TABLE machine_list AUTO_INCREMENT = 1;

-- process_name_types を削除
DELETE FROM process_name_types;
ALTER TABLE process_name_types AUTO_INCREMENT = 1;

-- products を削除（processesなど依存テーブルも削除される可能性あり）
DELETE FROM products;
ALTER TABLE products AUTO_INCREMENT = 1;

-- employees を削除
DELETE FROM employees;
ALTER TABLE employees AUTO_INCREMENT = 1;

-- customers を削除
DELETE FROM customers;
ALTER TABLE customers AUTO_INCREMENT = 1;

-- 外部キー制約を再有効化
SET FOREIGN_KEY_CHECKS = 1;

-- ========== 確認 ==========
SELECT 'customers' as tbl, COUNT(*) as cnt FROM customers
UNION ALL SELECT 'employees', COUNT(*) FROM employees
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'process_name_types', COUNT(*) FROM process_name_types
UNION ALL SELECT 'machine_list', COUNT(*) FROM machine_list;

SELECT 'クリーンアップ完了' as status;
