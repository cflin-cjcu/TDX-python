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
import dash_leaflet as dl

# 載入 .env 檔案
load_dotenv()

APP_ID = os.getenv("APP_ID", "")
APP_KEY = os.getenv("APP_KEY", "")
AUTH_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"

# 台灣車站經緯度數據
STATION_LOCATIONS = {
    '臺北': [25.0478, 121.5170],
    '板橋': [25.0145, 121.4635],
    '桃園': [24.9893, 121.3133],
    '中壢': [24.9539, 121.2256],
    '新竹': [24.8015, 120.9715],
    '苗栗': [24.5700, 120.8227],
    '臺中': [24.1369, 120.6869],
    '彰化': [24.0819, 120.5386],
    '員林': [23.9590, 120.5714],
    '斗六': [23.7117, 120.5419],
    '嘉義': [23.4791, 120.4412],
    '新營': [23.3061, 120.3162],
    '臺南': [22.9971, 120.2117],
    '高雄': [22.6394, 120.3024],
    '屏東': [22.6698, 120.4865],
    '花蓮': [23.9927, 121.6011],
    '臺東': [22.7933, 121.1230]
}

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
        # 左側區域（長條圖和列表）
        html.Div([
            # 長條圖容器
            html.Div([
                dcc.Graph(
                    id='bar-chart',
                    style={'height': '38vh'}
                )
            ], style={
                'backgroundColor': 'white',
                'borderRadius': '5px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'padding': '10px',
                'marginBottom': '10px'
            }),
            
            # 延誤列表容器
            html.Div([
                html.Div(
                    id='delay-table',
                    style={
                        'height': '42vh',
                        'overflowY': 'auto',
                        'overflowX': 'hidden',
                    }
                )
            ], style={
                'backgroundColor': 'white',
                'borderRadius': '5px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'padding': '15px'
            })
        ], style={
            'width': '50%',
            'marginRight': '10px',
            'display': 'flex',
            'flexDirection': 'column'
        }),
        
        # 右側地圖區域
        html.Div([
            dl.Map(
                id='train-map',
                center=[23.8, 121],
                zoom=7.2,
                style={
                    'height': '82vh',
                    'width': '100%',
                },
                children=[
                    dl.TileLayer(
                        url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    ),
                    dl.LayerGroup(id='marker-group')
                ]
            )
        ], style={
            'width': '50%',
            'backgroundColor': 'white',
            'borderRadius': '5px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'padding': '10px'
        })
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'padding': '10px',
        'backgroundColor': colors['background'],
        'height': '85vh'
    })
])

@app.callback(
    [Output('bar-chart', 'figure'),
     Output('delay-table', 'children'),
     Output('marker-group', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_layout(n_intervals):
    headers = get_api_token(APP_ID, APP_KEY, AUTH_URL)
    data = fetch_api_data(headers)
    
    if not data:
        return {}, [], []

    df = pd.DataFrame(data)
    df['StationName'] = df['StationName'].apply(lambda x: x['Zh_tw'])
    
    # 創建地圖標記
    markers = []
    for station, coords in STATION_LOCATIONS.items():
        station_data = df[df['StationName'].str.contains(station)]
        if not station_data.empty:
            delay_time = station_data.iloc[0]['DelayTime']
            color = 'red' if delay_time > 10 else 'blue'
            markers.append(
                dl.CircleMarker(
                    center=coords,
                    radius=15,
                    color="red",
                    fillColor="red",
                    fillOpacity=0.7,
                    weight=1,
                    children=[
                        dl.Tooltip(f"{station}: 延誤 {delay_time} 分鐘"),
                        html.Div(
                            str(delay_time),
                            style={
                                'color': 'white',
                                'textAlign': 'center',
                                'fontSize': '12px',
                                'fontWeight': 'bold',
                                'marginTop': '-8px'
                            }
                        )
                    ]
                )
            )
    
    # 美化長條圖
    fig = px.bar(
        df,
        x='StationName',
        y='DelayTime',
        title='各站列車延誤時間統計',
        labels={'StationName': '車站名稱', 'DelayTime': '延誤時間(分鐘)'},
        color='DelayTime',
        color_continuous_scale='RdYlBu_r'
    )
    
    # 更新圖表布局
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'color': colors['text'], 'family': 'Arial, 微軟正黑體'},
        title={
            'font': {'size': 20, 'color': colors['text']},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={'tickangle': 45},
        margin={'t': 40, 'l': 50, 'r': 50, 'b': 80},
        hoverlabel={'font_size': 14},
        showlegend=False,
        height=300  # 調整圖表高度
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

    table_header = [
        html.Thead(html.Tr([
            html.Th("車次", style=th_style),
            html.Th("車站名稱", style=th_style),
            html.Th("延誤時間", style=th_style),
            html.Th("更新時間", style=th_style)
        ]))
    ]
    
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
    ], markers

if __name__ == '__main__':
    app.run_server(debug=True)