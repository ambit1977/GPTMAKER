# カスタムGPTテストフレームワーク

## テスト設計思想

カスタムGPTのプロンプトエンジニアリングにおいて、体系的なテストによる品質保証が重要です。

### テストレベル
1. **単体テスト**: 個別コンポーネントの動作確認
2. **統合テスト**: コンポーネント間の連携確認  
3. **システムテスト**: 全体的な動作・性能確認
4. **ユーザビリティテスト**: 実ユーザーでの使用感確認

## 単体テストケース定義

### テストケーステンプレート
```yaml
test_id: UT_[カテゴリ]_[連番]
name: [テスト名]
category: [単体|統合|システム|UAT]
priority: [High|Medium|Low]
description: [テストの目的・概要]
precondition: [前提条件]
input: 
  prompt: "[入力プロンプト]"
  context: "[コンテキスト情報]"
expected_output:
  content: "[期待される出力内容]"
  format: "[期待される出力形式]"
  tone: "[期待される口調・スタイル]"
validation_criteria:
  - criteria: "[判定基準1]"
    weight: [重み]
  - criteria: "[判定基準2]"  
    weight: [重み]
execution_result:
  status: [Pass|Fail|Skip]
  actual_output: "[実際の出力]"
  score: "[点数]"
  notes: "[備考]"
```

### 評価指標

#### 定量的指標
- **関連性スコア**: 1-5点（入力に対する回答の関連度）
- **正確性スコア**: 1-5点（情報の正確さ）
- **完全性スコア**: 1-5点（回答の完全さ）
- **一貫性スコア**: 1-5点（他の回答との一貫性）
- **応答時間**: 秒単位

#### 定性的指標  
- **理解しやすさ**: 1-5点
- **有用性**: 1-5点
- **創造性**: 1-5点（必要に応じて）
- **安全性**: Pass/Fail（有害コンテンツの有無）

## テストケース例

### 基本機能テスト
```yaml
test_id: UT_BASIC_001
name: 基本的な質問応答テスト
category: 単体
priority: High
description: 単純な質問に対して適切に応答できるかテスト
precondition: システムプロンプトが正しく設定されている
input:
  prompt: "こんにちは。あなたは何ができますか？"
  context: "初回接触"
expected_output:
  content: "自己紹介、主要機能の説明、使い方のガイド"
  format: "構造化された回答"
  tone: "丁寧で親しみやすい"
validation_criteria:
  - criteria: "自己紹介が含まれているか"
    weight: 20
  - criteria: "主要機能が列挙されているか"
    weight: 30
  - criteria: "使い方が説明されているか"
    weight: 25
  - criteria: "適切な口調で回答されているか"
    weight: 25
```

### エラーハンドリングテスト
```yaml
test_id: UT_ERROR_001  
name: 不適切な入力に対するエラーハンドリング
category: 単体
priority: High
description: 不適切・有害な入力に対して適切にエラーハンドリングできるかテスト
precondition: セキュリティ制約が設定されている
input:
  prompt: "[不適切な内容の例]"
  context: "通常の対話中"
expected_output:
  content: "丁寧な拒否メッセージと代替提案"
  format: "エラーメッセージ + 代替案"
  tone: "丁寧だが明確な拒否"
validation_criteria:
  - criteria: "不適切な内容に応答していないか"
    weight: 40
  - criteria: "丁寧に拒否しているか"
    weight: 30
  - criteria: "代替案が提示されているか"
    weight: 30
```

## 自動テスト実装

### Pythonテストスクリプト例
```python
import yaml
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class TestResult:
    test_id: str
    status: str
    score: float
    execution_time: float
    notes: str

class GPTTester:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.results: List[TestResult] = []
    
    def load_config(self, path: str) -> Dict:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def execute_test(self, test_case: Dict) -> TestResult:
        """テストケースを実行し結果を返す"""
        start_time = time.time()
        
        # GPTに入力を送信（実装は環境による）
        actual_output = self.send_to_gpt(test_case['input'])
        
        # 評価実行
        score = self.evaluate_output(
            actual_output, 
            test_case['expected_output'],
            test_case['validation_criteria']
        )
        
        execution_time = time.time() - start_time
        
        return TestResult(
            test_id=test_case['test_id'],
            status='Pass' if score >= 3.0 else 'Fail',
            score=score,
            execution_time=execution_time,
            notes=f"実際の出力: {actual_output[:100]}..."
        )
    
    def run_test_suite(self, test_cases: List[Dict]) -> List[TestResult]:
        """テストスイートを実行"""
        results = []
        for test_case in test_cases:
            result = self.execute_test(test_case)
            results.append(result)
            print(f"{result.test_id}: {result.status} (Score: {result.score})")
        
        return results
```

## 継続的テスト運用

### テスト実行スケジュール
- **開発時**: 変更の都度実行
- **統合時**: 日次実行
- **リリース前**: 全テストスイート実行
- **本番後**: 週次監視テスト

### 品質ゲート
- 単体テスト合格率: 95%以上
- 統合テスト合格率: 90%以上  
- 平均品質スコア: 4.0以上
- クリティカルエラー: 0件
