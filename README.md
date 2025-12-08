# Factory Database Portal

製造業向けデータベース管理ポータル

## 技術スタック

- **フロントエンド**: Vue 3 + Vite + Pinia
- **バックエンド**: FastAPI + SQLAlchemy
- **データベース**: MySQL 8.0.32
- **インフラ**: Docker + docker-compose

## 機能

- Login（ログイン認証）
- Dashboard（ダッシュボード：統計・グラフ表示）
- Sales（PO登録/検索/表示）
- Press（工程登録/VIEW）
- Warehouse（PACKING/DELIVERY管理）
- Mold（金型故障管理）
- Schedule（スケジュール管理）
- Master（マスタデータ登録）
  - 顧客
  - 製品コード
  - サプライヤー
  - 工程名
  - 材料レート
  - 従業員
  - 機械リスト
  - カレンダー

## セットアップ

### 前提条件

- Docker
- Docker Compose

### 起動方法

1. リポジトリをクローン
```bash
git clone <repository-url>
cd factory-database-portal
```

2. 環境変数を設定（必要に応じて `.env` を編集）
```bash
cp .env.example .env  # 本番環境では必ず編集すること
```

3. Dockerコンテナを起動
```bash
docker-compose up -d
```

4. ブラウザでアクセス
- フロントエンド: http://localhost:5173
- API ドキュメント: http://localhost:8000/docs

### 初期ユーザー

- **ユーザー名**: admin
- **パスワード**: admin123

（本番環境では必ず変更してください）

## 開発

### バックエンド開発

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### フロントエンド開発

```bash
cd frontend
npm install
npm run dev
```

### データベースマイグレーション

```bash
# 将来実装予定（Alembic使用）
```

## プロジェクト構造

```
factory-database-portal/
├── backend/          # FastAPI バックエンド
├── frontend/         # Vue3 フロントエンド
├── database/         # DBスクリプト
└── docker-compose.yml
```

詳細は `PROJECT_STRUCTURE.md` を参照してください。

## ドキュメント

- [データベース設計](../DATABASE_SCHEMA_FINAL.md)
- [プロジェクト構造](../PROJECT_STRUCTURE.md)
- [API仕様書](http://localhost:8000/docs) ※起動後にアクセス

## ライセンス

Proprietary
