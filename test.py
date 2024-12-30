# filepath: /c:/Users/CJCU-CC/TDX-test/Test.py
from auth import Auth, get_api_token
import requests
import os
import time
from dotenv import load_dotenv
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# 載入 .env 檔案
load_dotenv()

APP_ID = os.getenv("APP_ID", "")
APP_KEY = os.getenv("APP_KEY", "")
AUTH_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"

def fetch_api_data(headers):
    try:
        # 使用 headers 訪問 API
        API_URL = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveTrainDelay?$top=30&$format=JSON"
        api_response = requests.get(API_URL, headers=headers)
        return api_response.json()

    
    except Exception as e:
        print(f"錯誤: {e}")
        return []

# 獲取帶有 token 的 headers
headers = get_api_token(APP_ID, APP_KEY, AUTH_URL)
print("成功獲取 token")
print("Headers:", headers)

# 建立 Dash 應用程式
app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='live-update-graph', style={'height': '80vh'}),
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # 30 秒
        n_intervals=0
    )
])

@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    data = fetch_api_data(headers)
    df = pd.DataFrame(data)
    print(df)
    if not df.empty:
        df['StationName'] = df['StationName'].apply(lambda x: x['Zh_tw'] if isinstance(x, dict) else x)
        fig = px.bar(df, x='StationName', y='DelayTime', title='Train Delay Time')
        return fig
    return {}

if __name__ == '__main__':
    app.run_server(debug=True)