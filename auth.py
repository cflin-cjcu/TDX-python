import json
import requests

class Auth:
    """處理 API 認證"""
    
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key
    
    def get_auth_header(self):
        """認證請求的 headers"""
        return {
            'content-type': 'application/x-www-form-urlencoded'
        }
    
    def get_auth_data(self):
        """認證請求的 data"""
        return {
            'grant_type': 'client_credentials',
            'client_id': self.app_id,
            'client_secret': self.app_key
        }

def get_api_token(app_id, app_key, auth_url):
    """獲取 API token"""
    try:
        # 創建認證實例
        auth = Auth(app_id, app_key)
        
        # 發送認證請求
        response = requests.post(
            auth_url,
            headers=auth.get_auth_header(),
            data=auth.get_auth_data()  # 將認證信息放在 data 中
        )
        
        # 檢查響應
        response.raise_for_status()
        
        # 解析響應
        token_data = response.json()
        
        # 檢查 token
        access_token = token_data.get('access_token')
        if not access_token:
            raise ValueError("回應中找不到 access_token")
            
        # 返回可用於 API 請求的 headers
        return {
            'authorization': f'Bearer {access_token}',
            'Accept-Encoding': 'gzip'
        }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"請求失敗: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("無法解析回應的 JSON 數據")
    except Exception as e:
        raise Exception(f"獲取 token 失敗: {str(e)}")

# 使用示例
