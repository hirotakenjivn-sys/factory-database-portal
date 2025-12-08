# データベースマイグレーションガイド

## is_deliveredカラムの追加

既存のデータベースに`is_delivered`カラムと`deleted_po`テーブルを追加するマイグレーションです。

### エラーが発生した場合

もし以下のエラーが出た場合：
```
1054 UNKNOWN COLUMN IS_DELIVERED in field list
```

このマイグレーションを実行してください。

### 実行方法

#### 方法1: Docker経由で実行

```bash
docker exec -i factory-db mysql -u root -ppassword123 factory_db < database/migration_add_is_delivered.sql
```

#### 方法2: MySQLクライアントから直接実行

```bash
mysql -h localhost -P 3306 -u app_user -papp_password factory_db < database/migration_add_is_delivered.sql
```

#### 方法3: Docker Composeで完全リセット（推奨）

データベースを完全に再作成する場合：

```bash
# プロジェクトルートで実行
cd /workspace/factory-database-portal

# 既存のコンテナとボリュームを削除
docker-compose down -v

# コンテナを起動（init.sqlが自動実行される）
docker-compose up -d

# ログを確認
docker-compose logs -f db
```

この方法では、最新の`init.sql`が使用されるため、`is_delivered`カラムと`deleted_po`テーブルが最初から含まれます。

### 実行後の確認

マイグレーションが成功したか確認：

```sql
-- poテーブルの構造を確認
DESCRIBE po;

-- is_deliveredカラムが追加されていることを確認
-- 以下のような出力があればOK：
-- | is_delivered | tinyint(1) | YES  |     | 0       |                             |

-- deleted_poテーブルが作成されていることを確認
SHOW TABLES LIKE 'deleted_po';
```

## トラブルシューティング

### IF NOT EXISTSエラーが出る場合

MySQL 8.0.32より古いバージョンを使用している場合、`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`がサポートされていない可能性があります。

その場合は、以下のSQLを手動で実行してください：

```sql
-- is_deliveredカラムを追加（既に存在する場合はエラーが出ますが無視してOK）
ALTER TABLE `po`
ADD COLUMN `is_delivered` BOOLEAN DEFAULT FALSE COMMENT '配送済みフラグ' AFTER `po_quantity`;

ALTER TABLE `po`
ADD INDEX `idx_po_is_delivered` (`is_delivered`);

-- 既存レコードを更新
UPDATE `po` SET `is_delivered` = FALSE WHERE `is_delivered` IS NULL;
```
