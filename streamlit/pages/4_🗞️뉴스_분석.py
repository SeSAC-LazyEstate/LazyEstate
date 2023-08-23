import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import streamlit as st
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.family']='AppleGothic'
from wordcloud import WordCloud
import re
from collections import Counter
from konlpy.tag import Okt
import nltk
from konlpy.tag import Mecab

# page config
st.set_page_config(layout='wide', initial_sidebar_state='auto')
st.set_option('deprecation.showPyplotGlobalUse', False)

# 헤더
st.header('다음뉴스 & 연합뉴스 분석')

st.markdown("""
            
### 빅데이터 분석의 4가지 단계
#### 1. 묘사분석 (Descriptive Analysis)

정의: 묘사분석은 과거와 현재의 데이터를 활용해 일어난 사건이나 현상을 '무엇이 일어났는지' 설명하는 분석 방법입니다. 기본적인 데이터 집계, 통계 및 시각화를 통해 데이터의 주요 특성 및 패턴을 확인합니다.
사례: 한 달 동안의 웹사이트 방문자 통계를 확인할 때, 각각의 날짜별 방문자 수, 평균 체류 시간, 주요 트래픽 소스 등을 보여주는 대시보드를 사용합니다. 이러한 대시보드는 묘사분석을 통해 웹사이트의 트래픽 패턴을 파악할 수 있게 도와줍니다.
뉴스 데이터 사례: 최근 6개월 동안 뉴스 헤드라인을 분석하여 주요 이슈나 키워드의 빈도를 파악합니다. 예를 들어, "환경"이나 "기후 변화"라는 키워드가 얼마나 자주 등장하는지, 특정 정치인의 이름이 어느 기간 동안 얼마나 많이 언급되었는지를 확인합니다.


#### 2. 진단분석 (Diagnostic Analysis)

정의: 진단분석은 '왜 그렇게 일어났는지'를 파악하기 위해 데이터 내에서 원인과 결과 간의 관계나 연관성을 탐색하는 분석 방법입니다.
사례: 웹사이트의 특정 페이지에서 이탈률이 급증했다면, 진단분석을 통해 해당 페이지의 변경 이력, 사용자 피드백, 서버 오류 로그 등을 분석하여 이탈률 증가의 원인을 파악합니다.
뉴스 데이터 사례: "기후 변화" 키워드의 언급 빈도가 급증한 원인을 파악하기 위해 관련된 뉴스 기사들을 상세히 분석합니다. 예를 들어, 특정 국제 기후 회의나 환경 관련 사건이 발생했는지, 유명 연예인이나 정치인이 관련된 발언을 했는지 등을 파악합니다.


#### 3. 예측분석 (Predictive Analysis)

정의: 예측분석은 현재와 과거의 데이터를 기반으로 미래의 이벤트나 결과를 예측하는 분석 방법입니다. 기계 학습 및 통계적 모델링 기법을 활용합니다.
사례: 쇼핑몰에서는 고객의 과거 구매 이력, 검색 패턴, 페이지 방문 이력 등을 기반으로 미래에 어떤 제품을 구매할 확률이 높은지 예측하는 모델을 만듭니다. 이를 통해 특정 사용자에게 개인화된 광고나 추천을 제공할 수 있습니다.
뉴스 데이터 사례: 과거 뉴스 데이터와 트렌드를 기반으로, 앞으로 어떤 키워드나 주제가 뜨거운 이슈가 될 가능성이 있는지 예측합니다. 예를 들어, 지속적으로 증가하는 '재생 에너지' 키워드 언급 빈도를 바탕으로, 이 주제가 앞으로 더 주요 뉴스 이슈로 부상할 것으로 예측할 수 있습니다.

#### 4. 처방분석 (Prescriptive Analysis)

정의: 처방분석은 예측된 결과를 기반으로 '어떻게 최선의 결과를 얻을 수 있을까'를 결정하는 조치나 전략을 추천하는 분석 방법입니다. 복잡한 최적화 및 시뮬레이션 기법을 활용합니다.
사례: 물류회사는 처방분석을 활용해 특정 상품을 어떤 창고에서 보관하고, 어떤 경로로 배송할 것인지 결정합니다. 예측분석으로 특정 지역의 수요가 증가할 것이라는 정보를 얻었다면, 처방분석을 통해 최적의 재고 관리 및 배송 전략을 수립하여 비용을 최소화하고 고객 만족도를 최대화합니다.
뉴스 데이터 사례: 뉴스 콘텐츠 제공자나 언론사의 입장에서, '재생 에너지' 키워드가 뜨거운 이슈로 예측된다면, 이 주제와 관련된 심층 기사나 특집 프로그램을 기획하는 것을 추천합니다. 이를 통해 독자나 시청자의 관심을 끌어, 더 많은 트래픽이나 높은 시청률을 기대할 수 있습니다.
            """)

