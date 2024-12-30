from auth import Auth, get_api_token
import requests
import os

'''
set APP_ID=your_app_id
set APP_KEY=your_app_key
'''
APP_ID = os.getenv("APP_ID", "")
APP_KEY = os.getenv("APP_KEY", "")
AUTH_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    
try:
    # 獲取帶有 token 的 headers
    headers = get_api_token(APP_ID, APP_KEY, AUTH_URL)
    print("成功獲取 token")
    print("Headers:", headers)
    
    # 使用 headers 訪問 API
    API_URL = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveTrainDelay?$top=30&$format=JSON"
    api_response = requests.get(API_URL, headers=headers)
    print("API 回應:", api_response.json())
    
except Exception as e:
    print(f"錯誤: {e}")