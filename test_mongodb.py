#!/usr/bin/env python3
"""
MongoDB 連接測試腳本
"""

import sys
import os
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mongodb_connection():
    """測試MongoDB連接"""
    print("=" * 50)
    print("開始測試 MongoDB 連接")
    print("=" * 50)
    
    try:
        from config.mongodb import MongoDBManager, get_mongodb_manager
        
        # 測試1: 直接建立連接
        print("\n1. 測試直接建立 MongoDB 連接...")
        mongodb = MongoDBManager()
        
        # 測試連接
        if mongodb.test_connection():
            print("✓ MongoDB 連接測試成功")
        else:
            print("✗ MongoDB 連接測試失敗")
            return False
        
        # 測試2: 取得資料庫資訊
        print("\n2. 測試取得資料庫資訊...")
        db_info = mongodb.get_database_info()
        print(f"資料庫名稱: {db_info.get('database_name', 'N/A')}")
        print(f"集合數量: {len(db_info.get('collections', []))}")
        print(f"集合列表: {db_info.get('collections', [])}")
        print(f"資料大小: {db_info.get('total_size', 0)} bytes")
        print(f"儲存大小: {db_info.get('storage_size', 0)} bytes")
        print(f"索引數量: {db_info.get('indexes', 0)}")
        
        # 測試3: 使用全域管理器
        print("\n3. 測試全域 MongoDB 管理器...")
        global_mongodb = get_mongodb_manager()
        if global_mongodb.test_connection():
            print("✓ 全域管理器連接測試成功")
        else:
            print("✗ 全域管理器連接測試失敗")
        
        # 測試4: 測試集合操作
        print("\n4. 測試集合操作...")
        
        # 測試插入測試資料
        test_etf = {
            "ticker": "TEST001",
            "name": "測試ETF",
            "issuer": "測試發行商",
            "description": "這是一個測試用的ETF資料"
        }
        
        # 插入測試資料
        result = global_mongodb.etfs.insert_one(test_etf)
        if result.inserted_id:
            print(f"✓ 測試資料插入成功，ID: {result.inserted_id}")
        else:
            print("✗ 測試資料插入失敗")
        
        # 查詢測試資料
        found_etf = global_mongodb.etfs.find_one({"ticker": "TEST001"})
        if found_etf:
            print(f"✓ 測試資料查詢成功: {found_etf['name']}")
        else:
            print("✗ 測試資料查詢失敗")
        
        # 刪除測試資料
        delete_result = global_mongodb.etfs.delete_one({"ticker": "TEST001"})
        if delete_result.deleted_count > 0:
            print("✓ 測試資料刪除成功")
        else:
            print("✗ 測試資料刪除失敗")
        
        # 測試5: 測試ETF資料管理器
        print("\n5. 測試 ETF 資料管理器...")
        from models.etf_data import ETFDataManager
        
        etf_manager = ETFDataManager()
        
        # 測試儲存ETF資料
        test_etf_data = {
            "ticker": "TEST002",
            "name": "測試ETF 2",
            "issuer": "測試發行商",
            "description": "這是第二個測試用的ETF資料"
        }
        
        if etf_manager.save_etf(test_etf_data):
            print("✓ ETF資料儲存成功")
        else:
            print("✗ ETF資料儲存失敗")
        
        # 測試查詢ETF資料
        saved_etf = etf_manager.get_etf("TEST002")
        if saved_etf:
            print(f"✓ ETF資料查詢成功: {saved_etf['name']}")
        else:
            print("✗ ETF資料查詢失敗")
        
        # 測試儲存持股資料
        test_holdings = [
            {
                "stock_code": "2330",
                "stock_name": "台積電",
                "weight": 5.5,
                "shares": 1000,
                "market_value": 500000
            },
            {
                "stock_code": "2317",
                "stock_name": "鴻海",
                "weight": 3.2,
                "shares": 800,
                "market_value": 320000
            }
        ]
        
        if etf_manager.save_holdings("TEST002", test_holdings, "2024-01-15"):
            print("✓ 持股資料儲存成功")
        else:
            print("✗ 持股資料儲存失敗")
        
        # 測試查詢持股資料
        holdings = etf_manager.get_holdings("TEST002", "2024-01-15")
        if holdings:
            print(f"✓ 持股資料查詢成功，共 {len(holdings)} 筆")
            for holding in holdings:
                print(f"  - {holding['stock_name']} ({holding['stock_code']}): {holding['weight']}%")
        else:
            print("✗ 持股資料查詢失敗")
        
        # 測試統計查詢
        etf_count = etf_manager.get_etf_count()
        holdings_count = etf_manager.get_holdings_count()
        print(f"\n統計資訊:")
        print(f"  ETF數量: {etf_count}")
        print(f"  持股資料數量: {holdings_count}")
        
        # 清理測試資料
        etf_manager.delete_etf("TEST002")
        print("✓ 測試資料清理完成")
        
        print("\n" + "=" * 50)
        print("所有測試完成！MongoDB 連接和操作正常")
        print("=" * 50)
        
        return True
        
    except ImportError as e:
        print(f"✗ 導入模組失敗: {e}")
        print("請確認已安裝 pymongo 套件: pip install pymongo")
        return False
        
    except Exception as e:
        print(f"✗ 測試過程中發生錯誤: {e}")
        return False