# 데이터 로드
df_금리 = pd.read_csv('../daum_news/금리.csv')
df_대출 = pd.read_csv('../daum_news/대출.csv')
df_아파트 = pd.read_csv('../daum_news/아파트.csv', index_col=0)
df_부동산_연합 = pd.read_csv('../daum_news/부동산_연합뉴스.csv', index_col=0)
df_부동산_다음 = pd.read_csv('../daum_news/부동산_다음뉴스.csv')



def format_day_column(df):
    df['day'] = df['day'].astype(str)
    df['day'] = pd.to_datetime(df['day'])
    df['day'] = df['day'].dt.strftime('%m-%d')
    df.drop([col for col in df.columns if 'Unnamed' in col], axis=1)
    
    return df

df_금리 = format_day_column(df_금리)
df_대출 = format_day_column(df_대출)
df_아파트 = format_day_column(df_아파트)
df_부동산_다음 = format_day_column(df_부동산_다음)




col1, col2 = st.columns([1,1])

# 일자별 뉴스 기사 개수
image = Image.open('../daum_news/일자별 뉴스 기사 개수.png')
col1.image(image, caption=None, width=None, use_column_width=True, clamp=False, channels="RGB", output_format="auto")

def display_top_nouns(count, top_n=50):
    """
    Display a bar chart of the top N nouns based on their frequencies.
    
    Parameters:
    - count: Counter object containing word frequencies.
    - top_n: Number of top nouns to display (default is 50).
    """
    
    # Extract top N nouns
    top_nouns = dict(count.most_common(top_n))

    # Create a bar chart using Plotly Express
    fig = px.bar(x=list(top_nouns.keys()), y=list(top_nouns.values()), title=f"Top {top_n} 빈도수 단어들")
    fig.update_layout(xaxis_title="단어", yaxis_title="횟수", xaxis_tickangle=-45)
    
    st.plotly_chart(fig, use_container_width=True)

def display_noun_wordcloud(df, column_name="text"):
    """
    Create and display a word cloud of nouns from the given DataFrame.
    
    Parameters:
    - df: DataFrame containing the text data.
    - stop_words: List of words to be excluded from the wordcloud.
    - column_name: Name of the column in df containing the text data (default is "text").
    """
    
    # Combine all the text from the 'text' column
    text = ' '.join(df[column_name])
    
    # Extract nouns from the text
    mecab = Mecab()
    nouns = mecab.nouns(text)
    nouns = [n for n in nouns if len(n) > 1 and n not in stop_words]
    
    # Calculate frequency of each noun
    count = Counter(nouns)
    
    # Generate word cloud
    wordcloud = WordCloud(font_path="font/AppleGothic.ttf",
                          background_color='white',
                          max_words=150,
                          max_font_size=150).generate_from_frequencies(count)
    
    # Display word cloud
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.subheader('명사 워드 클라우드')
    st.pyplot(use_container_width=True)
    return count


