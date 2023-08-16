# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# ## 라이브러리 임포트

from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from tqdm.auto import tqdm, trange
import plotly.express as px
import plotly.graph_objects as go
import json
import streamlit as st
# ### 데이터 불러오기

# +
pd.set_option('mode.chained_assignment',  None)  # SettingWithCopyWarning 무시

# SQLAlchemy를 사용하여 데이터베이스 연결
engine = create_engine("mysql+pymysql://admin:lazyestate@database-1.cr1v98drjdof.ap-northeast-2.rds.amazonaws.com:3306/LE")

# houseinfo_raw 데이터를 DataFrame으로 받기
df_realprice_raw = pd.read_sql_table('realprice1', engine.connect(), index_col='no')
df_realprice_raw['contract_price'] = df_realprice_raw['contract_price']*10000000
df_realprice_raw

# +
pd.set_option('mode.chained_assignment',  None)  # SettingWithCopyWarning 무시

# SQLAlchemy를 사용하여 데이터베이스 연결
engine = create_engine("mysql+pymysql://admin:lazyestate@database-1.cr1v98drjdof.ap-northeast-2.rds.amazonaws.com:3306/LE")

# houseinfo_raw 데이터를 DataFrame으로 받기
df_houseinfo = pd.read_sql_table('houseinfo', engine.connect(), index_col='no')
df_houseinfo
# -

df_realprice_raw.info()

df_realprice = df_realprice_raw.copy()

df_realprice['full_address_road'] = '서울' + ' ' + df_realprice['district'] + ' ' + df_realprice['road_name']

df_realprice[['full_address_road']][df_realprice['full_address_road'].str.contains('압구정로 309')]

df_houseinfo[['full_address_road']]

# +
merged_df = df_houseinfo.merge(df_realprice, on=['full_address_road', 'floor'], how='inner')

merged_df
# -

# 중복 열 삭제
merged_df = merged_df.drop(columns=[
    'city',
    'district',
    'neighborhood',
    'address_number',
    'road_name_y',
    'building_name',
])

# +
# 1. 'contract_year', 'contract_month', 'contract_date' 열을 이용하여 'contract_date_full' 열 생성
merged_df['contract_date_full'] = pd.to_datetime(merged_df['contract_year'].astype(str) + '-' + 
                                                merged_df['contract_month'].astype(str) + '-' + 
                                                merged_df['contract_date'].astype(str))

# 2. 'auction_date'와 'contract_date_full' 사이의 날짜 차이 계산
merged_df['date_difference'] = pd.to_datetime(merged_df['auction_date']) - merged_df['contract_date_full']
# -

merged_df.to_csv("merged_date_difference.csv")

# +
# 각 지역별 데이터의 평균을 계산
summary_df = merged_df.groupby(['region1', 'region2'])[['sale_price', 'contract_price']].mean().reset_index()

# 숫자를 억 단위로 변환하기 위한 함수
def billions_formatter(num):
    return f'{num / 1_0000_0000:.1f}억'


# +
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

fig

# +
# 사용할 색상 조합 변경
color_scale = px.colors.qualitative.Light24

# "서울시 모든 구"의 데이터를 준비 (region2 별로 합산)
all_data_grouped = merged_df.groupby(['region2']).size().reset_index(name='count')

# "서울시 모든 구"에 대한 트레이스 생성
color_dict = {region: color for region, color in zip(all_data_grouped['region2'], color_scale)}
all_trace_colors = all_data_grouped['region2'].map(color_dict)
all_trace = go.Bar(x=all_data_grouped['region2'], y=all_data_grouped['count'], 
                   name='서울시 모든 구', marker_color=all_trace_colors)
traces = [all_trace]

# 각 지역별 데이터와 그래프 생성
for idx, (reg1, reg2) in enumerate(merged_df.groupby(['region1', 'region2']).size().index):
    subset_df = merged_df[(merged_df['region1'] == reg1) & (merged_df['region2'] == reg2)]
    grouped_df = subset_df.groupby(['region3']).size().reset_index(name='count')
    
    trace = go.Bar(x=grouped_df['region3'], y=grouped_df['count'], 
                   name=f'{reg1} {reg2}', marker_color=color_scale[idx % len(color_scale)])
    traces.append(trace)

# 드롭다운 메뉴 설정
buttons = [dict(label="     서울시 모든 구    ", 
                method='update', 
                args=[{'visible': [True] + [False] * (len(traces)-1)}, 
                      {'title': '서울시 구별 경매-실거래 매칭 건수', 'xaxis': {'title': '구'}}])]

for j, (reg1, reg2) in enumerate(merged_df.groupby(['region1', 'region2']).size().index, start=1):
    button = dict(label=f'     {reg1}시 {reg2}     ', 
                  method='update', 
                  args=[{'visible': [i == j for i in range(len(traces))]}, 
                        {'title': f'{reg1}시 {reg2} 동별 경매-실거래 매칭 건수', 'xaxis': {'title': '동'}}])
    buttons.append(button)

