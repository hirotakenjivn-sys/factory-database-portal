-- ================================================
-- spmテーブルの構造変更
-- process_no → process_name (VARCHAR)
-- press_no → VARCHAR (既に変更済みの場合はスキップ)
-- ================================================

-- 既存データを削除
DELETE FROM spm;

-- process_noをprocess_nameに変更（カラム名と型を変更）
ALTER TABLE `spm`
CHANGE COLUMN `process_no` `process_name` VARCHAR(100) NOT NULL COMMENT '工程名（process_name_typesのprocess_nameを参照）';

-- press_noカラムの型を確認して変更（INTの場合のみ）
ALTER TABLE `spm`
MODIFY COLUMN `press_no` VARCHAR(100) NOT NULL COMMENT '機械番号（machine_listのmachine_noを参照）';

-- インデックスを追加（既存の場合はエラーになるが無視）
-- idx_spm_press_noが既に存在する場合はスキップ
ALTER TABLE `spm`
ADD INDEX `idx_spm_process_name` (`process_name`);

-- 確認
DESCRIBE spm;

SELECT 'spmテーブルの構造変更が完了しました' AS status;
