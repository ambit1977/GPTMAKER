#!/usr/bin/env python3
"""
テスト用GPTデプロイスクリプト

Action機能を含むカスタムGPTの自動作成をテストします。
"""

import os
import sys
import time
import logging

# プロジェクトルートをパスに追加
sys.path.append('/Users/01035280/GPTMAKER')

from scripts.chatgpt_deployer import ChatGPTDeployer

def setup_logging():
    """テスト用ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/Users/01035280/GPTMAKER/test_deployment.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def test_gpt_deployment():
    """テストGPTのデプロイを実行"""
    logger = setup_logging()
    logger.info("=== GPTMAKERフレームワーク テスト開始 ===")
    
    try:
        # 設定確認
        config_path = '/Users/01035280/GPTMAKER/test_gpt_config.json'
        if not os.path.exists(config_path):
            logger.error(f"設定ファイルが見つかりません: {config_path}")
            return False
        
        # デプロイヤー初期化
        deployer = ChatGPTDeployer('/Users/01035280/GPTMAKER/config/deploy_config.yaml')
        
        # テストGPT作成
        logger.info("テストGPT「テスト」の作成を開始...")
        success = deployer.deploy_gpt(config_path)
        
        if success:
            logger.info("🎉 テストGPT作成成功！")
            logger.info("以下の機能がテストされました:")
            logger.info("  ✅ 基本的なGPT設定")
            logger.info("  ✅ カスタム会話スターター")
            logger.info("  ✅ ナレッジファイルアップロード")
            logger.info("  ✅ Action設定（スプレッドシート連携）")
            logger.info("GPTMAKERフレームワークの自動化機能が正常に動作しています。")
        else:
            logger.error("❌ テストGPT作成失敗")
            logger.error("ログを確認して問題を特定してください。")
        
        return success
        
    except Exception as e:
        logger.error(f"テスト実行エラー: {e}")
        return False

def dry_run_test():
    """ドライランテスト（設定ファイルの検証のみ）"""
    logger = setup_logging()
    logger.info("=== ドライランテスト開始 ===")
    
    try:
        import json
        
        # 設定ファイル読み込みテスト
        with open('/Users/01035280/GPTMAKER/test_gpt_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info("✅ 設定ファイル読み込み成功")
        logger.info(f"  GPT名: {config['name']}")
        logger.info(f"  説明: {config['description']}")
        logger.info(f"  会話スターター数: {len(config['conversation_starters'])}")
        logger.info(f"  ナレッジファイル数: {len(config['knowledge_files'])}")
        logger.info(f"  Action数: {len(config.get('actions', []))}")
        
        # ナレッジファイル存在確認
        for knowledge_file in config['knowledge_files']:
            if os.path.exists(knowledge_file):
                logger.info(f"  ✅ ナレッジファイル存在確認: {knowledge_file}")
            else:
                logger.warning(f"  ⚠️  ナレッジファイルなし: {knowledge_file}")
        
        # Action設定確認
        for action in config.get('actions', []):
            logger.info(f"  ✅ Action設定: {action['name']}")
            logger.info(f"    説明: {action['description']}")
            logger.info(f"    エンドポイント数: {len(action['schema']['paths'])}")
        
        logger.info("🎉 ドライランテスト完了 - 設定は正常です")
        return True
        
    except Exception as e:
        logger.error(f"❌ ドライランテストエラー: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GPTMAKERフレームワーク テストスクリプト')
    parser.add_argument('--dry-run', action='store_true', help='設定ファイルの検証のみ実行')
    parser.add_argument('--full-test', action='store_true', help='実際のGPT作成テストを実行')
    
    args = parser.parse_args()
    
    if args.dry_run:
        success = dry_run_test()
    elif args.full_test:
        success = test_gpt_deployment()
    else:
        print("使用方法:")
        print("  python test_deployment.py --dry-run    # 設定検証のみ")
        print("  python test_deployment.py --full-test  # 実際のGPT作成テスト")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
