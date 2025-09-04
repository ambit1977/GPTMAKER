#!/usr/bin/env python3
"""
ChatGPT カスタムGPT 自動デプロイスクリプト

このスクリプトはSeleniumを使用してChatGPTのWeb UIを自動操作し、
カスタムGPTの作成・更新を自動化します。
"""

import os
import time
import json
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, Optional
import logging

class ChatGPTDeployer:
    """ChatGPT カスタムGPT自動デプロイクラス"""
    
    def __init__(self, config_path: str = "config/deploy_config.yaml"):
        """
        初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        self.config = self._load_config(config_path)
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self._setup_logging()
        
    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルを読み込む"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"設定ファイルが見つかりません: {config_path}")
            raise
            
    def _setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/deployment.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _setup_driver(self):
        """Selenium WebDriverを設定"""
        chrome_options = Options()
        
        # ヘッドレスモードの設定
        if self.config.get('headless', False):
            chrome_options.add_argument('--headless')
            
        # その他のオプション
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Chromeドライバーのパス設定
        service = Service(self.config.get('chrome_driver_path', 'chromedriver'))
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        self.logger.info("WebDriver初期化完了")
        
    def login(self) -> bool:
        """ChatGPTにログイン"""
        try:
            self.logger.info("ChatGPTにログインを開始")
            self.driver.get("https://chatgpt.com/")
            
            # ログインボタンをクリック
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
            )
            login_button.click()
            
            # メールアドレス入力
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.send_keys(self.config['credentials']['email'])
            
            # 続行ボタンクリック
            continue_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
            continue_button.click()
            
            # パスワード入力
            password_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.send_keys(self.config['credentials']['password'])
            
            # ログインボタンクリック
            login_submit = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
            login_submit.click()
            
            # ログイン完了まで待機
            self.wait.until(EC.url_contains("chatgpt.com"))
            self.logger.info("ログイン完了")
            return True
            
        except TimeoutException:
            self.logger.error("ログインタイムアウト")
            return False
        except Exception as e:
            self.logger.error(f"ログインエラー: {e}")
            return False
            
    def navigate_to_gpt_builder(self) -> bool:
        """GPTビルダーページに移動"""
        try:
            self.logger.info("GPTビルダーに移動")
            
            # マイGPTsページに移動
            self.driver.get("https://chatgpt.com/gpts/mine")
            time.sleep(3)
            
            # 新しいGPTを作成ボタンをクリック
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
            )
            create_button.click()
            
            self.logger.info("GPTビルダー画面に移動完了")
            return True
            
        except Exception as e:
            self.logger.error(f"GPTビルダー移動エラー: {e}")
            return False
            
    def create_custom_gpt(self, gpt_config: Dict) -> bool:
        """カスタムGPTを作成"""
        try:
            self.logger.info(f"カスタムGPT作成開始: {gpt_config['name']}")
            
            # 設定タブに移動
            configure_tab = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Configure')]"))
            )
            configure_tab.click()
            
            # GPT名を入力
            name_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Name your GPT']"))
            )
            name_input.clear()
            name_input.send_keys(gpt_config['name'])
            
            # 説明を入力
            description_input = self.driver.find_element(
                By.XPATH, "//textarea[@placeholder='Describe what your GPT does']"
            )
            description_input.clear()
            description_input.send_keys(gpt_config['description'])
            
            # 指示文を入力
            instructions_input = self.driver.find_element(
                By.XPATH, "//textarea[@placeholder='What does this GPT do? How does it behave?']"
            )
            instructions_input.clear()
            instructions_input.send_keys(gpt_config['instructions'])
            
            # 会話スターターを追加
            if 'conversation_starters' in gpt_config:
                self._add_conversation_starters(gpt_config['conversation_starters'])
            
            # ナレッジファイルをアップロード
            if 'knowledge_files' in gpt_config:
                self._upload_knowledge_files(gpt_config['knowledge_files'])
            
            # 機能設定
            if 'capabilities' in gpt_config:
                self._configure_capabilities(gpt_config['capabilities'])
            
            # Action設定
            if 'actions' in gpt_config:
                self._configure_actions(gpt_config['actions'])
                
            self.logger.info("カスタムGPT設定完了")
            return True
            
        except Exception as e:
            self.logger.error(f"カスタムGPT作成エラー: {e}")
            return False
            
    def _add_conversation_starters(self, starters: list):
        """会話スターターを追加"""
        for i, starter in enumerate(starters[:4]):  # 最大4個まで
            try:
                starter_input = self.driver.find_element(
                    By.XPATH, f"//input[@placeholder='Add a conversation starter {i+1}']"
                )
                starter_input.clear()
                starter_input.send_keys(starter)
            except NoSuchElementException:
                self.logger.warning(f"会話スターター{i+1}の入力欄が見つかりません")
                
    def _upload_knowledge_files(self, files: list):
        """ナレッジファイルをアップロード"""
        try:
            # ナレッジセクションまでスクロール
            knowledge_section = self.driver.find_element(
                By.XPATH, "//h3[contains(text(), 'Knowledge')]"
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", knowledge_section)
            
            # ファイルアップロードボタンをクリック
            upload_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Upload files')]"
            )
            upload_button.click()
            
            # ファイル選択
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            
            for file_path in files:
                if os.path.exists(file_path):
                    file_input.send_keys(os.path.abspath(file_path))
                    time.sleep(2)  # アップロード完了まで待機
                    self.logger.info(f"ファイルアップロード完了: {file_path}")
                else:
                    self.logger.warning(f"ファイルが見つかりません: {file_path}")
                    
        except Exception as e:
            self.logger.error(f"ナレッジファイルアップロードエラー: {e}")
            
    def _configure_capabilities(self, capabilities: Dict):
        """機能設定"""
        capability_map = {
            'web_browsing': 'Web Browsing',
            'dalle': 'DALL·E Image Generation',
            'code_interpreter': 'Code Interpreter'
        }
        
        for capability, enabled in capabilities.items():
            if capability in capability_map:
                try:
                    checkbox = self.driver.find_element(
                        By.XPATH, f"//label[contains(text(), '{capability_map[capability]}')]/..//input[@type='checkbox']"
                    )
                    if enabled and not checkbox.is_selected():
                        checkbox.click()
                    elif not enabled and checkbox.is_selected():
                        checkbox.click()
                        
                except NoSuchElementException:
                    self.logger.warning(f"機能設定が見つかりません: {capability}")
                    
    def _configure_actions(self, actions: list):
        """Action設定"""
        try:
            # Actionsセクションまでスクロール
            actions_section = self.driver.find_element(
                By.XPATH, "//h3[contains(text(), 'Actions')]"
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", actions_section)
            
            for action in actions:
                self.logger.info(f"Action設定開始: {action.get('name', 'Unnamed Action')}")
                
                # Create new actionボタンをクリック
                create_action_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create new action')]"))
                )
                create_action_button.click()
                time.sleep(2)
                
                # Action名を入力
                if 'name' in action:
                    name_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Action name']"))
                    )
                    name_input.clear()
                    name_input.send_keys(action['name'])
                
                # Action説明を入力
                if 'description' in action:
                    description_input = self.driver.find_element(
                        By.XPATH, "//textarea[@placeholder='Action description']"
                    )
                    description_input.clear()
                    description_input.send_keys(action['description'])
                
                # スキーマを入力
                if 'schema' in action:
                    schema_textarea = self.driver.find_element(
                        By.XPATH, "//textarea[@placeholder='Schema']"
                    )
                    schema_textarea.clear()
                    schema_textarea.send_keys(json.dumps(action['schema'], indent=2))
                
                # Saveボタンをクリック
                save_action_button = self.driver.find_element(
                    By.XPATH, "//button[contains(text(), 'Save')]"
                )
                save_action_button.click()
                time.sleep(2)
                
                self.logger.info(f"Action設定完了: {action.get('name', 'Unnamed Action')}")
                
        except Exception as e:
            self.logger.error(f"Action設定エラー: {e}")
            # スクリーンショットを撮影（デバッグ用）
            try:
                self.driver.save_screenshot(f"action_error_{int(time.time())}.png")
            except:
                pass
                    
    def save_and_publish(self, visibility: str = "private") -> bool:
        """GPTを保存・公開"""
        try:
            # 保存ボタンをクリック
            save_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save')]"))
            )
            save_button.click()
            
            # 公開設定
            if visibility == "public":
                public_radio = self.driver.find_element(
                    By.XPATH, "//input[@value='public']"
                )
                public_radio.click()
            elif visibility == "link":
                link_radio = self.driver.find_element(
                    By.XPATH, "//input[@value='link']"
                )
                link_radio.click()
            # デフォルトはprivate
            
            # 確認ボタンをクリック
            confirm_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Confirm')]"
            )
            confirm_button.click()
            
            self.logger.info(f"GPT保存・公開完了 (可視性: {visibility})")
            return True
            
        except Exception as e:
            self.logger.error(f"保存・公開エラー: {e}")
            return False
            
    def deploy_gpt(self, gpt_config_path: str) -> bool:
        """GPTデプロイのメイン処理"""
        try:
            # GPT設定を読み込み
            with open(gpt_config_path, 'r', encoding='utf-8') as f:
                gpt_config = json.load(f)
            
            # ブラウザ起動
            self._setup_driver()
            
            # ログイン
            if not self.login():
                return False
                
            # GPTビルダーに移動
            if not self.navigate_to_gpt_builder():
                return False
                
            # GPT作成
            if not self.create_custom_gpt(gpt_config):
                return False
                
            # 保存・公開
            if not self.save_and_publish(gpt_config.get('visibility', 'private')):
                return False
                
            self.logger.info("GPTデプロイ完了")
            return True
            
        except Exception as e:
            self.logger.error(f"デプロイエラー: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()
                
    def update_gpt(self, gpt_name: str, gpt_config_path: str) -> bool:
        """既存GPTの更新"""
        try:
            self.logger.info(f"GPT更新開始: {gpt_name}")
            
            # GPT設定を読み込み
            with open(gpt_config_path, 'r', encoding='utf-8') as f:
                gpt_config = json.load(f)
            
            # ブラウザ起動
            self._setup_driver()
            
            # ログイン
            if not self.login():
                return False
                
            # マイGPTsページに移動
            self.driver.get("https://chatgpt.com/gpts/mine")
            time.sleep(3)
            
            # 既存GPTを検索して編集
            gpt_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{gpt_name}')]"))
            )
            gpt_link.click()
            
            # 編集ボタンをクリック
            edit_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit')]"))
            )
            edit_button.click()
            
            # GPT設定を更新
            if not self.create_custom_gpt(gpt_config):
                return False
                
            # 保存
            if not self.save_and_publish(gpt_config.get('visibility', 'private')):
                return False
                
            self.logger.info("GPT更新完了")
            return True
            
        except Exception as e:
            self.logger.error(f"GPT更新エラー: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ChatGPT カスタムGPT自動デプロイツール')
    parser.add_argument('--config', required=True, help='GPT設定ファイルのパス')
    parser.add_argument('--action', choices=['create', 'update'], default='create', help='実行アクション')
    parser.add_argument('--name', help='更新対象のGPT名（updateの場合必須）')
    
    args = parser.parse_args()
    
    deployer = ChatGPTDeployer()
    
    if args.action == 'create':
        success = deployer.deploy_gpt(args.config)
    else:
        if not args.name:
            print("Error: --name は update アクションで必須です")
            exit(1)
        success = deployer.update_gpt(args.name, args.config)
    
    exit(0 if success else 1)
