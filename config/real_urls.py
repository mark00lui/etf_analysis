"""
實際網站URL設定檔
這些是各發行商的實際網站URL，需要根據實際情況調整
"""

# 元大投信實際網站
YUANTA_REAL_URLS = {
    'base_url': 'https://www.yuantaetfs.com',
    'etf_list_url': 'https://www.yuantaetfs.com/product/etf',
    'api_base': 'https://www.yuantaetfs.com/api',
    'etf_list_api': 'https://www.yuantaetfs.com/api/Etf/GetEtfList',
    'holdings_api': 'https://www.yuantaetfs.com/api/Etf/GetEtfHolding'
}

# 國泰投信實際網站
CATHAY_REAL_URLS = {
    'base_url': 'https://www.cathaysite.com.tw',
    'etf_list_url': 'https://www.cathaysite.com.tw/etf',
    'api_base': 'https://www.cathaysite.com.tw/api',
    'etf_list_api': 'https://www.cathaysite.com.tw/api/etf/list',
    'holdings_api': 'https://www.cathaysite.com.tw/api/etf/{ticker}/holdings'
}

# 中信投信實際網站
CTBC_REAL_URLS = {
    'base_url': 'https://www.ctbcinvestments.com',
    'etf_list_url': 'https://www.ctbcinvestments.com/etf',
    'api_base': 'https://www.ctbcinvestments.com/api',
    'etf_list_api': 'https://www.ctbcinvestments.com/api/etf/list',
    'holdings_api': 'https://www.ctbcinvestments.com/api/etf/{ticker}/holdings'
}

# 群益投信實際網站
CAPITAL_REAL_URLS = {
    'base_url': 'https://www.capitalfund.com.tw',
    'etf_list_url': 'https://www.capitalfund.com.tw/etf',
    'api_base': 'https://www.capitalfund.com.tw/api',
    'etf_list_api': 'https://www.capitalfund.com.tw/api/etf/list',
    'holdings_api': 'https://www.capitalfund.com.tw/api/etf/{ticker}/holdings'
}

# 富邦投信實際網站
FUBON_REAL_URLS = {
    'base_url': 'https://www.fubon.com',
    'etf_list_url': 'https://www.fubon.com/etf',
    'api_base': 'https://www.fubon.com/api',
    'etf_list_api': 'https://www.fubon.com/api/etf/list',
    'holdings_api': 'https://www.fubon.com/api/etf/{ticker}/holdings'
}

# 復華投信實際網站
FHTRUST_REAL_URLS = {
    'base_url': 'https://www.fhtrust.com.tw',
    'etf_list_url': 'https://www.fhtrust.com.tw/etf',
    'api_base': 'https://www.fhtrust.com.tw/api',
    'etf_list_api': 'https://www.fhtrust.com.tw/api/etf/list',
    'holdings_api': 'https://www.fhtrust.com.tw/api/etf/{ticker}/holdings'
}

# 所有發行商的實際URL設定
REAL_URLS = {
    'yuanta': YUANTA_REAL_URLS,
    'cathay': CATHAY_REAL_URLS,
    'ctbc': CTBC_REAL_URLS,
    'capital': CAPITAL_REAL_URLS,
    'fubon': FUBON_REAL_URLS,
    'fhtrust': FHTRUST_REAL_URLS
}

# 注意事項：
# 1. 這些URL可能需要根據實際網站結構進行調整
# 2. 某些網站可能需要特殊的請求頭或認證
# 3. 某些網站可能有反爬蟲機制，需要額外處理
# 4. API端點可能需要根據實際情況調整
