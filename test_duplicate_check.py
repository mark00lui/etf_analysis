#!/usr/bin/env python3
"""
測試重複檢查機制
"""

from models.etf_data import ETFDataManager

def test_duplicate_check():
    """測試重複檢查功能"""
    print("測試重複檢查機制")
    print("=" * 50)
    
    etf_manager = ETFDataManager()
    
    # 測試數據
    test_holdings = [
        {
            'stock_code': '2330',
            'stock_name': '台積電',
            'shares': 333314781,
            'weight': 58.75
        },
        {
            'stock_code': '2317',
            'stock_name': '鴻海',
            'shares': 166547825,
            'weight': 5.1
        }
    ]
    
    etf_code = "TEST001"
    date = "2025-09-08"
    
    print(f"測試ETF: {etf_code}")
    print(f"測試日期: {date}")
    print(f"測試數據: {len(test_holdings)} 筆")
    
    # 第一次保存
    print("\n第一次保存...")
    result1 = etf_manager.save_holdings(etf_code, test_holdings, date)
    print(f"結果: {'成功' if result1 else '失敗'}")
    
    # 檢查重複
    print("\n檢查重複...")
    duplicate_check = etf_manager.check_duplicate_holdings(etf_code, test_holdings, date)
    print(f"重複檢查結果: {duplicate_check}")
    
    # 第二次保存（應該被跳過）
    print("\n第二次保存（相同數據）...")
    result2 = etf_manager.save_holdings(etf_code, test_holdings, date)
    print(f"結果: {'成功' if result2 else '失敗'}")
    
    # 修改數據後保存
    modified_holdings = test_holdings.copy()
    modified_holdings[0]['weight'] = 60.0  # 修改權重
    
    print("\n第三次保存（修改後數據）...")
    result3 = etf_manager.save_holdings(etf_code, modified_holdings, date)
    print(f"結果: {'成功' if result3 else '失敗'}")
    
    # 強制更新
    print("\n強制更新...")
    result4 = etf_manager.save_holdings(etf_code, test_holdings, date, force_update=True)
    print(f"結果: {'成功' if result4 else '失敗'}")
    
    # 清理測試數據
    print("\n清理測試數據...")
    etf_manager.mongodb.holdings.delete_many({"etf_ticker": etf_code})
    print("測試完成")

if __name__ == "__main__":
    test_duplicate_check()
