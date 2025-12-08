#!/bin/bash

# ================================================
# PRESS機マスタデータ登録スクリプト
# ================================================

echo "================================================"
echo "PRESS機マスタデータ登録スクリプト"
echo "================================================"
echo ""

# データベース接続情報
DB_CONTAINER="factory-db"
DB_USER="app_user"
DB_PASSWORD="app_password"
DB_NAME="factory_db"

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "手順1: PRESS機のマスタデータを登録..."
docker exec -i $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < "$SCRIPT_DIR/insert_press_machines.sql"

if [ $? -eq 0 ]; then
    echo "✓ PRESS機のマスタデータ登録が完了しました"
else
    echo "✗ PRESS機のマスタデータ登録に失敗しました"
    exit 1
fi

echo ""
echo "手順2: SPMデータを正しい形式で再投入..."
docker exec -i $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < "$SCRIPT_DIR/insert_spm_data_with_machine_no.sql"

if [ $? -eq 0 ]; then
    echo "✓ SPMデータの再投入が完了しました"
else
    echo "✗ SPMデータの再投入に失敗しました"
    exit 1
fi

echo ""
echo "================================================"
echo "登録完了！"
echo "================================================"
echo ""
echo "確認用クエリ:"
echo ""
echo "# PRESS機の一覧表示"
echo "docker exec -it $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME -e \"SELECT machine_list_id, factory_id, machine_no, machine_type FROM machine_list WHERE machine_type = 'PRESS' ORDER BY machine_no;\""
echo ""
echo "# machine_typeごとの集計"
echo "docker exec -it $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME -e \"SELECT machine_type, COUNT(*) as count FROM machine_list GROUP BY machine_type;\""
echo ""
