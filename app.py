import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 및 스타일 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font='Malgun Gothic')

# [디자인 변경] layout="centered"로 설정하여 전체 앱이 화면 중앙에 고정되게 함
st.set_page_config(page_title="무역 통계 대시보드", layout="centered")

st.title("📊 한국 수출입 무역통계 분석기")
st.caption("2010년 이후 무역 통계 분석 (고정 크기 모드)")

@st.cache_data
def load_trade_data(file_path):
    df = pd.read_csv(file_path, skiprows=4)
    df.columns = ['순번', '시점', '수출금액', '수출증감률', '수입금액', '수입증감률', '무역수지']
    for col in ['수출금액', '수입금액', '무역수지']:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    df['연도_숫자'] = df['시점'].apply(lambda x: int(x.split('년')[0]))
    df = df[df['연도_숫자'] >= 2010]
    df = df.iloc[::-1].reset_index(drop=True)
    return df

# --- 설정 구역 ---
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
        year_ranges = [f"{unique_years[max(0, i+3)]}~{unique_years[i]}" for i in range(0, len(unique_years), 4) if i+3 < len(unique_years)]
        # 위 로직이 복잡할 수 있어 단순화된 범위 선택
        selected_range = st.selectbox("📅 조회 범위 (4년)", sorted(list(set([f"{y-(y%4)}~{y-(y%4)+3}" for y in unique_years])), reverse=True))
        start_y, end_y = map(int, selected_range.split('~'))
        plot_df = df[(df['연도_숫자'] >= start_y) & (df['연도_숫자'] <= end_y)]
    else:
        plot_df = df

    # --- 요약 수치 ---
    st.write("")
    m_cols = st.columns(len(target_metrics) if target_metrics else 1)
    for i, metric in enumerate(target_metrics):
        curr = plot_df[metric].iloc[-1]
        prev = plot_df[metric].iloc[-2] if len(plot_df) > 1 else curr
        m_cols[i].metric(metric, f"{curr:,.0f}", f"{curr-prev:,.0f}")

    # --- [핵심] 그래프 고정 크기 설정 ---
    if target_metrics:
        # figsize를 (8, 4)로 고정하여 컴팩트하게 유지
        fig, ax = plt.subplots(figsize=(8, 4))
        colors = {"수출금액": "#2ecc71", "수입금액": "#e74c3c", "무역수지": "#3498db"}
        
        for metric in target_metrics:
            sns.lineplot(data=plot_df, x='시점', y=metric, marker='o', label=metric, color=colors.get(metric), ax=ax)
            # 마지막 수치만 표시
            last_idx, last_val = len(plot_df) - 1, plot_df[metric].iloc[-1]
            ax.text(last_idx, last_val, f"{last_val:,.0f}", color=colors.get(metric), 
                    fontsize=9, fontweight='bold', va='bottom', ha='left')

        ax.set_ylabel("단위: 천불", fontsize=8)
        plt.xticks(rotation=45, fontsize=8)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=8)
        sns.despine()
        
        # [수정] use_container_width=False(기본값)로 설정하여 figsize 크기를 엄격히 준수
        st.pyplot(fig, use_container_width=False)
    
    with st.expander("📝 상세 데이터"):
        st.dataframe(plot_df.sort_values('시점', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"데이터 오류: {e}")