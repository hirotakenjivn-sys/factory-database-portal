-- 機械リストの総数確認
SELECT COUNT(*) as total FROM machine_list;

-- 工場・機械種別の集計
SELECT
    f.factory_name,
    mt.machine_type_name,
    COUNT(*) as count
FROM machine_list ml
LEFT JOIN factories f ON ml.factory_id = f.factory_id
LEFT JOIN machine_types mt ON ml.machine_type_id = mt.machine_type_id
GROUP BY f.factory_name, mt.machine_type_name
ORDER BY f.factory_name, mt.machine_type_name;

-- 全機械リスト
SELECT
    ml.machine_list_id,
    f.factory_name,
    ml.machine_no,
    mt.machine_type_name,
    ml.user,
    ml.timestamp
FROM machine_list ml
LEFT JOIN factories f ON ml.factory_id = f.factory_id
LEFT JOIN machine_types mt ON ml.machine_type_id = mt.machine_type_id
ORDER BY ml.factory_id, mt.machine_type_name, ml.machine_no;
