from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from tqdm.auto import tqdm, trange
import plotly.express as px
import plotly.graph_objects as go
import json
import streamlit as st

st.markdown('# 부동산 경매 낙찰가 예측 모델')
st.markdown('''
            ## 목차
            1. 팀 소개
            2. 주제 선정 이유
            3. 데이터 소스
            4. 데이터 전처리 과정
            5. EDA 탐색적 데이터 분석
            6. 결과 해석
            7. 제한점 및 향후 개전 방향
            8. 결롷 
            9. 참고문헌
            10. Q&A
            ''')
