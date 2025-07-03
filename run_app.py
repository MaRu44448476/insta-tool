#!/usr/bin/env python3
"""
Instagram Trend Tool - Web App Launcher
Streamlitアプリを起動するためのスクリプト
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """必要なパッケージがインストールされているかチェック"""
    try:
        import streamlit
        import pandas
        import instaloader
        return True
    except ImportError as e:
        print(f"❌ 必要なパッケージが不足しています: {e}")
        print("📦 以下のコマンドで依存関係をインストールしてください:")
        print("pip install -r requirements-streamlit.txt")
        return False

def main():
    """メイン実行関数"""
    print("🚀 Instagram Trend Tool - Web App")
    print("=" * 50)
    
    # 現在のディレクトリを確認
    current_dir = Path.cwd()
    app_file = current_dir / "app.py"
    
    if not app_file.exists():
        print("❌ app.py が見つかりません")
        print("このスクリプトはInstagram Trend Toolのルートディレクトリで実行してください")
        return 1
    
    # 依存関係チェック
    if not check_requirements():
        return 1
    
    print("✅ 依存関係チェック完了")
    print("🌐 Webアプリを起動します...")
    print("")
    print("📱 スマホからもアクセス可能！")
    print("🔗 ブラウザで自動的に開きます")
    print("")
    print("⚠️  終了するには Ctrl+C を押してください")
    print("=" * 50)
    
    try:
        # Streamlitアプリを起動
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",  # 外部からアクセス可能
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 アプリを終了しました")
        return 0
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())