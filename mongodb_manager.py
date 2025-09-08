#!/usr/bin/env python3
"""
MongoDB管理工具 - 簡化版本
"""

from config.mongodb import get_mongodb_manager
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def check_mongodb_status():
    """檢查MongoDB狀態"""
    try:
        mongodb = get_mongodb_manager()
        print("✓ MongoDB連接成功")
        
        # 基本統計
        db_stats = mongodb.db.command("dbStats")
        collections = mongodb.db.list_collection_names()
        
        print(f"數據庫: {mongodb.database_name}")
        print(f"集合數量: {len(collections)}")
        print(f"文檔總數: {db_stats.get('objects', 0):,}")
        
        # 檢查holdings集合
        if 'holdings' in collections:
            holdings = mongodb.db['holdings']
            total_count = holdings.count_documents({})
            print(f"持股數據: {total_count:,} 筆")
            
            # ETF統計
            pipeline = [
                {"$group": {
                    "_id": "$etf_ticker",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            
            etf_stats = list(holdings.aggregate(pipeline))
            print(f"ETF統計:")
            for stat in etf_stats:
                print(f"  {stat['_id']}: {stat['count']:,} 筆")
        
        return True
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"✗ MongoDB連接失敗: {e}")
        return False
    except Exception as e:
        print(f"✗ 檢查時發生錯誤: {e}")
        return False

def query_etf_data(etf_code, limit=10):
    """查詢ETF數據"""
    try:
        mongodb = get_mongodb_manager()
        collection = mongodb.db['holdings']
        
        holdings = list(collection.find(
            {"etf_ticker": etf_code}
        ).sort("weight", -1).limit(limit))
        
        print(f"ETF {etf_code} 持股數據 (前{limit}名):")
        print("-" * 60)
        
        for i, holding in enumerate(holdings, 1):
            print(f"{i:2d}. {holding.get('stock_name', 'N/A')} ({holding.get('stock_code', 'N/A')})")
            print(f"    權重: {holding.get('weight', 0):.2f}%")
            print(f"    持股數: {holding.get('shares', 0):,}")
            print(f"    日期: {holding.get('date', 'N/A')}")
            print()
        
        return holdings
        
    except Exception as e:
        print(f"查詢失敗: {e}")
        return []

def get_available_etfs():
    """獲取可用的ETF列表"""
    try:
        mongodb = get_mongodb_manager()
        collection = mongodb.db['holdings']
        
        pipeline = [
            {"$group": {
                "_id": "$etf_ticker",
                "count": {"$sum": 1},
                "latest_date": {"$max": "$date"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        etfs = list(collection.aggregate(pipeline))
        print("可用的ETF:")
        print("-" * 40)
        
        for i, etf_doc in enumerate(etfs, 1):
            print(f"{i:2d}. {etf_doc['_id']} ({etf_doc['count']} 筆數據, 最新: {etf_doc['latest_date']})")
        
        return [etf_doc['_id'] for etf_doc in etfs]
        
    except Exception as e:
        print(f"獲取ETF列表失敗: {e}")
        return []

def main():
    """主函數"""
    print("MongoDB管理工具")
    print("=" * 40)
    
    # 檢查狀態
    if not check_mongodb_status():
        return
    
    print("\n可用ETF:")
    etfs = get_available_etfs()
    
    if etfs:
        print(f"\n查詢示例:")
        print(f"python -c \"from mongodb_manager import query_etf_data; query_etf_data('0050', 5)\"")

if __name__ == "__main__":
    main()