# 그래프 레이아웃 설정
layout = go.Layout(title='서울시 구별 동별 경매-실거래 매칭 건수', showlegend=False,
                   updatemenus=[{'buttons': buttons, 
                                 'direction': 'down', 
                                 'active': 0, 
                                 'showactive': True, 
                                 'x': 1,  # x 위치를 중앙으로 조정
                                 'y': 1.07,  # y 위치를 상단으로 조정
                                 'xanchor': 'right',  # x 앵커를 중앙으로 설정
                                 'yanchor': 'top'}],  # y 앵커를 상단으로 설정}
                                 xaxis_title='구', yaxis_title='건수', width=1700, height=800)

# 그래프 생성 및 표시
fig = go.Figure(data=traces, layout=layout)
fig


# +
# 사용할 색상 조합 변경
color_scale = px.colors.qualitative.Light24

# "서울시 모든 구"의 데이터를 준비 (region2 별로 합산)
all_data_grouped = merged_df.groupby(['region2']).size().reset_index(name='count')

# "서울시 모든 구"에 대한 트레이스 생성
color_dict = {region: color for region, color in zip(all_data_grouped['region2'], color_scale)}
all_trace_colors = all_data_grouped['region2'].map(color_dict)
all_trace = go.Bar(x=all_data_grouped['region2'], y=all_data_grouped['count'], 
                   name='서울시 모든 구', marker_color=all_trace_colors)
traces = [all_trace]

# 각 지역별 데이터와 그래프 생성
for idx, (reg1, reg2) in enumerate(merged_df.groupby(['region1', 'region2']).size().index):
    subset_df = merged_df[(merged_df['region1'] == reg1) & (merged_df['region2'] == reg2)]
    grouped_df = subset_df.groupby(['region3']).size().reset_index(name='count')
    
    trace = go.Bar(x=grouped_df['region3'], y=grouped_df['count'], 
                   name=f'{reg1} {reg2}', marker_color=color_scale[idx % len(color_scale)])
    traces.append(trace)

# 슬라이더 스텝 설정
steps = []

# "서울시 모든 구"에 대한 스텝 추가
step = {
    'args': [{'visible': [True] + [False] * (len(traces)-1)}, 
             {'title': '서울시 구별 경매-실거래 매칭 건수', 'xaxis': {'title': '구'}}],
    'label': '서울시 모든 구',
    'method': 'update'
}
steps.append(step)

# 각 구별 스텝 추가
for j, (reg1, reg2) in enumerate(merged_df.groupby(['region1', 'region2']).size().index, start=1):
    step = {
        'args': [{'visible': [i == j for i in range(len(traces))]}, 
                 {'title': f'{reg1} {reg2} 동별 경매-실거래 매칭 건수', 'xaxis': {'title': '동'}}],
        'label': f'{reg2}',
        'method': 'update'
    }
    steps.append(step)

# 슬라이더 설정
sliders = [dict(
    active=0,
    yanchor='top',
    xanchor='left',
    currentvalue=dict(font=dict(size=16), prefix='Currently Displaying: ', visible=True),
    transition=dict(duration=3, easing='cubic-in-out'),
    pad=dict(b=10, t=50),
    len=1.0,  # 슬라이더 길이
    x=0.0,   # 슬라이더의 시작 위치
    y=0,
    steps=steps,
    ticklen=5  # 슬라이더 내부의 틱의 길이 조정
)]

# 그래프 레이아웃 설정
layout = go.Layout(
    title='서울시 구별 동별 경매-실거래 매칭 건수', 
    showlegend=False,
    xaxis_title='구', 
    yaxis_title='건수', 
    width=1700, 
    height=900,  # 그래프 높이를 약간 늘림
    sliders=sliders
)

# 그래프 생성 및 표시
fig = go.Figure(data=traces, layout=layout)
fig

# +
# "서울시 모든 구"의 데이터를 준비 (region2 별로 합산)
all_data_grouped = merged_df.groupby(['region2']).size().reset_index(name='count')

# 파이 차트 데이터 준비
labels = all_data_grouped['region2']
values = all_data_grouped['count']

# 파이 차트 생성
fig = px.pie(all_data_grouped, 
             names='region2', 
             values='count', 
             title='서울시 모든 구별 경매-실거래 매칭 건수')

# 라벨 업데이트 (백분율과 함께 구 이름 표시)
fig.update_traces(textinfo='label+percent', textfont_size=16)
fig.update_layout(width=1000, height=800)
fig.show()

# +
# # 각 region1 + region2 조합별로 데이터 필터링 및 그래프 생성
# for (reg1, reg2) in merged_df.groupby(['region1', 'region2']).size().index:
#     subset_df = merged_df[(merged_df['region1'] == reg1) & (merged_df['region2'] == reg2)]
    
#     # 'full_address_road'와 'floor'로 그룹화하고 해당 그룹의 레코드 수를 계산
#     grouped_df = subset_df.groupby(['full_address_road', 'floor']).size().reset_index(name='count')
    
#     # 'region3'와 'apartment_name'을 합쳐서 새로운 열 생성
#     grouped_df['address_label'] = subset_df['region3'] + ", " + subset_df['apartment_name']
    
