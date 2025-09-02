# ETF爬蟲排程執行說明

## 🎯 概述

本專案提供多種排程執行方案，可以自動化ETF持股資料的爬取和儲存。

## 🚀 推薦方案：Selenium爬蟲

### 優點
- ✅ 完全模擬瀏覽器操作
- ✅ 可以處理JavaScript渲染的頁面
- ✅ 支援點擊下載按鈕
- ✅ 適合排程執行

### 缺點
- ⚠️ 需要安裝Chrome瀏覽器
- ⚠️ 資源消耗較高
- ⚠️ 執行速度較慢

## 📋 安裝需求

### 1. 安裝Python套件
```bash
pip install -r requirements.txt
```

### 2. 安裝Chrome瀏覽器
- Windows: 下載並安裝 [Google Chrome](https://www.google.com/chrome/)
- Linux: `sudo apt-get install google-chrome-stable`
- macOS: 下載並安裝 [Google Chrome](https://www.google.com/chrome/)

### 3. 確認MongoDB服務運行
```bash
# Windows
net start MongoDB

# Linux/macOS
sudo systemctl start mongod
```

## ⏰ 排程執行方法

### 方法1: Windows Task Scheduler

#### 步驟1: 建立批次檔案
建立 `run_etf_scraper.bat`：
```batch
@echo off
cd /d "D:\github\etf_analysis"
python scheduled_etf_scraper.py
```

#### 步驟2: 設定Task Scheduler
1. 開啟「工作排程器」
2. 建立基本工作
3. 設定觸發器（例如：每天21:00）
4. 設定動作：啟動程式
5. 程式路徑：`D:\github\etf_analysis\run_etf_scraper.bat`

### 方法2: Linux/macOS cron

#### 編輯crontab
```bash
crontab -e
```

#### 添加排程任務
```bash
# 每天21:00執行
0 21 * * * cd /path/to/etf_analysis && python scheduled_etf_scraper.py

# 每小時執行
0 * * * * cd /path/to/etf_analysis && python scheduled_etf_scraper.py
```

### 方法3: Docker容器

#### 建立Dockerfile
```dockerfile
FROM python:3.9-slim

# 安裝Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 複製專案檔案
COPY . /app
WORKDIR /app

# 安裝Python套件
RUN pip install -r requirements.txt

# 設定時區
ENV TZ=Asia/Taipei

# 執行爬蟲
CMD ["python", "scheduled_etf_scraper.py"]
```

#### 建立docker-compose.yml
```yaml
version: '3.8'
services:
  etf-scraper:
    build: .
    volumes:
      - ./downloads:/app/downloads
      - ./logs:/app/logs
    environment:
      - MONGODB_URI=mongodb://host.docker.internal:27017/
      - MONGODB_DB=etf_analysis
    restart: unless-stopped
```

### 方法4: Python schedule套件

#### 建立schedule_runner.py
```python
#!/usr/bin/env python3
import schedule
import time
from scheduled_etf_scraper import main

# 設定排程
schedule.every().day.at("21:00").do(main)
schedule.every().hour.do(main)  # 每小時執行

# 執行排程
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🔧 配置選項

### 環境變數設定
在 `.env` 檔案中設定：
```bash
# MongoDB設定
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=etf_analysis

# 爬蟲設定
SCRAPER_TIMEOUT=30
SCRAPER_RETRY_TIMES=3
SCRAPER_DELAY=2

# 日誌設定
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/
```

### 爬蟲參數調整
在 `scheduled_etf_scraper.py` 中調整：
```python
# 無頭模式（適合排程執行）
with YuantaSeleniumScraper(headless=True) as scraper:

# 有頭模式（適合測試）
with YuantaSeleniumScraper(headless=False) as scraper:
```

## 📊 監控和日誌

### 日誌檔案
- 位置：`logs/scheduled_scraper_YYYYMMDD.log`
- 格式：包含時間戳記、執行狀態、錯誤訊息

### 執行狀態檢查
```bash
# 檢查今天的日誌
tail -f logs/scheduled_scraper_$(date +%Y%m%d).log

# 檢查MongoDB中的資料
python -c "from config.mongodb import get_mongodb_manager; m=get_mongodb_manager(); print(f'總資料量: {m.holdings.count_documents({})}')"
```

## 🚨 故障排除

### 常見問題

#### 1. Chrome瀏覽器未安裝
```bash
# 錯誤訊息：Chrome not found
# 解決方案：安裝Google Chrome瀏覽器
```

#### 2. ChromeDriver版本不匹配
```bash
# 錯誤訊息：ChromeDriver version mismatch
# 解決方案：webdriver-manager會自動處理
```

#### 3. MongoDB連接失敗
```bash
# 錯誤訊息：Connection refused
# 解決方案：檢查MongoDB服務狀態
```

#### 4. 記憶體不足
```bash
# 錯誤訊息：Out of memory
# 解決方案：增加系統記憶體或調整Chrome選項
```

### 調試模式
```python
# 在scheduled_etf_scraper.py中設定
with YuantaSeleniumScraper(headless=False) as scraper:  # 設為False
```

## 📈 性能優化

### 1. 並行執行
```python
import concurrent.futures

def scrape_etf_parallel(etfs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(scraper.scrape_etf_holdings, etf['ticker'], etf['name']): etf for etf in etfs}
        for future in concurrent.futures.as_completed(futures):
            etf = futures[future]
            try:
                result = future.result()
                print(f"{etf['ticker']}: {'成功' if result else '失敗'}")
            except Exception as e:
                print(f"{etf['ticker']}: 錯誤 - {e}")
```

### 2. 資源清理
```python
# 定期清理舊的日誌和檔案
import os
from datetime import datetime, timedelta

def cleanup_old_files():
    cutoff_date = datetime.now() - timedelta(days=30)
    
    # 清理舊日誌
    for log_file in os.listdir('logs'):
        if log_file.startswith('scheduled_scraper_'):
            file_path = os.path.join('logs', log_file)
            if os.path.getctime(file_path) < cutoff_date.timestamp():
                os.remove(file_path)
```

## 🔒 安全性考慮

### 1. 網路安全
- 使用HTTPS連接
- 設定適當的防火牆規則
- 限制網路訪問權限

### 2. 資料安全
- 定期備份MongoDB資料
- 設定資料庫存取權限
- 加密敏感資訊

### 3. 系統安全
- 定期更新系統和套件
- 監控系統資源使用
- 設定錯誤通知機制

## 📞 支援和聯絡

如果遇到問題，請檢查：
1. 日誌檔案中的錯誤訊息
2. 系統資源使用狀況
3. 網路連接狀態
4. MongoDB服務狀態

## 🎉 總結

使用Selenium爬蟲是最可靠的排程執行方案，可以：
- 自動化ETF資料爬取
- 處理JavaScript渲染的頁面
- 支援多種排程方式
- 提供完整的日誌和監控

建議在生產環境中使用無頭模式，並設定適當的錯誤處理和通知機制。
