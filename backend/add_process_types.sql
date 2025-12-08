-- ProcessNameTypesテーブルに未登録の工程を追加
-- これらの工程はすべてDAYタイプ（生産可能限界ベース）として登録

INSERT INTO process_name_types (process_name, day_or_spm, user, timestamp)
VALUES
    ('INSPECTION', FALSE, 'system', NOW()),
    ('PLATING', FALSE, 'system', NOW()),
    ('ASSEMBLY', FALSE, 'system', NOW()),
    ('PAINTING', FALSE, 'system', NOW()),
    ('COATING', FALSE, 'system', NOW()),
    ('WELDING', FALSE, 'system', NOW()),
    ('POLISHING', FALSE, 'system', NOW()),
    ('ANODIZING', FALSE, 'system', NOW()),
    ('HEAT_TREATMENT', FALSE, 'system', NOW()),
    ('TAPPING', FALSE, 'system', NOW())
ON DUPLICATE KEY UPDATE
    day_or_spm = VALUES(day_or_spm),
    user = VALUES(user),
    timestamp = VALUES(timestamp);
