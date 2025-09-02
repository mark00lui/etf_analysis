#!/usr/bin/env python3
"""
簡單的 MongoDB 連接測試
"""

try:
    from pymongo import MongoClient
    print("✓ pymongo 套件導入成功")
except ImportError:
    print("✗ pymongo 套件未安裝，請執行: pip install pymongo")
    exit(1)

def test_simple_connection():
    """簡單連接測試"""
    print("\n開始測試 MongoDB 連接...")
    
    try:
        # 建立連接
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # 測試連接
        client.admin.command('ping')
        print("✓ MongoDB 連接成功！")
        
        # 列出所有資料庫
        databases = client.list_database_names()
        print(f"可用資料庫: {databases}")
        
        # 選擇或建立測試資料庫
        db = client['test_db']
        
        # 測試集合操作
        collection = db['test_collection']
        
        # 插入測試資料
        test_doc = {"name": "測試", "value": 123, "timestamp": "2024-01-15"}
        result = collection.insert_one(test_doc)
        print(f"✓ 測試資料插入成功，ID: {result.inserted_id}")
        
        # 查詢測試資料
        found_doc = collection.find_one({"name": "測試"})
        if found_doc:
            print(f"✓ 測試資料查詢成功: {found_doc}")
        else:
            print("✗ 測試資料查詢失敗")
        
        # 刪除測試資料
        delete_result = collection.delete_one({"name": "測試"})
        if delete_result.deleted_count > 0:
            print("✓ 測試資料刪除成功")
        else:
            print("✗ 測試資料刪除失敗")
        
        # 關閉連接
        client.close()
        print("✓ MongoDB 連接測試完成")
        
        return True
        
    except Exception as e:
        print(f"✗ MongoDB 連接失敗: {e}")
        return False

if __name__ == "__main__":
    print("MongoDB 簡單連接測試")
    print("=" * 30)
    
    if test_simple_connection():
        print("\n🎉 測試成功！MongoDB 可以正常使用")
    else:
        print("\n❌ 測試失敗！請檢查 MongoDB 服務")
        print("\n檢查項目:")
        print("1. MongoDB 服務是否啟動")
        print("2. 預設埠號 27017 是否可用")
        print("3. 防火牆設定")
        print("4. MongoDB 版本")
