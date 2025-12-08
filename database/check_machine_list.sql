-- 機械リストの総数確認
SELECT COUNT(*) as total FROM machine_list;

-- 工場・機械種別の集計
SELECT
    f.factory_name,
    ml.machine_type,
    COUNT(*) as count
FROM machine_list ml
LEFT JOIN factories f ON ml.factory_id = f.factory_id
GROUP BY f.factory_name, ml.machine_type
ORDER BY f.factory_name, ml.machine_type;

-- 全機械リスト
SELECT
    ml.machine_list_id,
    f.factory_name,
    ml.machine_no,
    ml.machine_type,
    ml.user,
    ml.timestamp
FROM machine_list ml
LEFT JOIN factories f ON ml.factory_id = f.factory_id
ORDER BY ml.factory_id, ml.machine_type, ml.machine_no;
