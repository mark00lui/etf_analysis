import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from utils.logger import setup_logger

class BaseScraper:
    """基礎爬蟲類別"""
    
    def __init__(self, issuer: str):
        self.issuer = issuer
        self.logger = setup_logger(f"scraper.{issuer}", f"logs/{issuer}.log")
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get_page(self, url: str) -> BeautifulSoup:
        """取得網頁內容"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"取得網頁失敗: {url}, 錯誤: {e}")
            raise
    
    def parse_holdings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """解析持股資料 - 子類別需實作"""
        raise NotImplementedError("子類別必須實作 parse_holdings 方法")
    
    def get_etf_list(self) -> List[Dict[str, str]]:
        """取得ETF清單 - 子類別需實作"""
        raise NotImplementedError("子類別必須實作 get_etf_list 方法")
    
    def scrape_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """爬取所有ETF的持股資料"""
        results = {}
        etf_list = self.get_etf_list()
        
        for etf in etf_list:
            try:
                self.logger.info(f"正在爬取 {etf['name']} ({etf['ticker']})")
                holdings = self.scrape_etf_holdings(etf)
                results[etf['ticker']] = holdings
                self.logger.info(f"成功爬取 {etf['name']}, 共 {len(holdings)} 筆持股")
            except Exception as e:
                self.logger.error(f"爬取 {etf['name']} 失敗: {e}")
                results[etf['ticker']] = []
        
        return results
    
    def scrape_etf_holdings(self, etf: Dict[str, str]) -> List[Dict[str, Any]]:
        """爬取單一ETF的持股資料"""
        raise NotImplementedError("子類別必須實作 scrape_etf_holdings 方法")
    
    def clean_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清理資料"""
        cleaned_data = []
        for item in data:
            # 清理權重資料
            if 'weight' in item and item['weight']:
                try:
                    weight = str(item['weight']).replace('%', '').strip()
                    item['weight'] = float(weight) if weight else 0.0
                except:
                    item['weight'] = 0.0
            
            # 清理股數資料
            if 'shares' in item and item['shares']:
                try:
                    shares = str(item['shares']).replace(',', '').strip()
                    item['shares'] = int(float(shares)) if shares else 0
                except:
                    item['shares'] = 0
            
            # 清理市值資料
            if 'market_value' in item and item['market_value']:
                try:
                    market_value = str(item['market_value']).replace(',', '').replace('$', '').strip()
                    item['market_value'] = float(market_value) if market_value else 0.0
                except:
                    item['market_value'] = 0.0
            
            cleaned_data.append(item)
        
        return cleaned_data
