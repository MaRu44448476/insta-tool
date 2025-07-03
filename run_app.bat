@echo off
title Instagram Trend Tool - Web App
echo.
echo ==========================================
echo   Instagram Trend Tool - Web App
echo ==========================================
echo.

REM 仮想環境をアクティベート（存在する場合）
if exist "venv\Scripts\activate.bat" (
    echo 🔧 仮想環境をアクティベート中...
    call venv\Scripts\activate.bat
)

REM Python実行
echo 🚀 Webアプリを起動中...
python run_app.py

echo.
echo 👋 アプリを終了しました
pause