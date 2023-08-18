import pandas as pd
import numpy as np
import plotly
import json
from sqlalchemy import create_engine
import streamlit as st
import pymysql

# page config
st.set_page_config(layout='wide', initial_sidebar_state='auto', menu_items={"About":"test"})

# sidebar

st.sidebar.header('데이터 시각화')

# SQLAlchemy를 사용하여 데이터베이스 연결
engine = create_engine("mysql+pymysql://admin:lazyestate@database-1.cr1v98drjdof.ap-northeast-2.rds.amazonaws.com:3306/LE")

# houseinfo_raw 데이터를 DataFrame으로 받기
df_realprice = pd.read_sql_table('realprice', engine.connect(), index_col='no')
df_houseinfo = pd.read_sql_table('houseinfo', engine.connect(), index_col='no')

df_realprice['contract_price'] = df_realprice['contract_price']*10000000

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

# 각 지역별 데이터의 평균을 계산
summary_df = df_merged.groupby(['region1', 'region2'])[['sale_price', 'contract_price']].mean().reset_index()

# 숫자를 억 단위로 변환하기 위한 함수
def billions_formatter(num):
    return f'{num / 1_0000_0000:.1f}억'

# Creating the dataframe using the provided data

data = {
    'month': ['2022-08-01', '2022-09-01', '2022-09-01', '2022-10-01', '2022-11-01', '2022-12-01', '2023-01-01', 
            '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01', '2023-06-01', '2023-07-01'],
    'auction_total': [21, 40, 40, 53, 82, 42, 49, 61, 54, 60, 42, 61, 77],
    'auction_sale': [5, 7, 7, 8, 12, 8, 15, 23, 15, 8, 16, 13, 29],
    'sale_per': [23.8, 17.5, 17.5, 15.1, 14.6, 19.0, 30.6, 37.7, 27.8, 13.3, 38.1, 21.6, 37.7],
    'price_per': [98.6, 95.0, 95.0, 92.8, 84.5, 68.8, 85.9, 79.3, 74.0, 76.8, 83.1, 85.9, 84.1]
}

df = pd.DataFrame(data)
df
