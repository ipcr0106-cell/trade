import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 깨짐 방지 설정 (Windows 기준 나눔고딕/맑은고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="무역 데이터 분석", layout="wide")
st.title("🇰🇷 한국 수출입 무역통계 분석기")

# 1. 데이터 로드 함수
def load_trade_data(file_path):
    # K-stat 파일은 상단 4줄이 메타데이터이므로 skip
    df = pd.read_csv(file_path, skiprows=4)
    
    # 중복되거나 모호한 컬럼명 재설정
    # 파일 구조: 순번, 시점, 수출(금액), 수출(증감률), 수입(금액), 수입(증감률), 수지
    df.columns = ['순번', '시점', '수출금액', '수출증감률', '수입금액', '수입증감률', '무역수지']
    
    # 데이터가 최신순으로 되어있으므로 시계열 분석을 위해 역순 정렬
    df = df.iloc[::-1].reset_index(drop=True)
    return df

# 2. 사이드바 메뉴
st.sidebar.header("📍 조회 조건 설정")

# 파일 선택 (연도별 / 분기별)
data_mode = st.sidebar.radio("데이터 단위", ["연도별", "분기별"])

if data_mode == "연도별":
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계.xls - sheet1.csv"
else:
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계_분기별.xls - sheet1.csv"

# 지표 선택
target_metric = st.sidebar.selectbox("보고 싶은 지표", ["수출금액", "수입금액", "무역수지"])

# 3. 메인 화면 로직
try:
    df = load_trade_data(file_name)

    # 데이터 요약 수치
    last_value = df[target_metric].iloc[-1]
    prev_value = df[target_metric].iloc[-2]
    diff = last_value - prev_value

    col1, col2, col3 = st.columns(3)
    col1.metric(f"최근 {target_metric}", f"{last_value:,.0f} $", f"{diff:,.0f} $")
    
    # 4. 그래프 그리기 (Matplotlib & Seaborn 활용)
    st.subheader(f"📅 {data_mode} {target_metric} 추이")
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Seaborn 디자인 적용
    sns.lineplot(data=df, x='시점', y=target_metric, marker='o', color='#1f77b4', ax=ax)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # 차트 출력
    st.pyplot(fig)

    # 5. 데이터 테이블 출력
    with st.expander("원본 데이터 보기"):
        st.dataframe(df.sort_values('시점', ascending=False))

except Exception as e:
    st.error(f"파일을 읽는 중 오류가 발생했습니다. 파일명과 위치를 확인해주세요.")
    st.info(f"상세 에러: {e}")