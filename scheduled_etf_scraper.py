#!/usr/bin/env python3
"""
排程執行的ETF爬蟲腳本
適合在Windows Task Scheduler、Linux cron或Docker中執行
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scrapers.yuanta_selenium_scraper import YuantaSeleniumScraper
from utils.logger import setup_logger

def setup_scheduled_logging():
    """設定排程執行的日誌"""
    # 建立logs目錄
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # 設定日誌檔案名稱（包含日期）
    today = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"scheduled_scraper_{today}.log"
    
    # 設定日誌格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """主執行函數"""
    logger = setup_scheduled_logging()
    
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("開始執行排程ETF爬蟲任務")
    logger.info(f"執行時間: {start_time}")
    logger.info("=" * 60)
    
    try:
        # 使用Selenium爬蟲（無頭模式，適合排程執行）
        with YuantaSeleniumScraper(headless=True) as scraper:
            logger.info("Selenium爬蟲初始化成功")
            
            # 爬取所有ETF
            logger.info("開始爬取所有ETF的持股資料...")
            results = scraper.scrape_all_etfs()
            
            # 統計結果
            success_count = sum(results.values())
            total_count = len(results)
            
            logger.info(f"爬取完成: 成功 {success_count}/{total_count}")
            
            # 詳細結果
            for ticker, success in results.items():
                status = "✓" if success else "✗"
                logger.info(f"{status} {ticker}")
            
            # 檢查MongoDB中的資料
            try:
                mongodb = scraper.mongodb
                total_holdings = mongodb.holdings.count_documents({})
                logger.info(f"MongoDB中總持股資料數量: {total_holdings}")
                
                # 檢查今天的資料
                today = datetime.now().strftime("%Y-%m-%d")
                today_holdings = mongodb.holdings.count_documents({"date": today})
                logger.info(f"今天新增的持股資料數量: {today_holdings}")
                
            except Exception as e:
                logger.error(f"檢查MongoDB資料失敗: {e}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 60)
        logger.info("排程ETF爬蟲任務執行完成")
        logger.info(f"結束時間: {end_time}")
        logger.info(f"執行時長: {duration}")
        logger.info("=" * 60)
        
        # 返回成功狀態碼
        return 0
        
    except Exception as e:
        logger.error(f"排程ETF爬蟲任務執行失敗: {e}")
        logger.error("=" * 60)
        return 1

def run_single_etf(etf_ticker: str, etf_name: str):
    """執行單一ETF爬取（用於測試或特定需求）"""
    logger = setup_scheduled_logging()
    
    logger.info(f"開始執行單一ETF爬取: {etf_ticker} ({etf_name})")
    
    try:
        with YuantaSeleniumScraper(headless=True) as scraper:
            success = scraper.scrape_etf_holdings(etf_ticker, etf_name)
            
            if success:
                logger.info(f"✓ {etf_ticker} 爬取成功")
                return 0
            else:
                logger.error(f"✗ {etf_ticker} 爬取失敗")
                return 1
                
    except Exception as e:
        logger.error(f"執行單一ETF爬取失敗: {e}")
        return 1

if __name__ == "__main__":
    # 檢查是否有命令行參數
    if len(sys.argv) > 2:
        # 執行單一ETF爬取
        etf_ticker = sys.argv[1]
        etf_name = sys.argv[2]
        exit_code = run_single_etf(etf_ticker, etf_name)
    else:
        # 執行所有ETF爬取
        exit_code = main()
    
    # 退出並返回狀態碼
    sys.exit(exit_code)
