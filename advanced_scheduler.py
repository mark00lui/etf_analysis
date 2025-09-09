#!/usr/bin/env python3
"""
元大ETF爬蟲進階定時執行器
使用APScheduler實現更靈活的排程功能
"""

import os
import sys
import subprocess
from datetime import datetime, time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from utils.logger import setup_logger

class AdvancedETFScraperScheduler:
    """進階ETF爬蟲定時執行器"""
    
    def __init__(self):
        self.logger = setup_logger("advanced_scheduler", "logs/advanced_scheduler.log")
        self.scraper_script = os.path.join(os.getcwd(), "yuanta_etf_scraper.py")
        self.scheduler = BlockingScheduler()
        
    def run_scraper(self):
        """執行爬蟲腳本"""
        try:
            self.logger.info("=" * 50)
            self.logger.info("開始執行元大ETF爬蟲...")
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
        finally:
            self.logger.info("=" * 50)
    
    def setup_schedules(self):
        """設定多種排程選項"""
        
        # 選項1: 每日上午9:00執行
        self.scheduler.add_job(
            func=self.run_scraper,
            trigger=CronTrigger(hour=9, minute=0),
            id='daily_9am',
            name='每日上午9:00執行ETF爬蟲',
            replace_existing=True
        )
        
        # 選項2: 每週一上午9:00執行
        self.scheduler.add_job(
            func=self.run_scraper,
            trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
            id='weekly_monday',
            name='每週一上午9:00執行ETF爬蟲',
            replace_existing=True
        )
        
        # 選項3: 每週一、三、五上午9:00執行
        self.scheduler.add_job(
            func=self.run_scraper,
            trigger=CronTrigger(day_of_week='mon,wed,fri', hour=9, minute=0),
            id='weekdays_9am',
            name='每週一、三、五上午9:00執行ETF爬蟲',
            replace_existing=True
        )
        
        # 選項4: 每4小時執行一次 (測試用)
        # self.scheduler.add_job(
        #     func=self.run_scraper,
        #     trigger=IntervalTrigger(hours=4),
        #     id='every_4_hours',
        #     name='每4小時執行ETF爬蟲',
        #     replace_existing=True
        # )
        
        self.logger.info("排程已設定完成")
        self.logger.info("已啟用的排程:")
        for job in self.scheduler.get_jobs():
            self.logger.info(f"  - {job.name} (ID: {job.id})")
    
    def run_scheduler(self):
        """運行排程器"""
        self.setup_schedules()
        
        self.logger.info("進階排程器已啟動")
        print("🚀 進階排程器已啟動！")
        print("📅 已設定的排程:")
        
        for job in self.scheduler.get_jobs():
            print(f"  - {job.name}")
            print(f"    下次執行: {job.next_run_time}")
        
        print("\n按 Ctrl+C 停止排程器")
        
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            self.logger.info("排程器已停止")
            print("\n⏹️ 排程器已停止")
            self.scheduler.shutdown()

def main():
    """主函數"""
    scheduler = AdvancedETFScraperScheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
