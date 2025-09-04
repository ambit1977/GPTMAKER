# カスタムGPT開発・運用ガイド

## クイックスタート

### 1. 環境セットアップ

```bash
# リポジトリクローン
git clone <your-repo-url>
cd GPTMAKER

# Python環境セットアップ（推奨: Python 3.9+）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# ChromeDriverインストール（自動化用）
# macOS
brew install chromedriver

# Linux
sudo apt-get install chromium-chromedriver

# Windows
# https://chromedriver.chromium.org/ からダウンロード
```

### 2. 設定ファイル編集

```bash
# ビルド設定
cp config/build_config.yaml config/build_config.local.yaml
# build_config.local.yamlを編集してGPT設定をカスタマイズ

# デプロイ設定
cp config/deploy_config.yaml config/deploy_config.local.yaml
# deploy_config.local.yamlを編集してデプロイ設定をカスタマイズ
```

### 3. 環境変数設定

```bash
# .envファイル作成
cat > .env << EOF
CHATGPT_EMAIL=your-email@example.com
CHATGPT_PASSWORD=your-password
EOF
```

## 開発ワークフロー

### Phase 1: 要件定義

1. **要件定義書作成**
   ```bash
   cp docs/requirements/requirements_template.md docs/requirements/my_gpt_requirements.md
   # 要件定義書を編集
   ```

2. **ペルソナ・ユースケース定義**
   - ターゲットユーザーの明確化
   - 主要ユースケースの洗い出し
   - 成功指標（KPI）の設定

### Phase 2: 設計

1. **プロンプト設計**
   ```bash
   cp docs/design/prompt_design_template.md docs/design/my_gpt_design.md
   # プロンプト設計書を編集
   ```

2. **コンポーネント設計**
   - ロール定義の作成
   - 指示文の構造化
   - 会話フローの設計

### Phase 3: 実装

1. **プロンプトコンポーネント作成**
   ```bash
   # ロール定義
   vim src/prompts/role_definition.md
   
   # メイン指示文
   vim src/instructions/main_instructions.md
   
   # 例文・サンプル
   vim src/examples/example_001.md
   
   # ナレッジベース
   # src/knowledge/ にファイル配置
   ```

2. **設定ファイル更新**
   ```bash
   vim config/build_config.yaml
   ```

### Phase 4: テスト

1. **単体テスト作成・実行**
   ```bash
   # テストケース作成
   vim tests/unit/test_basic_functionality.py
   
   # テスト実行
   python -m pytest tests/unit/ -v
   ```

2. **統合テスト実行**
   ```bash
   python -m pytest tests/integration/ -v
   ```

### Phase 5: ビルド・デプロイ

1. **ローカルビルド**
   ```bash
   python scripts/build_prompts.py
   
   # ビルド結果確認
   cat build/main_prompt.txt
   cat build/gpt_config.json
   ```

2. **ローカルデプロイ（テスト）**
   ```bash
   python scripts/chatgpt_deployer.py --config build/gpt_config.json --action create
   ```

3. **Git管理**
   ```bash
   git add .
   git commit -m "feat: 新機能追加"
   git push origin develop
   ```

## CI/CD パイプライン

### 自動化ワークフロー

1. **開発ブランチ（develop）**
   - プッシュ時: 自動テスト実行
   - 成功時: 開発環境自動デプロイ

2. **本番ブランチ（main）**
   - プッシュ時: 承認ワークフロー起動
   - 承認後: 本番環境デプロイ

### GitHub Secrets設定

```bash
# GitHubリポジトリの Settings > Secrets and variables > Actions で設定

CHATGPT_EMAIL: "your-email@example.com"
CHATGPT_PASSWORD: "your-password"
SLACK_WEBHOOK_URL: "https://hooks.slack.com/..."
APPROVERS: "username1,username2"
```

## ファイル構成詳細

### ソースファイル
```
src/
├── prompts/           # プロンプトコンポーネント
│   ├── role_definition.md
│   └── behavior_rules.md
├── instructions/      # 指示文
│   ├── main_instructions.md
│   └── error_handling.md
├── examples/          # 例文・サンプル
│   ├── example_001.md
│   └── example_002.md
└── knowledge/         # ナレッジベース
    ├── documents/
    └── data/
```

### 設定ファイル
```
config/
├── build_config.yaml      # ビルド設定
├── deploy_config.yaml     # デプロイ設定
└── test_config.yaml       # テスト設定
```

### テストファイル
```
tests/
├── unit/              # 単体テスト
├── integration/       # 統合テスト
├── scenarios/         # シナリオテスト
└── fixtures/          # テストデータ
```

## トラブルシューティング

### よくある問題

1. **ビルドエラー**
   ```bash
   # 設定ファイル確認
   python -c "import yaml; print(yaml.safe_load(open('config/build_config.yaml')))"
   
   # 依存関係確認
   pip check
   ```

2. **デプロイエラー**
   ```bash
   # ChromeDriverバージョン確認
   chromedriver --version
   
   # ログ確認
   tail -f logs/deployment.log
   ```

3. **テストエラー**
   ```bash
   # 詳細ログでテスト実行
   python -m pytest -v -s --tb=long
   ```

### ログ確認

```bash
# デプロイログ
tail -f logs/deployment.log

# ビルドログ
cat build/build_info.json

# テストログ
cat test-results-*.xml
```

## ベストプラクティス

### プロンプト開発
1. **モジュラー設計**: コンポーネントを小さく分割
2. **バージョン管理**: 変更は段階的に実施
3. **テスト駆動**: 期待動作を先にテスト化
4. **継続改善**: メトリクスに基づく改善

### 運用管理
1. **定期監視**: パフォーマンス・品質の定期チェック
2. **バックアップ**: 重要な設定・データのバックアップ
3. **文書化**: 変更履歴・運用ノウハウの文書化
4. **チーム共有**: ナレッジの共有・標準化

## 拡張・カスタマイズ

### 新機能追加
1. 新しいコンポーネントテンプレート作成
2. ビルドスクリプトの拡張
3. テストケースの追加
4. CI/CDパイプラインの更新

### 他プラットフォーム対応
- Claude（Anthropic）対応
- Bard（Google）対応
- Custom GPT以外のプラットフォーム
