import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 깨짐 방지 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="무역 데이터 분석", layout="wide")
st.title("🇰🇷 한국 수출입 무역통계 분석기")

# 1. 데이터 로드 및 전처리 함수
def load_trade_data(file_path):
    # skiprows=4로 상단 메타데이터 제외
    df = pd.read_csv(file_path, skiprows=4)
    
    # 컬럼명 재설정
    df.columns = ['순번', '시점', '수출금액', '수출증감률', '수입금액', '수입증감률', '무역수지']
    
    # [수정 포인트] 숫자 컬럼에서 쉼표(,) 제거 후 숫자형(float)으로 변환
    numeric_cols = ['수출금액', '수입금액', '무역수지']
    for col in numeric_cols:
        if df[col].dtype == 'object':  # 데이터 타입이 문자열인 경우에만 실행
            df[col] = df[col].str.replace(',', '').astype(float)
    
    # 데이터 역순 정렬 (과거 -> 최신 순으로 그래프를 그리기 위함)
    df = df.iloc[::-1].reset_index(drop=True)
    return df

# 2. 사이드바 메뉴
st.sidebar.header("📍 조회 조건 설정")

data_mode = st.sidebar.radio("데이터 단위", ["연도별", "분기별"])

if data_mode == "연도별":
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계.csv"
else:
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계_분기별.csv"

target_metric = st.sidebar.selectbox("보고 싶은 지표", ["수출금액", "수입금액", "무역수지"])

# 3. 메인 화면 로직
try:
    df = load_trade_data(file_name)

    # 데이터 요약 수치 (이제 숫자로 변환되었으므로 연산 가능)
    last_value = df[target_metric].iloc[-1]
    prev_value = df[target_metric].iloc[-2]
    diff = last_value - prev_value

    col1, col2, col3 = st.columns(3)
    # delta 인자에는 차이값을 넣어줍니다.
    col1.metric(f"최근 {target_metric}", f"{last_value:,.0f} $", f"{diff:,.0f} $")
    
    # 4. 그래프 그리기
    st.subheader(f"📅 {data_mode} {target_metric} 추이")
    
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=df, x='시점', y=target_metric, marker='o', color='#1f77b4', ax=ax)
    
    # x축 라벨이 너무 많을 경우 겹치지 않게 회전
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    st.pyplot(fig)

    # 5. 데이터 테이블 출력
    with st.expander("원본 데이터 보기"):
        st.dataframe(df.sort_values('시점', ascending=False))

except Exception as e:
    st.error(f"오류가 발생했습니다.")
    st.info(f"상세 에러 내용: {e}")