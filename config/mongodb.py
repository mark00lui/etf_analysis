import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
from utils.logger import setup_logger

class MongoDBManager:
    """MongoDB 資料庫管理器"""
    
    def __init__(self, connection_string: str = None, database_name: str = "etf_analysis"):
        self.logger = setup_logger("mongodb", "logs/mongodb.log")
        self.database_name = database_name
        
        # 如果沒有提供連接字串，使用預設的本地連接
        if connection_string is None:
            connection_string = "mongodb://localhost:27017/"
        
        try:
            # 建立MongoDB客戶端
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,  # 5秒超時
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # 測試連接
            self.client.admin.command('ping')
            self.logger.info("MongoDB 連接成功")
            
            # 取得資料庫
            self.db = self.client[database_name]
            
            # 初始化集合
            self._init_collections()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"MongoDB 連接失敗: {e}")
            raise
        except Exception as e:
            self.logger.error(f"MongoDB 初始化失敗: {e}")
            raise
    
    def _init_collections(self):
        """初始化資料庫集合"""
        try:
            # ETF基本資料集合
            self.etfs = self.db.etfs
            
            # 持股資料集合
            self.holdings = self.db.holdings
            
            # 爬蟲日誌集合
            self.scraper_logs = self.db.scraper_logs
            
            # 建立索引
            self._create_indexes()
            
            self.logger.info("MongoDB 集合初始化完成")
            
        except Exception as e:
            self.logger.error(f"集合初始化失敗: {e}")
            raise
    
    def _create_indexes(self):
        """建立資料庫索引"""
        try:
            # ETFs 集合索引
            self.etfs.create_index("ticker", unique=True)
            self.etfs.create_index("issuer")
            self.etfs.create_index("updated_at")
            
            # Holdings 集合索引
            self.holdings.create_index([("etf_ticker", 1), ("date", 1)])
            self.holdings.create_index("stock_code")
            self.holdings.create_index("date")
            
            # Scraper logs 集合索引
            self.scraper_logs.create_index("timestamp")
            self.scraper_logs.create_index("issuer")
            
            self.logger.info("MongoDB 索引建立完成")
            
        except Exception as e:
            self.logger.error(f"索引建立失敗: {e}")
            raise
    
    def test_connection(self) -> bool:
        """測試資料庫連接"""
        try:
            # 執行ping命令
            self.client.admin.command('ping')
            self.logger.info("MongoDB 連接測試成功")
            return True
        except Exception as e:
            self.logger.error(f"MongoDB 連接測試失敗: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """取得資料庫資訊"""
        try:
            db_stats = self.db.command("dbStats")
            collections = self.db.list_collection_names()
            
            info = {
                "database_name": self.database_name,
                "collections": collections,
                "total_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0),
                "indexes": db_stats.get("indexes", 0)
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"取得資料庫資訊失敗: {e}")
            return {}
    
    def close_connection(self):
        """關閉資料庫連接"""
        try:
            if self.client:
                self.client.close()
                self.logger.info("MongoDB 連接已關閉")
        except Exception as e:
            self.logger.error(f"關閉連接失敗: {e}")

# 全域MongoDB管理器實例
_mongodb_manager: Optional[MongoDBManager] = None

def get_mongodb_manager() -> MongoDBManager:
    """取得MongoDB管理器實例"""
    global _mongodb_manager
    
    if _mongodb_manager is None:
        # 從環境變數讀取設定
        connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        database_name = os.getenv("MONGODB_DB", "etf_analysis")
        
        _mongodb_manager = MongoDBManager(connection_string, database_name)
    
    return _mongodb_manager

def close_mongodb_connection():
    """關閉MongoDB連接"""
    global _mongodb_manager
    
    if _mongodb_manager:
        _mongodb_manager.close_connection()
        _mongodb_manager = None
