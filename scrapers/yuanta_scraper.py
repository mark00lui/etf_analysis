import json
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class YuantaScraper(BaseScraper):
    """元大投信ETF爬蟲"""
    
    def __init__(self):
        super().__init__("元大")
        self.base_url = "https://www.yuantaetfs.com"
        self.api_url = "https://www.yuantaetfs.com/api/Etf/GetEtfList"
    
    def get_etf_list(self) -> List[Dict[str, str]]:
        """取得元大ETF清單"""
        try:
            # 使用API取得ETF清單
            response = self.session.post(self.api_url, json={})
            response.raise_for_status()
            data = response.json()
            
            etf_list = []
            for etf in data.get('Data', []):
                if etf.get('EtfType') == 'ETF':  # 只取ETF，排除其他商品
                    etf_list.append({
                        'ticker': etf.get('EtfCode', ''),
                        'name': etf.get('EtfName', ''),
                        'url': f"{self.base_url}/product/detail/{etf.get('EtfCode', '')}"
                    })
            
            self.logger.info(f"取得 {len(etf_list)} 檔元大ETF")
            return etf_list
            
        except Exception as e:
            self.logger.error(f"取得ETF清單失敗: {e}")
            return []
    
    def scrape_etf_holdings(self, etf: Dict[str, str]) -> List[Dict[str, Any]]:
        """爬取單一ETF的持股資料"""
        try:
            # 取得持股資料API
            holdings_api = f"https://www.yuantaetfs.com/api/Etf/GetEtfHolding"
            payload = {
                "etfCode": etf['ticker'],
                "date": ""  # 空字串會取得最新資料
            }
            
            response = self.session.post(holdings_api, json=payload)
            response.raise_for_status()
            data = response.json()
            
            holdings = []
            for holding in data.get('Data', []):
                holdings.append({
                    'stock_code': holding.get('StockCode', ''),
                    'stock_name': holding.get('StockName', ''),
                    'weight': holding.get('Weight', 0.0),
                    'shares': holding.get('Shares', 0),
                    'market_value': holding.get('MarketValue', 0.0)
                })
            
            return self.clean_data(holdings)
            
        except Exception as e:
            self.logger.error(f"爬取 {etf['ticker']} 持股資料失敗: {e}")
            return []
