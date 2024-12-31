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
        API_URL = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveTrainDelay?$top=30&$format=JSON"
        api_response = requests.get(API_URL, headers=headers)
        api_response.raise_for_status()
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

# 初始化 Dash 應用程式
app = Dash(__name__)

# 定義應用程式的顏色主題
colors = {
    'background': '#F0F2F6',
    'text': '#2C3E50',
    'primary': '#3498DB',
    'secondary': '#E74C3C',
    'accent': '#2ECC71'
}

app.layout = html.Div([
    # 頁面標題
    html.H1(
        '台鐵列車延誤即時監控',
        style={
            'textAlign': 'center',
            'color': 'white',
            'padding': '15px',
            'backgroundColor': colors['primary'],
            'marginBottom': '20px',
            'borderRadius': '5px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }
    ),
    
    # 自動更新間隔
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 每分鐘更新一次
        n_intervals=0
    ),
    
    # 主要內容區域 - 使用 flexbox 布局
    html.Div([
        # 左側圖表區域
        html.Div([
            dcc.Graph(
                id='bar-chart',
                style={'height': '80vh'}  # 固定圖表高度
            )
        ], style={
            'width': '50%',
            'backgroundColor': 'white',
            'borderRadius': '5px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'padding': '15px',
            'marginRight': '10px'
        }),
        
        # 右側表格區域
        html.Div([
            # 表格容器
            html.Div(
                id='delay-table',
                style={
                    'height': '80vh',  # 固定表格容器高度
                    'overflowY': 'auto',  # 垂直捲動
                    'overflowX': 'hidden',  # 隱藏水平捲動
                }
            )
        ], style={
            'width': '50%',
            'backgroundColor': 'white',
            'borderRadius': '5px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'padding': '15px',
        })
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'padding': '10px',
        'backgroundColor': colors['background'],
        'height': '85vh'  # 設定主容器高度
    })
])

@app.callback(
    [Output('bar-chart', 'figure'),
     Output('delay-table', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_layout(n_intervals):
    headers = get_api_token(APP_ID, APP_KEY, AUTH_URL)
    data = fetch_api_data(headers)
    
    if not data:
        return {}, []

    df = pd.DataFrame(data)
    df['StationName'] = df['StationName'].apply(lambda x: x['Zh_tw'])
    
    # 美化長條圖
    fig = px.bar(
        df,
        x='StationName',
        y='DelayTime',
        title='各站列車延誤時間統計',
        labels={'StationName': '車站名稱', 'DelayTime': '延誤時間(分鐘)'},
        color='DelayTime',
        color_continuous_scale='RdYlBu_r'  # 使用紅黃藍漸層色
    )
    
    # 更新圖表布局
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'color': colors['text'], 'family': 'Arial, 微軟正黑體'},
        title={
            'font': {'size': 24, 'color': colors['text']},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={'tickangle': 45},
        margin={'t': 50, 'l': 50, 'r': 50, 'b': 100},
        hoverlabel={'font_size': 14},
        showlegend=False,
        height=700  # 調整圖表高度
    )
    
    # 添加懸停資訊
    fig.update_traces(
        hovertemplate='<b>車站</b>: %{x}<br>' +
                      '<b>延誤時間</b>: %{y} 分鐘<br>' +
                      '<extra></extra>'
    )
    
    # 定義表格樣式
    table_style = {
        'width': '100%',
        'borderCollapse': 'collapse',
        'fontFamily': 'Arial, 微軟正黑體',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
    }
    
    # 定義表頭樣式
    th_style = {
        'backgroundColor': colors['primary'],
        'color': 'white',
        'padding': '15px',
        'textAlign': 'left',
        'borderBottom': f'2px solid {colors["primary"]}',
        'fontSize': '16px'
    }
    
    # 定義單元格樣式
    td_style = {
        'padding': '12px',
        'textAlign': 'left',
        'borderBottom': '1px solid #eee',
        'fontSize': '14px'
    }

    # 創建表格標題
    table_header = [
        html.Thead(html.Tr([
            html.Th("車次", style=th_style),
            html.Th("車站名稱", style=th_style),
            html.Th("延誤時間", style=th_style),
            html.Th("更新時間", style=th_style)
        ]))
    ]
    
    # 創建表格內容
    table_body = [html.Tbody([
        html.Tr([
            html.Td(row['TrainNo'], style=td_style),
            html.Td(row['StationName'], style=td_style),
            html.Td(f"{row['DelayTime']} 分鐘", style=dict(
                **td_style,
                color='red' if row['DelayTime'] > 10 else 'black'
            )),
            html.Td(row['UpdateTime'], style=td_style)
        ], style={
            'backgroundColor': '#f8f9fa' if i % 2 else 'white',
            'transition': 'background-color 0.3s'
        })
        for i, (_, row) in enumerate(df.iterrows())
    ])]

    return fig, [
        html.H2('即時延誤列表', style={
            'color': colors['text'],
            'marginBottom': '20px',
            'textAlign': 'center'
        }),
        html.Table(table_header + table_body, style=table_style)
    ]

if __name__ == '__main__':
    app.run_server(debug=True)