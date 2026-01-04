-- ================================================
-- 重複データのクリーンアップ
-- シードデータ関連テーブルを全削除して再投入準備
-- ================================================

SET NAMES utf8mb4;
USE factory_db;

-- 外部キー制約を一時的に無効化
SET FOREIGN_KEY_CHECKS = 0;

-- ========== 依存テーブルを先に削除 ==========

-- production_schedule を削除
DELETE FROM production_schedule;
ALTER TABLE production_schedule AUTO_INCREMENT = 1;

-- stamp_traces を削除
DELETE FROM stamp_traces;
ALTER TABLE stamp_traces AUTO_INCREMENT = 1;

-- outsource_traces を削除
DELETE FROM outsource_traces;
ALTER TABLE outsource_traces AUTO_INCREMENT = 1;

-- finished_products を削除
DELETE FROM finished_products;
ALTER TABLE finished_products AUTO_INCREMENT = 1;

-- lot を削除
DELETE FROM lot;
ALTER TABLE lot AUTO_INCREMENT = 1;

-- deleted_po を削除
DELETE FROM deleted_po;
ALTER TABLE deleted_po AUTO_INCREMENT = 1;

-- po を削除
DELETE FROM po;
ALTER TABLE po AUTO_INCREMENT = 1;

-- processes を削除
DELETE FROM processes;
ALTER TABLE processes AUTO_INCREMENT = 1;

-- cycletimes を削除
DELETE FROM cycletimes;
ALTER TABLE cycletimes AUTO_INCREMENT = 1;

-- ========== マスタテーブルを削除 ==========

-- machine_list を削除
DELETE FROM machine_list;
ALTER TABLE machine_list AUTO_INCREMENT = 1;

-- process_name_types を削除
DELETE FROM process_name_types;
ALTER TABLE process_name_types AUTO_INCREMENT = 1;

-- products を削除
DELETE FROM products;
ALTER TABLE products AUTO_INCREMENT = 1;

-- employees を削除
DELETE FROM employees;
ALTER TABLE employees AUTO_INCREMENT = 1;

-- customers を削除
DELETE FROM customers;
ALTER TABLE customers AUTO_INCREMENT = 1;

-- suppliers を削除
DELETE FROM suppliers;
ALTER TABLE suppliers AUTO_INCREMENT = 1;

-- 外部キー制約を再有効化
SET FOREIGN_KEY_CHECKS = 1;

-- ========== 確認 ==========
SELECT 'customers' as tbl, COUNT(*) as cnt FROM customers
UNION ALL SELECT 'employees', COUNT(*) FROM employees
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'processes', COUNT(*) FROM processes
UNION ALL SELECT 'process_name_types', COUNT(*) FROM process_name_types
UNION ALL SELECT 'machine_list', COUNT(*) FROM machine_list
UNION ALL SELECT 'po', COUNT(*) FROM po
UNION ALL SELECT 'lot', COUNT(*) FROM lot
UNION ALL SELECT 'finished_products', COUNT(*) FROM finished_products
UNION ALL SELECT 'cycletimes', COUNT(*) FROM cycletimes
UNION ALL SELECT 'production_schedule', COUNT(*) FROM production_schedule
UNION ALL SELECT 'stamp_traces', COUNT(*) FROM stamp_traces
UNION ALL SELECT 'outsource_traces', COUNT(*) FROM outsource_traces
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers;

SELECT 'クリーンアップ完了' as status;
