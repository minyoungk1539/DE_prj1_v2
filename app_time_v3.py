import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="복용 단계별 부작용 분포", page_icon="💊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=JetBrains+Mono:wght@500&display=swap');
:root {
    --ewha:#00462A; --ewha-light:#1a7a50; --ewha-pale:#d4ede2;
    --ewha-faint:#eef7f2; --bg:#f2f6f4; --surface:#ffffff;
    --border:#cce0d6; --text:#1a2e24; --muted:#5a7a68;
    --radius-md:12px; --shadow-sm:0 2px 8px rgba(0,70,42,0.07);
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] > div {
    background:var(--bg) !important; color:var(--text) !important;
    font-family:'Noto Sans KR', sans-serif !important;
}
[data-testid="stHeader"], [data-testid="stDecoration"] { display:none !important; }
[data-testid="stSidebar"] { background:#001f14 !important; }
[data-testid="stSidebar"] * { color:#c8e0d4 !important; }
.block-container { padding:1.8rem 2.2rem 3rem !important; max-width:1400px !important; }

.page-hero {
    background:linear-gradient(135deg,#002e1c 0%,#00462A 60%,#1a7a50 100%);
    border-radius:16px; padding:2.2rem 2.8rem; margin-bottom:1.8rem;
    box-shadow:0 6px 30px rgba(0,70,42,0.18);
}
.page-hero-eyebrow {
    font-family:'JetBrains Mono', monospace; font-size:.65rem;
    letter-spacing:.2em; text-transform:uppercase; color:#a0c8b4; margin-bottom:.6rem;
}
.page-hero-title {
    font-size:clamp(1.5rem,2.5vw,2rem); font-weight:700;
    color:#fff; line-height:1.25; margin:0 0 .35rem;
}
.page-hero-sub { font-size:.8rem; color:#a0c8b4; }

.section-title {
    font-size:.92rem; font-weight:700; color:var(--ewha);
    margin:1.6rem 0 .8rem; display:flex; align-items:center; gap:10px;
}
.section-title::after {
    content:''; flex:1; height:1px;
    background:linear-gradient(90deg,var(--border),transparent);
}

/* 첫 번째 사진: 라디오 배경색 제거 + 진한 초록 글자 */
[data-testid="stRadio"] > label {
    color:var(--ewha) !important; font-weight:700 !important; font-size:.85rem !important;
}
[data-testid="stRadio"] div[role="radiogroup"] {
    background:transparent !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label,
[data-testid="stRadio"] div[role="radiogroup"] label * {
    color:var(--ewha) !important;
    background:transparent !important;
    box-shadow:none !important;
    font-weight:500 !important;
    font-size:.85rem !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) * {
    color:var(--ewha) !important;
    background:transparent !important;
    font-weight:700 !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] div:first-child {
    border-color:var(--ewha) !important;
    background-color:transparent !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] div:first-child::after {
    background-color:var(--ewha) !important;
}

[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background-color:var(--ewha) !important; border-radius:6px !important;
}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
    color:#fff !important; font-size:.74rem !important;
}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
    fill:rgba(255,255,255,.8) !important;
}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    background:rgba(255,255,255,.06) !important;
    border:1px solid rgba(255,255,255,.15) !important;
    border-radius:8px !important;
}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] input { color:#d4ede2 !important; }

.info-banner {
    background:var(--ewha-faint); border:1px solid var(--ewha-pale);
    border-left:4px solid var(--ewha);
    border-radius:0 var(--radius-md) var(--radius-md) 0;
    padding:11px 16px; font-size:.81rem; color:var(--ewha);
    font-weight:500; margin-bottom:1rem;
}

/* 표 제목: 옅은 초록 배경 */
.table-title-box {
    background:var(--ewha-faint);
    border:1.5px solid var(--border);
    border-radius:var(--radius-md) var(--radius-md) 0 0;
    padding:12px 16px;
    margin-top:1.4rem;
    color:var(--ewha);
    font-weight:700;
    font-size:.9rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("C:\\Users\\kim20\\Downloads\\SideEffect_Analysis_Data.csv")
    df = df[(df["author"] != "[deleted]") & (df["side_effect"] != "unknown")]

    def assign_stage(m):
        if m < 3:
            return "Early-term"
        elif m < 6:
            return "Mid-term"
        else:
            return "Long-term"

    df["Stage"] = df["rel_month"].apply(assign_stage)
    return df

df = load_data()

STAGE_ORDER = ["Early-term", "Mid-term", "Long-term"]
STAGE_LABELS = {
    "Early-term": "Early-term (0–3M)",
    "Mid-term": "Mid-term (3–6M)",
    "Long-term": "Long-term (6M+)",
}
STAGE_COLORS = {
    "Early-term": "#1a4f7a",
    "Mid-term": "#2e8b57",
    "Long-term": "#6db88a",
}

# 막대그래프/표 표시용: 한글명 / 영문명
SE_MAP = {
    "appetite_loss": "식욕감소 / Appetite Loss",
    "nausea": "오심/메스꺼움 / Nausea",
    "stomach_pain": "복통 / Stomach Pain",
    "diarrhea": "설사 / Diarrhea",
    "hypoglycemia": "저혈당 / Hypoglycemia",
    "insomnia": "불면증 / Insomnia",
    "acid_reflux": "위식도역류 / Acid Reflux",
    "fatigue": "피로/무기력 / Fatigue",
    "severe_gastrointestinal": "심한 위장장애 / Severe GI",
    "constipation": "변비 / Constipation",
    "hair_loss": "탈모 / Hair Loss",
    "gallbladder_disease": "담낭질환 / Gallbladder Disease",
    "heart_rate_increase": "심박수 증가 / Tachycardia",
    "headache": "두통 / Headache",
    "skin_changes": "피부 이상 / Skin Changes",
    "hypersensitivity": "과민반응 / Hypersensitivity",
    "pancreatitis": "췌장염 / Pancreatitis",
    "vomiting": "구토 / Vomiting",
    "dizziness": "어지러움 / Dizziness",
    "aspiration_risk": "흡인 위험 / Aspiration Risk",
    "thyroid_tumor": "갑상선 종양 / Thyroid Tumor",
    "kidney_injury": "신장 손상 / Kidney Injury",
    "retinopathy_aggravation": "망막병증 악화 / Retinopathy Aggravation",
    "muscle_pain": "근육통 / Muscle Pain",
    "burping": "트림 / Burping",
    "bloating": "고창/가스참 / Bloating",
    "indigestion": "소화불량 / Indigestion",
    "hypotension": "저혈압 / Hypotension",
    "weight_loss": "체중 감소 / Weight Loss",
    "dehydration": "탈수 / Dehydration",
    "anxiety": "불안 / Anxiety",
    "injection_site": "주사 부위 반응 / Injection Site Reaction",
    "구토": "구토 / Vomiting",
    "오심(메스꺼움)": "오심/메스꺼움 / Nausea",
    "오심/메스꺼움": "오심/메스꺼움 / Nausea",
    "부작용 (명시되지 않음)": "기타 부작용 / Other SE",
    "기타부작용": "기타 부작용 / Other SE",
    "설사": "설사 / Diarrhea",
    "피로/무기력": "피로/무기력 / Fatigue",
    "변비": "변비 / Constipation",
    "트림": "트림 / Burping",
    "두통": "두통 / Headache",
    "어지러움": "어지러움 / Dizziness",
    "소화불량": "소화불량 / Indigestion",
    "고창(가스참)": "고창/가스참 / Bloating",
    "위식도 역류": "위식도역류 / Acid Reflux",
    "피부 이상": "피부 이상 / Skin Changes",
    "근육통": "근육통 / Muscle Pain",
    "탈모": "탈모 / Hair Loss",
    "불면증": "불면증 / Insomnia",
    "복통": "복통 / Stomach Pain",
    "저혈압": "저혈압 / Hypotension",
    "저혈당": "저혈당 / Hypoglycemia",
    "심박수 증가": "심박수 증가 / Tachycardia",
    "담낭 질환": "담낭질환 / Gallbladder Disease",
    "췌장염": "췌장염 / Pancreatitis",
    "신장 손상": "신장 손상 / Kidney Injury",
    "식욕감소": "식욕감소 / Appetite Loss",
}

def se_display_name(x) -> str:
    if pd.isna(x):
        return ""

    raw = str(x).strip()
    key = raw.lower()

    if key in SE_MAP:
        return SE_MAP[key].replace("\n", " / ")
    if raw in SE_MAP:
        return SE_MAP[raw].replace("\n", " / ")
    if " / " in raw:
        return raw
    if "\n" in raw:
        return raw.replace("\n", " / ")

    return raw.replace("_", " ").title()

st.markdown("""
<div class='page-hero'>
    <div class='page-hero-eyebrow'>Pharmacovigilance · Distribution of Side Effects by Treatment Stage </div>
    <div class='page-hero-title'>📊 복용 단계별 부작용 분포 분석</div>
    <div class='page-hero-sub'>복용 기간에 따른 주요 부작용 비중 변화를 비교합니다. 사이드바에서 항목을 선택해 차트를 정리하세요.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style='font-size:1.05rem;font-weight:700;color:#d4ede2;margin:1rem 0 0.3rem'>⚙️ 분석 설정</div>
    <div style='height:1px;background:rgba(255,255,255,0.1);margin-bottom:1.2rem'></div>
    """, unsafe_allow_html=True)

    # 두 번째 사진 요청 반영: '상위 부작용 풀 크기' 슬라이더 자체 제거
    top_n = 15

    st.markdown("""
    <div style='font-size:0.62rem;letter-spacing:0.16em;text-transform:uppercase;
                color:#7aad95;margin-bottom:0.7rem;font-weight:700'>
        부작용 항목 선택
    </div>
    """, unsafe_allow_html=True)

    top_pool = df["side_effect"].value_counts().head(top_n).index.tolist()
    pool_df = df[df["side_effect"].isin(top_pool)]
    sorted_pool = pool_df["side_effect"].value_counts().index.tolist()

    if "selected_ses" not in st.session_state:
        st.session_state["selected_ses"] = sorted_pool.copy()

    valid = [s for s in st.session_state["selected_ses"] if s in sorted_pool]

    selected_ses = st.multiselect(
        "표시할 부작용 선택",
        options=sorted_pool,
        default=valid,
        key="multiselect_ses",
        format_func=se_display_name,
        help="검색창에 입력해 빠르게 찾을 수 있습니다.",
    )
    st.session_state["selected_ses"] = selected_ses

    st.markdown(f"""
    <div style='margin-top:0.8rem;background:rgba(255,255,255,0.05);border-radius:8px;
                padding:10px 13px;font-size:0.75rem;color:#a0c8b4;line-height:1.65'>
    선택된 항목: <b style="color:#d4ede2">{len(selected_ses)}개</b> / {len(sorted_pool)}개
    </div>
    """, unsafe_allow_html=True)

stage_totals = df.groupby("Stage").size().reset_index(name="stage_total")
all_counts = (
    pool_df.groupby(["Stage", "side_effect"])
    .size()
    .reset_index(name="count")
    .merge(stage_totals, on="Stage")
)
all_counts["percentage"] = all_counts["count"] / all_counts["stage_total"] * 100

st.markdown("<div class='section-title'>📐 비율 기준 선택</div>", unsafe_allow_html=True)

pct_mode = st.radio(
    "Y축 기준",
    ["전체 데이터 기준 비율 (%)", "선택 항목 기준 상대 비율 (%)"],
    index=0,
    horizontal=True,
    help=(
        "**전체 데이터 기준 비율**: 해당 단계의 모든 언급 중 이 부작용의 비중\n\n"
        "**선택 항목 기준 상대 비율**: 선택 항목끼리의 상대 비중 (압도적 항목 제거 후 비교에 유용)"
    ),
    label_visibility="collapsed",
)

if not selected_ses:
    st.warning("⚠️ 사이드바에서 부작용을 1개 이상 선택해주세요.")
    st.stop()

filtered = all_counts[all_counts["side_effect"].isin(selected_ses)].copy()

if pct_mode == "선택 항목 합계 대비 (%)":
    sel_totals = filtered.groupby("Stage")["count"].sum().reset_index(name="sel_total")
    filtered = filtered.merge(sel_totals, on="Stage")
    filtered["percentage"] = filtered["count"] / filtered["sel_total"] * 100
    yaxis_label = "선택 항목 합계 대비 비율 (%)"
    banner_msg = "선택한 부작용들의 합계를 100%로 두고 각 항목의 상대 비중을 표시합니다."
else:
    yaxis_label = "해당 단계 전체 언급 대비 비율 (%)"
    banner_msg = "각 복용 단계의 총 언급 수 대비 해당 부작용의 비중을 표시합니다."

st.markdown(f"<div class='info-banner'>📌 {banner_msg}</div>", unsafe_allow_html=True)

order_base = (
    filtered.groupby("side_effect")["count"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)
filtered["side_effect_label"] = filtered["side_effect"].apply(se_display_name)
order_base_label = [se_display_name(se) for se in order_base]

st.markdown(
    f"<div class='section-title'>📈 선택 부작용 {len(selected_ses)}개 · 복용 단계별 비중 비교</div>",
    unsafe_allow_html=True,
)

filtered["Stage_label"] = filtered["Stage"].map(STAGE_LABELS)
stage_label_order = [STAGE_LABELS[s] for s in STAGE_ORDER]
stage_color_label = {STAGE_LABELS[k]: v for k, v in STAGE_COLORS.items()}

fig = px.bar(
    filtered,
    x="side_effect_label",
    y="percentage",
    color="Stage_label",
    barmode="group",
    text_auto=".1f",
    category_orders={
        "Stage_label": stage_label_order,
        "side_effect_label": order_base_label,
    },
    color_discrete_map=stage_color_label,
    template="plotly_white",
    labels={"Stage_label": "복용 단계", "side_effect_label": "부작용 항목"},
)

fig.update_layout(
    xaxis_title="부작용 항목",
    yaxis_title=yaxis_label,
    # 세 번째 사진 요청 반영: 복용 단계 글자색 진한 초록
    legend_title_text="복용 단계",
    legend_title_font=dict(color="#00462A", size=13, family="Noto Sans KR"),
    height=580,
    margin=dict(t=30, b=130, l=65, r=20),
    font=dict(family="Noto Sans KR", size=12, color="#1a2e24"),
    plot_bgcolor="#f9fcfa",
    paper_bgcolor="#ffffff",
    xaxis=dict(tickfont=dict(color="#1a2e24", size=10), title_font=dict(color="#1a2e24")),
    yaxis=dict(
        tickfont=dict(color="#1a2e24", size=11),
        title_font=dict(color="#1a2e24"),
        gridcolor="#e8f3ed",
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="right",
        x=1,
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#cce0d6",
        borderwidth=1,
        font=dict(color="#1a2e24", size=12),
    ),
)

fig.update_traces(
    textposition="outside",
    textfont=dict(color="#1a2e24", size=11, family="JetBrains Mono"),
    marker_line_color="white",
    marker_line_width=1.2,
    opacity=0.93,
    cliponaxis=False,
)
fig.update_xaxes(tickangle=-35)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# 단계별 상세수치 확인 표: expander 제거, 항상 고정 표시
st.markdown("<div class='table-title-box'>📝 단계별 상세 수치 확인</div>", unsafe_allow_html=True)

pivot_df = (
    filtered.pivot(index="side_effect_label", columns="Stage", values="percentage")
    .reindex(columns=STAGE_ORDER)
    .fillna(0)
    .round(2)
)

pivot_df = pivot_df.loc[pivot_df.sum(axis=1).sort_values(ascending=False).index]

col_headers = "".join(
    f"<th class='num-hd'>{STAGE_LABELS[c]}</th>"
    for c in pivot_df.columns
)

rows_html = ""
for i, (idx, row) in enumerate(pivot_df.iterrows(), 1):
    cells = "".join(f"<td class='num'>{v:.2f}%</td>" for v in row)
    rows_html += (
        f"<tr>"
        f"<td class='rank'>{i}</td>"
        f"<td class='se-name'>{idx}</td>"
        f"{cells}"
        f"</tr>"
    )

st.markdown(f"""
<style>
.htbl-wrap {{
    background:#fff;
    border-radius:0 0 12px 12px;
    overflow:hidden;
    border:1.5px solid #cce0d6;
    border-top:none;
    margin-bottom:1rem;
    box-shadow:var(--shadow-sm);
}}
.htbl {{
    width:100%;
    border-collapse:collapse;
    font-family:'Noto Sans KR', sans-serif;
    font-size:.82rem;
    color:#1a2e24;
}}
.htbl thead tr {{ background:#eef7f2; }}
.htbl thead th {{
    padding:11px 18px;
    font-size:.68rem;
    font-weight:700;
    letter-spacing:.1em;
    text-transform:uppercase;
    color:#00462A;
    border-bottom:2px solid #cce0d6;
    white-space:nowrap;
}}
.htbl thead th.num-hd {{ text-align:right; }}
.htbl tbody tr:nth-child(even) {{ background:#f7fbf9; }}
.htbl tbody tr:hover {{ background:#eef7f2; }}
.htbl tbody td {{
    padding:9px 18px;
    border-bottom:1px solid #e8f3ed;
    border-right:1px solid #e0ede6;
}}
.htbl tbody td:last-child {{ border-right:none; }}
.htbl thead th:not(:last-child) {{ border-right:1px solid #cce0d6; }}
.htbl .rank {{
    font-family:'JetBrains Mono', monospace;
    color:#5a7a68;
    text-align:center;
    width:32px;
    border-right:1px solid #e0ede6 !important;
    font-weight:400;
}}
.htbl .se-name {{
    color:#1a2e24;
    font-weight:500;
    border-right:1px solid #e0ede6 !important;
}}
.htbl .num {{
    font-family:'JetBrains Mono', monospace;
    color:#00462A;
    font-weight:400;
    text-align:right;
}}
</style>
<div class='htbl-wrap'>
  <table class='htbl'>
    <thead>
      <tr>
        <th style='text-align:center'>#</th>
        <th>부작용</th>
        {col_headers}
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)
