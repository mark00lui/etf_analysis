#!/usr/bin/env python3
"""
元大ETF爬蟲定時執行器
使用schedule庫實現每日自動執行
"""

import schedule
import time
import subprocess
import sys
import os
from datetime import datetime
from utils.logger import setup_logger

class ETFScraperScheduler:
    """ETF爬蟲定時執行器"""
    
    def __init__(self):
        self.logger = setup_logger("scheduler", "logs/scheduler.log")
        self.scraper_script = os.path.join(os.getcwd(), "yuanta_etf_scraper.py")
        
    def run_scraper(self):
        """執行爬蟲腳本 (帶重試機制)"""
        try:
            self.logger.info("🚀 開始執行元大ETF爬蟲 (帶重試機制)...")
            start_time = datetime.now()
            
            # 執行爬蟲腳本
            result = subprocess.run([
                sys.executable, self.scraper_script
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                self.logger.info(f"✅ 爬蟲執行成功！耗時: {duration:.2f}秒")
                if result.stdout:
                    self.logger.info(f"輸出: {result.stdout}")
            else:
                self.logger.error(f"❌ 爬蟲執行失敗！返回碼: {result.returncode}")
                if result.stderr:
                    self.logger.error(f"錯誤: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"❌ 執行爬蟲時發生錯誤: {e}")
    
    def setup_schedule(self):
        """設定排程"""
        # 每日上午9:00執行
        schedule.every().day.at("09:00").do(self.run_scraper)
        
        # 也可以設定其他時間
        # schedule.every().monday.at("09:00").do(self.run_scraper)  # 每週一
        # schedule.every().hour.do(self.run_scraper)  # 每小時
        # schedule.every(30).minutes.do(self.run_scraper)  # 每30分鐘
        
        self.logger.info("排程已設定：每日上午9:00執行元大ETF爬蟲")
    
    def run_scheduler(self):
        """運行排程器"""
        self.setup_schedule()
        
        self.logger.info("排程器已啟動，等待執行...")
        print("排程器已啟動！")
        print("執行時間：每日上午9:00")
        print("按 Ctrl+C 停止排程器")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
        except KeyboardInterrupt:
            self.logger.info("排程器已停止")
            print("\n排程器已停止")

def main():
    """主函數"""
    scheduler = ETFScraperScheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