stop_words = ['아', '휴', '아이구', '아이쿠', '아이고', '어', '나', '우리', '저희', '따라', '의해', '을', '를', '에', '의', '가', '으로', '로', '에게', '뿐이다', '의거하여', '근거하여', '입각하여', '기준으로', '예하면', '예를 들면', '예를 들자면', '저', '소인', '소생', '저희', '지말고', '하지마', '하지마라', '다른', '물론', '또한', '그리고', '비길수 없다', '해서는 안된다', '뿐만 아니라', '만이 아니다', '만은 아니다', '막론하고', '관계없이', '그치지 않다', '그러나', '그런데', '하지만', '든간에', '논하지 않다', '따지지 않다', '설사', '비록', '더라도', '아니면', '만 못하다', '하는 편이 낫다', '불문하고', '향하여', '향해서', '향하다', '쪽으로', '틈타', '이용하여', '타다', '오르다', '제외하고', '이 외에', '이 밖에', '하여야', '비로소', '한다면 몰라도', '외에도', '이곳', '여기', '부터', '기점으로', '따라서', '할 생각이다', '하려고하다', '이리하여', '그리하여', '그렇게 함으로써', '하지만', '일때', '할때', '앞에서', '중에서', '보는데서', '으로써', '로써', '까지', '해야한다', '일것이다', '반드시', '할줄알다', '할수있다', '할수있어', '임에 틀림없다', '한다면', '등', '등등', '제', '겨우', '단지', '다만', '할뿐', '딩동', '댕그', '대해서', '대하여', '대하면', '훨씬', '얼마나', '얼마만큼', '얼마큼', '남짓', '여', '얼마간', '약간', '다소', '좀', '조금', '다수', '몇', '얼마', '지만', '하물며', '또한', '그러나', '그렇지만', '하지만', '이외에도', '대해 말하자면', '뿐이다', '다음에', '반대로', '반대로 말하자면', '이와 반대로', '바꾸어서 말하면', '바꾸어서 한다면', '만약', '그렇지않으면', '까악', '툭', '딱', '삐걱거리다', '보드득', '비걱거리다', '꽈당', '응당', '해야한다', '에 가서', '각', '각각', '여러분', '각종', '각자', '제각기', '하도록하다', '와', '과', '그러므로', '그래서', '고로', '한 까닭에', '하기 때문에', '거니와', '이지만', '대하여', '관하여', '관한', '과연', '실로', '아니나다를가', '생각한대로', '진짜로', '한적이있다', '하곤하였다', '하', '하하', '허허', '아하', '거바', '와', '오', '왜', '어째서', '무엇때문에', '어찌', '하겠는가', '무슨', '어디', '어느곳', '더군다나', '하물며', '더욱이는', '어느때', '언제', '야', '이봐', '어이', '여보시오', '흐흐', '흥', '휴', '헉헉', '헐떡헐떡', '영차', '여차', '어기여차', '끙끙', '아야', '앗', '아야', '콸콸', '졸졸', '좍좍', '뚝뚝', '주룩주룩', '솨', '우르르', '그래도', '또', '그리고', '바꾸어말하면', '바꾸어말하자면', '혹은', '혹시', '답다', '및', '그에 따르는', '때가 되어', '즉', '지든지', '설령', '가령', '하더라도', '할지라도', '일지라도', '지든지', '몇', '거의', '하마터면', '인젠', '이젠', '된바에야', '된이상', '만큼\t어찌됏든', '그위에', '게다가', '점에서 보아', '비추어 보아', '고려하면', '하게될것이다', '일것이다', '비교적', '좀', '보다더', '비하면', '시키다', '하게하다', '할만하다', '의해서', '연이서', '이어서', '잇따라', '뒤따라', '뒤이어', '결국', '의지하여', '기대여', '통하여', '자마자', '더욱더', '불구하고', '얼마든지', '마음대로', '주저하지 않고', '곧', '즉시', '바로', '당장', '하자마자', '밖에 안된다', '하면된다', '그래', '그렇지', '요컨대', '다시 말하자면', '바꿔 말하면', '즉', '구체적으로', '말하자면', '시작하여', '시초에', '이상', '허', '헉', '허걱', '바와같이', '해도좋다', '해도된다', '게다가', '더구나', '하물며', '와르르', '팍', '퍽', '펄렁', '동안', '이래', '하고있었다', '이었다', '에서', '로부터', '까지', '예하면', '했어요', '해요', '함께', '같이', '더불어', '마저', '마저도', '양자', '모두', '습니다', '가까스로', '하려고하다', '즈음하여', '다른', '다른 방면으로', '해봐요', '습니까', '했어요', '말할것도 없고', '무릎쓰고', '개의치않고', '하는것만 못하다', '하는것이 낫다', '매', '매번', '들', '모', '어느것', '어느', '로써', '갖고말하자면', '어디', '어느쪽', '어느것', '어느해', '어느 년도', '라 해도', '언젠가', '어떤것', '어느것', '저기', '저쪽', '저것', '그때', '그럼', '그러면', '요만한걸', '그래', '그때', '저것만큼', '그저', '이르기까지', '할 줄 안다', '할 힘이 있다', '너', '너희', '당신', '어찌', '설마', '차라리', '할지언정', '할지라도', '할망정', '할지언정', '구토하다', '게우다', '토하다', '메쓰겁다', '옆사람', '퉤', '쳇', '의거하여', '근거하여', '의해', '따라', '힘입어', '그', '다음', '버금', '두번째로', '기타', '첫번째로', '나머지는', '그중에서', '견지에서', '형식으로 쓰여', '입장에서', '위해서', '단지', '의해되다', '하도록시키다', '뿐만아니라', '반대로', '전후', '전자', '앞의것', '잠시', '잠깐', '하면서', '그렇지만', '다음에', '그러한즉', '그런즉', '남들', '아무거나', '어찌하든지', '같다', '비슷하다', '예컨대', '이럴정도로', '어떻게', '만약', '만일', '위에서 서술한바와같이', '인 듯하다', '하지 않는다면', '만약에', '무엇', '무슨', '어느', '어떤', '아래윗', '조차', '한데', '그럼에도 불구하고', '여전히', '심지어', '까지도', '조차도', '하지 않도록', '않기 위하여', '때', '시각', '무렵', '시간', '동안', '어때', '어떠한', '하여금', '네', '예', '우선', '누구', '누가 알겠는가', '아무도', '줄은모른다', '줄은 몰랏다', '하는 김에', '겸사겸사', '하는바', '그런 까닭에', '한 이유는', '그러니', '그러니까', '때문에', '그', '너희', '그들', '너희들', '타인', '것', '것들', '너', '위하여', '공동으로', '동시에', '하기 위하여', '어찌하여', '무엇때문에', '붕붕', '윙윙', '나', '우리', '엉엉', '휘익', '윙윙', '오호', '아하', '어쨋든', '만 못하다\t하기보다는', '차라리', '하는 편이 낫다', '흐흐', '놀라다', '상대적으로 말하자면', '마치', '아니라면', '쉿', '그렇지 않으면', '그렇지 않다면', '안 그러면', '아니었다면', '하든지', '아니면', '이라면', '좋아', '알았어', '하는것도', '그만이다', '어쩔수 없다', '하나', '일', '일반적으로', '일단', '한켠으로는', '오자마자', '이렇게되면', '이와같다면', '전부', '한마디', '한항목', '근거로', '하기에', '아울러', '하지 않도록', '않기 위해서', '이르기까지', '이 되다', '로 인하여', '까닭으로', '이유만으로', '이로 인하여', '그래서', '이 때문에', '그러므로', '그런 까닭에', '알 수 있다', '결론을 낼 수 있다', '으로 인하여', '있다', '어떤것', '관계가 있다', '관련이 있다', '연관되다', '어떤것들', '에 대해', '이리하여', '그리하여', '여부', '하기보다는', '하느니', '하면 할수록', '운운', '이러이러하다', '하구나', '하도다', '다시말하면', '다음으로', '에 있다', '에 달려 있다', '우리', '우리들', '오히려', '하기는한데', '어떻게', '어떻해', '어찌됏어', '어때', '어째서', '본대로', '자', '이', '이쪽', '여기', '이것', '이번', '이렇게말하자면', '이런', '이러한', '이와 같은', '요만큼', '요만한 것', '얼마 안 되는 것', '이만큼', '이 정도의', '이렇게 많은 것', '이와 같다', '이때', '이렇구나', '것과 같이', '끼익', '삐걱', '따위', '와 같은 사람들', '부류의 사람들', '왜냐하면', '중의하나', '오직', '오로지', '에 한하다', '하기만 하면', '도착하다', '까지 미치다', '도달하다', '정도에 이르다', '할 지경이다', '결과에 이르다', '관해서는', '여러분', '하고 있다', '한 후', '혼자', '자기', '자기집', '자신', '우에 종합한것과같이', '총적으로 보면', '총적으로 말하면', '총적으로', '대로 하다', '으로서', '참', '그만이다', '할 따름이다', '쿵', '탕탕', '쾅쾅', '둥둥', '봐', '봐라', '아이야', '아니', '와아', '응', '아이', '참나', '년', '월', '일', '령', '영', '일', '이', '삼', '사', '오', '육', '륙', '칠', '팔', '구', '이천육', '이천칠', '이천팔', '이천구', '하나', '둘', '셋', '넷', '다섯', '여섯', '일곱', '여덟', '아홉', '령', '영', '', '\n', "'", '…', ',', '[', ']', '(', ')', '"', '주', '에', '코스닥', '특징', '종목', '·', '장', '코스피', '증시', '-', '적', '도', '기술', '분석', '마감', '‘', '`', '요약', '가', '’', '의', '이', '오전', '★', '은', '“', '대', '”', '한', 'B', '로', '?', '3', '선', 'A', '오후', '는', '5', '!', '"…', '상', '들', '1', '만에', '제', '2', '…"', '20', '일', '서', '명', "'…", '기', '···', '10', '소', '등', '으로', '자', '전', '률', '미', '…', '50', '세', '시', '안', '폭', "…'", '만', '9', 'VI', '까지', '눈', '더', 'e', '량', '고', '인', '52', '성', '띄네', '1%', '부터', '다', '감', '을', '지', '4', '에도', '수', '7', '것', '째', '체크', '기', '···', '중', '계', '관련', '왜', '1억원', '총', '내', '과', '젠', '또', '연', '엔', '차', '굿모닝', '할', '8', '.', '보다', '새', '주간', '전망', '추천', '이슈', '플러스', '사', '개월', '때', '..', '임', '속', '’…', 'G', '나', '개', '원', '에서', '하는', '이유', '달', '→', '권', '?…', '단독', '간', '배', '30', 'K', '저', '와', '하', '/', '1조', '6', '두', '해야', '분', '형', '황', '공', '&', '앞두고', '보', '문', '이번', '익', 'X', '1억', ']"', '치', '산', '를', '오', '해', 'S', '우리', '그', '된', '준', '▶', '건', '재', '반', '라', '10년', '초', '3분', '월', '신', 'p', '급', '조', '줄', '경', '했다', '구', '진', '이어', '올', '발', 'vs', '강', '국', '9억', '1년', '난', '판', '면', '"(', '`…', '살', '아', '인데', '번', '텍', '팜', '8월', 'Q', '메', '2년', '점', '하고', '10월', 'D', '비', '됐다', '채', "]'", '보니', '손', '확', '종', '동', '팔', '40', '타', '~', '9월', '2100', '30%', '땐', '말', '한다', '요', "',", '스', '…`', '단', '16', '길', '12', '3억', '회', '될까', '호', '용', '2조', '번째', '일까', '듯', '최', '\n', "'", '…', ',', '[', ']', '(', ')', '"', '주', '에', '코스닥', '특징', '종목', '·', '장', '코스피', '증시', '-', '적', '도', '기술', '분석', '마감', '‘', '`', '요약', '가', '’', '의', '이', '오전', '★', '은', '“', '대', '”', '한', 'B', '로', '?', '3', '선', 'A', '오후', '는', '5', '!', '"…', '상', '들', '1', '만에', '제', '2', '…"', '20', '일', '서', '명', "'…", '기', '···', '10', '소', '등', '으로', '자', '전', '률', '미', '…', '50', '세', '시', '안', '폭', "…'", '만', '9', 'VI', '까지', '눈', '더', 'e', '량', '고', '인', '52', '성', '띄네', '1%', '부터', '다', '감', '을', '지', '4', '에도', '수', '7', '것', '째', '체크', '기', '···', '중', '계', '관련', '왜', '1억원', '총', '내', '과', '젠', '또', '연', '엔', '차', '굿모닝', '할', '8', '.', '보다', '새', '주간', '전망', '추천', '이슈', '플러스', '사', '개월', '때', '..', '임', '속', '’…', 'G', '나', '개', '원', '에서', '하는', '이유', '달', '→', '권', '?…', '단독', '간', '배', '30', 'K', '저', '와', '하', '/', '1조', '6', '두', '해야', '분', '형', '황', '공', '&', '앞두고', '보', '문', '이번', '익', 'X', '1억', ']"', '치', '산', '를', '오', '해', 'S', '우리', '그', '된', '준', '▶', '건', '재', '반', '라', '10년', '초', '3분', '월', '신', 'p', '급', '조', '줄', '경', '했다', '구', '진', '이어', '올', '발', 'vs', '강', '국', '9억', '1년', '난', '판', '면', '"(', '`…', '살', '아', '인데', '번', '텍', '팜', '8월', 'Q', '메', '2년', '점', '하고', '10월', 'D', '비', '됐다', '채', "]'", '보니', '손', '확', '종', '동', '팔', '40', '타', '~', '9월', '2100', '30%', '땐', '말', '한다', '요', "',", '스', '…`', '단', '16', '길', '12', '3억', '회', '될까', '호', '용', '2조', '번째', '일까', '듯', '최', '](', '0', '것으로', '이후', '지난', '이날', '금지', '7월', '재배포', '따르면', '대한', '경기', '최근', '있는', '올해', '지난해', '6월', '위해', '15', '무단전재', '있다는', '며', '현재', '이라고', '전재', '가능성이', '이는',    '0', '지난', '것으로', '최근', '금지', '재배포', '있는', '위해', '말했다', '따르면', '위한', '며', '최대', '무단전재', '통해', 
    '이라고', '대한', '지난해', '등을', '올해', '이후', '밝혔다', '저작권자', '대해', '포인트', '대비', '같은', '전재', '경우', 
    '관계자는', '전체', '가장', '지난달', '16일', '받은', 'kr', '대상으로', '무단', '있다는', '것이다', '17일', '은행권', '이달', 
    '6월', '만큼', '이에', '금융당국은', '관리', '특히', '7월', '약', '기간', '추가', 'c', '주요', 'com', '등이', '2023', 
    '현재', '등으로', 'www', 'co', '해당', '국유재산', '가운데', '된다', '평균', '돈을', '이날', '재배포금지', '21일', '이라며', 
    '있습니다', '후', '18일', '뒤', '나타났다', '열린', '이를', '김주현', '무단복제', '신규', '국내', '다시', '정부가', '은행의', 
    '고객', '앞서', '김', '것은', '큰', 'ytn', '보인다', '15', '설명했다', '나온다', '14', '것을', '수출금융', '판매를', 
    'copyright', '주담대에', '것이', 'pf', '규제를 않은 한도를', '게', '방안', '아니라', '2021년', '대출을', '상품을', 
    '않은', '한도를', '2021년', '위원장은', '케이뱅크', '점검', '그는', '있고', '때문이다', '제공', '2분기', '시중은행', '금융권에', 
    '국민의힘', '데', '뉴스', '될', '잔액은', '5대', '중구', '있어', '내부통제', '없다', '받을', '있다고', '이북현', '상반기', 
    '향후', '금감원은', '있는지', '되는', '신한', '따른', '제대로', '등의', '엄영수는', '예정이다', '필요한', '보고', '미납률은', 
    '등으로', '이복현', 'copyrights', '34세', '영향을', '내지', '은행장', '집계됐다', '중심으로', '5월', '면서', '제때', 
    '24', '들어', '바', '카카오뱅크', '않고', '또는', 'sbs', '이는', '시장', '포함', '역할을', '자료에', '우회', '은행권의', 
    '기록했다', '고객을', '했습니다', '가능성이', '시스템', '라고', '강조했다', '밝혔습니다', '갚는', '김희곤', '관련해 11월', 
    '일부', '있을', '제도', '없이', '감담회', '대출은', '대해서는', '이벤트', '모든', '한편', '케이뱅크는', '원장은', '15일', 
    '대출의', '계획이다', '카톡', '20일', '13', '대출이', '주담대가', '오는', '국민을', '횡령', 'kb국민', '대상', '12월', 
    '상품으로', '기존', '다양한', '가능하다', '못', '지적이', '카카오뱅크의', '직접', '3월', 'kbs', '국민', '지적했다', '제한을', 
    '오늘', '당초', '규모의', '없는', '원인', '상황에서', '수단으로', '경우가', '가로챈', '점검을', 'news1', '농협은행은', 
    '은행들은', '자금을', 'okjebo', '이들은', '계속', '제보는', '잘', '인터넷은행', '인터넷은행의', '보이고', '혐의로', '4명', 
    '금리도', '당국이', '있는데', '저축은행', '4월', '보면', '받고', '전했다', '있기', '00', 'https', '폰트', '설정', '닫기', '홈', '스포츠']
