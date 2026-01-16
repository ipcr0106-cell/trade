import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 깨짐 방지 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="무역 데이터 분석", layout="wide")
st.title("🇰🇷 한국 수출입 무역통계 분석기")

def load_trade_data(file_path):
    df = pd.read_csv(file_path, skiprows=4)
    df.columns = ['순번', '시점', '수출금액', '수출증감률', '수입금액', '수입증감률', '무역수지']
    
    numeric_cols = ['수출금액', '수입금액', '무역수지']
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    
    # '시점' 컬럼에서 '2024년'만 추출해서 '연도' 컬럼 생성
    df['연도'] = df['시점'].apply(lambda x: x.split(' ')[0])
    
    df = df.iloc[::-1].reset_index(drop=True)
    return df

# 1. 사이드바 설정
st.sidebar.header("📍 조회 조건 설정")
data_mode = st.sidebar.radio("데이터 단위", ["연도별", "분기별"])

if data_mode == "연도별":
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계.csv"
else:
    file_name = "한국무역통계 총괄 - K-stat 수출입 무역통계_분기별.csv"

target_metric = st.sidebar.selectbox("보고 싶은 지표", ["수출금액", "수입금액", "무역수지"])

# 2. 메인 로직
try:
    df = load_trade_data(file_name)

    # --- 연도 선택 필터 추가 ---
    if data_mode == "분기별":
        # 사용 가능한 연도 리스트 추출 (중복 제거 및 정렬)
        year_list = sorted(df['연도'].unique(), reverse=True)
        selected_year = st.selectbox("📅 확인하고 싶은 연도를 선택하세요", year_list)
        
        # 선택된 연도의 데이터만 필터링
        plot_df = df[df['연도'] == selected_year]
        display_title = f"📅 {selected_year} {target_metric} 추이"
    else:
        plot_df = df
        display_title = f"📅 전체 연도별 {target_metric} 추이"

    # 3. 요약 수치 (필터링된 데이터 기준)
    last_value = plot_df[target_metric].iloc[-1]
    # 데이터가 1개만 있을 경우를 대비한 예외 처리
    prev_value = plot_df[target_metric].iloc[-2] if len(plot_df) > 1 else last_value
    diff = last_value - prev_value

    col1, col2 = st.columns([1, 4])
    with col1:
        st.metric(f"최근 {target_metric}", f"{last_value:,.0f} $", f"{diff:,.0f} $")
    
    # 4. 그래프 그리기
    st.subheader(display_title)
    
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=plot_df, x='시점', y=target_metric, marker='o', color='#1f77b4', ax=ax)
    
    # 그래프 상단에 값 표시 (분기별일 때 가독성 업!)
    for i in range(len(plot_df)):
        ax.text(i, plot_df[target_metric].iloc[i], f"{plot_df[target_metric].iloc[i]:,.0f}", 
                ha='center', va='bottom', fontsize=10)

    plt.xticks(rotation=0) # 분기별은 라벨이 적으니 회전 안 함
    plt.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

    # 5. 원본 데이터 (필터링된 것만)
    with st.expander("선택한 기간 데이터 보기"):
        st.dataframe(plot_df.sort_values('시점', ascending=False))

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")