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
def load_trade_data(file_path):
    df = pd.read_csv(file_path, skiprows=4)
    df.columns = ['순번', '시점', '수출금액', '수출증감률', '수입금액', '수입증감률', '무역수지']
    
    numeric_cols = ['수출금액', '수입금액', '무역수지']
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    
    # 연도 숫자 추출
    df['연도_숫자'] = df['시점'].apply(lambda x: int(x.split('년')[0]))
    df = df.iloc[::-1].reset_index(drop=True)
    return df

# 2. 사이드바 설정
st.sidebar.header("📍 데이터 설정")
data_mode = st.sidebar.radio("데이터 단위", ["연도별", "분기별"])

if data_mode == "연도별":
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계.csv"
else:
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계_분기별.csv"

# [기능 추가] 다중 지표 선택 (체크박스 형태의 멀티셀렉트)
target_metrics = st.sidebar.multiselect(
    "비교할 지표를 선택하세요", 
    ["수출금액", "수입금액", "무역수지"],
    default=["수출금액"] # 기본값
)

# 3. 메인 로직
try:
    df = load_trade_data(file_name)

    # 4년 단위 범위 생성
    unique_years = sorted(df['연도_숫자'].unique())
    year_ranges = []
    for i in range(0, len(unique_years), 4):
        group = unique_years[i : i + 4]
        label = f"{group[0]}~{group[-1]}"
        year_ranges.append((label, group))
    
    year_ranges.reverse()
    range_labels = [r[0] for r in year_ranges]

    # 상단 필터 레이아웃
    filter_col1, filter_col2 = st.columns([2, 3])
    with filter_col1:
        selected_range_label = st.selectbox("📅 조회 연도 범위 (4년 단위)", range_labels)
    
    # 데이터 필터링
    selected_years = [r[1] for r in year_ranges if r[0] == selected_range_label][0]
    plot_df = df[df['연도_숫자'].isin(selected_years)]

    # 4. [요청 반영] 서브헤더 및 지표 배너 위치 변경
    st.divider()
    
    # 헤더와 메트릭을 한 줄에 배치
    header_col, m1, m2, m3 = st.columns([2, 1, 1, 1])
    
    with header_col:
        st.subheader(f"📈 {selected_range_label} 추이")

    # 선택된 지표들에 대해서만 상단에 요약 수치 표시
    metrics_map = {"수출금액": m1, "수입금액": m2, "무역수지": m3}
    for m_name, col in metrics_map.items():
        if m_name in target_metrics:
            last_val = plot_df[m_name].iloc[-1]
            prev_val = plot_df[m_name].iloc[-2] if len(plot_df) > 1 else last_val
            diff = last_val - prev_val
            col.metric(m_name, f"{last_val:,.0f}", f"{diff:,.0f}")

    # 5. [기능 추가] 그래프 그리기 (다중 지표 비교)
    if not target_metrics:
        st.warning("왼쪽 사이드바에서 최소 하나 이상의 지표를 선택해 주세요.")
    else:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 색상 매핑
        colors = {"수출금액": "#2ecc71", "수입금액": "#e74c3c", "무역수지": "#3498db"}
        
        for metric in target_metrics:
            sns.lineplot(data=plot_df, x='시점', y=metric, marker='o', 
                         label=metric, color=colors.get(metric), ax=ax)
            
            # 수치 표시 (지표가 여러개일 땐 가독성을 위해 마지막 값만 표시하거나 생략 가능)
            # 여기서는 마지막 점에만 값을 표시해 보겠습니다.
            last_idx = len(plot_df) - 1
            ax.text(last_idx, plot_df[metric].iloc[-1], f"{plot_df[metric].iloc[-1]:,.0f}", 
                    color=colors.get(metric), fontweight='bold')

        plt.xticks(rotation=45)
        plt.legend(loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

    # 6. 데이터 테이블
    with st.expander("데이터 상세 보기"):
        st.dataframe(plot_df.sort_values('시점', ascending=False))

except Exception as e:
    st.error("데이터 로딩 중 에러가 발생했습니다.")
    st.info(f"에러 내용: {e}")