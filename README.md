# AI Message Correction App

日本語ビジネスメッセージの添削機能を持つチャットアプリケーション（フェーズ1 MVP）

## 機能

- LINE風チャットインターフェース
- 日本語メッセージの自動添削（誤字脱字、敬語変換）
- OpenAI GPT-4o による高精度な日本語処理
- 3つの修正候補（丁寧表現、カジュアル表現、誤字修正+敬語）
- UNDO機能（添削履歴の管理）
- 添削履歴の永続化

## 技術スタック

- **フロントエンド**: React + TypeScript + Vite
- **バックエンド**: Python FastAPI
- **データベース**: SQLite
- **AI**: OpenAI GPT-4o API

## セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルにOpenAI APIキーを設定:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 依存関係のインストール

#### Python（バックエンド）
```bash
# uvを使用してPython依存関係をインストール
uv sync
```

#### Node.js（フロントエンド）
```bash
# Node.js依存関係をインストール
npm install
```

## 実行方法

### 開発サーバーの起動

フロントエンドとバックエンドを同時に起動:
```bash
npm run dev:all
```

または、個別に起動:

#### バックエンドのみ
```bash
npm run backend
# または
uv run uvicorn main:app --reload --port 8000
```

#### フロントエンドのみ
```bash
npm run dev
```

### アクセス

- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- API文書: http://localhost:8000/docs

## 使用方法

1. メッセージ入力フィールドに日本語テキストを入力
2. 「添削」ボタンをクリック
3. 3つの修正候補から選択
4. 選択した候補が入力フィールドに反映
5. 必要に応じて「元に戻す」ボタンでUNDO
6. 「送信」ボタンでメッセージを送信

## API エンドポイント

### POST /api/correct
メッセージの添削を実行

**リクエスト:**
```json
{
  "text": "お疲れ様です",
  "user_id": "user123"
}
```

**レスポンス:**
```json
{
  "original_text": "お疲れ様です",
  "variants": [
    {
      "text": "お疲れさまでした",
      "type": "polite", 
      "reason": "より丁寧な表現に変換"
    },
    {
      "text": "お疲れさま！",
      "type": "casual",
      "reason": "親しみやすい表現に変換"
    },
    {
      "text": "お疲れさまです",
      "type": "corrected",
      "reason": "誤字を修正し適切な敬語に変換"
    }
  ]
}
```

## データベース

SQLiteを使用し、以下のテーブルが自動作成されます:

- `correction_history`: 添削履歴
- `user_settings`: ユーザー設定

## フェーズ1で実装済みの機能

- ✅ 基本的な添削機能（誤字脱字、敬語変換）  
- ✅ OpenAI GPT-4o連携
- ✅ 基本的なUI実装
- ✅ UNDO機能

## 今後の予定（フェーズ2以降）

- Claude 3連携追加
- AIモデル選択機能
- 履歴管理機能強化
- UI/UX改善