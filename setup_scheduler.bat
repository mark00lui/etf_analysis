@echo off
echo 設定元大ETF爬蟲每日自動執行...

REM 創建工作排程器任務
schtasks /create /tn "YuantaETFScraper" /tr "python \"%cd%\yuanta_etf_scraper.py\"" /sc daily /st 09:00 /f

echo 工作排程器任務已創建！
echo 任務名稱: YuantaETFScraper
echo 執行時間: 每日上午9:00
echo 執行命令: python yuanta_etf_scraper.py

echo.
echo 如需修改執行時間，請使用以下命令：
echo schtasks /change /tn "YuantaETFScraper" /st 新的時間
echo.
echo 如需刪除任務，請使用：
echo schtasks /delete /tn "YuantaETFScraper" /f

pause
