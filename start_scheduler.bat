@echo off
title 元大ETF爬蟲定時執行器
echo ========================================
echo    元大ETF爬蟲定時執行器
echo ========================================
echo.

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到Python，請先安裝Python
    pause
    exit /b 1
)

REM 檢查必要套件
echo 🔍 檢查必要套件...
python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo 📦 安裝schedule套件...
    pip install schedule
)

python -c "import apscheduler" >nul 2>&1
if errorlevel 1 (
    echo 📦 安裝APScheduler套件...
    pip install apscheduler
)

echo ✅ 套件檢查完成
echo.

REM 選擇執行方式
echo 請選擇執行方式:
echo 1. 使用schedule庫 (簡單版)
echo 2. 使用APScheduler (進階版)
echo 3. 設定Windows工作排程器
echo 4. 手動執行一次 (帶重試機制)
echo.

set /p choice="請輸入選項 (1-4): "

if "%choice%"=="1" (
    echo 🚀 啟動schedule版排程器...
    python scheduler.py
) else if "%choice%"=="2" (
    echo 🚀 啟動APScheduler版排程器...
    python advanced_scheduler.py
) else if "%choice%"=="3" (
    echo 🔧 設定Windows工作排程器...
    call setup_scheduler.bat
) else if "%choice%"=="4" (
    echo 🏃 手動執行爬蟲 (帶重試機制)...
    python yuanta_etf_scraper.py
) else (
    echo ❌ 無效選項
)

echo.
pause
