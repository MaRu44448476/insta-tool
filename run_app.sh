#!/bin/bash

echo "=========================================="
echo "  Instagram Trend Tool - Web App"
echo "=========================================="
echo ""

# 仮想環境をアクティベート（存在する場合）
if [ -f "venv/bin/activate" ]; then
    echo "🔧 仮想環境をアクティベート中..."
    source venv/bin/activate
fi

# Python実行
echo "🚀 Webアプリを起動中..."
python3 run_app.py

echo ""
echo "👋 アプリを終了しました"