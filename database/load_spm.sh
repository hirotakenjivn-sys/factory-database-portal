#!/bin/bash
# SPMサンプルデータを読み込むスクリプト

echo "==========================================="
echo "SPMサンプルデータ読み込み"
echo "==========================================="

# MySQLに接続してSQLファイルを実行
cat /workspace/factory-database-portal/database/insert_spm_correct.sql | \
  mysql -h localhost -u app_user -papp_password factory_db

if [ $? -eq 0 ]; then
    echo "✓ SPMデータの読み込みが完了しました"
else
    echo "✗ SPMデータの読み込みに失敗しました"
fi
