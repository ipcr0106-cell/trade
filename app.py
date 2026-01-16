import streamlit as st
import pandas as pd

# 레이아웃 설정
st.set_page_config(page_title="무역 통계 대시보드", layout="centered")

st.title("📊 한국 수출입 무역통계 분석기")
st.caption("2010년 이후 무역 데이터 분석 (고정 크기 모드)")

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_trade_data(file_path):
    df = pd.read_csv(file_path, skiprows=4)
    df.columns = ['순번', '시점', '수출금액', '수출증감률', '수입금액', '수입증감률', '무역수지']
    
    # 숫자 데이터 전처리
    for col in ['수출금액', '수입금액', '무역수지']:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
            
    df['연도_숫자'] = df['시점'].apply(lambda x: int(x.split('년')[0]))
    df = df[df['연도_숫자'] >= 2010]
    df = df.iloc[::-1].reset_index(drop=True)
    return df

# --- 2. 상단 설정 구역 ---
st.write("---")
c1, c2 = st.columns([1, 1])
with c1:
    data_mode = st.radio("📈 단위 선택", ["연도별", "분기별"], horizontal=True)
with c2:
    target_metrics = st.multiselect("📍 지표 선택", ["수출금액", "수입금액", "무역수지"], default=["수출금액", "수입금액"])

file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계.csv" if data_mode == "연도별" else "한국무역통계 총괄 - K-stat 수출입 무역통계_분기별.csv"

try:
    df = load_trade_data(file_name)
    
    if data_mode == "분기별":
        unique_years = sorted(df['연도_숫자'].unique(), reverse=True)
        # 4년 단위 범위 필터
        selected_range = st.selectbox("📅 조회 범위", sorted(list(set([f"{y-(y%4)}~{y-(y%4)+3}" for y in unique_years])), reverse=True))
        start_y, end_y = map(int, selected_range.split('~'))
        plot_df = df[(df['연도_숫자'] >= start_y) & (df['연도_숫자'] <= end_y)]
    else:
        plot_df = df

    # --- 3. 요약 수치 (Metric) ---
    st.write("")
    if target_metrics:
        m_cols = st.columns(len(target_metrics))
        for i, metric in enumerate(target_metrics):
            curr = plot_df[metric].iloc[-1]
            prev = plot_df[metric].iloc[-2] if len(plot_df) > 1 else curr
            m_cols[i].metric(metric, f"{curr:,.0f}", f"{curr-prev:,.0f}")

        # --- 4. [핵심] Streamlit 내장 차트로 변경 ---
        # 내장 차트는 폰트 설정 없이 한글이 지원됩니다.
        st.write(f"### 📈 {data_mode} 추이 (단위: 천불)")
        
        # 차트용 데이터 가공: '시점'을 인덱스로 설정
        chart_data = plot_df.set_index('시점')[target_metrics]
        
        # 고정 크기처럼 보이게 하기 위해 container 너비 사용 옵션 해제 가능
        st.line_chart(chart_data, use_container_width=True)
        
    else:
        st.warning("지표를 선택해 주세요.")

    # --- 5. 상세 데이터 ---
    with st.expander("📝 상세 데이터 보기"):
        st.dataframe(plot_df.sort_values('시점', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")