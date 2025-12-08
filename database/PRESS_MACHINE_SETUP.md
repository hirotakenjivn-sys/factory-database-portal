# PRESS機マスタデータ登録手順

## 問題の概要

現在のデータベースには以下の問題があります：

1. `machine_list` テーブルに `machine_type` が設定されていない
2. `spm` テーブルの `press_no` が数値（1-5）で記録されている（本来は 'PRESS-001' のような文字列）
3. PRESS機のマスタデータが不足している

## 解決方法

以下の手順でPRESS機のマスタデータを登録し、整合性を確保します。

### 手順1: PRESS機のマスタデータを登録

```bash
# Dockerコンテナ内でMySQLに接続
docker exec -it factory-db mysql -u app_user -papp_password factory_db

# または、SQLファイルを直接実行
docker exec -i factory-db mysql -u app_user -papp_password factory_db < database/insert_press_machines.sql
```

このスクリプトは以下を実行します：

- 既存の `machine_list` レコードに `machine_type` を設定
  - M-0001 ～ M-0070: PRESS
  - M-0071 ～ M-0130: TAP
  - M-0131 ～ M-0200: BARREL
- SPM工程用のPRESS機を追加
  - PRESS-001 ～ PRESS-008（標準PRESS機）
  - PRESS-S001 ～ PRESS-S004（小型PRESS機）

### 手順2: SPMテーブルのデータを修正

**オプション A: 既存データを更新**

```bash
docker exec -i factory-db mysql -u app_user -papp_password factory_db < database/fix_spm_press_references.sql
```

これにより、press_noの数値（1-5）が対応するPRESS機（PRESS-001～PRESS-005）に変換されます。

**オプション B: 正しいSPMデータを再投入（推奨）**

```bash
docker exec -i factory-db mysql -u app_user -papp_password factory_db < database/insert_spm_data_with_machine_no.sql
```

このファイルには、正しい形式のPRESS機参照を含むSPMデータが含まれています。

## 登録されるPRESS機一覧

### 標準PRESS機
- PRESS-001
- PRESS-002
- PRESS-003
- PRESS-004
- PRESS-005
- PRESS-006
- PRESS-007
- PRESS-008

### 小型PRESS機
- PRESS-S001
- PRESS-S002
- PRESS-S003
- PRESS-S004

## 確認方法

### PRESS機の登録確認

```sql
-- PRESS機の一覧表示
SELECT machine_list_id, factory_id, machine_no, machine_type, user
FROM machine_list
WHERE machine_type = 'PRESS'
ORDER BY machine_no;
```

### machine_typeの集計

```sql
-- machine_typeごとの集計
SELECT machine_type, COUNT(*) as count
FROM machine_list
GROUP BY machine_type
ORDER BY machine_type;
```

期待される結果:
- PRESS: 12件（M-0001～M-0070の70件 + PRESS-001～PRESS-008の8件 + PRESS-S001～PRESS-S004の4件 = 82件）
- TAP: 60件
- BARREL: 70件

### SPMデータの整合性確認

```sql
-- SPMデータとmachine_listの結合確認
SELECT
    s.product_id,
    p.product_code,
    s.process_name,
    s.press_no,
    s.cycle_time,
    ml.machine_type
FROM spm s
JOIN products p ON s.product_id = p.product_id
LEFT JOIN machine_list ml ON s.press_no = ml.machine_no
ORDER BY s.product_id, s.process_name
LIMIT 20;

-- machine_listに存在しないpress_noをチェック（結果が0件であること）
SELECT DISTINCT s.press_no
FROM spm s
LEFT JOIN machine_list ml ON s.press_no = ml.machine_no
WHERE ml.machine_list_id IS NULL;
```

## トラブルシューティング

### エラー: Duplicate entry for key 'machine_no'

PRESS機がすでに登録されている場合、`insert_press_machines.sql` 内の DELETE 文が実行されます。

### SPMデータが正しく参照できない

1. `machine_list` にPRESS機が登録されているか確認
2. `spm` テーブルの `press_no` が文字列形式（'PRESS-001'）になっているか確認
3. 必要に応じて `insert_spm_data_with_machine_no.sql` を再実行

## 関連ファイル

- `insert_press_machines.sql` - PRESS機のマスタデータ登録
- `fix_spm_press_references.sql` - SPMテーブルのpress_no修正
- `insert_spm_data_with_machine_no.sql` - 正しい形式のSPMデータ（既存）
- `update_machine_types.sql` - machine_typeの一括更新（既存）
