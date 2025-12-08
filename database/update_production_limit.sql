-- DAYタイプの工程（process_name_typesでday_or_spm = FALSE）の
-- production_limitを99999に更新するSQL

-- DAYタイプの工程名リスト:
-- TAPPING, PLATING, HEAT_TREATMENT, WELDING, ASSEMBLY,
-- INSPECTION, PAINTING, ANODIZING, COATING, POLISHING

UPDATE processes
SET production_limit = 99999
WHERE process_name IN (
    'TAPPING',
    'PLATING',
    'HEAT_TREATMENT',
    'WELDING',
    'ASSEMBLY',
    'INSPECTION',
    'PAINTING',
    'ANODIZING',
    'COATING',
    'POLISHING'
);

-- 確認クエリ
SELECT process_name, COUNT(*) as count,
       MIN(production_limit) as min_limit,
       MAX(production_limit) as max_limit
FROM processes
WHERE process_name IN (
    'TAPPING', 'PLATING', 'HEAT_TREATMENT', 'WELDING',
    'ASSEMBLY', 'INSPECTION', 'PAINTING', 'ANODIZING',
    'COATING', 'POLISHING'
)
GROUP BY process_name
ORDER BY process_name;
