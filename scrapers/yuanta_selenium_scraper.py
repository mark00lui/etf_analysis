#!/usr/bin/env python3
"""
元大ETF Selenium爬蟲 - 適合排程執行
使用Selenium模擬瀏覽器操作來下載Excel檔案
"""

import os
import time
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config.mongodb import get_mongodb_manager
from utils.logger import setup_logger

class YuantaSeleniumScraper:
    """元大ETF Selenium爬蟲"""
    
    def __init__(self, headless: bool = True):
        self.logger = setup_logger("yuanta_selenium", "logs/yuanta_selenium.log")
        self.download_dir = "downloads/yuanta"
        os.makedirs(self.download_dir, exist_ok=True)
        
        # MongoDB 連接
        self.mongodb = get_mongodb_manager()
        
        # 設定Chrome選項
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")  # 無頭模式，適合排程執行
        
        # 其他必要的選項
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # 設定下載目錄
        prefs = {
            "download.default_directory": os.path.abspath(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = None
    
    def setup_driver(self):
        """設定WebDriver"""
        try:
            # 自動下載並設定ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            
            # 設定隱式等待
            self.driver.implicitly_wait(10)
            
            self.logger.info("WebDriver設定成功")
            return True
            
        except Exception as e:
            self.logger.error(f"WebDriver設定失敗: {e}")
            return False
    
    def download_excel(self, etf_ticker: str, etf_name: str) -> Optional[str]:
        """使用Selenium下載Excel檔案"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return None
            
            # 構建頁面URL
            page_url = f"https://www.yuantaetfs.com/product/detail/{etf_ticker}/ratio"
            
            self.logger.info(f"開始下載 {etf_ticker} ({etf_name}) 的持股資料")
            
            # 訪問頁面
            self.driver.get(page_url)
            
            # 等待頁面載入
            time.sleep(3)
            
            # 尋找excelBtn view按鈕
            try:
                excel_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "excelBtn.view"))
                )
                
                self.logger.info("找到Excel下載按鈕")
                
                # 點擊下載按鈕
                excel_button.click()
                
                # 等待下載開始
                time.sleep(5)
                
                # 檢查下載目錄中的檔案
                downloaded_files = self._get_downloaded_files(etf_ticker)
                
                if downloaded_files:
                    # 找到最新的下載檔案
                    latest_file = max(downloaded_files, key=os.path.getctime)
                    self.logger.info(f"Excel檔案下載成功: {latest_file}")
                    return latest_file
                else:
                    self.logger.warning("未找到下載的檔案")
                    return None
                    
            except Exception as e:
                self.logger.error(f"點擊Excel下載按鈕失敗: {e}")
                return None
            
        except Exception as e:
            self.logger.error(f"下載 {etf_ticker} Excel檔案失敗: {e}")
            return None
    
    def _get_downloaded_files(self, etf_ticker: str) -> List[str]:
        """獲取下載的檔案列表"""
        try:
            files = []
            for filename in os.listdir(self.download_dir):
                if filename.startswith(etf_ticker) and filename.endswith('.xlsx'):
                    filepath = os.path.join(self.download_dir, filename)
                    files.append(filepath)
            return files
        except Exception as e:
            self.logger.error(f"獲取下載檔案列表失敗: {e}")
            return []
    
    def parse_excel_data(self, filepath: str, etf_ticker: str) -> Optional[Dict]:
        """解析Excel檔案內容"""
        try:
            self.logger.info(f"開始解析Excel檔案: {filepath}")
            
            # 嘗試讀取Excel檔案
            try:
                df = pd.read_excel(filepath, engine='openpyxl', skiprows=17)
            except Exception as e:
                self.logger.error(f"讀取Excel檔案失敗: {e}")
                return None
            
            # 分析資料結構
            self.logger.info(f"Excel檔案結構: {df.shape}")
            self.logger.info(f"欄位名稱: {list(df.columns)}")
            
            # 顯示前幾行資料
            self.logger.info(f"前5行資料:\n{df.head()}")
            
            # 根據實際資料結構來解析
            holdings_data = self._extract_holdings_data(df, etf_ticker)
            
            if holdings_data:
                self.logger.info(f"成功解析 {etf_ticker} 持股資料，共 {len(holdings_data)} 筆")
                return {
                    "etf_ticker": etf_ticker,
                    "parse_date": datetime.now().isoformat(),
                    "file_path": filepath,
                    "total_holdings": len(holdings_data),
                    "holdings": holdings_data
                }
            else:
                self.logger.warning(f"無法解析 {etf_ticker} 的持股資料")
                return None
                
        except Exception as e:
            self.logger.error(f"解析Excel檔案失敗: {e}")
            return None
    
    def _extract_holdings_data(self, df: pd.DataFrame, etf_ticker: str) -> List[Dict]:
        """從DataFrame中提取持股資料"""
        try:
            holdings = []
            
            # 重新命名欄位
            if len(df.columns) >= 4:
                df.columns = ['stock_code', 'stock_name', 'quantity', 'weight']
                self.logger.info("已重新命名欄位")
            
            # 提取持股資料
            for index, row in df.iterrows():
                try:
                    # 跳過標題行和空行
                    if pd.isna(row['stock_code']) or str(row['stock_code']).strip() == '':
                        continue
                    
                    # 檢查是否為股票代碼（4位數字）
                    stock_code = str(row['stock_code']).strip()
                    if not stock_code.isdigit() or len(stock_code) != 4:
                        continue
                    
                    stock_name = str(row['stock_name']).strip()
                    quantity = self._parse_number(row['quantity'])
                    weight = self._parse_percentage(row['weight'])
                    
                    # 驗證資料有效性
                    if (stock_code and 
                        stock_name and 
                        quantity > 0 and
                        weight > 0):
                        holding = {
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'quantity': quantity,
                            'weight': weight
                        }
                        holdings.append(holding)
                        
                except Exception as e:
                    self.logger.warning(f"解析第 {index} 行資料失敗: {e}")
                    continue
            
            return holdings
            
        except Exception as e:
            self.logger.error(f"提取持股資料失敗: {e}")
            return []
    
    def _parse_number(self, value) -> int:
        """解析數字值"""
        try:
            if pd.isna(value):
                return 0
            if isinstance(value, str):
                value = value.replace(',', '').replace(' ', '')
            return int(float(value))
        except:
            return 0
    
    def _parse_percentage(self, value) -> float:
        """解析百分比值"""
        try:
            if pd.isna(value):
                return 0.0
            if isinstance(value, str):
                value = value.replace('%', '').replace(' ', '')
            return float(value)
        except:
            return 0.0
    
    def save_to_mongodb(self, parsed_data: Dict) -> bool:
        """將解析後的資料儲存到MongoDB"""
        try:
            if not parsed_data or 'holdings' not in parsed_data:
                return False
            
            etf_ticker = parsed_data['etf_ticker']
            holdings = parsed_data['holdings']
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_timestamp = datetime.now()
            
            # 儲存到MongoDB
            collection = self.mongodb.holdings
            
            # 先刪除該ETF當天的舊資料
            collection.delete_many({
                "etf_ticker": etf_ticker,
                "date": current_date
            })
            
            # 插入新資料
            holdings_data = []
            for holding in holdings:
                holding_doc = {
                    "etf_ticker": etf_ticker,
                    "stock_code": holding['stock_code'],
                    "stock_name": holding['stock_name'],
                    "quantity": holding['quantity'],
                    "weight": holding['weight'],
                    "date": current_date,
                    "download_date": parsed_data['parse_date'],
                    "file_path": parsed_data['file_path'],
                    "created_at": current_timestamp,
                    "updated_at": current_timestamp
                }
                holdings_data.append(holding_doc)
            
            if holdings_data:
                result = collection.insert_many(holdings_data)
                self.logger.info(f"成功儲存 {etf_ticker} 持股資料到MongoDB，共 {len(result.inserted_ids)} 筆，日期: {current_date}")
                return True
            else:
                self.logger.warning(f"沒有 {etf_ticker} 的持股資料需要儲存")
                return False
                
        except Exception as e:
            self.logger.error(f"儲存到MongoDB失敗: {e}")
            return False
    
    def scrape_etf_holdings(self, etf_ticker: str, etf_name: str) -> bool:
        """完整的ETF持股爬取流程"""
        try:
            self.logger.info(f"開始爬取 {etf_ticker} ({etf_name}) 的持股資料")
            
            # 1. 下載Excel檔案
            excel_file = self.download_excel(etf_ticker, etf_name)
            if not excel_file:
                return False
            
            # 2. 解析Excel資料
            parsed_data = self.parse_excel_data(excel_file, etf_ticker)
            if not parsed_data:
                return False
            
            # 3. 儲存到MongoDB
            if self.save_to_mongodb(parsed_data):
                self.logger.info(f"{etf_ticker} 持股資料爬取完成")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"爬取 {etf_ticker} 持股資料失敗: {e}")
            return False
    
    def scrape_all_etfs(self) -> Dict[str, bool]:
        """爬取所有ETF的持股資料"""
        try:
            etfs = [
                {"ticker": "0050", "name": "元大台灣卓越50基金"},
                {"ticker": "0056", "name": "元大高股息"},
                {"ticker": "0061", "name": "元大寶滬深"},
                {"ticker": "00692", "name": "元大台灣50"},
                {"ticker": "00881", "name": "元大台灣50正2"},
                {"ticker": "00882", "name": "元大台灣50反1"},
            ]
            
            results = {}
            
            for etf in etfs:
                ticker = etf['ticker']
                name = etf['name']
                
                self.logger.info(f"開始爬取 {ticker} ({name})")
                
                success = self.scrape_etf_holdings(ticker, name)
                results[ticker] = success
                
                # 避免請求過於頻繁
                time.sleep(3)
            
            # 統計結果
            success_count = sum(results.values())
            total_count = len(results)
            
            self.logger.info(f"爬取完成: 成功 {success_count}/{total_count}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"爬取所有ETF失敗: {e}")
            return {}
    
    def close(self):
        """關閉WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver已關閉")
        except Exception as e:
            self.logger.error(f"關閉WebDriver失敗: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

def main():
    """主測試函數"""
    print("元大ETF Selenium爬蟲測試")
    print("請確保已安裝Chrome瀏覽器")
    
    # 使用上下文管理器確保資源正確釋放
    with YuantaSeleniumScraper(headless=False) as scraper:  # 測試時設為False
        # 測試單一ETF
        print("測試下載 0050 的持股資料...")
        success = scraper.scrape_etf_holdings("0050", "元大台灣卓越50基金")
        
        if success:
            print("✓ 0050 持股資料下載成功")
        else:
            print("✗ 0050 持股資料下載失敗")

if __name__ == "__main__":
    main()
