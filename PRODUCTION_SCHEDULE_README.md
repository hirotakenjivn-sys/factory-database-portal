# 生産スケジュール自動生成システム

## 概要

このシステムは、MySQLデータベースに登録されたPO（発注）情報と工程データを基に、PRESS機を含む全工程の1週間の生産スケジュールを自動生成します。

## 主な機能

1. **納期優先のスケジューリング**: POの納期（delivery_date）が早い順に生産を計画
2. **全工程の管理**: PRESS → TAP → BARREL → PACKING まで順次スケジュール
3. **機械の空き時間管理**: 各機械が同時に1工程のみ処理
4. **休日考慮**: calendarテーブルの休日情報を考慮
5. **段取り時間**: 各工程の前にsetup_timeを加算
6. **待機状態の管理**: 機械が使用中の場合、待機状態として記録

## テーブル構成

### production_schedule（生産スケジュール）
生成されたスケジュールを保存するテーブル

| カラム名 | 型 | 説明 |
|---------|-----|-----|
| schedule_id | INT | スケジュールID（主キー） |
| po_id | INT | 発注ID |
| product_id | INT | 製品ID |
| process_id | INT | 工程ID |
| machine_list_id | INT | 使用機械ID（PRESS/TAP/BARREL） |
| process_no | INT | 工程番号 |
| process_name | VARCHAR(100) | 工程名 |
| status | ENUM | 状態（scheduled, waiting, in_progress, completed） |
| planned_start_datetime | DATETIME | 予定開始日時 |
| planned_end_datetime | DATETIME | 予定終了日時 |
| po_quantity | INT | PO数量 |
| production_time_minutes | DECIMAL(10,2) | 生産時間（分） |
| setup_time_minutes | DECIMAL(10,2) | 段取り時間（分） |

## セットアップ

### 1. テーブル作成

```bash
mysql -u app_user -p factory_db < database/create_production_schedule_table.sql
```

### 2. Python環境設定

必要なパッケージはすでにインストール済みです（requirements.txt参照）:
- pymysql
- python-dotenv

### 3. 環境変数設定

`.env`ファイルで以下の環境変数が設定されていることを確認:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=app_user
DB_PASSWORD=app_password
DB_NAME=factory_db
```

## 使用方法

### 方法1: Pythonスクリプトで直接実行

```bash
cd /workspace/factory-database-portal
python3 generate_production_schedule.py
```

### 方法2: FastAPI経由で実行

```bash
# サーバーを起動
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# APIエンドポイントを呼び出し
curl -X POST "http://localhost:8000/api/schedule/production-schedule/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "working_hours": 8,
    "days_ahead": 7
  }'
```

### スケジュールの確認

```bash
# 生成されたスケジュールを取得
curl -X GET "http://localhost:8000/api/schedule/production-schedule" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## アルゴリズムの詳細

### 1. データ取得
- 未配送のPO（is_delivered=FALSE）を納期順に取得
- 各POに対応する製品の工程リスト（process_no順）を取得
- カレンダー（休日）情報を取得
- 機械リスト（PRESS、TAP、BARREL）を取得

### 2. スケジューリング
各POに対して：

1. **工程を順次処理**（process_no=1から）
2. **前工程の終了時刻 + 段取り時間 = 開始時刻**
3. **工程タイプを確認**
   - SPM: `(数量 / (サイクルタイム × 0.7))`で生産時間を計算
   - DAY: `CEILING(数量 / production_limit) × rough_cycletime × 1日の稼働分数`
4. **使用機械の決定**
   - spmテーブル（PRESS工程）
   - using_machineテーブル
   - 工程名に基づく自動判定（PRESS/TAP/BARREL）
5. **機械の空き時間をチェック**
   - 空いている: スケジュールに追加（status='scheduled'）
   - 使用中: 待機状態として記録（status='waiting'）
6. **終了時刻を計算**して次工程へ
7. **PACKINGまで繰り返す**

### 3. 稼働時間の計算

デフォルト稼働時間: 8時間（休憩時間40分を除いた実稼働時間: 440分）

