import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GLP-1 Side Effect Stages", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("C:\\Users\\kim20\\Downloads\\SideEffect_Analysis_Data.csv")
    # 신뢰도를 위해 [deleted] 및 무의미한 태그 필터링
    df = df[(df['author'] != '[deleted]') & (df['side_effect'] != 'unknown')]
    
    # 1. 구간 설정 (0-2M: 초기 / 3-5M: 중기 / 6M+: 장기)
    def assign_stage(m):
        if m < 3: return 'Early (0-3M)'
        elif m < 6: return 'Mid (3-6M)'
        else: return 'Long-term (6M+)'
    
    df['Stage'] = df['rel_month'].apply(assign_stage)
    return df

df = load_data()

st.title("📊 복용 단계별 전체 부작용 분포 분석")
st.markdown("복용 기간에 따른 모든 주요 부작용의 비중 변화를 비교합니다.")

# --- 사이드바 설정 ---
st.sidebar.header("차트 설정")
top_n = st.sidebar.slider("표시할 상위 부작용 개수", 5, 30, 15)

# --- 데이터 집계 로직 ---
# 1. 전체에서 가장 많이 언급된 상위 N개 부작용 추출
top_side_effects = df['side_effect'].value_counts().head(top_n).index.tolist()
filtered_df = df[df['side_effect'].isin(top_side_effects)]

# 2. 단계(Stage)별, 부작용별 빈도 계산
stage_counts = filtered_df.groupby(['Stage', 'side_effect']).size().reset_index(name='count')

# 3. 비율 계산: 각 단계(Stage)별 '전체 언급량' 대비 해당 부작용의 비중 (%)
# 이 방식이 올려주신 이미지의 'Percentage of Mentions'와 동일한 로직입니다.
stage_totals = df.groupby('Stage').size().reset_index(name='stage_total')
stage_counts = stage_counts.merge(stage_totals, on='Stage')
stage_counts['percentage'] = (stage_counts['count'] / stage_counts['stage_total']) * 100

# --- 시각화: Grouped Bar Chart ---
st.subheader(f"🔝 상위 {top_n}개 부작용 단계별 비중 비교")

# 시각적 구분감이 좋은 컬러 팔레트 사용
fig_bar = px.bar(stage_counts, 
                 x="side_effect", 
                 y="percentage", 
                 color="Stage",
                 barmode="group",
                 text_auto='.1f',
                 category_orders={"Stage": ['Early (0-3M)', 'Mid (3-6M)', 'Long-term (6M+)']},
                 color_discrete_map={
                     'Early (0-3M)': '#2E5A88',  # Deep Blue (이미지 느낌)
                     'Mid (3-6M)': '#4FB06D',    # Medium Green
                     'Long-term (6M+)': '#A3D39C' # Light Green (이미지 느낌)
                 },
                 template="plotly_white")

# 레이아웃 정밀 조정
fig_bar.update_layout(
    xaxis_title="부작용 항목",
    yaxis_title="해당 단계 전체 언급 대비 비율 (%)",
    legend_title="복용 단계",
    xaxis={'categoryorder':'total descending'}, # 빈도순 정렬
    height=600
)

fig_bar.update_traces(
    textposition='outside',
    marker_line_color='white',
    marker_line_width=1,
    opacity=0.9
)

st.plotly_chart(fig_bar, use_container_width=True)

# --- 추가 인사이트 데이터 테이블 ---
with st.expander("📝 단계별 상세 수치 확인"):
    pivot_df = stage_counts.pivot(index='side_effect', columns='Stage', values='percentage').fillna(0)
    # 장기(Long-term)에서 비중이 높아지는 순서대로 정렬해서 보여주기
    st.dataframe(pivot_df.sort_values(by='Long-term (6M+)', ascending=False), use_container_width=True)