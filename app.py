import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 깨짐 방지 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="무역 데이터 분석", layout="wide")
st.title("🇰🇷 한국 수출입 무역통계 분석기")

# 1. 데이터 로드 및 전처리 함수
@st.cache_data
def load_trade_data(file_path):
    df = pd.read_csv(file_path, skiprows=4)
    df.columns = ['순번', '시점', '수출금액', '수출증감률', '수입금액', '수입증감률', '무역수지']
    
    # 숫자 데이터 전처리
    numeric_cols = ['수출금액', '수입금액', '무역수지']
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    
    # 연도 숫자 추출 및 2010년 이후 데이터만 필터링
    df['연도_숫자'] = df['시점'].apply(lambda x: int(x.split('년')[0]))
    df = df[df['연도_숫자'] >= 2010] # [수정 포인트] 2010년 데이터부터 사용
    
    df = df.iloc[::-1].reset_index(drop=True)
    return df

# --- 2. 본문 상단 설정 구역 ---
st.write("---")
ctrl_col1, ctrl_col2 = st.columns([1, 2])

with ctrl_col1:
    data_mode = st.radio("📊 데이터 단위", ["연도별", "분기별"], horizontal=True)

with ctrl_col2:
    target_metrics = st.multiselect(
        "🔍 비교할 지표를 선택하세요", 
        ["수출금액", "수입금액", "무역수지"],
        default=["수출금액", "수입금액"]
    )

if data_mode == "연도별":
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계.csv"
else:
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계_분기별.csv"

try:
    df = load_trade_data(file_name)

    if data_mode == "분기별":
        # 필터링된 데이터(2010년~)를 기준으로 연도 범위 생성
        unique_years = sorted(df['연도_숫자'].unique())
        year_ranges = []
        for i in range(0, len(unique_years), 4):
            group = unique_years[i : i + 4]
            label = f"{group[0]}~{group[-1]}"
            year_ranges.append((label, group))
        
        year_ranges.reverse()
        range_labels = [r[0] for r in year_ranges]
        
        selected_range_label = st.selectbox("📅 조회할 분기 범위 선택 (4년 단위)", range_labels)
        selected_years = [r[1] for r in year_ranges if r[0] == selected_range_label][0]
        plot_df = df[df['연도_숫자'].isin(selected_years)]
        display_title = f"{selected_range_label} 분기별 추이"
    else:
        plot_df = df
        display_title = "2010년 이후 연도별 무역 추이"

    # --- 3. 데이터 요약 배너 및 서브헤더 ---
    st.write("")
    header_col, m1, m2, m3 = st.columns([2.5, 1, 1, 1])
    
    with header_col:
        st.subheader(f"📈 {display_title}")

    metrics_map = {"수출금액": m1, "수입금액": m2, "무역수지": m3}
    for m_name, col in metrics_map.items():
        if m_name in target_metrics:
            last_val = plot_df[m_name].iloc[-1]
            prev_val = plot_df[m_name].iloc[-2] if len(plot_df) > 1 else last_val
            diff = last_val - prev_val
            col.metric(m_name, f"{last_val:,.0f}", f"{diff:,.0f}")

    # --- 4. 메인 그래프 (단위: 천불 반영) ---
    if not target_metrics:
        st.info("💡 상단에서 지표를 하나 이상 선택해 주세요.")
    else:
        fig_width = 12 if data_mode == "분기별" else 16
        fig, ax = plt.subplots(figsize=(fig_width, 6))
        colors = {"수출금액": "#2ecc71", "수입금액": "#e74c3c", "무역수지": "#3498db"}
        
        for metric in target_metrics:
            sns.lineplot(data=plot_df, x='시점', y=metric, marker='o', markersize=6,
                         label=metric, color=colors.get(metric), ax=ax)
            
            # 모든 점에 작은 수치 추가
            for i in range(len(plot_df)):
                val = plot_df[metric].iloc[i]
                ax.text(i, val, f"{val:,.0f}", color=colors.get(metric), 
                        fontsize=8, va='bottom', ha='center')

        # Y축 단위 표기
        ax.set_ylabel("금액 (단위: 천불)", fontsize=10, fontweight='bold')
        plt.xticks(rotation=45)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid(True, linestyle='--', alpha=0.3)
        
        # 수치 잘림 방지를 위한 상단 여백 확보
        ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1] * 1.1)
        
        plt.tight_layout()
        st.pyplot(fig)

    # 5. 하단 원본 데이터 테이블
    with st.expander("데이터 상세 테이블 보기"):
        st.dataframe(plot_df.sort_values('시점', ascending=False))

except Exception as e:
    st.error("데이터를 처리하는 중 오류가 발생했습니다.")
    st.info(f"상세 에러: {e}")