# プロジェクト構成定義 (Refactor Project Structure)

このドキュメントでは、`new_app/` におけるフルスタック（フロントエンド・バックエンド・データベース）のディレクトリ構成と、各モジュールの責務について定義します。
`REFACTOR_PROMPT.md` での作業を行う際は、この構成に従ってください。

## 1. 全体構成図

```text
new_app/
├── backend/                # バックエンド (FastAPI)
│   ├── app/
│   │   ├── core/           # 設定・セキュリティ
│   │   ├── db/             # DB接続・セッション
│   │   ├── models/         # SQLAlchemyモデル
│   │   ├── schemas/        # Pydanticスキーマ
│   │   ├── routers/        # APIエンドポイント
│   │   ├── services/       # ビジネスロジック
│   │   └── main.py         # エントリーポイント
│   ├── tests/              # テストコード
│   ├── alembic/            # DBマイグレーション
│   ├── alembic.ini
│   ├── pyproject.toml      # 依存関係管理 (Poetry推奨)
│   └── Dockerfile
├── frontend/               # フロントエンド (Vue 3 + Vite)
│   ├── src/
│   │   ├── assets/         # 静的リソース
│   │   ├── components/     # 共通コンポーネント
│   │   ├── composables/    # Composable関数 (Hooks)
│   │   ├── layouts/        # レイアウト定義
│   │   ├── router/         # ルーティング設定
│   │   ├── stores/         # 状態管理 (Pinia)
│   │   ├── types/          # TypeScript型定義
│   │   ├── views/          # ページコンポーネント
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── database/               # データベース初期化スクリプトなど
│   ├── init/               # 初期データ投入スクリプト
│   └── docker-entrypoint-initdb.d/
└── docker-compose.yml      # 全体起動用
```

## 2. 各領域の技術スタックと責務

### Backend (`backend/`)
*   **Framework**: FastAPI
*   **Language**: Python 3.10+
*   **ORM**: SQLAlchemy 2.0+ (Async推奨)
*   **Migration**: Alembic
*   **責務**:
    *   RESTful APIの提供。
    *   ビジネスロジックの実行（スケジュール計算、トレース登録など）。
    *   データベースとのやり取り。
    *   **注意**: 複雑な計算ロジックは `services/` に集約し、Routerには記述しない。

### Frontend (`frontend/`)
*   **Framework**: Vue.js 3 (Composition API)
*   **Build Tool**: Vite
*   **Language**: TypeScript
*   **State Management**: Pinia
*   **UI Library**: Tailwind CSS (推奨) または 既存のCSS設計
*   **責務**:
    *   ユーザーインターフェースの提供。
    *   APIとの通信（Axios等）。
    *   画面遷移の管理。
    *   **注意**: `TraceView` や `ScheduleView` などの主要機能は、コンポーネントを適切に分割して実装する。

### Database (`database/`)
*   **Engine**: MySQL 8.0+
*   **責務**:
    *   データの永続化。
    *   初期データの管理。

## 3. 命名規則 (Naming Conventions)

### 共通
*   **ディレクトリ**: ケバブケース (例: `user-profile`) または スネークケース (Pythonの場合)
*   **ファイル**:
    *   Python: スネークケース (例: `user_service.py`)
    *   TypeScript/Vue: パスカルケース (例: `UserProfile.vue`, `useAuth.ts`)

### Backend
*   **クラス名**: パスカルケース (例: `ProductionSchedule`)
*   **変数/関数**: スネークケース (例: `calculate_schedule`)

### Frontend
*   **コンポーネント名**: パスカルケース (例: `AppButton.vue`)
*   **変数/関数**: キャメルケース (例: `fetchData`)
