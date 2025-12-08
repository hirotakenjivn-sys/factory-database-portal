-- マイグレーション: processesテーブルに複合ユニーク制約を追加
-- 実行日: 2025-01-XX
-- 説明: product_id と process_no の組み合わせをユニークにする

-- 既存の重複データを確認
SELECT product_id, process_no, COUNT(*) as count
FROM processes
GROUP BY product_id, process_no
HAVING count > 1;

-- 重複がある場合は、手動で削除または修正してから以下を実行

-- 複合ユニーク制約を追加
ALTER TABLE `processes`
ADD UNIQUE KEY `uk_product_process` (`product_id`, `process_no`);
