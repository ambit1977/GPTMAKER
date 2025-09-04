#!/usr/bin/env python3
"""
プロンプトビルドスクリプト

分割されたプロンプトコンポーネントを統合し、
デプロイ可能な形式に変換します。
"""

import os
import json
import yaml
import argparse
from typing import Dict, List
from pathlib import Path
import logging

class PromptBuilder:
    """プロンプトビルダークラス"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.build_dir = self.project_root / "build"
        self.config_dir = self.project_root / "config"
        
        # ディレクトリが存在しない場合は作成
        self.build_dir.mkdir(exist_ok=True)
        
        # ログ設定
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def load_build_config(self) -> Dict:
        """ビルド設定を読み込み"""
        config_path = self.config_dir / "build_config.yaml"
        
        if not config_path.exists():
            # デフォルト設定を作成
            default_config = {
                "gpt_name": "MyCustomGPT",
                "description": "カスタムGPTの説明",
                "visibility": "private",
                "components": {
                    "role_definition": "src/prompts/role_definition.md",
                    "instructions": "src/instructions/main_instructions.md",
                    "examples": "src/examples/",
                    "knowledge": "src/knowledge/"
                },
                "capabilities": {
                    "web_browsing": True,
                    "dalle": False,
                    "code_interpreter": True
                },
                "conversation_starters": [
                    "何について相談したいですか？",
                    "どのような支援が必要ですか？",
                    "具体的な課題を教えてください",
                    "まずは概要を説明してください"
                ]
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
                
            self.logger.info(f"デフォルト設定ファイルを作成しました: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def load_component(self, component_path: str) -> str:
        """コンポーネントファイルを読み込み"""
        file_path = self.project_root / component_path
        
        if not file_path.exists():
            self.logger.warning(f"コンポーネントファイルが見つかりません: {file_path}")
            return ""
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.logger.error(f"ファイル読み込みエラー: {file_path} - {e}")
            return ""
            
    def load_directory_components(self, dir_path: str) -> List[str]:
        """ディレクトリ内の全コンポーネントを読み込み"""
        directory = self.project_root / dir_path
        
        if not directory.exists():
            self.logger.warning(f"ディレクトリが見つかりません: {directory}")
            return []
            
        components = []
        for file_path in directory.glob("*.md"):
            component = self.load_component(str(file_path.relative_to(self.project_root)))
            if component:
                components.append(component)
                
        return components
        
    def build_main_prompt(self, config: Dict) -> str:
        """メインプロンプトを構築"""
        prompt_parts = []
        
        # ロール定義部分
        role_def = self.load_component(config["components"]["role_definition"])
        if role_def:
            prompt_parts.append("# あなたの役割")
            prompt_parts.append(role_def)
            prompt_parts.append("")
            
        # 指示文部分
        instructions = self.load_component(config["components"]["instructions"])
        if instructions:
            prompt_parts.append("# 指示・制約")
            prompt_parts.append(instructions)
            prompt_parts.append("")
            
        # 例文部分
        examples = self.load_directory_components(config["components"]["examples"])
        if examples:
            prompt_parts.append("# 応答例")
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"## 例 {i}")
                prompt_parts.append(example)
                prompt_parts.append("")
                
        # 一般的な制約を追加
        prompt_parts.extend([
            "# 重要な制約",
            "- 回答は正確で有用な情報を提供する",
            "- 不適切な内容には応答しない", 
            "- 不明な点は素直に「わからない」と伝える",
            "- ユーザーの質問に対して構造化された回答を心がける",
            ""
        ])
        
        return "\n".join(prompt_parts)
        
    def collect_knowledge_files(self, config: Dict) -> List[str]:
        """ナレッジファイルのパス一覧を取得"""
        knowledge_dir = self.project_root / config["components"]["knowledge"]
        
        if not knowledge_dir.exists():
            return []
            
        knowledge_files = []
        for file_path in knowledge_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.pdf', '.txt', '.md', '.docx']:
                knowledge_files.append(str(file_path))
                
        return knowledge_files
        
    def create_gpt_config(self, config: Dict, main_prompt: str) -> Dict:
        """GPT設定JSONを作成"""
        knowledge_files = self.collect_knowledge_files(config)
        
        gpt_config = {
            "name": config["gpt_name"],
            "description": config["description"], 
            "instructions": main_prompt,
            "conversation_starters": config.get("conversation_starters", []),
            "knowledge_files": knowledge_files,
            "capabilities": config.get("capabilities", {}),
            "visibility": config.get("visibility", "private")
        }
        
        return gpt_config
        
    def validate_build(self, gpt_config: Dict) -> bool:
        """ビルド結果の検証"""
        issues = []
        
        # 必須項目チェック
        if not gpt_config.get("name"):
            issues.append("GPT名が設定されていません")
            
        if not gpt_config.get("instructions"):
            issues.append("指示文が空です")
            
        if len(gpt_config.get("instructions", "")) < 100:
            issues.append("指示文が短すぎます（100文字以上推奨）")
            
        if len(gpt_config.get("instructions", "")) > 8000:
            issues.append("指示文が長すぎます（8000文字以下推奨）")
            
        # 会話スターターチェック
        starters = gpt_config.get("conversation_starters", [])
        if len(starters) > 4:
            issues.append("会話スターターが多すぎます（4個まで）")
            
        if issues:
            self.logger.error("ビルド検証エラー:")
            for issue in issues:
                self.logger.error(f"  - {issue}")
            return False
            
        self.logger.info("ビルド検証完了")
        return True
        
    def build(self) -> bool:
        """ビルド実行"""
        try:
            self.logger.info("プロンプトビルド開始")
            
            # 設定読み込み
            config = self.load_build_config()
            
            # メインプロンプト構築
            main_prompt = self.build_main_prompt(config)
            
            # GPT設定作成
            gpt_config = self.create_gpt_config(config, main_prompt)
            
            # 検証
            if not self.validate_build(gpt_config):
                return False
                
            # ファイル出力
            # メインプロンプトをテキストファイルで出力
            with open(self.build_dir / "main_prompt.txt", 'w', encoding='utf-8') as f:
                f.write(main_prompt)
                
            # GPT設定をJSONで出力
            with open(self.build_dir / "gpt_config.json", 'w', encoding='utf-8') as f:
                json.dump(gpt_config, f, ensure_ascii=False, indent=2)
                
            # ビルド情報を出力
            build_info = {
                "build_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
                "prompt_length": len(main_prompt),
                "knowledge_files_count": len(gpt_config.get("knowledge_files", [])),
                "config": config
            }
            
            with open(self.build_dir / "build_info.json", 'w', encoding='utf-8') as f:
                json.dump(build_info, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"ビルド完了:")
            self.logger.info(f"  - プロンプト長: {len(main_prompt)} 文字")
            self.logger.info(f"  - ナレッジファイル: {len(gpt_config.get('knowledge_files', []))} 個")
            self.logger.info(f"  - 出力先: {self.build_dir}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"ビルドエラー: {e}")
            return False
            

def main():
    parser = argparse.ArgumentParser(description='カスタムGPTプロンプトビルダー')
    parser.add_argument('--project-root', default='.', help='プロジェクトルートディレクトリ')
    parser.add_argument('--clean', action='store_true', help='ビルド前にbuildディレクトリをクリア')
    
    args = parser.parse_args()
    
    builder = PromptBuilder(args.project_root)
    
    # クリーンビルドの場合
    if args.clean:
        import shutil
        if builder.build_dir.exists():
            shutil.rmtree(builder.build_dir)
            builder.build_dir.mkdir()
            
    success = builder.build()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
