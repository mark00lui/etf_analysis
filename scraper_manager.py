import time
from datetime import datetime
from typing import Dict, List, Any
from config.database import get_supabase_client
from config.scraper_config import ISSUER_CONFIGS
from scrapers import (
    YuantaScraper, CathayScraper, CTBCScraper,
    CapitalScraper, FubonScraper, FHTrustScraper
)
from utils.logger import setup_logger

class ScraperManager:
    """爬蟲管理器"""
    
    def __init__(self):
        self.logger = setup_logger("scraper_manager", "logs/manager.log")
        self.supabase = get_supabase_client()
        
        # 初始化所有爬蟲
        self.scrapers = {
            'yuanta': YuantaScraper(),
            'cathay': CathayScraper(),
            'ctbc': CTBCScraper(),
            'capital': CapitalScraper(),
            'fubon': FubonScraper(),
            'fhtrust': FHTrustScraper()
        }
    
    def run_all_scrapers(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """執行所有爬蟲"""
        self.logger.info("開始執行所有ETF爬蟲")
        results = {}
        
        for issuer, scraper in self.scrapers.items():
            try:
                self.logger.info(f"開始爬取 {ISSUER_CONFIGS[issuer]['name']} 的ETF資料")
                issuer_results = scraper.scrape_all()
                results[issuer] = issuer_results
                self.logger.info(f"完成 {ISSUER_CONFIGS[issuer]['name']} 爬取，共 {len(issuer_results)} 檔ETF")
                
                # 避免過於頻繁的請求
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"爬取 {ISSUER_CONFIGS[issuer]['name']} 失敗: {e}")
                results[issuer] = {}
        
        return results
    
    def save_to_database(self, results: Dict[str, Dict[str, List[Dict[str, Any]]]]):
        """儲存資料到資料庫"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.logger.info(f"開始儲存資料到資料庫，日期: {today}")
        
        total_etfs = 0
        total_holdings = 0
        
        for issuer, etf_results in results.items():
            for ticker, holdings in etf_results.items():
                try:
                    # 儲存ETF基本資料
                    etf_data = {
                        'ticker': ticker,
                        'issuer': ISSUER_CONFIGS[issuer]['name'],
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # 更新或插入ETF資料
                    self.supabase.table('etfs').upsert(etf_data).execute()
                    
                    # 儲存持股資料
                    for holding in holdings:
                        holding_data = {
                            'etf_ticker': ticker,
                            'stock_code': holding.get('stock_code', ''),
                            'stock_name': holding.get('stock_name', ''),
                            'weight': holding.get('weight', 0.0),
                            'shares': holding.get('shares', 0),
                            'market_value': holding.get('market_value', 0.0),
                            'date': today,
                            'created_at': datetime.now().isoformat()
                        }
                        
                        self.supabase.table('holdings').upsert(holding_data).execute()
                    
                    total_etfs += 1
                    total_holdings += len(holdings)
                    
                except Exception as e:
                    self.logger.error(f"儲存 {ticker} 資料失敗: {e}")
        
        self.logger.info(f"資料儲存完成，共 {total_etfs} 檔ETF，{total_holdings} 筆持股資料")
    
    def run_daily_scraping(self):
        """執行每日爬蟲任務"""
        try:
            # 執行所有爬蟲
            results = self.run_all_scrapers()
            
            # 儲存到資料庫
            self.save_to_database(results)
            
            self.logger.info("每日爬蟲任務完成")
            
        except Exception as e:
            self.logger.error(f"每日爬蟲任務失敗: {e}")
            raise
    
    def get_scraper_status(self) -> Dict[str, bool]:
        """取得各爬蟲狀態"""
        status = {}
        for issuer, scraper in self.scrapers.items():
            try:
                # 測試取得ETF清單
                etf_list = scraper.get_etf_list()
                status[issuer] = len(etf_list) > 0
            except:
                status[issuer] = False
        
        return status

if __name__ == "__main__":
    # 測試爬蟲管理器
    manager = ScraperManager()
    
    # 檢查爬蟲狀態
    status = manager.get_scraper_status()
    print("爬蟲狀態:", status)
    
    # 執行爬蟲
    # manager.run_daily_scraping()
