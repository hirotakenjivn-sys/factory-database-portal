# Antigravity用 フルスタックリビルドプロンプト (REFACTOR_PROMPT)

## 1. 目的 (Objective)
**全く新しいアプリケーション（フロントエンド・バックエンド・データベース）**を `new_app/` ディレクトリにゼロから作成してください。
既存の `backend/app/` や `frontend/` は「スパゲッティコード」化しているため、**修正やリファクタリングは行わず**、仕様の参照元としてのみ使用してください。

目標は、**クリーンアーキテクチャに基づいたモダンなフルスタックアプリケーション**を構築することです。

## 2. 必須要件 (Core Requirements)

1.  **新規ディレクトリ**: 全てのファイルは `new_app/` 内に作成すること。
2.  **ロジックの実装禁止 (No Logic Implementation)**:
    *   **重要**: 複雑な計算ロジック（スケジューリング、工程計算など）は**コピーも実装もしないでください**。
    *   バックエンドのService層には、**インターフェース（メソッド定義）のみ**を作成し、中身は `pass` またはダミーデータを返すようにしてください。
    *   フロントエンドの画面も、ダミーデータで表示を確認できる「ガワ」だけを作成してください。
3.  **技術スタックの刷新**:
    *   **Frontend**: Vue 3 (Composition API) + Vite + TypeScript + Pinia
    *   **Backend**: FastAPI + Python 3.10+ + SQLAlchemy 2.0 (Async)
    *   **Database**: MySQL 8.0 (スキーマ改善あり)

## 3. 参照ドキュメント (References)

以下のドキュメントに従って実装を行ってください。

*   **[refactor-project-structure.md](./refactor-project-structure.md)**: `new_app/` 以下のディレクトリ構成、各層の責務、命名規則。
*   **[refactor-database-schema.md](./refactor-database-schema.md)**: 新しいデータベーススキーマの定義と命名規則。

## 4. 実装ステップ (Implementation Steps)

### Step 1: Project Setup (基盤構築)
*   `new_app/` ディレクトリを作成。
*   `backend/`, `frontend/`, `database/` の基本構造を作成。
*   `docker-compose.yml` を作成し、3つのコンテナが連携して起動するように設定。

### Step 2: Database (スキーマ定義)
*   `refactor-database-schema.md` に基づき、`backend/app/models/` にSQLAlchemyモデルを作成。
*   Alembicをセットアップし、初期マイグレーションファイルを生成。

### Step 3: Backend API (インターフェース定義)
*   Pydanticスキーマ (`schemas/`) を定義。
*   Router (`routers/`) を作成し、エンドポイントを定義。
*   Service (`services/`) のプレースホルダーを作成（ロジックは空）。

### Step 4: Frontend (UI構築)
*   ViteでVue 3 + TypeScriptプロジェクトを初期化。
*   主要な画面 (`TraceView`, `ScheduleView` 相当) のコンポーネントを作成。
*   APIクライアント (Axios) を設定し、バックエンドのダミーAPIを叩いて画面が表示されることを確認。

## 5. 禁止事項 (What NOT to do)
*   既存コードのコピペ（特にロジック部分）。
*   複雑なアルゴリズムの実装。
*   `new_app` 以外への書き込み。

## 6. 成果物 (Deliverables)
*   `new_app` ディレクトリ一式。
*   `docker-compose up` 一発で、DB、Backend、Frontendが起動し、ブラウザから画面にアクセスできる状態。
