import json
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class CapitalScraper(BaseScraper):
    """群益投信ETF爬蟲"""
    
    def __init__(self):
        super().__init__("群益")
        self.base_url = "https://www.capitalfund.com.tw"
        self.api_url = "https://www.capitalfund.com.tw/api/etf"
    
    def get_etf_list(self) -> List[Dict[str, str]]:
        """取得群益ETF清單"""
        try:
            # 取得ETF清單頁面
            url = f"{self.base_url}/etf"
            soup = self.get_page(url)
            
            etf_list = []
            # 尋找ETF列表
            etf_items = soup.find_all('div', class_='etf-item') or soup.find_all('div', class_='product-card')
            
            for item in etf_items:
                # 尋找連結
                link = item.find('a')
                if link:
                    href = link.get('href', '')
                    ticker = href.split('/')[-1] if href else ''
                    
                    # 取得ETF名稱
                    name_elem = item.find('h3') or item.find('div', class_='title') or item.find('h2')
                    name = name_elem.get_text(strip=True) if name_elem else ''
                    
                    if ticker and name:
                        etf_list.append({
                            'ticker': ticker,
                            'name': name,
                            'url': f"{self.base_url}{href}" if href.startswith('/') else href
                        })
            
            # 如果沒有找到，嘗試其他選擇器
            if not etf_list:
                etf_links = soup.find_all('a', href=re.compile(r'/etf/'))
                for link in etf_links:
                    href = link.get('href', '')
                    ticker = href.split('/')[-1] if href else ''
                    name = link.get_text(strip=True)
                    
                    if ticker and name:
                        etf_list.append({
                            'ticker': ticker,
                            'name': name,
                            'url': f"{self.base_url}{href}"
                        })
            
            self.logger.info(f"取得 {len(etf_list)} 檔群益ETF")
            return etf_list
            
        except Exception as e:
            self.logger.error(f"取得ETF清單失敗: {e}")
            return []
    
    def scrape_etf_holdings(self, etf: Dict[str, str]) -> List[Dict[str, Any]]:
        """爬取單一ETF的持股資料"""
        try:
            # 取得持股資料頁面
            holdings_url = f"{etf['url']}/holdings" if not etf['url'].endswith('/holdings') else etf['url']
            soup = self.get_page(holdings_url)
            
            holdings = []
            
            # 尋找持股表格
            table = soup.find('table', class_='holdings-table') or soup.find('table', class_='portfolio-table')
            if table:
                rows = table.find_all('tr')[1:]  # 跳過標題行
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        holdings.append({
                            'stock_code': cells[0].get_text(strip=True),
                            'stock_name': cells[1].get_text(strip=True),
                            'weight': cells[2].get_text(strip=True),
                            'shares': cells[3].get_text(strip=True),
                            'market_value': cells[4].get_text(strip=True) if len(cells) > 4 else ''
                        })
            
            # 如果表格解析失敗，嘗試API
            if not holdings:
                holdings = self._get_holdings_from_api(etf['ticker'])
            
            return self.clean_data(holdings)
            
        except Exception as e:
            self.logger.error(f"爬取 {etf['ticker']} 持股資料失敗: {e}")
            return []
    
    def _get_holdings_from_api(self, ticker: str) -> List[Dict[str, Any]]:
        """從API取得持股資料"""
        try:
            api_url = f"{self.api_url}/{ticker}/holdings"
            response = self.session.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            holdings = []
            for holding in data.get('data', []):
                holdings.append({
                    'stock_code': holding.get('stock_code', ''),
                    'stock_name': holding.get('stock_name', ''),
                    'weight': holding.get('weight', 0.0),
                    'shares': holding.get('shares', 0),
                    'market_value': holding.get('market_value', 0.0)
                })
            
            return holdings
            
        except Exception as e:
            self.logger.error(f"API取得持股資料失敗: {e}")
            return []
