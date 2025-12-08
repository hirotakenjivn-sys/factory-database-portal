-- マイグレーション: processesテーブルに段取時間と生産可能限界を追加
-- 実行日: 2025-01-XX
-- 説明: SPM/DAY判定用のフィールドを追加

-- 段取時間（SPMの場合に使用）
ALTER TABLE `processes`
ADD COLUMN `setup_time` DECIMAL(10, 2) COMMENT '段取時間（分）' AFTER `rough_cycletime`;

-- 生産可能限界（DAYの場合に使用）
ALTER TABLE `processes`
ADD COLUMN `production_limit` INT COMMENT '生産可能限界' AFTER `setup_time`;
