import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase 設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """取得 Supabase 客戶端"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("請設定 SUPABASE_URL 和 SUPABASE_KEY 環境變數")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def init_database():
    """初始化資料庫表格"""
    supabase = get_supabase_client()
    
    # 建立 ETF 基本資料表格
    supabase.table("etfs").upsert({
        "id": "etf_id",
        "name": "ETF名稱",
        "ticker": "股票代碼",
        "issuer": "發行商",
        "created_at": "2024-01-01T00:00:00Z"
    }).execute()
    
    # 建立持股資料表格
    supabase.table("holdings").upsert({
        "id": "holding_id",
        "etf_id": "etf_id",
        "stock_code": "股票代碼",
        "stock_name": "股票名稱",
        "weight": 0.0,
        "shares": 0,
        "market_value": 0.0,
        "date": "2024-01-01",
        "created_at": "2024-01-01T00:00:00Z"
    }).execute()
