-- Update process_name_types with PRESS variations
-- すべてのPRESS工程バリエーションを追加

SET NAMES utf8mb4;

INSERT INTO `process_name_types` (`process_name`, `day_or_spm`, `user`) VALUES
('PRESS', TRUE, 'admin'),
('PRESS 1/2', TRUE, 'admin'),
('PRESS 2/2', TRUE, 'admin'),
('PRESS 1/3', TRUE, 'admin'),
('PRESS 2/3', TRUE, 'admin'),
('PRESS 3/3', TRUE, 'admin'),
('PRESS 1/4', TRUE, 'admin'),
('PRESS 2/4', TRUE, 'admin'),
('PRESS 3/4', TRUE, 'admin'),
('PRESS 4/4', TRUE, 'admin'),
('PRESS 1/5', TRUE, 'admin'),
('PRESS 2/5', TRUE, 'admin'),
('PRESS 3/5', TRUE, 'admin'),
('PRESS 4/5', TRUE, 'admin'),
('PRESS 5/5', TRUE, 'admin'),
('TAPPING', FALSE, 'admin'),
('PLATING', FALSE, 'admin'),
('HEAT_TREATMENT', FALSE, 'admin'),
('WELDING', FALSE, 'admin'),
('ASSEMBLY', FALSE, 'admin'),
('INSPECTION', FALSE, 'admin'),
('PAINTING', FALSE, 'admin'),
('ANODIZING', FALSE, 'admin'),
('COATING', FALSE, 'admin'),
('POLISHING', FALSE, 'admin')
ON DUPLICATE KEY UPDATE
    day_or_spm = VALUES(day_or_spm),
    user = VALUES(user);
