#!/usr/bin/env python3
"""
測試爬蟲功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers import (
    YuantaScraper, CathayScraper, CTBCScraper,
    CapitalScraper, FubonScraper, FHTrustScraper
)
from utils.logger import setup_logger

def test_scraper(scraper_class, scraper_name):
    """測試單一爬蟲"""
    logger = setup_logger("test", "logs/test.log")
    logger.info(f"開始測試 {scraper_name} 爬蟲")
    
    try:
        scraper = scraper_class()
        
        # 測試取得ETF清單
        etf_list = scraper.get_etf_list()
        logger.info(f"{scraper_name}: 找到 {len(etf_list)} 檔ETF")
        
        # 如果有ETF，測試爬取第一檔的持股資料
        if etf_list:
            first_etf = etf_list[0]
            logger.info(f"測試爬取 {first_etf['name']} ({first_etf['ticker']}) 的持股資料")
            
            holdings = scraper.scrape_etf_holdings(first_etf)
            logger.info(f"成功爬取 {len(holdings)} 筆持股資料")
            
            # 顯示前5筆持股資料
            for i, holding in enumerate(holdings[:5]):
                logger.info(f"持股 {i+1}: {holding.get('stock_name', 'N/A')} ({holding.get('stock_code', 'N/A')}) - {holding.get('weight', 0)}%")
        
        return True
        
    except Exception as e:
        logger.error(f"{scraper_name} 測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    logger = setup_logger("test", "logs/test.log")
    logger.info("開始測試所有爬蟲")
    
    # 定義要測試的爬蟲
    scrapers = [
        (YuantaScraper, "元大投信"),
        (CathayScraper, "國泰投信"),
        (CTBCScraper, "中信投信"),
        (CapitalScraper, "群益投信"),
        (FubonScraper, "富邦投信"),
        (FHTrustScraper, "復華投信")
    ]
    
    results = {}
    
    for scraper_class, name in scrapers:
        success = test_scraper(scraper_class, name)
        results[name] = success
        print(f"{name}: {'成功' if success else '失敗'}")
    
    # 總結
    successful = sum(results.values())
    total = len(results)
    logger.info(f"測試完成: {successful}/{total} 個爬蟲成功")
    
    print(f"\n測試總結: {successful}/{total} 個爬蟲成功")
    for name, success in results.items():
        print(f"  {name}: {'✓' if success else '✗'}")

if __name__ == "__main__":
    main()
