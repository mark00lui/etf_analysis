from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
from config.mongodb import get_mongodb_manager
from utils.logger import setup_logger

class ETFDataManager:
    """ETF資料管理器 - MongoDB操作"""
    
    def __init__(self):
        self.mongodb = get_mongodb_manager()
        self.logger = setup_logger("etf_data", "logs/etf_data.log")
    
    # ==================== ETF基本資料操作 ====================
    
    def save_etf(self, etf_data: Dict[str, Any]) -> bool:
        """儲存ETF基本資料"""
        try:
            # 添加時間戳
            etf_data['created_at'] = datetime.now()
            etf_data['updated_at'] = datetime.now()
            
            # 使用upsert操作，如果ticker已存在則更新
            result = self.mongodb.etfs.update_one(
                {"ticker": etf_data['ticker']},
                {"$set": etf_data},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                self.logger.info(f"ETF資料儲存成功: {etf_data['ticker']}")
                return True
            else:
                self.logger.warning(f"ETF資料儲存無變化: {etf_data['ticker']}")
                return False
                
        except Exception as e:
            self.logger.error(f"儲存ETF資料失敗: {e}")
            return False
    
    def get_etf(self, ticker: str) -> Optional[Dict[str, Any]]:
        """取得單一ETF資料"""
        try:
            etf = self.mongodb.etfs.find_one({"ticker": ticker})
            if etf:
                # 移除MongoDB的_id欄位
                etf.pop('_id', None)
            return etf
        except Exception as e:
            self.logger.error(f"取得ETF資料失敗: {e}")
            return None
    
    def get_all_etfs(self, issuer: str = None) -> List[Dict[str, Any]]:
        """取得所有ETF資料"""
        try:
            filter_query = {}
            if issuer:
                filter_query['issuer'] = issuer
            
            etfs = list(self.mongodb.etfs.find(filter_query))
            
            # 移除MongoDB的_id欄位
            for etf in etfs:
                etf.pop('_id', None)
            
            return etfs
            
        except Exception as e:
            self.logger.error(f"取得所有ETF資料失敗: {e}")
            return []
    
    def update_etf(self, ticker: str, update_data: Dict[str, Any]) -> bool:
        """更新ETF資料"""
        try:
            update_data['updated_at'] = datetime.now()
            
            result = self.mongodb.etfs.update_one(
                {"ticker": ticker},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"ETF資料更新成功: {ticker}")
                return True
            else:
                self.logger.warning(f"ETF資料更新無變化: {ticker}")
                return False
                
        except Exception as e:
            self.logger.error(f"更新ETF資料失敗: {e}")
            return False
    
    def delete_etf(self, ticker: str) -> bool:
        """刪除ETF資料"""
        try:
            result = self.mongodb.etfs.delete_one({"ticker": ticker})
            
            if result.deleted_count > 0:
                self.logger.info(f"ETF資料刪除成功: {ticker}")
                return True
            else:
                self.logger.warning(f"ETF資料不存在: {ticker}")
                return False
                
        except Exception as e:
            self.logger.error(f"刪除ETF資料失敗: {e}")
            return False
    
    # ==================== 持股資料操作 ====================
    
    def save_holdings(self, etf_ticker: str, holdings: List[Dict[str, Any]], date: str = None) -> bool:
        """儲存持股資料"""
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # 先刪除該ETF該日期的舊資料
            self.mongodb.holdings.delete_many({
                "etf_ticker": etf_ticker,
                "date": date
            })
            
            # 準備新資料
            holdings_data = []
            for holding in holdings:
                holding_data = {
                    "etf_ticker": etf_ticker,
                    "date": date,
                    "stock_code": holding.get('stock_code', ''),
                    "stock_name": holding.get('stock_name', ''),
                    "weight": holding.get('weight', 0.0),
                    "shares": holding.get('shares', 0),
                    "market_value": holding.get('market_value', 0.0),
                    "created_at": datetime.now()
                }
                holdings_data.append(holding_data)
            
            # 批量插入新資料
            if holdings_data:
                result = self.mongodb.holdings.insert_many(holdings_data)
                self.logger.info(f"持股資料儲存成功: {etf_ticker} - {date}, 共 {len(result.inserted_ids)} 筆")
                return True
            else:
                self.logger.warning(f"沒有持股資料需要儲存: {etf_ticker} - {date}")
                return False
                
        except Exception as e:
            self.logger.error(f"儲存持股資料失敗: {e}")
            return False
    
    def get_holdings(self, etf_ticker: str, date: str = None) -> List[Dict[str, Any]]:
        """取得持股資料"""
        try:
            filter_query = {"etf_ticker": etf_ticker}
            if date:
                filter_query["date"] = date
            
            holdings = list(self.mongodb.holdings.find(filter_query).sort("weight", -1))
            
            # 移除MongoDB的_id欄位
            for holding in holdings:
                holding.pop('_id', None)
            
            return holdings
            
        except Exception as e:
            self.logger.error(f"取得持股資料失敗: {e}")
            return []
    
    def get_holdings_by_date(self, date: str) -> List[Dict[str, Any]]:
        """取得指定日期的所有持股資料"""
        try:
            holdings = list(self.mongodb.holdings.find({"date": date}))
            
            # 移除MongoDB的_id欄位
            for holding in holdings:
                holding.pop('_id', None)
            
            return holdings
            
        except Exception as e:
            self.logger.error(f"取得日期持股資料失敗: {e}")
            return []
    
    def get_holdings_history(self, etf_ticker: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """取得持股歷史資料"""
        try:
            filter_query = {"etf_ticker": etf_ticker}
            
            if start_date and end_date:
                filter_query["date"] = {"$gte": start_date, "$lte": end_date}
            elif start_date:
                filter_query["date"] = {"$gte": start_date}
            elif end_date:
                filter_query["date"] = {"$lte": end_date}
            
            holdings = list(self.mongodb.holdings.find(filter_query).sort("date", -1))
            
            # 移除MongoDB的_id欄位
            for holding in holdings:
                holding.pop('_id', None)
            
            return holdings
            
        except Exception as e:
            self.logger.error(f"取得持股歷史資料失敗: {e}")
            return []
    
    # ==================== 爬蟲日誌操作 ====================
    
    def save_scraper_log(self, issuer: str, action: str, details: Dict[str, Any]) -> bool:
        """儲存爬蟲日誌"""
        try:
            log_data = {
                "issuer": issuer,
                "action": action,
                "details": details,
                "timestamp": datetime.now(),
                "status": "success"
            }
            
            result = self.mongodb.scraper_logs.insert_one(log_data)
            
            if result.inserted_id:
                self.logger.info(f"爬蟲日誌儲存成功: {issuer} - {action}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"儲存爬蟲日誌失敗: {e}")
            return False
    
    def get_scraper_logs(self, issuer: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """取得爬蟲日誌"""
        try:
            filter_query = {}
            if issuer:
                filter_query["issuer"] = issuer
            
            logs = list(self.mongodb.scraper_logs.find(filter_query).sort("timestamp", -1).limit(limit))
            
            # 移除MongoDB的_id欄位
            for log in logs:
                log.pop('_id', None)
            
            return logs
            
        except Exception as e:
            self.logger.error(f"取得爬蟲日誌失敗: {e}")
            return []
    
    # ==================== 統計查詢操作 ====================
    
    def get_etf_count(self, issuer: str = None) -> int:
        """取得ETF數量"""
        try:
            filter_query = {}
            if issuer:
                filter_query["issuer"] = issuer
            
            count = self.mongodb.etfs.count_documents(filter_query)
            return count
            
        except Exception as e:
            self.logger.error(f"取得ETF數量失敗: {e}")
            return 0
    
    def get_holdings_count(self, etf_ticker: str = None, date: str = None) -> int:
        """取得持股資料數量"""
        try:
            filter_query = {}
            if etf_ticker:
                filter_query["etf_ticker"] = etf_ticker
            if date:
                filter_query["date"] = date
            
            count = self.mongodb.holdings.count_documents(filter_query)
            return count
            
        except Exception as e:
            self.logger.error(f"取得持股數量失敗: {e}")
            return 0
    
    def get_latest_date(self) -> Optional[str]:
        """取得最新的資料日期"""
        try:
            latest = self.mongodb.holdings.find_one(
                {},
                sort=[("date", -1)]
            )
            
            return latest["date"] if latest else None
            
        except Exception as e:
            self.logger.error(f"取得最新日期失敗: {e}")
            return None
