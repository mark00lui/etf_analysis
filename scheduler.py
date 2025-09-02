import schedule
import time
from datetime import datetime
from scraper_manager import ScraperManager
from utils.logger import setup_logger

def daily_scraping_job():
    """每日爬蟲任務"""
    logger = setup_logger("scheduler", "logs/scheduler.log")
    logger.info("開始執行每日爬蟲任務")
    
    try:
        manager = ScraperManager()
        manager.run_daily_scraping()
        logger.info("每日爬蟲任務完成")
    except Exception as e:
        logger.error(f"每日爬蟲任務失敗: {e}")

def main():
    """主程式"""
    logger = setup_logger("scheduler", "logs/scheduler.log")
    logger.info("ETF爬蟲排程服務啟動")
    
    # 設定每日執行時間 (例如: 每天晚上9點)
    schedule.every().day.at("21:00").do(daily_scraping_job)
    
    # 也可以設定每小時執行一次 (測試用)
    # schedule.every().hour.do(daily_scraping_job)
    
    # 或者設定每週執行
    # schedule.every().monday.at("21:00").do(daily_scraping_job)
    
    logger.info("排程已設定，等待執行...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
        except KeyboardInterrupt:
            logger.info("收到中斷信號，停止排程服務")
            break
        except Exception as e:
            logger.error(f"排程執行錯誤: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
