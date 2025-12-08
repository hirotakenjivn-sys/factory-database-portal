# 今週のプレス計画に関わるデータベーステーブル

## 使用されるテーブル一覧

### 1. **machine_list** (機械リスト)
- **役割**: PRESS機械の一覧を取得
- **使用カラム**:
  - `machine_no` - 機械番号（PRESS-001など）
  - `machine_list_id` - 機械ID
  - `machine_type` - 機械種別（'PRESS'でフィルタ）
  - `factory_id` - 工場ID

### 2. **products** (製品マスタ)
- **役割**: 製品情報の取得
- **使用カラム**:
  - `product_id` - 製品ID
  - `product_code` - 製品コード
  - `customer_id` - 顧客ID
  - `is_active` - 有効フラグ

### 3. **customers** (顧客マスタ)
- **役割**: 顧客名の取得
- **使用カラム**:
  - `customer_id` - 顧客ID
  - `customer_name` - 顧客名

### 4. **po** (発注)
- **役割**: 未配送のPO（発注）情報を取得、納期から生産計画を逆算
- **使用カラム**:
  - `po_id` - PO ID
  - `product_id` - 製品ID
  - `po_quantity` - 発注数量
  - `delivery_date` - 納期
  - `is_delivered` - 配送済みフラグ（FALSE のみ対象）
  - `date_receive_po` - PO受領日

### 5. **processes** (工程)
- **役割**: 製品の工程情報、PRESS工程の抽出、所要時間の計算
- **使用カラム**:
  - `process_id` - 工程ID
  - `product_id` - 製品ID
  - `process_no` - 工程番号
  - `process_name` - 工程名（「PRESS」を含むものを抽出）
  - `rough_cycletime` - 概算サイクルタイム
  - `setup_time` - 段取時間（分）
  - `production_limit` - 生産可能限界

### 6. **process_name_types** (工程名マスタ)
- **役割**: 工程タイプ（SPM/DAY）の判定
- **使用カラム**:
  - `process_name_id` - 工程名ID
  - `process_name` - 工程名
  - `day_or_spm` - 工程タイプ（TRUE: SPM, FALSE: DAY）

### 7. **calendar** (カレンダー)
- **役割**: 休日判定、稼働日の計算
- **使用カラム**:
  - `calendar_id` - カレンダーID
  - `date_holiday` - 休日日付
  - `holiday_type_id` - 休日種別ID

### 8. **spm** (SPM設定) ※現在は直接使用されていない
- **役割**: 将来的にプレス機械と工程の詳細な関連付けに使用可能
- **使用カラム**:
  - `spm_id` - SPM ID
  - `product_id` - 製品ID
  - `process_name` - 工程名
  - `press_no` - プレス番号（機械番号）
  - `cycle_time` - サイクルタイム

## データフロー

```
1. machine_list (PRESS機械のリスト取得)
   ↓
2. products + customers (未配送POを持つ製品一覧)
   ↓
3. po (未配送PO、納期から逆算)
   ↓
4. processes (各製品の工程情報)
   ↓
5. process_name_types (工程タイプ判定: SPM/DAY)
   ↓
6. 所要時間計算 (rough_cycletime, setup_time, production_limit)
   ↓
7. calendar (休日考慮した日程計算)
   ↓
8. PRESS機械への割り当て & スケジュール生成
```

## 計算ロジック

### SPM工程の場合（day_or_spm = TRUE）
```
総生産時間（分） = (PO数量 / (rough_cycletime × 0.7)) + setup_time
必要日数 = 総生産時間 / 稼働時間
```

### DAY工程の場合（day_or_spm = FALSE）
```
必要サイクル数 = CEILING(PO数量 / production_limit)
総必要日数 = 必要サイクル数 × rough_cycletime
```

## 重要な条件

1. **対象PO**: `is_delivered = FALSE` かつ納期が今日から+28日以内
2. **対象製品**: 有効な製品（`is_active = TRUE`）
3. **対象工程**: 工程名に「PRESS」を含む工程
4. **計画期間**: 今日～今日+7日
5. **スケジュール対象**: 生産計画日が今日～今日+3日のPRESS工程

## 現在の制限事項

- `spm`テーブルは現在使用されていません
- 機械とプレス番号の紐づけは将来的な拡張として想定
- 現在は全てのPRESS機械に対して公平に負荷分散

## データ確認コマンド

```sql
-- PRESS機械リスト
SELECT * FROM machine_list WHERE machine_type = 'PRESS';

-- 未配送PO
SELECT * FROM po WHERE is_delivered = FALSE ORDER BY delivery_date;

-- PRESS工程を持つ製品
SELECT DISTINCT p.product_id, p.product_code, c.customer_name
FROM products p
JOIN customers c ON p.customer_id = c.customer_id
JOIN processes pr ON pr.product_id = p.product_id
WHERE pr.process_name LIKE '%PRESS%' AND p.is_active = TRUE;

-- 工程名タイプ
SELECT * FROM process_name_types WHERE process_name LIKE '%PRESS%';

-- カレンダー（今後の休日）
SELECT * FROM calendar WHERE date_holiday >= CURDATE() ORDER BY date_holiday;
```