def test_mongodb_performance():
    """測試MongoDB性能"""
    print("\n" + "=" * 50)
    print("開始測試 MongoDB 性能")
    print("=" * 50)
    
    try:
        from models.etf_data import ETFDataManager
        import time
        
        etf_manager = ETFDataManager()
        
        # 測試批量插入性能
        print("\n1. 測試批量插入性能...")
        
        # 準備測試資料
        test_etfs = []
        for i in range(100):
            test_etfs.append({
                "ticker": f"PERF{i:03d}",
                "name": f"性能測試ETF {i}",
                "issuer": "性能測試發行商",
                "description": f"這是第 {i} 個性能測試用的ETF資料"
            })
        
        # 測試插入時間
        start_time = time.time()
        for etf in test_etfs:
            etf_manager.save_etf(etf)
        end_time = time.time()
        
        print(f"插入 100 筆ETF資料耗時: {end_time - start_time:.2f} 秒")
        print(f"平均每筆耗時: {(end_time - start_time) / 100 * 1000:.2f} 毫秒")
        
        # 測試查詢性能
        print("\n2. 測試查詢性能...")
        
        start_time = time.time()
        all_etfs = etf_manager.get_all_etfs()
        end_time = time.time()
        
        print(f"查詢 {len(all_etfs)} 筆ETF資料耗時: {end_time - start_time:.2f} 秒")
        
        # 測試條件查詢性能
        start_time = time.time()
        issuer_etfs = etf_manager.get_all_etfs("性能測試發行商")
        end_time = time.time()
        
        print(f"條件查詢 {len(issuer_etfs)} 筆ETF資料耗時: {end_time - start_time:.2f} 秒")
        
        # 清理測試資料
        print("\n3. 清理測試資料...")
        for etf in test_etfs:
            etf_manager.delete_etf(etf['ticker'])
        
        print("✓ 性能測試完成")
        return True
        
    except Exception as e:
        print(f"✗ 性能測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("MongoDB 連接和功能測試")
    print("請確保 MongoDB 服務正在運行")
    print("預設連接: mongodb://localhost:27017/")
    
    # 基本連接測試
    if test_mongodb_connection():
        # 性能測試
        test_mongodb_performance()
        
        print("\n🎉 所有測試通過！MongoDB 已準備就緒")
    else:
        print("\n❌ 測試失敗，請檢查 MongoDB 服務和連接設定")
        print("\n常見問題:")
        print("1. 確認 MongoDB 服務是否正在運行")
        print("2. 確認連接字串是否正確")
        print("3. 確認防火牆設定")
        print("4. 確認 MongoDB 版本相容性")

if __name__ == "__main__":
    main()
