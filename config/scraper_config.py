"""
爬蟲設定檔
包含各發行商的網站URL、API端點等設定
"""

# 元大投信設定
YUANTA_CONFIG = {
    'name': '元大投信',
    'base_url': 'https://www.yuantaetfs.com',
    'etf_list_api': 'https://www.yuantaetfs.com/api/Etf/GetEtfList',
    'holdings_api': 'https://www.yuantaetfs.com/api/Etf/GetEtfHolding',
    'headers': {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
}

# 國泰投信設定
CATHAY_CONFIG = {
    'name': '國泰投信',
    'base_url': 'https://www.cathaysite.com.tw',
    'etf_list_url': 'https://www.cathaysite.com.tw/etf',
    'holdings_api': 'https://www.cathaysite.com.tw/api/etf/{ticker}/holdings',
    'table_selectors': [
        'table.holdings-table',
        'table.portfolio-table',
        'table'
    ]
}

# 中信投信設定
CTBC_CONFIG = {
    'name': '中信投信',
    'base_url': 'https://www.ctbcinvestments.com',
    'etf_list_url': 'https://www.ctbcinvestments.com/etf',
    'holdings_api': 'https://www.ctbcinvestments.com/api/etf/{ticker}/holdings',
    'table_selectors': [
        'table.holdings-table',
        'table.portfolio-table',
        'table'
    ]
}

# 群益投信設定
CAPITAL_CONFIG = {
    'name': '群益投信',
    'base_url': 'https://www.capitalfund.com.tw',
    'etf_list_url': 'https://www.capitalfund.com.tw/etf',
    'holdings_api': 'https://www.capitalfund.com.tw/api/etf/{ticker}/holdings',
    'table_selectors': [
        'table.holdings-table',
        'table.portfolio-table',
        'table'
    ]
}

# 富邦投信設定
FUBON_CONFIG = {
    'name': '富邦投信',
    'base_url': 'https://www.fubon.com',
    'etf_list_url': 'https://www.fubon.com/etf',
    'holdings_api': 'https://www.fubon.com/api/etf/{ticker}/holdings',
    'table_selectors': [
        'table.holdings-table',
        'table.portfolio-table',
        'table'
    ]
}

# 復華投信設定
FHTRUST_CONFIG = {
    'name': '復華投信',
    'base_url': 'https://www.fhtrust.com.tw',
    'etf_list_url': 'https://www.fhtrust.com.tw/etf',
    'holdings_api': 'https://www.fhtrust.com.tw/api/etf/{ticker}/holdings',
    'table_selectors': [
        'table.holdings-table',
        'table.portfolio-table',
        'table'
    ]
}

# 所有發行商設定
ISSUER_CONFIGS = {
    'yuanta': YUANTA_CONFIG,
    'cathay': CATHAY_CONFIG,
    'ctbc': CTBC_CONFIG,
    'capital': CAPITAL_CONFIG,
    'fubon': FUBON_CONFIG,
    'fhtrust': FHTRUST_CONFIG
}

# 爬蟲通用設定
SCRAPER_SETTINGS = {
    'timeout': 30,
    'retry_times': 3,
    'retry_delay': 5,
    'user_agent_rotation': True,
    'respect_robots_txt': True,
    'delay_between_requests': 2
}

# 資料庫設定
DATABASE_SETTINGS = {
    'batch_size': 100,
    'max_retries': 3,
    'retry_delay': 1
}
