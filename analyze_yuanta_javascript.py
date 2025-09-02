#!/usr/bin/env python3
"""
分析元大網站JavaScript下載機制
"""

import requests
import re
from bs4 import BeautifulSoup
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def analyze_yuanta_javascript():
    """分析元大網站的JavaScript下載機制"""
    
    url = "https://www.yuantaetfs.com/product/detail/0050/ratio"
    
    try:
        # 獲取頁面內容
        response = requests.get(url, verify=False, timeout=30)
        response.raise_for_status()
        
        html_content = response.text
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("=" * 60)
        print("分析元大網站JavaScript下載機制")
        print("=" * 60)
        
        # 1. 尋找excelBtn view按鈕
        excel_buttons = soup.find_all('div', class_='excelBtn view')
        print(f"找到 {len(excel_buttons)} 個excelBtn view按鈕")
        
        for i, button in enumerate(excel_buttons):
            print(f"\n按鈕 {i+1}:")
            print(f"  屬性: {button.attrs}")
            
            # 檢查父元素
            parent = button.parent
            if parent:
                print(f"  父元素: {parent.name} - {parent.attrs}")
                
                # 檢查兄弟元素
                siblings = parent.find_all('div', recursive=False)
                print(f"  兄弟元素數量: {len(siblings)}")
        
        # 2. 尋找JavaScript代碼
        scripts = soup.find_all('script')
        print(f"\n找到 {len(scripts)} 個script標籤")
        
        for i, script in enumerate(scripts):
            script_content = script.string
            if script_content:
                # 尋找可能的下載相關代碼
                if 'excel' in script_content.lower() or 'download' in script_content.lower():
                    print(f"\nScript {i+1} (可能包含下載邏輯):")
                    print(f"  類型: {script.get('type', 'text/javascript')}")
                    print(f"  內容預覽: {script_content[:200]}...")
                    
                    # 尋找下載相關的函數或事件
                    download_patterns = [
                        r'function\s+(\w*excel\w*)\s*\(',
                        r'function\s+(\w*download\w*)\s*\(',
                        r'(\w*excel\w*)\s*[:=]\s*function',
                        r'(\w*download\w*)\s*[:=]\s*function',
                        r'onclick\s*[:=]\s*["\']([^"\']*)["\']',
                        r'addEventListener\s*\(\s*["\']click["\']\s*,\s*(\w+)',
                    ]
                    
                    for pattern in download_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        if matches:
                            print(f"    找到匹配: {matches}")
        
        # 3. 尋找Vue.js相關代碼
        vue_scripts = soup.find_all('script', attrs={'type': 'text/javascript'})
        for script in vue_scripts:
            if script.string and 'data-v-' in str(script.string):
                print(f"\n找到Vue.js相關代碼:")
                print(f"  內容預覽: {script.string[:300]}...")
        
        # 4. 尋找可能的API端點
        api_patterns = [
            r'["\'](/[^"\']*export[^"\']*)["\']',
            r'["\'](/[^"\']*download[^"\']*)["\']',
            r'["\'](/[^"\']*excel[^"\']*)["\']',
            r'["\'](/api/[^"\']*)["\']',
        ]
        
        print(f"\n可能的API端點:")
        for pattern in api_patterns:
            matches = re.findall(pattern, html_content)
            if matches:
                print(f"  {pattern}: {matches}")
        
        # 5. 檢查網路請求
        print(f"\n檢查網路請求...")
        possible_urls = [
            f"https://www.yuantaetfs.com/product/detail/0050/ratio/export",
            f"https://www.yuantaetfs.com/product/detail/0050/ratio/download",
            f"https://www.yuantaetfs.com/api/etf/0050/holdings/export",
            f"https://www.yuantaetfs.com/product/detail/0050/ratio/excel",
        ]
        
        for url in possible_urls:
            try:
                test_response = requests.head(url, verify=False, timeout=10)
                print(f"  {url}: {test_response.status_code}")
                if test_response.status_code == 200:
                    print(f"    Content-Type: {test_response.headers.get('content-type')}")
            except Exception as e:
                print(f"  {url}: 錯誤 - {e}")
        
        return True
        
    except Exception as e:
        print(f"分析失敗: {e}")
        return False

if __name__ == "__main__":
    analyze_yuanta_javascript()
