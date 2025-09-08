#!/usr/bin/env python3
"""
元大ETF統一抓取系統
支持所有元大ETF產品的數據抓取和入庫
"""

import os
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from models.etf_data import ETFDataManager
from utils.logger import setup_logger

class YuantaETFScraper:
    """元大ETF抓取器"""
    
    def __init__(self):
        self.logger = setup_logger("yuanta_scraper", "logs/yuanta_scraper.log")
        self.etf_manager = ETFDataManager()
        self.download_dir = os.path.join(os.getcwd(), "downloads", "yuanta")
        
        # 確保下載目錄存在
        os.makedirs(self.download_dir, exist_ok=True)
        
        # 元大ETF列表
        self.etf_list = [
            "0050", "0051", "0053", "0055", "0056", 
            "006201", "006203", "00713", "00850", "00940"
        ]
        
        # 基礎URL模板
        self.base_url = "https://www.yuantaetfs.com/product/detail/{}/ratio"
    
    def setup_chrome_driver(self):
        """設置Chrome瀏覽器驅動"""
        chrome_options = Options()
        
        # 性能優化選項
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--window-size=1280,720")
        
        # 設置下載目錄
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "profile.default_content_setting_values": {
                "images": 2,
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "media_stream": 2,
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 禁用日誌
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(5)
            return driver
        except Exception as e:
            self.logger.error(f"無法啟動Chrome驅動: {e}")
            return None
    
    def extract_date_from_csv(self, lines):
        """從CSV第一行提取日期"""
        try:
            if lines and len(lines) > 0:
                first_line = lines[0].strip()
                date_pattern = r'(\d{4}/\d{1,2}/\d{1,2})'
                match = re.search(date_pattern, first_line)
                if match:
                    date_str = match.group(1)
                    date_obj = datetime.strptime(date_str, '%Y/%m/%d')
                    return date_obj.strftime('%Y-%m-%d')
            return None
        except Exception as e:
            self.logger.error(f"提取日期時發生錯誤: {e}")
            return None
    
    def download_etf_data(self, etf_code):
        """下載單一ETF的數據"""
        url = self.base_url.format(etf_code)
        
        self.logger.info(f"開始下載ETF {etf_code} 數據")
        
        driver = self.setup_chrome_driver()
        if not driver:
            return False
        
        try:
            # 訪問頁面
            self.logger.info(f"正在訪問: {url}")
            driver.get(url)
            
            # 等待頁面加載
            wait = WebDriverWait(driver, 10)
            
            # 尋找「匯出excel」按鈕
            excel_button_selectors = [
                "//span[contains(text(), '匯出excel')]",
                "//button[contains(text(), '匯出excel')]",
                "//a[contains(text(), '匯出excel')]",
                "//div[contains(text(), '匯出excel')]",
            ]
            
            excel_button = None
            for selector in excel_button_selectors:
                try:
                    excel_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    self.logger.info(f"找到按鈕: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not excel_button:
                self.logger.warning(f"未找到「匯出excel」按鈕: {etf_code}")
                return False
            
            # 記錄下載前的文件列表
            files_before = set(os.listdir(self.download_dir))
            
            # 點擊按鈕
            driver.execute_script("arguments[0].click();", excel_button)
            
            # 等待下載完成
            max_wait_time = 30
            check_interval = 1
            waited_time = 0
            
            while waited_time < max_wait_time:
                time.sleep(check_interval)
                waited_time += check_interval
                
                files_after = set(os.listdir(self.download_dir))
                new_files = files_after - files_before
                
                if new_files:
                    self.logger.info(f"ETF {etf_code} 下載完成，新文件: {new_files}")
                    return True
                
                if waited_time % 5 == 0:
                    self.logger.info(f"等待下載中... ({waited_time}/{max_wait_time}秒)")
            
            self.logger.warning(f"ETF {etf_code} 下載超時")
            return False
            
        except Exception as e:
            self.logger.error(f"下載ETF {etf_code} 時發生錯誤: {e}")
            return False
        finally:
            driver.quit()
    
    def analyze_csv_file(self, file_path, etf_code):
        """分析CSV文件並提取數據"""
        try:
            self.logger.info(f"分析文件: {file_path}")
            
            # 讀取文件內容
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 提取日期
            date = self.extract_date_from_csv(lines)
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            self.logger.info(f"提取到日期: {date}")
            
            # 尋找股票數據表格
            stock_data_start = None
            for i, line in enumerate(lines):
                if '商品代碼,商品名稱,商品數量,商品權重' in line:
                    stock_data_start = i
                    break
            
            if stock_data_start is None:
                self.logger.warning(f"未找到股票數據表格: {etf_code}")
                return False
            
            # 提取股票數據
            stock_lines = []
            for i in range(stock_data_start + 1, len(lines)):
                line = lines[i].strip()
                if line and ',' in line and not line.startswith('期貨'):
                    parts = line.split(',')
                    if len(parts) >= 4 and parts[0].isdigit():
                        stock_lines.append(line)
                    elif '期貨' in line:
                        break
            
            if not stock_lines:
                self.logger.warning(f"未找到股票數據: {etf_code}")
                return False
            
            # 準備持股數據
            holdings = []
            for line in stock_lines:
                parts = line.split(',')
                if len(parts) >= 4:
                    holding = {
                        'stock_code': parts[0],
                        'stock_name': parts[1],
                        'shares': int(parts[2]) if parts[2].isdigit() else 0,
                        'weight': float(parts[3])
                    }
                    holdings.append(holding)
            
            # 檢查重複數據
            duplicate_check = self.etf_manager.check_duplicate_holdings(etf_code, holdings, date)
            self.logger.info(f"ETF {etf_code} 重複檢查: {duplicate_check['message']}")
            
            if duplicate_check['is_duplicate']:
                self.logger.info(f"ETF {etf_code} 數據重複，跳過保存")
                return True
            
            # 保存到MongoDB
            success = self.etf_manager.save_holdings(etf_code, holdings, date)
            
            if success:
                self.logger.info(f"ETF {etf_code} 數據保存成功: {len(holdings)} 筆持股數據")
                return True
            else:
                self.logger.error(f"ETF {etf_code} 數據保存失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"分析ETF {etf_code} 文件時發生錯誤: {e}")
            return False
    
    def scrape_all_etfs(self):
        """抓取所有ETF數據"""
        self.logger.info("開始抓取所有元大ETF數據")
        
        results = {}
        total_start_time = time.time()
        
        for i, etf_code in enumerate(self.etf_list, 1):
            self.logger.info(f"處理ETF {etf_code} ({i}/{len(self.etf_list)})")
            
            etf_start_time = time.time()
            
            # 下載數據
            download_success = self.download_etf_data(etf_code)
            
            if download_success:
                # 找到最新下載的文件
                files = os.listdir(self.download_dir)
                csv_files = [f for f in files if f.endswith('.csv')]
                
                if csv_files:
                    latest_file = max([os.path.join(self.download_dir, f) for f in csv_files], 
                                     key=os.path.getctime)
                    
                    # 分析文件
                    analysis_success = self.analyze_csv_file(latest_file, etf_code)
                    
                    if analysis_success:
                        results[etf_code] = "成功"
                        self.logger.info(f"ETF {etf_code} 處理完成")
                    else:
                        results[etf_code] = "分析失敗"
                        self.logger.error(f"ETF {etf_code} 分析失敗")
                else:
                    results[etf_code] = "文件未找到"
                    self.logger.error(f"ETF {etf_code} 下載文件未找到")
            else:
                results[etf_code] = "下載失敗"
                self.logger.error(f"ETF {etf_code} 下載失敗")
            
            etf_time = time.time() - etf_start_time
            self.logger.info(f"ETF {etf_code} 處理耗時: {etf_time:.2f}秒")
            
            # 避免請求過於頻繁
            if i < len(self.etf_list):
                time.sleep(2)
        
        total_time = time.time() - total_start_time
        
        # 輸出結果摘要
        self.logger.info("=" * 60)
        self.logger.info("抓取結果摘要")
        self.logger.info("=" * 60)
        
        success_count = sum(1 for status in results.values() if status == "成功")
        
        for etf_code, status in results.items():
            self.logger.info(f"ETF {etf_code}: {status}")
        
        self.logger.info(f"總耗時: {total_time:.2f}秒")
        self.logger.info(f"成功: {success_count}/{len(self.etf_list)}")
        self.logger.info("=" * 60)
        
        return results

def main():
    """主函數"""
    scraper = YuantaETFScraper()
    results = scraper.scrape_all_etfs()
    
    print("抓取完成！")
    print("結果摘要:")
    for etf_code, status in results.items():
        print(f"  {etf_code}: {status}")

if __name__ == "__main__":
    main()
