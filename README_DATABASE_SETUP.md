# データベースセットアップガイド

## サンプルデータについて

このプロジェクトには、各テーブルに約200件のサンプルデータが用意されています。

### 含まれるデータ

- **顧客 (Customers)**: 200件
- **製品 (Products)**: 200件
- **従業員 (Employees)**: 200件
- **サプライヤー (Suppliers)**: 200件
- **工程 (Processes)**: 200件
- **発注 (PO)**: 200件
- **ロット (Lot)**: 200件
- **材料レート (Material Rates)**: 200件
- **SPM設定 (SPM Settings)**: 200件
- **完成品 (Finished Products)**: 200件
- **機械リスト (Machine List)**: 200件
- その他、カレンダー（祝日）、工程名マスタ、稼働時間など

## セットアップ方法

### 方法1: Docker Composeを使う（推奨）

Docker Composeを使用すると、データベースの初期化とサンプルデータの投入が自動的に行われます。

```bash
# プロジェクトルートディレクトリで実行
cd /workspace/factory-database-portal

# 既存のコンテナとボリュームを削除（データをリセット）
docker-compose down -v

# コンテナを起動（init.sqlとseed.sqlが自動実行される）
docker-compose up -d

# ログを確認
docker-compose logs -f db
```

### 方法2: MySQLクライアントから直接実行

MySQLクライアントがインストールされている場合:

```bash
cd /workspace/factory-database-portal/database

# スクリプトに実行権限を付与
chmod +x setup_database.sh

# セットアップスクリプトを実行
./setup_database.sh
```

または、手動で実行:

```bash
# .envファイルから環境変数を読み込む
export $(cat ../.env | grep -v '^#' | xargs)

# テーブルを初期化
mysql -h localhost -P 3306 -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < init.sql

# サンプルデータを投入
mysql -h localhost -P 3306 -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < seed.sql
```

### 方法3: Dockerコンテナ内から実行

Dockerコンテナが既に起動している場合:

```bash
# データベースコンテナに接続
docker exec -it factory-db bash

# コンテナ内でMySQLに接続してSQLを実行
mysql -u root -ppassword123 factory_db < /docker-entrypoint-initdb.d/init.sql
mysql -u root -ppassword123 factory_db < /docker-entrypoint-initdb.d/seed.sql
```

## データの確認

データが正しく投入されたか確認:

```bash
# MySQLに接続
mysql -h localhost -P 3306 -u app_user -papp_password factory_db

# または Docker経由
docker exec -it factory-db mysql -u root -ppassword123 factory_db
```

MySQLプロンプトで:

```sql
-- 各テーブルのレコード数を確認
SELECT COUNT(*) FROM customers;      -- 200件
SELECT COUNT(*) FROM products;       -- 200件
SELECT COUNT(*) FROM employees;      -- 200件
SELECT COUNT(*) FROM suppliers;      -- 200件

-- サンプルデータを確認
SELECT * FROM customers LIMIT 10;
SELECT * FROM products LIMIT 10;
```

## サンプルデータの再生成

サンプルデータを変更したい場合:

```bash
cd /workspace/factory-database-portal/database

# Pythonスクリプトで生成（Python 3が必要）
python3 generate_seed_data.py

# または、Bashスクリプトで生成
bash generate_seed.sh
```

生成後、上記のいずれかの方法で再度データベースに投入してください。

## トラブルシューティング

### データが投入されない

1. `init.sql`が正常に実行されているか確認
2. データベースの文字コードが`utf8mb4`になっているか確認
3. エラーログを確認: `docker-compose logs db`

### 既存データをリセットしたい

```bash
# Docker Composeの場合
docker-compose down -v  # ボリュームも削除
docker-compose up -d

# MySQL直接の場合
mysql -u root -p -e "DROP DATABASE factory_db; CREATE DATABASE factory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# その後、init.sqlとseed.sqlを再実行
```

## 開発時の注意点

- サンプルデータは開発・テスト用です
- 本番環境では使用しないでください
- パスワードなどの認証情報は必ず変更してください（`.env`ファイル）
