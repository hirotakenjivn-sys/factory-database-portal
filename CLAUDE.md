# CLAUDE.md - Factory Database Portal

## プロジェクト概要
工場管理データベースポータル。受注(PO)管理、生産スケジューリング、工程管理、トレース、倉庫出荷、金型管理、材料管理を統合したWebアプリ。

## 技術スタック
- **Backend**: FastAPI + SQLAlchemy 2.0 + PyMySQL (Python 3.11)
- **Frontend**: Vue 3 (Composition API `<script setup>`) + Pinia + Vue Router + Vite 5
- **DB**: MySQL 8.0 (UTF8MB4, タイムゾーン UTC+7 ベトナム)
- **デプロイ**: Docker Compose (api / frontend / db) + Nginx リバースプロキシ
- **認証**: JWT Bearer (python-jose), OAuth2PasswordBearer, 24時間有効

## 起動方法
```bash
docker-compose up -d          # 全サービス起動
# Frontend: http://localhost:5173  |  API Docs: http://localhost:8000/docs
# 初期ログイン: admin / admin123

# ローカル開発
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

## ディレクトリ構成
```
backend/app/
  main.py          # FastAPIエントリ、全ルーター登録
  config.py        # pydantic-settings (.env読込)
  database.py      # SQLAlchemy engine, SessionLocal, Base
  models/          # SQLAlchemy ORMモデル (17ファイル)
  routers/         # APIエンドポイント (auth, sales, press, schedule, trace, warehouse, mold, master, dashboard, admin, iot, material_mgmt, process)
  schemas/         # Pydantic リクエスト/レスポンススキーマ
  services/        # ビジネスロジック (production_scheduler.py)
  utils/           # auth.py (JWT/パスワード), delivery_calculator.py
frontend/src/
  router/index.js  # 30+ルート, requiresAuth メタ
  stores/auth.js   # Pinia認証ストア (localStorage永続化)
  utils/api.js     # Axios インスタンス (Bearer自動付与, 401→ログイン遷移)
  views/           # ページコンポーネント (Dashboard, Sales, Press, Schedule, Trace, Warehouse, Mold, Factory, Outsource, master/)
  components/      # 共通UI (AppLayout, AppNavigation, AutocompleteInput等)
```

## コーディング規約・パターン
- **言語**: コメント・ドキュメントは日本語、コード・API名は英語
- **Backend**: ルーターごとにファイル分割、`Depends(get_db)` でセッション注入、`Depends(get_current_user)` で認証ガード
- **Frontend**: Vue 3 `<script setup>` + `ref()`/`computed()`, Axios経由で `/api` にリクエスト
- **DB**: 全テーブルに `timestamp` (自動更新) と `user` (操作者) カラム。PO削除はソフトデリート (deleted_po テーブル)
- **ページネーション**: `skip` / `limit` パラメータ、ソートは `sort_by` クエリパラメータ

## 主要ドメイン
| ドメイン | ルーター | 概要 |
|---------|---------|------|
| 受注管理 | sales | PO登録・検索・CSV/クリップボードインポート |
| 生産スケジュール | schedule | 機械・サイクルタイム・休日考慮した自動スケジューリング |
| プレス工程 | press | 工程一覧・登録・更新 |
| トレース | trace | スタンプ(自社)・外注の作業実績記録 |
| 倉庫 | warehouse | 梱包・出荷管理 |
| 金型 | mold | 金型破損報告・修理スケジュール |
| マスタ | master | 顧客・製品・従業員・サプライヤー・工程名・機械等のCRUD |
| 材料管理 | material_mgmt | 材料種別・ロット・在庫・入出庫トランザクション |
| ダッシュボード | dashboard | KPIカード・週次売上・日次生産チャート |

## DB接続情報 (開発環境)
```
mysql+pymysql://app_user:app_password@db:3306/factory_db
```

## 注意事項
- タイムゾーンは UTC+7 (Asia/Ho_Chi_Minh) 固定。日時処理時に注意
- CORS許可: localhost:5173, localhost:3000, hirota-vn.net
- Nginx: `/api/` → FastAPI, その他 → Vue SPA (index.htmlフォールバック)
- ProductionScheduler (services/production_scheduler.py) は300行超の複雑なアルゴリズム
