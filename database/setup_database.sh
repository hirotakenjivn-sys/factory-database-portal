#!/bin/bash
# データベースセットアップスクリプト
# このスクリプトはMySQLデータベースに接続してinit.sqlとseed.sqlを実行します

set -e

# 環境変数の読み込み
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# デフォルト値
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"
DB_NAME="${MYSQL_DATABASE:-factory_db}"
DB_USER="${MYSQL_USER:-app_user}"
DB_PASSWORD="${MYSQL_PASSWORD:-app_password}"
DB_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-password123}"

echo "========================================"
echo "Factory Database Setup"
echo "========================================"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "========================================"
echo ""

# MySQLコマンドの確認
if ! command -v mysql &> /dev/null; then
    echo "エラー: mysqlコマンドが見つかりません"
    echo "MySQLクライアントをインストールするか、Docker経由で実行してください"
    exit 1
fi

# データベース接続テスト
echo "データベース接続をテスト中..."
if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" &> /dev/null; then
    echo "✓ データベースに接続できました"
else
    echo "✗ データベースに接続できませんでした"
    echo "接続情報を確認してください"
    exit 1
fi

# 既存のテーブルを削除するか確認
read -p "既存のデータを削除して再作成しますか？ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "データベースを初期化中..."
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < init.sql
    echo "✓ テーブルの初期化が完了しました"

    echo "サンプルデータを投入中..."
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < seed.sql
    echo "✓ サンプルデータの投入が完了しました"

    echo ""
    echo "========================================"
    echo "セットアップ完了！"
    echo "========================================"
else
    echo "キャンセルされました"
fi
