#!/usr/bin/env python3
"""
元大ETF Excel檔案下載爬蟲
專門用於下載元大ETF的持股Excel檔案並分析資料
"""

import os
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import time
import re
import urllib3
from config.mongodb import get_mongodb_manager
from utils.logger import setup_logger

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class YuantaExcelScraper:
    """元大ETF Excel檔案下載爬蟲"""
    
    def __init__(self):
        self.logger = setup_logger("yuanta_excel", "logs/yuanta_excel.log")
        self.base_url = "https://www.yuantaetfs.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 建立下載目錄
        self.download_dir = "downloads/yuanta"
        os.makedirs(self.download_dir, exist_ok=True)
        
        # MongoDB 連接
        self.mongodb = get_mongodb_manager()
    
    def get_etf_list(self) -> List[Dict[str, str]]:
        """取得元大ETF清單"""
        try:
            # 元大ETF產品頁面
            url = "https://www.yuantaetfs.com/product"
            
            # 使用verify=False來跳過SSL驗證
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            # 這裡需要根據實際頁面結構來解析ETF清單
            # 暫時返回已知的ETF清單
            known_etfs = [
                {"ticker": "0050", "name": "元大台灣卓越50基金", "url": "/product/detail/0050/ratio"},
                {"ticker": "0056", "name": "元大高股息", "url": "/product/detail/0056/ratio"},
                {"ticker": "0061", "name": "元大寶滬深", "url": "/product/detail/0061/ratio"},
                {"ticker": "00692", "name": "元大台灣50", "url": "/product/detail/00692/ratio"},
                {"ticker": "00881", "name": "元大台灣50正2", "url": "/product/detail/00881/ratio"},
                {"ticker": "00882", "name": "元大台灣50反1", "url": "/product/detail/00882/ratio"},
            ]
            
            self.logger.info(f"取得元大ETF清單，共 {len(known_etfs)} 檔")
            return known_etfs
            
        except Exception as e:
            self.logger.error(f"取得元大ETF清單失敗: {e}")
            # 即使網路請求失敗，也返回已知的ETF清單
            known_etfs = [
                {"ticker": "0050", "name": "元大台灣卓越50基金", "url": "/product/detail/0050/ratio"},
                {"ticker": "0056", "name": "元大高股息", "url": "/product/detail/0056/ratio"},
                {"ticker": "0061", "name": "元大寶滬深", "url": "/product/detail/0061/ratio"},
                {"ticker": "00692", "name": "元大台灣50", "url": "/product/detail/00692/ratio"},
                {"ticker": "00881", "name": "元大台灣50正2", "url": "/product/detail/00881/ratio"},
                {"ticker": "00882", "name": "元大台灣50反1", "url": "/product/detail/00882/ratio"},
            ]
            self.logger.info(f"使用預設ETF清單，共 {len(known_etfs)} 檔")
            return known_etfs
    
    def download_excel(self, etf_ticker: str, etf_name: str) -> Optional[str]:
        """下載指定ETF的持股資料（模擬點擊excelBtn view按鈕）"""
        try:
            # 構建頁面URL
            page_url = f"https://www.yuantaetfs.com/product/detail/{etf_ticker}/ratio"
            
            self.logger.info(f"開始下載 {etf_ticker} ({etf_name}) 的持股資料")
            
            # 訪問頁面獲取持股資料
            response = self.session.get(page_url, timeout=30, verify=False)
            response.raise_for_status()
            
            # 尋找excelBtn view按鈕並模擬點擊
            excel_download_url = self._find_excel_download_button(response.text, etf_ticker)
            
            if excel_download_url:
                # 下載Excel檔案
                excel_response = self.session.get(excel_download_url, timeout=60, verify=False)
                excel_response.raise_for_status()
                
                # 儲存檔案
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{etf_ticker}_{etf_name}_{timestamp}.xlsx"
                filepath = os.path.join(self.download_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(excel_response.content)
                
                self.logger.info(f"Excel檔案下載成功: {filepath}")
                return filepath
            else:
                # 如果找不到下載按鈕，嘗試直接從HTML解析
                self.logger.warning(f"找不到 {etf_ticker} 的Excel下載按鈕，嘗試從HTML解析")
                holdings_data = self._parse_html_holdings(response.text, etf_ticker)
                
                if holdings_data:
                    # 將資料儲存為CSV檔案
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{etf_ticker}_{etf_name}_{timestamp}.csv"
                    filepath = os.path.join(self.download_dir, filename)
                    
                    # 建立DataFrame並儲存為CSV
                    df = pd.DataFrame(holdings_data)
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                    
                    self.logger.info(f"持股資料儲存成功: {filepath}")
                    return filepath
                else:
                    self.logger.warning(f"無法從HTML頁面解析 {etf_ticker} 的持股資料")
                    return None
            
        except Exception as e:
            self.logger.error(f"下載 {etf_ticker} 持股資料失敗: {e}")
            return None
    
    def _find_excel_download_button(self, html_content: str, etf_ticker: str) -> Optional[str]:
        """尋找excelBtn view按鈕並獲取下載URL"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 尋找excelBtn view按鈕
            excel_buttons = soup.find_all('div', class_='excelBtn view')
            
            if excel_buttons:
                for button in excel_buttons:
                    # 檢查按鈕的屬性
                    button_attrs = button.attrs
                    self.logger.info(f"找到excelBtn view按鈕: {button_attrs}")
                    
                    # 尋找可能的點擊事件或下載連結
                    # 方法1: 檢查onclick事件
                    onclick = button.get('onclick')
                    if onclick:
                        # 提取URL
                        url_match = re.search(r"['\"]([^'\"]*\.xlsx?)['\"]", onclick)
                        if url_match:
                            download_url = url_match.group(1)
                            if not download_url.startswith('http'):
                                download_url = urljoin(self.base_url, download_url)
                            self.logger.info(f"從onclick事件找到下載URL: {download_url}")
                            return download_url
                    
                    # 方法2: 檢查data屬性
                    for attr, value in button_attrs.items():
                        if 'url' in attr.lower() or 'download' in attr.lower():
                            if value and ('.xlsx' in value or '.xls' in value):
                                download_url = value if value.startswith('http') else urljoin(self.base_url, value)
                                self.logger.info(f"從{attr}屬性找到下載URL: {download_url}")
                                return download_url
                    
                    # 方法3: 檢查父元素或兄弟元素的連結
                    parent = button.parent
                    if parent:
                        links = parent.find_all('a', href=True)
                        for link in links:
                            href = link['href']
                            if '.xlsx' in href or '.xls' in href:
                                download_url = href if href.startswith('http') else urljoin(self.base_url, href)
                                self.logger.info(f"從父元素連結找到下載URL: {download_url}")
                                return download_url
            
            # 方法4: 嘗試構建下載URL
            possible_urls = [
                f"https://www.yuantaetfs.com/product/detail/{etf_ticker}/ratio/export",
                f"https://www.yuantaetfs.com/product/detail/{etf_ticker}/ratio/download",
                f"https://www.yuantaetfs.com/api/etf/{etf_ticker}/holdings/export",
                f"https://www.yuantaetfs.com/product/detail/{etf_ticker}/ratio/excel",
            ]
            
            for url in possible_urls:
                try:
                    test_response = self.session.head(url, timeout=10, verify=False)
                    if test_response.status_code == 200:
                        self.logger.info(f"找到可用的Excel下載URL: {url}")
                        return url
                except:
                    continue
            
            self.logger.warning(f"無法找到 {etf_ticker} 的Excel下載按鈕或URL")
            return None
            
        except Exception as e:
            self.logger.error(f"尋找Excel下載按鈕失敗: {e}")
            return None
    
    def _parse_html_holdings(self, html_content: str, etf_ticker: str) -> List[Dict]:
        """從HTML頁面解析持股資料"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            holdings = []
            
            # 根據元大網站的HTML結構來解析
            # 尋找持股資訊的表格
            tables = soup.find_all('table')
            
            for table in tables:
                # 尋找包含持股資訊的表格
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:  # 至少需要4個欄位
                        try:
                            # 檢查是否為持股資料行
                            first_cell = cells[0].get_text(strip=True)
                            if first_cell and first_cell.isdigit() and len(first_cell) == 4:
                                # 這可能是股票代碼
                                stock_code = first_cell
                                stock_name = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                                quantity_text = cells[2].get_text(strip=True) if len(cells) > 2 else "0"
                                weight_text = cells[3].get_text(strip=True) if len(cells) > 3 else "0"
                                
                                # 解析數量和權重
                                quantity = self._parse_number(quantity_text)
                                weight = self._parse_percentage(weight_text)
                                
                                if stock_code and stock_name and quantity > 0:
                                    holding = {
                                        'stock_code': stock_code,
                                        'stock_name': stock_name,
                                        'quantity': quantity,
                                        'weight': weight
                                    }
                                    holdings.append(holding)
                                    self.logger.debug(f"解析到持股: {stock_code} {stock_name} {quantity} {weight}%")
                        except Exception as e:
                            self.logger.debug(f"解析行資料失敗: {e}")
                            continue
            
            if not holdings:
                # 嘗試其他解析方法
                holdings = self._parse_html_alternative(html_content, etf_ticker)
            
            # 過濾和清理資料
            holdings = self._filter_holdings_data(holdings)
            
            self.logger.info(f"從HTML解析到 {len(holdings)} 筆持股資料")
            return holdings
            
        except Exception as e:
            self.logger.error(f"解析HTML持股資料失敗: {e}")
            return []
    
    def _parse_html_alternative(self, html_content: str, etf_ticker: str) -> List[Dict]:
        """替代的HTML解析方法"""
        try:
            holdings = []
            
            # 使用更精確的正則表達式尋找持股資料
            # 尋找股票代碼和名稱的模式，但更嚴格
            stock_pattern = r'(\d{4})\s+([^\d\s\-\.]{2,20})\s+([\d,]+)\s+([\d.]+)'
            matches = re.findall(stock_pattern, html_content)
            
            for match in matches:
                try:
                    stock_code = match[0]
                    stock_name = match[1].strip()
                    quantity_text = match[2].replace(',', '')
                    weight_text = match[3]
                    
                    # 驗證資料品質
                    if not self._is_valid_stock_data(stock_code, stock_name, quantity_text, weight_text):
                        continue
                    
                    quantity = self._parse_number(quantity_text)
                    weight = self._parse_percentage(weight_text)
                    
                    if stock_code and stock_name and quantity > 0:
                        holding = {
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'quantity': quantity,
                            'weight': weight
                        }
                        holdings.append(holding)
                        
                except Exception as e:
                    self.logger.debug(f"正則解析失敗: {e}")
                    continue
            
            self.logger.info(f"使用正則表達式解析到 {len(holdings)} 筆持股資料")
            return holdings
            
        except Exception as e:
            self.logger.error(f"替代HTML解析失敗: {e}")
            return []
    
    def _is_valid_stock_data(self, stock_code: str, stock_name: str, quantity_text: str, weight_text: str) -> bool:
        """驗證持股資料的有效性"""
        try:
            # 股票代碼必須是4位數字
            if not stock_code.isdigit() or len(stock_code) != 4:
                return False
            
            # 股票名稱不能太短或包含特殊字符
            if len(stock_name) < 2 or len(stock_name) > 20:
                return False
            
            # 股票名稱不能包含常見的無效字符
            invalid_chars = ['{', '}', '(', ')', '[', ']', '<', '>', ';', ':', '"', "'", '\\', '/', '|', '`', '~']
            if any(char in stock_name for char in invalid_chars):
                return False
            
            # 數量必須是正整數
            if not quantity_text.replace(',', '').isdigit():
                return False
            
            # 權重必須是合理的百分比
            try:
                weight = float(weight_text)
                if weight < 0 or weight > 100:
                    return False
            except:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _filter_holdings_data(self, holdings: List[Dict]) -> List[Dict]:
        """過濾和清理持股資料"""
        try:
            filtered_holdings = []
            
            for holding in holdings:
                # 基本驗證
                if not self._is_valid_holding(holding):
                    continue
                
                # 檢查是否為重複資料
                if not self._is_duplicate_holding(holding, filtered_holdings):
                    filtered_holdings.append(holding)
            
            # 按權重排序
            filtered_holdings.sort(key=lambda x: x['weight'], reverse=True)
            
            self.logger.info(f"過濾後剩餘 {len(filtered_holdings)} 筆有效持股資料")
            return filtered_holdings
            
        except Exception as e:
            self.logger.error(f"過濾持股資料失敗: {e}")
            return holdings
    
    def _is_valid_holding(self, holding: Dict) -> bool:
        """檢查單筆持股資料是否有效"""
        try:
            # 檢查必要欄位
            required_fields = ['stock_code', 'stock_name', 'quantity', 'weight']
            for field in required_fields:
                if field not in holding:
                    return False
            
            # 股票代碼驗證
            stock_code = str(holding['stock_code'])
            if not stock_code.isdigit() or len(stock_code) != 4:
                return False
            
            # 股票名稱驗證
            stock_name = str(holding['stock_name'])
            if len(stock_name) < 2 or len(stock_name) > 20:
                return False
            
            # 數量驗證
            quantity = holding['quantity']
            if not isinstance(quantity, (int, float)) or quantity <= 0:
                return False
            
            # 權重驗證
            weight = holding['weight']
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 100:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _is_duplicate_holding(self, holding: Dict, existing_holdings: List[Dict]) -> bool:
        """檢查是否為重複的持股資料"""
        try:
            stock_code = holding['stock_code']
            
            for existing in existing_holdings:
                if existing['stock_code'] == stock_code:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def parse_excel_data(self, filepath: str, etf_ticker: str) -> Optional[Dict]:
        """解析Excel或CSV檔案內容"""
        try:
            self.logger.info(f"開始解析檔案: {filepath}")
            
            # 根據檔案副檔名選擇讀取方法
            if filepath.endswith('.csv'):
                # 讀取CSV檔案，跳過前17行標題
                df = pd.read_csv(filepath, encoding='utf-8-sig', skiprows=17)
            elif filepath.endswith('.xlsx'):
                # 嘗試讀取Excel檔案，明確指定引擎
                try:
                    # 首先嘗試使用 openpyxl 引擎
                    df = pd.read_excel(filepath, engine='openpyxl', skiprows=17)
                except Exception as e1:
                    self.logger.warning(f"使用 openpyxl 引擎失敗: {e1}")
                    try:
                        # 嘗試使用 xlrd 引擎
                        df = pd.read_excel(filepath, engine='xlrd', skiprows=17)
                    except Exception as e2:
                        self.logger.warning(f"使用 xlrd 引擎失敗: {e2}")
                        try:
                            # 最後嘗試不指定引擎
                            df = pd.read_excel(filepath, skiprows=17)
                        except Exception as e3:
                            self.logger.error(f"所有Excel讀取方法都失敗: {e3}")
                            return None
            else:
                self.logger.error(f"不支援的檔案格式: {filepath}")
                return None
            
            # 分析資料結構
            self.logger.info(f"檔案結構: {df.shape}")
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
            self.logger.error(f"解析檔案失敗: {e}")
            return None
    
    def _extract_holdings_data(self, df: pd.DataFrame, etf_ticker: str) -> List[Dict]:
        """從DataFrame中提取持股資料"""
        try:
            holdings = []
            
            # 根據實際的CSV結構來調整欄位名稱
            # 根據0050.csv的格式，欄位應該是：商品代碼,商品名稱,商品數量,商品權重
            
            # 檢查欄位名稱
            columns = list(df.columns)
            self.logger.info(f"實際欄位名稱: {columns}")
            
            # 如果欄位名稱不正確，嘗試重新命名
            if len(columns) >= 4:
                # 重新命名欄位
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
                # 移除逗號和空格
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
                # 移除%符號
                value = value.replace('%', '').replace(' ', '')
            return float(value)
        except:
            return 0.0
    
    def save_to_mongodb(self, parsed_data: Dict) -> bool:
        """將解析後的資料儲存到MongoDB，加上時間戳記"""
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
            
            # 插入新資料，加上時間戳記
            holdings_data = []
            for holding in holdings:
                holding_doc = {
                    "etf_ticker": etf_ticker,
                    "stock_code": holding['stock_code'],
                    "stock_name": holding['stock_name'],
                    "quantity": holding['quantity'],
                    "weight": holding['weight'],
                    "date": current_date,  # 新增日期欄位
                    "download_date": parsed_data['parse_date'],
                    "file_path": parsed_data['file_path'],
                    "created_at": current_timestamp,
                    "updated_at": current_timestamp  # 新增更新時間
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
            etfs = self.get_etf_list()
            results = {}
            
            for etf in etfs:
                ticker = etf['ticker']
                name = etf['name']
                
                self.logger.info(f"開始爬取 {ticker} ({name})")
                
                success = self.scrape_etf_holdings(ticker, name)
                results[ticker] = success
                
                # 避免請求過於頻繁
                time.sleep(2)
            
            # 統計結果
            success_count = sum(results.values())
            total_count = len(results)
            
            self.logger.info(f"爬取完成: 成功 {success_count}/{total_count}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"爬取所有ETF失敗: {e}")
            return {}

def main():
    """主測試函數"""
    scraper = YuantaExcelScraper()
    
    # 測試單一ETF
    print("測試下載 0050 的持股資料...")
    success = scraper.scrape_etf_holdings("0050", "元大台灣卓越50基金")
    
    if success:
        print("✓ 0050 持股資料下載成功")
    else:
        print("✗ 0050 持股資料下載失敗")
    
    # 測試所有ETF
    print("\n開始下載所有ETF的持股資料...")
    results = scraper.scrape_all_etfs()
    
    print("\n下載結果:")
    for ticker, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {ticker}")

if __name__ == "__main__":
    main()
