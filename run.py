#!/usr/bin/env python3
"""
ETF爬蟲系統快速啟動腳本
"""

import sys
import os
import argparse
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description='ETF持股分析爬蟲系統')
    parser.add_argument('command', choices=['test', 'scrape', 'schedule', 'status'], 
                       help='執行的命令')
    parser.add_argument('--issuer', choices=['yuanta', 'cathay', 'ctbc', 'capital', 'fubon', 'fhtrust'],
                       help='指定發行商 (僅適用於 test 和 scrape 命令)')
    parser.add_argument('--debug', action='store_true', help='啟用除錯模式')
    
    args = parser.parse_args()
    
    if args.debug:
        print(f"除錯模式: {args.debug}")
        print(f"命令: {args.command}")
        print(f"發行商: {args.issuer}")
    
    if args.command == 'test':
        run_test(args.issuer)
    elif args.command == 'scrape':
        run_scrape(args.issuer)
    elif args.command == 'schedule':
        run_schedule()
    elif args.command == 'status':
        run_status()

def run_test(issuer=None):
    """執行測試"""
    print("開始測試爬蟲...")
    
    if issuer:
        # 測試指定發行商
        from test_scrapers import test_scraper
        from scrapers import (
            YuantaScraper, CathayScraper, CTBCScraper,
            CapitalScraper, FubonScraper, FHTrustScraper
        )
        
        scrapers = {
            'yuanta': (YuantaScraper, "元大投信"),
            'cathay': (CathayScraper, "國泰投信"),
            'ctbc': (CTBCScraper, "中信投信"),
            'capital': (CapitalScraper, "群益投信"),
            'fubon': (FubonScraper, "富邦投信"),
            'fhtrust': (FHTrustScraper, "復華投信")
        }
        
        if issuer in scrapers:
            scraper_class, name = scrapers[issuer]
            success = test_scraper(scraper_class, name)
            print(f"{name}: {'成功' if success else '失敗'}")
        else:
            print(f"不支援的發行商: {issuer}")
    else:
        # 測試所有發行商
        os.system('python test_scrapers.py')

def run_scrape(issuer=None):
    """執行爬蟲"""
    print("開始執行爬蟲...")
    
    if issuer:
        # 爬取指定發行商
        from scraper_manager import ScraperManager
        manager = ScraperManager()
        
        if issuer in manager.scrapers:
            scraper = manager.scrapers[issuer]
            results = scraper.scrape_all()
            print(f"完成 {issuer} 爬取，共 {len(results)} 檔ETF")
        else:
            print(f"不支援的發行商: {issuer}")
    else:
        # 爬取所有發行商
        from scraper_manager import ScraperManager
        manager = ScraperManager()
        manager.run_daily_scraping()

def run_schedule():
    """啟動排程服務"""
    print("啟動排程服務...")
    print("按 Ctrl+C 停止服務")
    os.system('python scheduler.py')

def run_status():
    """檢查爬蟲狀態"""
    print("檢查爬蟲狀態...")
    
    from scraper_manager import ScraperManager
    manager = ScraperManager()
    status = manager.get_scraper_status()
    
    print("\n爬蟲狀態:")
    for issuer, is_working in status.items():
        status_icon = "✓" if is_working else "✗"
        print(f"  {issuer}: {status_icon}")

if __name__ == "__main__":
    main()