| 稼働時間 | 実稼働時間（分） | 休憩時間 |
|---------|----------------|---------|
| 8時間 | 440分 | 40分 |
| 9時間 | 500分 | 40分 |
| 10時間 | 560分 | 40分 |
| 11時間 | 620分 | 70分 |
| 12時間 | 680分 | 70分 |

作業開始時刻: 6:00

## 出力例

```
============================================================
生産スケジュール自動生成
============================================================
未配送PO数: 150

処理中: PO#1 - ABC-001 (納期: 2025-01-15)
  工程1: PRESS-1
    開始: 2025-01-08 06:00
    終了: 2025-01-08 14:30
    生産時間: 480分
  工程2: TAP
    開始: 2025-01-08 14:50
    終了: 2025-01-09 10:20
    生産時間: 350分
  工程3: PACKING
    開始: 2025-01-09 10:30
    終了: 2025-01-09 12:00
    生産時間: 90分

=== スケジュール保存中 ===
既存のスケジュールを削除しました
450件のスケジュールを保存しました

=== スケジュール生成完了 ===
対象PO数: 150
生成されたスケジュール数: 450
期間: 2025-01-08 ～ 2025-01-15

完了しました！
```

## APIエンドポイント

### GET /api/schedule/production-schedule
生成されたスケジュールを取得

**パラメータ:**
- `skip`: スキップする件数（デフォルト: 0）
- `limit`: 取得する件数（デフォルト: 1000）

**レスポンス:**
```json
[
  {
    "schedule_id": 1,
    "po_id": 1,
    "po_number": "PO-2025-001",
    "product_code": "ABC-001",
    "customer_name": "トヨタ自動車",
    "process_name": "PRESS-1",
    "machine_no": "P-001",
    "status": "scheduled",
    "planned_start_datetime": "2025-01-08T06:00:00",
    "planned_end_datetime": "2025-01-08T14:30:00",
    "po_quantity": 1000,
    "production_time_minutes": 480.0,
    "setup_time_minutes": 30.0,
    "delivery_date": "2025-01-15"
  }
]
```

### POST /api/schedule/production-schedule/generate
スケジュールを自動生成

**リクエストボディ:**
```json
{
  "working_hours": 8,
  "days_ahead": 7
}
```

**レスポンス:**
```json
{
  "message": "スケジュールを正常に生成しました",
  "output": "生成ログ..."
}
```

### DELETE /api/schedule/production-schedule
すべてのスケジュールを削除

## トラブルシューティング

### 工程に機械が割り当てられない
- spmテーブルまたはusing_machineテーブルにデータが登録されているか確認
- machine_listテーブルに機械タイプ（PRESS/TAP/BARREL）が正しく設定されているか確認

### 生産時間が0になる
- processesテーブルのrough_cycletimeまたはproduction_limitが設定されているか確認
- process_name_typesテーブルで工程タイプ（SPM/DAY）が正しく設定されているか確認

### 休日が考慮されない
- calendarテーブルに休日が登録されているか確認

## 今後の拡張

1. **リアルタイム更新**: 工程の実績（actual_start_datetime, actual_end_datetime）を記録
2. **ガントチャート表示**: フロントエンドでビジュアル表示
3. **アラート機能**: 納期遅延の警告
4. **最適化アルゴリズム**: 機械の稼働率を最大化
5. **複数工場対応**: factory_idを考慮したスケジューリング

## ファイル構成

```
factory-database-portal/
├── database/
│   └── create_production_schedule_table.sql  # テーブル作成SQL
├── backend/
│   └── app/
│       ├── models/
│       │   └── schedule.py                   # ProductionScheduleモデル
│       ├── schemas/
│       │   └── schedule.py                   # スケジュールスキーマ
│       └── routers/
│           └── schedule.py                   # APIエンドポイント
├── generate_production_schedule.py           # スケジュール生成スクリプト
└── PRODUCTION_SCHEDULE_README.md             # このファイル
```

## ライセンス

このシステムは工場管理システムの一部です。
