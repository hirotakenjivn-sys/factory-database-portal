-- production_schedule テーブル作成
-- 生産計画スケジュールを格納するテーブル

CREATE TABLE IF NOT EXISTS production_schedule (
  schedule_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'スケジュールID（主キー）',
  po_id INT NOT NULL COMMENT 'PO ID',
  process_id INT NOT NULL COMMENT '工程ID',
  machine_list_id INT NULL COMMENT 'マシンID（PRESS機の場合のみ設定）',
  planned_start_datetime DATETIME NOT NULL COMMENT '開始予定日時',
  planned_end_datetime DATETIME NOT NULL COMMENT '終了予定日時',
  po_quantity INT NOT NULL COMMENT 'PO数量',
  setup_time DECIMAL(10,2) DEFAULT 0 COMMENT '段取時間（分）',
  processing_time DECIMAL(10,2) DEFAULT 0 COMMENT '加工時間（分）',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  user VARCHAR(100) COMMENT '作成ユーザー',

  FOREIGN KEY (po_id) REFERENCES po(po_id) ON DELETE CASCADE,
  FOREIGN KEY (process_id) REFERENCES processes(process_id) ON DELETE CASCADE,
  FOREIGN KEY (machine_list_id) REFERENCES machine_list(machine_list_id) ON DELETE SET NULL,

  INDEX idx_po_id (po_id),
  INDEX idx_process_id (process_id),
  INDEX idx_machine_list_id (machine_list_id),
  INDEX idx_planned_start (planned_start_datetime),
  INDEX idx_planned_end (planned_end_datetime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生産計画スケジュール';
