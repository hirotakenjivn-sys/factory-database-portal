# データベーススキーマ定義指針 (Refactor Database Schema)

このドキュメントでは、`new_app/backend/app/models/` におけるデータベースモデルの定義方針と、スキーマ改善案について定義します。
フルスタックリファクタリングに伴い、テーブル名やカラム名の整合性を向上させます。

## 1. 基本方針

*   **命名規則の統一**:
    *   テーブル名: **複数形・スネークケース** (例: `products`, `purchase_orders`)
    *   カラム名: **スネークケース**
    *   主キー: `id` または `table_name_id` (統一する。ここでは `id` 推奨だが、既存との兼ね合いで `table_name_id` も可とする。今回はわかりやすさ重視で `id` への移行を検討するが、移行コストを考え `table_name_id` を維持する方針とする)
*   **外部キー制約**: 必ず外部キー制約 (`ForeignKey`) を定義し、`ondelete` などの動作を明示する。
*   **共通カラム**: 全テーブルに `created_at`, `updated_at` を付与する。

## 2. モデル定義 (改善案)

### 2.1. Products & Processes (製品・工程)

*   **`products`** (旧: `products`)
    *   `product_id` (PK)
    *   `product_code` (Unique, Index)
    *   `customer_id` (FK -> `customers.customer_id`)
    *   `is_active` (Boolean)
*   **`processes`** (旧: `processes`)
    *   `process_id` (PK)
    *   `product_id` (FK -> `products.product_id`)
    *   `process_no` (Integer) - 工程順序
    *   `process_name` (String)
    *   `machine_type` (String) - 'PRESS', 'TAP' など (工程名から分離して管理することを推奨)
*   **`process_types`** (旧: `process_name_type`)
    *   `process_type_id` (PK)
    *   `process_name` (Unique)
    *   `calculation_type` (Enum: 'SPM', 'DAY') - 旧 `day_or_spm` をわかりやすく

### 2.2. Orders (注文)

*   **`purchase_orders`** (旧: `po`)
    *   `po_id` (PK)
    *   `po_number` (String, Index)
    *   `product_id` (FK -> `products.product_id`)
    *   `quantity` (Integer) - 旧 `po_quantity`
    *   `delivery_date` (Date)
    *   `status` (Enum: 'OPEN', 'DELIVERED', 'CANCELLED') - フラグ管理からステータス管理へ

### 2.3. Factory Resources (工場リソース)

*   **`machines`** (旧: `machine_list`)
    *   `machine_id` (PK)
    *   `machine_code` (String)
    *   `machine_type` (String)
*   **`employees`** (旧: `employees`)
    *   `employee_id` (PK)
    *   `employee_code` (String)
    *   `name` (String)

### 2.4. Production & Trace (生産・実績)

*   **`production_schedules`** (旧: `production_schedule`)
    *   `schedule_id` (PK)
    *   `po_id` (FK)
    *   `process_id` (FK)
    *   `machine_id` (FK)
    *   `planned_start_at` (DateTime)
    *   `planned_end_at` (DateTime)
*   **`process_results`** (旧: `stamp_traces`) - 名前をより汎用的に
    *   `result_id` (PK)
    *   `po_id` (FK, Nullable) - POに紐づく場合
    *   `product_id` (FK)
    *   `process_id` (FK)
    *   `machine_id` (FK, Nullable)
    *   `employee_id` (FK)
    *   `lot_number` (String)
    *   `ok_quantity` (Integer)
    *   `ng_quantity` (Integer)
    *   `status` (Enum: 'PASS', 'FAIL', 'REWORK')
    *   `started_at` (DateTime)
    *   `finished_at` (DateTime)

## 3. マイグレーション戦略

フルリビルドのため、以下の手順を推奨します。

1.  **新規DB作成**: 既存DBとは別に、新しいスキーマ用のデータベースを作成する。
2.  **データ移行スクリプト**: 旧DBからデータを読み出し、新スキーマに合わせて変換・投入するPythonスクリプトを作成する。
    *   特にテーブル名やカラム名の変更（マッピング）をここで行う。
3.  **API互換性**: バックエンドのPydanticスキーマ (`schemas/`) で、フロントエンドへのレスポンス形式を旧APIと合わせることで、DBスキーマ変更の影響を吸収する。

## 4. コーディング規約 (SQLAlchemy)

*   **Baseクラス**: `core.db.Base` を継承。
*   **Mixin**: `TimestampMixin` (`created_at`, `updated_at`) を使用。
*   **型ヒント**: 全てのリレーションシップに型ヒントを付与。
