# Factory Database Portal - セットアップガイド

## 作成されたプロジェクトの概要

Vue3 + Vite + FastAPI + MySQL の統合プロジェクトが完成しました。

### 実装済み機能

1. **ログイン認証** (JWT)
2. **Dashboard** - 統計カード表示
3. **Sales** - PO登録/一覧表示
4. **Press** - 工程登録/一覧表示
5. **Master** - マスタデータ管理
   - 顧客マスタ（完全実装）
   - 製品/従業員/サプライヤー（画面のみ）

### データベース

- **21テーブル** 完全定義
- **サンプルデータ** 投入済み
- **スペルミス・命名規則** 修正済み

---

## 起動手順

### 前提条件

- Docker Desktop インストール済み
- Git インストール済み（オプション）

### 1. プロジェクトディレクトリに移動

```bash
cd /workspace/factory-database-portal
```

### 2. Dockerコンテナを起動

```bash
docker-compose up -d
```

初回起動時は以下の処理が実行されます：
- MySQL データベース作成
- テーブル作成（21テーブル）
- サンプルデータ投入
- FastAPI 起動
- Vue3 (Vite) 起動

**初回起動には5-10分程度かかります。**

### 3. ログの確認（オプション）

```bash
# すべてのコンテナのログを確認
docker-compose logs -f

# 特定のコンテナのログを確認
docker-compose logs -f api        # FastAPI
docker-compose logs -f frontend   # Vue3
docker-compose logs -f db         # MySQL
```

### 4. 起動確認

以下のURLにアクセスして確認：

- **フロントエンド**: http://localhost:5173
- **APIドキュメント**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

### 5. ログイン

デフォルトユーザー：
- **Username**: `admin`
- **Password**: `admin123`

---

## 停止・再起動

### 停止

```bash
docker-compose down
```

### 再起動

```bash
docker-compose restart
```

### 完全削除（データベース含む）

```bash
docker-compose down -v
```

---

## トラブルシューティング

### ポートが既に使用されている

```bash
# ポート確認
netstat -ano | findstr :3306   # MySQL
netstat -ano | findstr :8000   # FastAPI
netstat -ano | findstr :5173   # Vite

# 該当プロセスを停止するか、docker-compose.ymlでポート番号を変更
```

### データベース接続エラー

```bash
# MySQLコンテナの状態確認
docker-compose ps

# MySQLのヘルスチェック確認
docker inspect factory-db

# MySQLコンテナに直接接続して確認
docker exec -it factory-db mysql -uroot -ppassword123
```

### フロントエンドがビルドエラー

```bash
# node_modulesを再インストール
docker-compose exec frontend rm -rf node_modules
docker-compose exec frontend npm install
docker-compose restart frontend
```

### バックエンドがエラー

```bash
# Pythonパッケージを再インストール
docker-compose exec api pip install -r requirements.txt
docker-compose restart api
```

---

## 開発環境

### ローカル開発（Docker外）

#### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .envファイルを修正（DATABASE_URLをlocalhost:3306に変更）
uvicorn app.main:app --reload
```

#### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

---

## データベース管理

### MySQL接続情報

- **Host**: localhost
- **Port**: 3306
- **Database**: factory_db
- **User**: app_user
- **Password**: app_password
- **Root Password**: password123

### 推奨ツール

- **MySQL Workbench**
- **DBeaver**
- **phpMyAdmin**（別途セットアップ必要）

### 接続例（MySQL Workbench）

1. New Connection
2. Connection Name: `Factory DB`
3. Hostname: `localhost`
4. Port: `3306`
5. Username: `app_user`
6. Password: `app_password`

---

## API エンドポイント一覧

### 認証

- `POST /api/auth/login` - ログイン
- `GET /api/auth/me` - ユーザー情報取得

### Dashboard

- `GET /api/dashboard/cards` - 統計カード
- `GET /api/dashboard/sales-weekly` - 週別売上
- `GET /api/dashboard/production-daily` - 日別生産数

### Sales

- `GET /api/sales/po` - PO一覧
- `POST /api/sales/po` - PO登録
- `PUT /api/sales/po/{po_id}` - PO更新

### Press

- `GET /api/press/processes` - 工程一覧
- `POST /api/press/processes` - 工程登録

### Master

- `GET /api/master/customers` - 顧客一覧
- `POST /api/master/customers` - 顧客登録
- `PUT /api/master/customers/{customer_id}` - 顧客更新
- `GET /api/master/products` - 製品一覧
- `POST /api/master/products` - 製品登録
- `GET /api/master/employees` - 従業員一覧
- `POST /api/master/employees` - 従業員登録
- `GET /api/master/suppliers` - サプライヤー一覧
- `POST /api/master/suppliers` - サプライヤー登録

詳細は http://localhost:8000/docs を参照

---

## 次のステップ（拡張機能）

### 優先度: 高

1. **Warehouse画面** 実装
2. **Mold画面** 実装
3. **Schedule画面** 実装
4. **製品・従業員・サプライヤーマスタ** の完全実装
5. **Dashboard グラフ** 実装（Chart.js）

### 優先度: 中

6. **CSV アップロード** 機能（Sales）
7. **検索フィルタ** 強化（JOINクエリ）
8. **ページネーション** 実装
9. **バリデーション** 強化
10. **エラーハンドリング** 改善

### 優先度: 低

11. **テスト** 追加（pytest, Vitest）
12. **本番環境用設定** 追加
13. **CI/CD** セットアップ
14. **ログイン履歴** 管理
15. **権限管理** （RBAC）

---

## サポート

- **ドキュメント**: `/workspace/DATABASE_SCHEMA_FINAL.md`, `PROJECT_STRUCTURE.md`
- **Issue**: プロジェクトの問題点や改善案は issue として管理

---

## ライセンス

Proprietary
