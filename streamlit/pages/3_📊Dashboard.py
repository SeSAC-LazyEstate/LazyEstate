import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from sqlalchemy import create_engine
import streamlit as st
import pymysql
import pydeck as pdk

# page config
st.set_page_config(layout='wide', initial_sidebar_state='auto', menu_items={"About":"test"})

# sidebar

st.sidebar.header('데이터 시각화')

# SQLAlchemy를 사용하여 데이터베이스 연결
engine = create_engine("mysql+pymysql://"+ st.secrets['DB_USERNAME'] +":"+ st.secrets['DB_PASSWORD'] + "@" + st.secrets['DB_URL'])

# houseinfo_raw 데이터를 DataFrame으로 받기
df_realprice = pd.read_sql_table('realprice', engine.connect(), index_col='no')
df_houseinfo = pd.read_sql_table('houseinfo', engine.connect(), index_col='no')

df_realprice['contract_price'] = df_realprice['contract_price']

df_realprice['full_address_road'] = '서울' + ' ' + df_realprice['district'] + ' ' + df_realprice['road_name']
df_merged = df_houseinfo.merge(df_realprice, on=['full_address_road', 'floor'], how='inner')
df_merged = df_merged.drop(columns=[
    'city',
    'district',
    'neighborhood',
    'address_number',
    'road_name_y',
    'building_name',
])
# 1. 'contract_year', 'contract_month', 'contract_date' 열을 이용하여 'contract_date_full' 열 생성
df_merged['contract_date_full'] = pd.to_datetime(df_merged['contract_year'].astype(str) + '-' + 
                                                df_merged['contract_month'].astype(str) + '-' + 
                                                df_merged['contract_date'].astype(str))

# 2. 'auction_date'와 'contract_date_full' 사이의 날짜 차이 계산
df_merged['date_difference'] = pd.to_datetime(df_merged['auction_date']) - df_merged['contract_date_full']

# 각 지역별 데이터의 평균을 계산
summary_df = df_merged.groupby(['region1', 'region2'])[['sale_price', 'contract_price']].mean().reset_index()

# 숫자를 억 단위로 변환하기 위한 함수
def billions_formatter(num):
    return f'{num / 1_0000_0000:.1f}억'




# 헤더
st.header('Dashboard')

# 컬럼
col1, col2 = st.columns([1,1])

with col1:
    col1.markdown('## 서울시 아파트 거래량')

    # tabs
    tab1, tab2, tab3 = st.tabs(["경매가", "실거래가", "경매가+실거래가"])

    with tab1:
        tab1.subheader("경매가")
        df_houseinfo

    with tab2:
        tab2.subheader("실거래가")
        df_realprice

    with tab3:
        tab3.subheader("경매가+실거래가")
        df_merged

with col2:
    col2.markdown('## TOP5 ')
    # 상위 5개 구를 실거래가 기준으로 선택
    sorted_df = summary_df.sort_values(by='contract_price', ascending=False).head(5)

    # y축의 표시 방식을 위한 변수 정의
    max_val = max(sorted_df['sale_price'].max(), sorted_df['contract_price'].max())
    ticks = [i for i in range(0, int(max_val) + 500_000_000, 500_000_000)]

    # 데이터 준비
    x = sorted_df['region2']
    y1 = sorted_df['sale_price']
    y2 = sorted_df['contract_price']

    # 그래프 생성
    fig = go.Figure()

    # 경매매각가 바 추가
    fig.add_trace(go.Bar(x=x, y=y1, name='경매매각가'))

    # 실거래가 바 추가
    fig.add_trace(go.Bar(x=x, y=y2, name='실거래가'))

    # 레이아웃 설정
    fig.update_layout(title='서울시 구별 평균 경매매각가, 실거래가 (상위 5개 구)', 
                    xaxis_title="서울시 구", 
                    yaxis_title="평균 가격",
                    yaxis_tickvals=ticks, 
                    yaxis_ticktext=[billions_formatter(tick) for tick in ticks],
                    barmode='group',
                    legend_title_text='거래 유형',
                    width=1700, height=1000)

    # 호버 템플릿 수정
    fig.update_traces(hovertemplate='%{y:,.0f}원<br>%{x}')

    st.plotly_chart(fig, use_container_width=True)








# y축의 표시 방식을 위한 변수 정의
max_val = max(summary_df['sale_price'].max(), summary_df['contract_price'].max())
ticks = [i for i in range(0, int(max_val) + 500_000_000, 500_000_000)]

# 데이터 준비
x = summary_df['region2']
y1 = summary_df['sale_price']
y2 = summary_df['contract_price']

# 그래프 생성
fig = go.Figure()

# 경매매각가 바 추가
fig.add_trace(go.Bar(x=x, y=y1, name='경매매각가'))

# 실거래가 바 추가
fig.add_trace(go.Bar(x=x, y=y2, name='실거래가'))

# 레이아웃 설정
fig.update_layout(title='서울시 구별 평균 경매매각가, 실거래가', 
                xaxis_title="서울시 구", 
                yaxis_title="평균 가격",
                yaxis_tickvals=ticks, 
                yaxis_ticktext=[billions_formatter(tick) for tick in ticks],
                barmode='group',
                legend_title_text='거래 유형',
                width=1700, height=1000)

# 호버 템플릿 수정
fig.update_traces(hovertemplate='%{y:,.0f}원<br>%{x}')

st.plotly_chart(fig, use_container_width=True)

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=37.563383,
        longitude=126.996039,
        zoom=10.5,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=df_merged,
           get_position='[longitude, latitude]',
           radius=200,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),
        pdk.Layer(
            'HeatmapLayer',
            data=df_merged,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))