def create_wordcloud(df, column_name="text"):
    """
    Create and display a word cloud based on the text from the given DataFrame.
    
    Parameters:
    - df: DataFrame containing the text data.
    - col: Streamlit column for displaying the wordcloud.
    - column_name: Name of the column in df containing the text data (default is "text").
    """


    # Extract words from each row and aggregate into a list
    word_list = [word for text in df[column_name] for word in re.findall(r'\w+', text.lower())]
    
    # Count occurrences of each word
    word_counter = Counter(word_list)
    
    # Filter out stop words and select the top 100 words
    top_words = {word: count for word, count in word_counter.most_common(150) if word not in stop_words}
    
    # Generate word cloud
    wordcloud = WordCloud(font_path='font/AppleGothic.ttf', background_color='white', colormap="Blues").generate_from_frequencies(top_words)

    # Display word cloud
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.subheader('워드 클라우드')
    st.pyplot(use_container_width=True)

def display_top_tokens_with_okt(df, column_name="title", top_n=50, title="제목에 가장 많이 포함된 단어"):
    """
    Display a bar chart of the top N tokens based on their frequencies using Okt tokenizer.
    
    Parameters:
    - df: DataFrame containing the text data.
    - stop_words: List of words to be excluded from the analysis.
    - column_name: Name of the column in df containing the text data (default is "title").
    - top_n: Number of top tokens to display (default is 50).
    - title: Title for the bar chart.
    """
    
    # Extract titles and concatenate them
    title_list = df[column_name].values.tolist()
    title_text = '\n'.join(title_list)
    
    # Tokenize using Okt tokenizer
    t = Okt()
    tokens_ko = t.morphs(title_text)
    
    # Remove stop words
    filtered_tokens = [each_word for each_word in tokens_ko if each_word not in stop_words]

    # Create an NLTK Text object
    ko = nltk.Text(filtered_tokens)

    # Extract top N tokens and their frequencies
    top_n_tokens = ko.vocab().most_common(top_n)
    tokens = [token[0] for token in top_n_tokens]
    frequencies = [token[1] for token in top_n_tokens]

    # Create a bar chart using Plotly Express

    fig = px.bar(x=tokens, y=frequencies, title=title, labels={'x': '단어', 'y': '횟수'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)



def plot_news_frequency(df, title):
    """
    Display a bar chart of news frequency by day and optionally the DataFrame itself.
    
    Parameters:
    - df: DataFrame containing the date and news data.
    - tab: Streamlit tab for displaying the data.
    - title: Title for the data/chart.
    """
    # Checkbox for displaying the DataFrame
    show_df = col1.checkbox(f'{title} 데이터 보기')
    if show_df:
        st.write(df)
    # Count news articles by day
    day_counts = df['day'].value_counts().reset_index()
    day_counts.columns = ['day', 'count']
    day_counts = day_counts.sort_values('day')
    
    # Create bar chart using Plotly
    fig = px.bar(day_counts, x='day', y='count', title=f'일자별 {title} 뉴스 기사 수')
    fig.update_layout(
        title_font_size=30, 
        xaxis = dict(title='일자', titlefont_size=23, tickfont_size=20), 
        yaxis=dict(title='뉴스 개수', titlefont_size=23, tickfont_size=20), xaxis_tickangle=-45, bargap=0.1)
    
    # Display the chart in Streamlit
    col1.plotly_chart(fig, use_container_width=True)


# tabs
tab1, tab2, tab3, tab4 = st.tabs(["##### 부동산", "##### 금리", "##### 대출", "##### 아파트"])

# 부동산
with tab1:
    tab1.subheader("부동산")

    st.markdown('''

        ### 주요 키워드
        - 중국: 중국 부동산 시장의 문제가 한국 부동산 시장에도 영향을 미칠 것으로 예상되어, 중국 부동산 관련 이슈에 대한 보도와 이해가 중요합니다.

        - 경제: 중국 경제의 세계적인 영향력과 부동산 시장의 안정성과 관련하여 경제적인 측면이 부각되고 있는 것으로 보입니다.

        - 시장: 중국 부동산 시장의 변화와 구조적 전환에 대한 어려움과 관련된 시장의 불안정성에 대한 이슈들이 강조되고 있습니다.
        ''')
    st.markdown('''---''')  
    col1, col2, col3 = tab1.columns([2,1,1])
    with col1:
        plot_news_frequency(df_부동산_다음, "부동산")
    with col2:
        create_wordcloud(df_부동산_연합)
    with col3:
        count_부동산 = display_noun_wordcloud(df_부동산_연합)

    col1, col2 = tab1.columns([1,1])
    with col1:
        display_top_nouns(count_부동산, 50)
    with col2:
        display_top_tokens_with_okt(df_부동산_연합)

    image = Image.open('../daum_news/부동산.png')
    st.image(image, caption=None, width=None, use_column_width=False, clamp=False, channels="RGB", output_format="auto")

    
# 금리    
with tab2:
    tab2.subheader("금리")

    st.markdown('''

    ### 주요 키워드
    - 중국: 중국의 경제 상황과 금융리스크에 대한 대응으로 중국의 금리 변동이 부동산 시장에 미치는 영향에 대한 논의가 진행되고 있습니다.

    - 미국: 미국의 정책금리 변화는 한국의 기준금리에 직접적인 영향을 미치며, 미국의 통화정책 변화는 한국 경제에 영향을 미칠 수 있습니다. 미국의 경제 및 금융 동향을 주시하여 한국 경제의 안정성을 유지하는 데 중요한 역할을 하고 있습니다.

    - 만기: 50년 만기 주택담보대출과 기업채의 만기와 관련된 금리 변동에 대한 이슈가 주목되고 있습니다. 또한, 중국의 LPR 금리와 관련된 뉴스 역시 금리 동향을 파악하는 데 중요한 정보로 작용할 것입니다.
         ''')

    st.markdown('''---''')
    col1, col2, col3 = tab2.columns([2,1,1])
    with col1:
        plot_news_frequency(df_금리, "금리")
    with col2:
        create_wordcloud(df_금리, "new_text")
    with col3:
        count_금리 = display_noun_wordcloud(df_금리, "new_text")

    col1, col2 = tab2.columns([1,1])
    with col1:
        display_top_nouns(count_금리, 50)
    with col2:
        display_top_tokens_with_okt(df_금리)

    image = Image.open('../daum_news/금리.png')
    st.image(image, caption=None, width=None, use_column_width=False, clamp=False, channels="RGB", output_format="auto")

    

# 대출
with tab3:
    tab3.subheader("대출")

    st.markdown('''
        ### 주요 키워드

        - 만기: 50년 만기 주택담보대출의 등장으로 대출 상품의 만기와 관련된 이슈가 주목받고 있습니다.

        - 50년: 주택담보대출의 50년 만기 상품이 시장에 도입되면서 대출 상품의 변화와 이에 따른 영향에 대한 논의가 진행되고 있습니다.

        - 주담대: 주택담보대출의 약어로, 주택을 담보로 하는 대출에 관련된 이슈가 주목되며, 최근 50년 만기 주택담보대출 상품의 출시와 관련한 논의가 활발히 이루어지고 있습니다.
        ''')

    st.markdown('''---''')

    col1, col2, col3= tab3.columns([2,1,1])
    with col1:
        plot_news_frequency(df_대출, "대출")
    with col2:
        create_wordcloud(df_대출, "new_text")
    with col3:
        count_대출 = display_noun_wordcloud(df_대출, "new_text")

    col1, col2 = tab3.columns([1,1])
    with col1:
        display_top_nouns(count_대출, 50)
    with col2:
        display_top_tokens_with_okt(df_대출)
    
    image = Image.open('../daum_news/대출.png')
    st.image(image, caption=None, width=None, use_column_width=False, clamp=False, channels="RGB", output_format="auto")

    
# 아파트
with tab4:
    tab4.subheader("아파트")

    st.markdown('''

    ### 주요 키워드
    - 서울: 서울이 경제적 중심지로 부동산 시장에 영향을 많이 끼치기 때문에 많이 언급 된 것으로 추정됩니다.

    - LH: 최근 철근 누락 이슈로 인해 주목받은 주택관리공사(LH)와 관련된 이슈입니다.

    - 상승: 민간 아파트 분양가 및 거래량이 상승세를 보이고 있어 부동산 시장에서의 상승에 대한 논의가 빈번하게 이루어지고 있습니다.

    ''')

    st.markdown('''---''')

    col1, col2, col3= tab4.columns([2,1,1])
    with col1:
        plot_news_frequency(df_아파트, "아파트")
    with col2:
        create_wordcloud(df_아파트)
    with col3:
        count_아파트 = display_noun_wordcloud(df_아파트)
    
    col1, col2 = tab4.columns([1,1])
    with col1:
        display_top_nouns(count_아파트, 50)
    with col2:
        display_top_tokens_with_okt(df_아파트)


    
    image = Image.open('../daum_news/아파트.png')
    st.image(image, caption=None, width=None, use_column_width=False, clamp=False, channels="RGB", output_format="auto")


    image = Image.open('../daum_news/일자별 아파트 관련 단어 트렌드.png')
    st.image(image, caption=None, width=None, use_column_width=False, clamp=False, channels="RGB", output_format="auto")

    image = Image.open('../daum_news/아파트_일자별.png')
    st.image(image, caption=None, width=None, use_column_width=False, clamp=False, channels="RGB", output_format="auto")

    
    


st.markdown("""---""")


st.markdown('''

## 예측분석

1. 50년 만기 주택담보대출과 대출 실행:
부동산 시장에 최근 등장한 50년 만기 주택담보대출로 한 달여 만에 2조 가량의 대출 실행은 부동산 시장의 역동성을 나타냅니다. 이는 부동산 투자에 대한 관심이 높아지고 있음을 시사합니다.
또한, 중국과 미국의 금리 변화와 함께 부동산 대출 수요도 변화하고 있는 것으로 예상됩니다.

2. 부동산 시장 진입 시점의 중요성: 
현재 시기는 부동산 경매 참여에 적절한 시점으로 평가됩니다. 아파트 가격이 상승하고 거래량이 증가하는 추세를 보이며, 이는 부동산 시장의 활발한 움직임을 나타냅니다. 
따라서 이러한 흐름을 고려하여 부동산 경매에 참여하면 차익을 얻을 가능성이 크다고 판단됩니다.

3. 특정 브랜드 아파트 가격 하락과 경매 입찰 전략: 
철근 이슈로 아파트 가격 하락이 예상될 경우, 경매 입찰 시에는 보수적인 입찰 전략을 고려하는 것이 현명합니다. 가격 하락으로 인해 저렴한 가격에 아파트를 얻는 기회가 있을 수 있습니다.

4. 가격 상승 가능성 고려: 
현재 시장에서는 아파트 가격의 상승이 예상되고 있는 추세입니다. 이에 따라 부동산 거래를 고려하는 경우, 현재 시기에 부동산 경매에 참여하는 것이 미래의 수익을 고려한 선택일 수 있습니다.

5. 미국과 중국 금리 변동의 영향: 
미국과 중국의 금리 변동은 부동산 시장에 직접적인 영향을 미칠 가능성이 있습니다. 금리 상승은 부동산 투자와 대출 이자에 영향을 줄 수 있으므로, 이러한 금리 변화를 예측하고 경매 입찰을 결정하는 데 중요한 요소로 고려해야 합니다.

6. 미국 실리콘밸리뱅크 파산 사례와 국내 영향: 
과거의 미국 실리콘밸리뱅크 파산 사례에서는 국내에 큰 영향을 미치지 않았던 사례도 있습니다. 현재 중국발 금융리스크 역시 중요한 이슈지만, 일정 시간이 경과한 뒤에 국내 시장에 미치는 영향이 상대적으로 줄어들 가능성도 있습니다. 이를 고려하여 금리 변동과 관련된 판단을 내릴 수 있습니다.




## 처방분석

1. 현재는 아파트 구매에 유리한 시기로, 저렴한 가격에 구매하여 큰 이익을 얻기 위해 부동산 경매에 참여하는 것이 필요한 시점입니다.

2. 철근 이슈로 인해 특정 브랜드의 아파트 가격 하락은 일시적인 현상일 수 있습니다. 이에 따라 해당 아파트의 시장 회복을 예상하면서, 부동산 경매에서 해당 아파트를 저렴하게 획득하는 전략을 세워야 합니다.

3. 과거 국제 경제에 이슈가 발생한 이후 부동산 시장이 회복됐던 사례를 보여주면서, 부동산을 매입할 수 있도록 공동 투자자를 모집할 수 있습니다. 

4. 부동산 시장이 활성화되고 경매를 하기 좋은 시기이므로 부동산 시세 차익을 얻는 데 도움을 주는 경매 낙찰 프로그램을 제작할 수 있습니다.
            ''')