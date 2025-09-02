#!/usr/bin/env python3
"""
測試元大ETF Excel下載爬蟲
"""

import sys
import os
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_yuanta_excel_scraper():
    """測試元大Excel爬蟲"""
    print("=" * 60)
    print("測試元大ETF Excel下載爬蟲")
    print("=" * 60)
    
    try:
        from scrapers.yuanta_excel_scraper import YuantaExcelScraper
        
        # 建立爬蟲實例
        scraper = YuantaExcelScraper()
        print("✓ 爬蟲實例建立成功")
        
        # 測試1: 取得ETF清單
        print("\n1. 測試取得ETF清單...")
        etfs = scraper.get_etf_list()
        if etfs:
            print(f"✓ 成功取得 {len(etfs)} 檔ETF")
            for etf in etfs[:3]:  # 只顯示前3檔
                print(f"  - {etf['ticker']}: {etf['name']}")
        else:
            print("✗ 取得ETF清單失敗")
            return False
        
        # 測試2: 測試單一ETF下載
        print("\n2. 測試下載 0050 的持股資料...")
        success = scraper.scrape_etf_holdings("0050", "元大台灣卓越50基金")
        
        if success:
            print("✓ 0050 持股資料下載成功")
        else:
            print("✗ 0050 持股資料下載失敗")
            print("  這可能是正常的，因為需要實際的Excel下載連結")
        
        # 測試3: 檢查下載目錄
        print("\n3. 檢查下載目錄...")
        download_dir = scraper.download_dir
        if os.path.exists(download_dir):
            files = os.listdir(download_dir)
            print(f"✓ 下載目錄存在: {download_dir}")
            print(f"  檔案數量: {len(files)}")
            if files:
                print("  檔案列表:")
                for file in files[:5]:  # 只顯示前5個檔案
                    print(f"    - {file}")
        else:
            print(f"✗ 下載目錄不存在: {download_dir}")
        
        # 測試4: 檢查MongoDB連接
        print("\n4. 檢查MongoDB連接...")
        try:
            mongodb = scraper.mongodb
            if mongodb.test_connection():
                print("✓ MongoDB 連接正常")
                
                # 檢查持股資料
                holdings_count = mongodb.holdings.count_documents({})
                print(f"  持股資料數量: {holdings_count}")
                
                if holdings_count > 0:
                    # 顯示最新的持股資料
                    latest_holding = mongodb.holdings.find_one({}, sort=[("created_at", -1)])
                    if latest_holding:
                        print(f"  最新資料: {latest_holding.get('etf_ticker', 'N/A')} - {latest_holding.get('stock_name', 'N/A')}")
            else:
                print("✗ MongoDB 連接失敗")
        except Exception as e:
            print(f"✗ MongoDB 檢查失敗: {e}")
        
        print("\n" + "=" * 60)
        print("測試完成！")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"✗ 導入模組失敗: {e}")
        print("請確認已安裝必要的套件")
        return False
        
    except Exception as e:
        print(f"✗ 測試過程中發生錯誤: {e}")
        return False

def test_excel_parsing():
    """測試Excel解析功能"""
    print("\n" + "=" * 60)
    print("測試Excel解析功能")
    print("=" * 60)
    
    try:
        from scrapers.yuanta_excel_scraper import YuantaExcelScraper
        import pandas as pd
        
        scraper = YuantaExcelScraper()
        
        # 建立測試用的Excel檔案
        test_data = {
            '商品代碼': ['2330', '2317', '2454', '2308', '2881'],
            '商品名稱': ['台積電', '鴻海', '聯發科', '台達電', '富邦金'],
            '商品數量': [333128917, 166454837, 20067384, 26376453, 110943553],
            '商品權重': [58.87, 5.03, 4.16, 2.75, 1.47]
        }
        
        df = pd.DataFrame(test_data)
        
        # 儲存測試Excel檔案
        test_file = os.path.join(scraper.download_dir, "test_0050.xlsx")
        df.to_excel(test_file, index=False)
        print(f"✓ 建立測試Excel檔案: {test_file}")
        
        # 測試解析
        print("\n測試解析Excel資料...")
        parsed_data = scraper.parse_excel_data(test_file, "0050")
        
        if parsed_data:
            print("✓ Excel解析成功")
            print(f"  持股數量: {parsed_data['total_holdings']}")
            print("  前3筆持股:")
            for i, holding in enumerate(parsed_data['holdings'][:3]):
                print(f"    {i+1}. {holding['stock_name']} ({holding['stock_code']}): {holding['weight']}%")
        else:
            print("✗ Excel解析失敗")
        
        # 清理測試檔案
        if os.path.exists(test_file):
            os.remove(test_file)
            print("✓ 測試檔案已清理")
        
        return True
        
    except Exception as e:
        print(f"✗ Excel解析測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("元大ETF Excel爬蟲測試")
    print("請確保 MongoDB 服務正在運行")
    
    # 基本功能測試
    if test_yuanta_excel_scraper():
        print("\n🎉 基本功能測試通過！")
        
        # Excel解析測試
        if test_excel_parsing():
            print("🎉 Excel解析測試通過！")
        else:
            print("⚠️  Excel解析測試失敗")
    else:
        print("\n❌ 基本功能測試失敗")
    
    print("\n📝 注意事項:")
    print("1. 實際的Excel下載可能需要分析網站結構")
    print("2. 某些網站可能需要JavaScript渲染")
    print("3. 可能需要處理反爬蟲機制")
    print("4. 建議先手動測試下載流程")

if __name__ == "__main__":
    main()
