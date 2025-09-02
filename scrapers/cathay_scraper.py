import json
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class CathayScraper(BaseScraper):
    """國泰投信ETF爬蟲"""
    
    def __init__(self):
        super().__init__("國泰")
        self.base_url = "https://www.cathaysite.com.tw"
        self.api_url = "https://www.cathaysite.com.tw/api/etf/list"
    
    def get_etf_list(self) -> List[Dict[str, str]]:
        """取得國泰ETF清單"""
        try:
            # 取得ETF清單頁面
            url = f"{self.base_url}/etf"
            soup = self.get_page(url)
            
            etf_list = []
            # 尋找ETF列表
            etf_links = soup.find_all('a', href=re.compile(r'/etf/detail/'))
            
            for link in etf_links:
                href = link.get('href', '')
                ticker = href.split('/')[-1] if href else ''
                
                # 取得ETF名稱
                name_elem = link.find('h3') or link.find('div', class_='title')
                name = name_elem.get_text(strip=True) if name_elem else ''
                
                if ticker and name:
                    etf_list.append({
                        'ticker': ticker,
                        'name': name,
                        'url': f"{self.base_url}{href}"
                    })
            
            self.logger.info(f"取得 {len(etf_list)} 檔國泰ETF")
            return etf_list
            
        except Exception as e:
            self.logger.error(f"取得ETF清單失敗: {e}")
            return []
    
    def scrape_etf_holdings(self, etf: Dict[str, str]) -> List[Dict[str, Any]]:
        """爬取單一ETF的持股資料"""
        try:
            # 取得持股資料頁面
            holdings_url = f"{etf['url']}/holdings"
            soup = self.get_page(holdings_url)
            
            holdings = []
            
            # 尋找持股表格
            table = soup.find('table', class_='holdings-table') or soup.find('table')
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
            api_url = f"https://www.cathaysite.com.tw/api/etf/{ticker}/holdings"
            response = self.session.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            holdings = []
            for holding in data.get('holdings', []):
                holdings.append({
                    'stock_code': holding.get('code', ''),
                    'stock_name': holding.get('name', ''),
                    'weight': holding.get('weight', 0.0),
                    'shares': holding.get('shares', 0),
                    'market_value': holding.get('market_value', 0.0)
                })
            
            return holdings
            
        except Exception as e:
            self.logger.error(f"API取得持股資料失敗: {e}")
            return []
