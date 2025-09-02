# ETF 持股分析爬蟲系統

這是一個用於爬取台灣六大ETF發行商持股資料的自動化系統。

## 支援的發行商

- 元大投信 (Yuanta)
- 國泰投信 (Cathay)
- 中信投信 (CTBC)
- 群益投信 (Capital)
- 富邦投信 (Fubon)
- 復華投信 (FHTrust)

## 功能特色

- 自動爬取各發行商ETF持股資料
- 支援多種資料來源 (網頁表格、API)
- 自動資料清理和驗證
- 儲存到 Supabase 雲端資料庫
- 完整的日誌記錄
- 可排程執行

## 安裝需求

```bash
pip install -r requirements.txt
```

## 環境設定

1. 複製 `env_example.txt` 為 `.env`
2. 填入您的 Supabase 設定：
   ```
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   ```

## 使用方法

### 1. 手動執行爬蟲

```bash
python scraper_manager.py
```

### 2. 啟動排程服務

```bash
python scheduler.py
```

### 3. 測試單一發行商

```python
from scrapers import YuantaScraper

scraper = YuantaScraper()
results = scraper.scrape_all()
print(results)
```

## 專案結構

```
etf_analysis/
├── scrapers/                 # 爬蟲模組
│   ├── base_scraper.py      # 基礎爬蟲類別
│   ├── yuanta_scraper.py    # 元大爬蟲
│   ├── cathay_scraper.py    # 國泰爬蟲
│   ├── ctbc_scraper.py      # 中信爬蟲
│   ├── capital_scraper.py   # 群益爬蟲
│   ├── fubon_scraper.py     # 富邦爬蟲
│   └── fhtrust_scraper.py   # 復華爬蟲
├── config/                  # 設定檔
│   ├── database.py         # 資料庫設定
│   └── scraper_config.py   # 爬蟲設定
├── utils/                   # 工具模組
│   └── logger.py           # 日誌工具
├── logs/                    # 日誌檔案
├── scraper_manager.py       # 爬蟲管理器
├── scheduler.py             # 排程服務
├── requirements.txt         # 依賴套件
└── README.md               # 說明文件
```

## 資料庫結構

### ETFs 表格
- `ticker`: ETF代碼
- `name`: ETF名稱
- `issuer`: 發行商
- `created_at`: 建立時間
- `updated_at`: 更新時間

### Holdings 表格
- `etf_ticker`: ETF代碼
- `stock_code`: 股票代碼
- `stock_name`: 股票名稱
- `weight`: 權重 (%)
- `shares`: 持股數量
- `market_value`: 市值
- `date`: 資料日期
- `created_at`: 建立時間

## 注意事項

1. **遵守網站規範**: 請遵守各發行商網站的robots.txt和使用條款
2. **請求頻率**: 系統已設定適當的請求延遲，避免對伺服器造成負擔
3. **資料準確性**: 爬取的資料僅供參考，實際投資請以官方公告為準
4. **錯誤處理**: 系統包含完整的錯誤處理和重試機制

## 授權

本專案僅供學習和研究使用，請勿用於商業用途。

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案。
