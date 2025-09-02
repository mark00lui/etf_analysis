# MongoDB 資料庫整合說明

## 概述

本專案已整合 MongoDB 作為本地資料庫，用於儲存 ETF 持股資料和爬蟲日誌。

## 安裝需求

### 1. 安裝 MongoDB 套件
```bash
pip install pymongo dnspython
```

### 2. 啟動 MongoDB 服務

#### Windows
```bash
# 如果已安裝 MongoDB 服務
net start MongoDB

# 或者手動啟動
"C:\Program Files\MongoDB\Server\{version}\bin\mongod.exe"
```

#### macOS (使用 Homebrew)
```bash
# 安裝 MongoDB
brew tap mongodb/brew
brew install mongodb-community

# 啟動服務
brew services start mongodb/brew/mongodb-community
```

#### Linux (Ubuntu/Debian)
```bash
# 安裝 MongoDB
sudo apt update
sudo apt install mongodb

# 啟動服務
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

## 連接設定

### 環境變數設定
複製 `env_example.txt` 為 `.env` 並設定：

```bash
# MongoDB 設定
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=etf_analysis
```

### 預設連接
- **主機**: localhost
- **埠號**: 27017
- **資料庫**: etf_analysis
- **認證**: 無 (本地開發環境)

## 資料庫結構

### 集合 (Collections)

#### 1. `etfs` - ETF 基本資料
```json
{
  "ticker": "0056",
  "name": "元大高股息",
  "issuer": "元大投信",
  "description": "追蹤台灣高股息指數",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

#### 2. `holdings` - 持股資料
```json
{
  "etf_ticker": "0056",
  "date": "2024-01-15",
  "stock_code": "2330",
  "stock_name": "台積電",
  "weight": 5.5,
  "shares": 1000,
  "market_value": 500000,
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### 3. `scraper_logs` - 爬蟲日誌
```json
{
  "issuer": "元大投信",
  "action": "scrape_etf_list",
  "details": {
    "etf_count": 25,
    "status": "success"
  },
  "timestamp": "2024-01-15T10:00:00Z",
  "status": "success"
}
```

### 索引 (Indexes)
- `etfs.ticker` - 唯一索引
- `etfs.issuer` - 普通索引
- `holdings.etf_ticker + date` - 複合索引
- `holdings.stock_code` - 普通索引
- `scraper_logs.timestamp` - 普通索引

## 使用方法

### 1. 基本連接
```python
from config.mongodb import get_mongodb_manager

# 取得 MongoDB 管理器
mongodb = get_mongodb_manager()

# 測試連接
if mongodb.test_connection():
    print("連接成功")
```

### 2. ETF 資料操作
```python
from models.etf_data import ETFDataManager

etf_manager = ETFDataManager()

# 儲存 ETF 資料
etf_data = {
    "ticker": "0056",
    "name": "元大高股息",
    "issuer": "元大投信"
}
etf_manager.save_etf(etf_data)

# 查詢 ETF 資料
etf = etf_manager.get_etf("0056")
```

### 3. 持股資料操作
```python
# 儲存持股資料
holdings = [
    {"stock_code": "2330", "stock_name": "台積電", "weight": 5.5},
    {"stock_code": "2317", "stock_name": "鴻海", "weight": 3.2}
]
etf_manager.save_holdings("0056", holdings, "2024-01-15")

# 查詢持股資料
holdings = etf_manager.get_holdings("0056", "2024-01-15")
```

## 測試連接

### 1. 簡單測試
```bash
python simple_mongodb_test.py
```

### 2. 完整功能測試
```bash
python test_mongodb.py
```

## 常見問題

### 1. 連接失敗
- 確認 MongoDB 服務是否啟動
- 檢查埠號 27017 是否被佔用
- 確認防火牆設定

### 2. 權限問題
- 本地開發環境通常不需要認證
- 如果設定認證，請在連接字串中加入使用者名稱和密碼

### 3. 版本相容性
- 建議使用 MongoDB 4.4+ 版本
- pymongo 4.6.0 支援 MongoDB 4.0+

## 性能優化

### 1. 索引策略
- 已建立必要的索引以提升查詢效能
- 根據查詢模式可調整索引策略

### 2. 批量操作
- 支援批量插入和更新
- 減少網路往返次數

### 3. 連接池
- 使用連接池管理連接
- 自動處理連接的生命週期

## 監控和維護

### 1. 日誌記錄
- 所有操作都有詳細的日誌記錄
- 日誌檔案位於 `logs/` 目錄

### 2. 資料庫統計
```python
# 取得資料庫資訊
db_info = mongodb.get_database_info()
print(f"資料大小: {db_info['total_size']} bytes")
print(f"集合數量: {len(db_info['collections'])}")
```

### 3. 定期備份
- 建議定期備份 MongoDB 資料
- 可使用 `mongodump` 工具進行備份

## 下一步

1. 執行測試腳本確認連接正常
2. 整合到爬蟲系統中
3. 根據實際需求調整資料結構
4. 設定定期備份策略
