# 元大ETF爬蟲定時執行器使用說明

## 概述
本專案提供多種方式來設定元大ETF爬蟲的定時執行，讓您可以自動化數據抓取流程。爬蟲已內建完整的重試機制，大幅提高成功率。

## 安裝必要套件

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1: 使用啟動腳本 (推薦新手)
```bash
# Windows
start_scheduler.bat

# 或直接雙擊 start_scheduler.bat 文件
```

### 方法2: Windows工作排程器 (推薦)
```bash
# 執行設定腳本
setup_scheduler.bat

# 或手動設定
schtasks /create /tn "YuantaETFScraper" /tr "python \"%cd%\yuanta_etf_scraper.py\"" /sc daily /st 09:00 /f
```

### 方法3: 使用schedule庫 (簡單版)
```bash
python scheduler.py
```

**特點:**
- 簡單易用
- 每日上午9:00執行
- 內建重試機制
- 適合基本需求

### 方法4: 使用APScheduler (進階版)
```bash
python advanced_scheduler.py
```

**特點:**
- 功能豐富
- 支援多種排程選項
- 可設定多個執行時間
- 內建重試機制
- 適合複雜需求

## 排程選項

### 基本排程
- **每日執行**: 每天上午9:00
- **每週執行**: 每週一上午9:00
- **工作日執行**: 每週一、三、五上午9:00

### 進階排程 (APScheduler)
- **Cron表達式**: 支援複雜的時間設定
- **間隔執行**: 每N小時/分鐘執行
- **多任務**: 同時設定多個執行時間

## 日誌文件
所有排程器的執行記錄都會保存在 `logs/` 目錄下：
- `scheduler.log` - schedule版排程器日誌
- `advanced_scheduler.log` - APScheduler版排程器日誌
- `yuanta_scraper.log` - 爬蟲執行日誌

## 管理排程任務

### Windows工作排程器
```bash
# 查看任務
schtasks /query /tn "YuantaETFScraper"

# 修改執行時間
schtasks /change /tn "YuantaETFScraper" /st 10:00

# 刪除任務
schtasks /delete /tn "YuantaETFScraper" /f
```

### 停止Python排程器
- 按 `Ctrl+C` 停止正在運行的排程器

## 故障排除

### 常見問題

1. **Python未找到**
   - 確保Python已正確安裝並加入PATH
   - 檢查 `python --version` 命令是否正常

2. **套件未安裝**
   - 執行 `pip install -r requirements.txt`
   - 確保網路連接正常

3. **權限問題**
   - 以管理員身份運行命令提示字元
   - 檢查文件寫入權限

4. **Chrome驅動問題**
   - 確保Chrome瀏覽器已安裝
   - 檢查ChromeDriver版本兼容性

### 日誌檢查
```bash
# 查看最新日誌
tail -f logs/scheduler.log
tail -f logs/yuanta_scraper.log
```

## 自定義設定

### 修改執行時間
編輯對應的Python文件，修改時間設定：

```python
# schedule版
schedule.every().day.at("10:00").do(self.run_scraper)  # 改為上午10:00

# APScheduler版
self.scheduler.add_job(
    func=self.run_scraper,
    trigger=CronTrigger(hour=10, minute=0),  # 改為上午10:00
    id='daily_10am',
    name='每日上午10:00執行ETF爬蟲'
)
```

### 添加新的排程
在 `advanced_scheduler.py` 中添加新的排程任務：

```python
# 每週二、四下午2:00執行
self.scheduler.add_job(
    func=self.run_scraper,
    trigger=CronTrigger(day_of_week='tue,thu', hour=14, minute=0),
    id='tue_thu_2pm',
    name='每週二、四下午2:00執行ETF爬蟲'
)
```

## 重試機制

### 自動重試功能
- **最大重試次數**: 3次 (可調整)
- **重試間隔**: 5秒 (可調整)
- **隨機延遲**: 避免被檢測為機器人
- **智能錯誤處理**: 區分不同錯誤類型
- **統計追蹤**: 記錄重試次數和成功率

### 重試效果
- 大幅提高成功率
- 自動處理網路不穩定
- 智能處理頁面載入問題
- 詳細的錯誤日誌

## 注意事項

1. **網路連接**: 確保執行時有穩定的網路連接
2. **系統資源**: 爬蟲會使用Chrome瀏覽器，確保有足夠的系統資源
3. **磁碟空間**: 確保有足夠的磁碟空間存儲下載的CSV文件
4. **MongoDB**: 確保MongoDB服務正在運行
5. **防火牆**: 確保防火牆不會阻擋爬蟲的網路請求
6. **重試機制**: 爬蟲已內建重試機制，無需額外設定

## 支援

如有問題，請檢查日誌文件或聯繫開發團隊。
