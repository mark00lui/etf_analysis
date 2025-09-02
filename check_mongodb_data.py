#!/usr/bin/env python3
"""
檢查MongoDB中的ETF持股資料
"""

from config.mongodb import get_mongodb_manager

def main():
    mongodb = get_mongodb_manager()
    
    # 檢查0050 ETF的持股資料
    holdings = list(mongodb.holdings.find(
        {'etf_ticker': '0050'}, 
        sort=[('weight', -1)]
    ).limit(5))
    
    print('0050 ETF 權重最高的5檔持股:')
    for i, holding in enumerate(holdings):
        print(f'{i+1:2d}. {holding["stock_name"]} ({holding["stock_code"]}): {holding["weight"]:6.2f}%')
        print(f'    欄位: {list(holding.keys())}')
        if i == 0:  # 只顯示第一筆的完整欄位
            print(f'    完整資料: {holding}')
        print()
    
    # 檢查資料統計
    total_holdings = mongodb.holdings.count_documents({'etf_ticker': '0050'})
    print(f'總持股數量: {total_holdings}')
    
    # 檢查最新資料
    latest_holding = mongodb.holdings.find_one(
        {'etf_ticker': '0050'}, 
        sort=[('created_at', -1)]
    )
    if latest_holding:
        print(f'\n最新資料時間: {latest_holding["created_at"]}')
        print(f'檔案路徑: {latest_holding["file_path"]}')
        print(f'下載日期: {latest_holding["download_date"]}')

if __name__ == "__main__":
    main()
