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
        api_response.raise_for_status()  # 檢查 HTTP 狀態碼
        return api_response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []


# 獲取帶有 token 的 headers
headers = get_api_token(APP_ID, APP_KEY, AUTH_URL)
print("成功獲取 token")
print("Headers:", headers)

# 初始化 Dash 應用程式
app = Dash(__name__)
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 每分鐘更新一次
        n_intervals=0
    ),
    html.Div([
        dcc.Graph(id='bar-chart')
    ], style={'width': '50%', 'display': 'inline-block'}),
    html.Div([
        html.Table(id='delay-table')
    ], style={'width': '50%', 'display': 'inline-block'})
])

@app.callback(
    [Output('bar-chart', 'figure'),
     Output('delay-table', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_layout(n_intervals):
    # headers = {
    #     'authorization': f'Bearer {get_api_token(APP_ID, APP_KEY, AUTH_URL)}'
    # }
    headers = get_api_token(APP_ID, APP_KEY, AUTH_URL)
    data = fetch_api_data(headers)
    
    if not data:
        return {}, []

    df = pd.DataFrame(data)
    df['StationName'] = df['StationName'].apply(lambda x: x['Zh_tw'])
    fig = px.bar(df, x='StationName', y='DelayTime', title='Train Delays')

    table_header = [
        html.Thead(html.Tr([html.Th("Station Name"), html.Th("Delay Time")]))
    ]
    table_body = [html.Tbody([html.Tr([html.Td(row['StationName']), html.Td(row['DelayTime'])]) for index, row in df.iterrows()])]

    return fig, table_header + table_body

if __name__ == '__main__':
    app.run_server(debug=True)