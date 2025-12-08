#!/usr/bin/env python3
"""
production_scheduleテーブルを作成するスクリプト
"""
import pymysql
import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# データベース接続情報を取得
db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://app_user:app_password@db:3306/factory_db')

# URLをパース
# mysql+pymysql://app_user:app_password@db:3306/factory_db
parts = db_url.replace('mysql+pymysql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')

user = user_pass[0]
password = user_pass[1]
host_port = host_db[0].split(':')
host = host_port[0]
port = int(host_port[1]) if len(host_port) > 1 else 3306
database = host_db[1]

print(f"接続情報: {user}@{host}:{port}/{database}")

try:
    # データベースに接続
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )

    print("データベースに接続しました")

    with connection.cursor() as cursor:
        # テーブル作成SQL
        create_table_sql = """
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生産計画スケジュール'
        """

        cursor.execute(create_table_sql)
        connection.commit()
        print("production_scheduleテーブルを作成しました")

        # テーブルが存在するか確認
        cursor.execute("SHOW TABLES LIKE 'production_schedule'")
        result = cursor.fetchone()
        if result:
            print(f"✓ テーブル作成確認: {result[0]}")
        else:
            print("✗ テーブルが見つかりません")

    connection.close()
    print("完了しました")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
