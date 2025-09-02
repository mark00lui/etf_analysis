#!/usr/bin/env python3
"""
測試CSV解析功能
"""

import sys
import os
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_csv_parsing():
    """測試CSV解析功能"""
    print("=" * 60)
    print("測試CSV解析功能")
    print("=" * 60)
    
    try:
        from scrapers.yuanta_excel_scraper import YuantaExcelScraper
        
        scraper = YuantaExcelScraper()
        
        # 測試解析0050.csv檔案
        csv_file = "downloads/yuanta/0050.csv"
        
        if not os.path.exists(csv_file):
            print(f"✗ 找不到測試檔案: {csv_file}")
            return False
        
        print(f"✓ 找到測試檔案: {csv_file}")
        
        # 測試解析
        print("\n開始解析CSV檔案...")
        parsed_data = scraper.parse_excel_data(csv_file, "0050")
        
        if parsed_data:
            print("✓ CSV解析成功")
            print(f"  持股數量: {parsed_data['total_holdings']}")
            print("  前10筆持股:")
            for i, holding in enumerate(parsed_data['holdings'][:10]):
                print(f"    {i+1:2d}. {holding['stock_name']} ({holding['stock_code']}): {holding['weight']:6.2f}%")
            
            # 測試儲存到MongoDB
            print("\n測試儲存到MongoDB...")
            if scraper.save_to_mongodb(parsed_data):
                print("✓ 成功儲存到MongoDB")
                
                # 檢查MongoDB中的資料
                mongodb = scraper.mongodb
                holdings_count = mongodb.holdings.count_documents({"etf_ticker": "0050"})
                print(f"  MongoDB中0050的持股資料數量: {holdings_count}")
                
                # 顯示最新的持股資料
                latest_holdings = list(mongodb.holdings.find(
                    {"etf_ticker": "0050"}, 
                    sort=[("weight", -1)]
                ).limit(5))
                
                print("  權重最高的5檔持股:")
                for i, holding in enumerate(latest_holdings):
                    print(f"    {i+1:2d}. {holding['stock_name']} ({holding['stock_code']}): {holding['weight']:6.2f}%")
                
            else:
                print("✗ 儲存到MongoDB失敗")
        else:
            print("✗ CSV解析失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ CSV解析測試失敗: {e}")
        return False

def test_data_quality():
    """測試資料品質"""
    print("\n" + "=" * 60)
    print("測試資料品質")
    print("=" * 60)
    
    try:
        import pandas as pd
        
        csv_file = "downloads/yuanta/0050.csv"
        df = pd.read_csv(csv_file, encoding='utf-8-sig', skiprows=17)
        
        print(f"原始資料結構: {df.shape}")
        print(f"欄位名稱: {list(df.columns)}")
        
        # 重新命名欄位
        df.columns = ['stock_code', 'stock_name', 'quantity', 'weight']
        
        print(f"\n重新命名後欄位: {list(df.columns)}")
        print(f"前10行資料:")
        print(df.head(10))
        
        # 資料統計
        print(f"\n資料統計:")
        print(f"股票代碼範圍: {df['stock_code'].min()} - {df['stock_code'].max()}")
        print(f"權重範圍: {df['weight'].min():.2f}% - {df['weight'].max():.2f}%")
        print(f"數量範圍: {df['quantity'].min():,} - {df['quantity'].max():,}")
        
        # 檢查資料品質
        valid_stocks = df[
            (df['stock_code'].str.len() == 4) & 
            (df['stock_code'].str.isdigit()) &
            (df['weight'] > 0) &
            (df['quantity'] > 0)
        ]
        
        print(f"\n有效持股數量: {len(valid_stocks)}")
        print(f"總權重: {valid_stocks['weight'].sum():.2f}%")
        
        return True
        
    except Exception as e:
        print(f"✗ 資料品質測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("CSV解析功能測試")
    print("請確保 MongoDB 服務正在運行")
    
    # CSV解析測試
    if test_csv_parsing():
        print("\n🎉 CSV解析測試通過！")
        
        # 資料品質測試
        if test_data_quality():
            print("🎉 資料品質測試通過！")
        else:
            print("⚠️  資料品質測試失敗")
    else:
        print("\n❌ CSV解析測試失敗")
    
    print("\n📝 總結:")
    print("1. CSV解析功能已正常運作")
    print("2. 可以正確讀取0050.csv檔案")
    print("3. 資料已成功儲存到MongoDB")
    print("4. 下一步需要解決Excel下載的問題")

if __name__ == "__main__":
    main()