#     # plotly express를 사용하여 바 차트 생성 (RdBu 컬러 스키마 사용)
#     fig = px.bar(grouped_df, 
#                  x='address_label', 
#                  y='count', 
#                  color='floor', 
#                  title=f'{reg1} {reg2} - 주소 및 층 별 레코드 수',
#                  labels={'address_label': '주소', 'count': '레코드 수'},
#                  height=600,
#                  color_continuous_scale=px.colors.sequential.RdBu)
    
#     fig.show()

# +
color_scale = px.colors.sequential.Oryel

# 'date_difference'를 기반으로 데이터 필터링
filtered_data = merged_df[merged_df['date_difference'].dt.days.abs() <= 365]

# 'region2'와 'floor'로 그룹화하여 sale_price와 contract_price의 평균 계산
grouped_data_by_region = filtered_data.groupby(['region2', 'floor', ])[['sale_price', 'contract_price']].mean().reset_index()

# sale_price와 contract_price 사이의 가격 차이를 새로운 열로 생성
grouped_data_by_region['price_difference'] = grouped_data_by_region['sale_price'] - grouped_data_by_region['contract_price']


# sale_price와 contract_price의 가격 차이를 나타내는 바 차트 생성
fig2_region_colored = px.bar(grouped_data_by_region, x='region2', y='price_difference', color='floor',
                             color_continuous_scale=color_scale,
                             title='구별 경매매각가와 실거래가의 가격 차이')

fig2_region_colored.show()

# +
# import plotly.express as px

# # date_difference가 365일 이내인 데이터 필터링
# filtered_data = merged_df[merged_df['date_difference'].dt.days.abs() <= 365]

# # 'full_address_road'와 'floor'로 그룹화하여 sale_price와 contract_price의 평균 계산
# grouped_data = filtered_data.groupby(['full_address_road', 'floor'])[['sale_price', 'contract_price']].mean().reset_index()

# # sale_price와 contract_price 사이의 가격 차이 계산하여 새로운 열 생성
# grouped_data['price_difference'] = grouped_data['sale_price'] - grouped_data['contract_price']

# # 주소에서 '구'만 추출하여 새로운 열 생성
# grouped_data['구'] = grouped_data['full_address_road'].str.split().str[1]

# # '구' 별로 데이터를 분할하여 시각화
# for region in grouped_data['구'].unique():
#     subset_data = grouped_data[grouped_data['구'] == region]
    
#     # sale_price와 contract_price 비교 바 플롯 생성
#     fig1 = px.bar(subset_data, x='full_address_road', y=['sale_price', 'contract_price'], 
#                   color='floor', barmode='group', 
#                   title=f'{region} - 매각가와 실거래가 비교',
#                   color_discrete_sequence=px.colors.sequential.Teal)
    
#     fig1.show()

# -

geo_json_gu = json.load(open("../../data/map/서울시_자치구.geojson"))

# +
import plotly.express as px

# 지도 그래프 생성
fig = px.scatter_mapbox(merged_df, lat='latitude', lon='longitude', mapbox_style="carto-positron", 
                        hover_name='full_address_road', 
                        hover_data=['sale_price', 'contract_price'],
                        color_continuous_scale=color_scale, color ='contract_price',
                        zoom=10, height=600)

# 지도 스타일 설정
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

# 구 경계선 나타내기
fig.update_layout(mapbox={
    "layers": [
            {
                "source": geo_json_gu,
                "below":"traces",
                "type": "line",
                "color": "grey",
                "opacity":0.5
            }
        ]
    })
fig.show()

# -

df_price_by_gu = df_realprice_raw.groupby('district')[['contract_price']].mean()
df_price_by_gu = df_price_by_gu.reset_index()
df_price_by_gu

# +
# 레전드에 억 단위로 표시하기 위한 설정
max_value = df_price_by_gu['contract_price'].max()
ticks = list(range(0, int(max_value), int(5e8))) + [int(max_value)]

# Choropleth Map 생성
fig = px.choropleth_mapbox(df_price_by_gu,
                           geojson=geo_json_gu,
                           locations='district',
                           color='contract_price',
                           color_continuous_scale='Oryel', 
                           featureidkey='properties.SIG_KOR_NM',
                           mapbox_style='carto-positron',
                           height=1000,
                           zoom=10.5,
                           center={"lat": 37.563383, "lon": 126.996039},
                           opacity=0.5,
                           title='서울시 자치구별 실거래가격',
                           range_color=(0, max_value),
                           color_continuous_midpoint=max_value/2
                          )

# 호버 템플릿 설정
fig.update_traces(hovertemplate='<b>%{location}</b><br>평균 실거래가: ' + 
                  '%{z:₩,.0f}<br>' + 
                  '<b>억 단위:</b> ' + 
                  '<b>' + '%{customdata[0]:.1f}' + '억</b>',
                  customdata=np.array([df_price_by_gu['contract_price'] / 1_0000_0000]).T)

# 레전드 설정
fig.update_layout(coloraxis_colorbar=dict(
    tickvals=ticks,title="평균 실거래가",
    ticktext=[billions_formatter(tick) for tick in ticks]
))

fig.show()

# -


