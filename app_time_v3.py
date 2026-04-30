import streamlit as st
import pandas as pd
import plotly.express as px
import os
import gdown

FILE_IDS = {
    "SideEffect_Analysis_Data.csv":         "1uXOLCoMnDnq_OyXjVS6-WD74nCslIb80",
}

def download_if_needed(filename, file_id):
    if not os.path.exists(filename):
        gdown.download(f"https://drive.google.com/uc?id={file_id}", filename, quiet=False)

for fname, fid in FILE_IDS.items():
    download_if_needed(fname, fid)

st.set_page_config(page_title="복용 기간별 부작용 분포", page_icon="💊", layout="wide")

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

/* 약물 카드 헤더 */
.drug-header {
    border-radius:10px; padding:14px 20px; margin-bottom:1rem;
    font-weight:700; font-size:1rem;
}
.drug-header-mounjaro {
    background:linear-gradient(90deg,#1a4f7a,#2e73b0);
    color:#fff;
}
.drug-header-wegovy {
    background:linear-gradient(90deg,#2e8b57,#4aad78);
    color:#fff;
}

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
    df = pd.read_csv("SideEffect_Analysis_Data.csv")
    df = df[(df["author"] != "[deleted]") & (df["side_effect"] != "unknown")]

    def assign_stage(m):
        if m < 3:
            return "Early-term"
        elif m < 6:
            return "Mid-term"
        else:
            return "Long-term"

    df["Stage"] = df["rel_month"].apply(assign_stage)

    # drug 컬럼 정규화: 소문자 + strip
    df["drug_clean"] = df["drug"].str.lower().str.strip()
    return df


df = load_data()

# 약물 목록 확인 후 Mounjaro / Wegovy 분리
DRUG_MOUNJARO_KEYS = ["mounjaro", "tirzepatide"]
DRUG_WEGOVY_KEYS   = ["wegovy", "semaglutide", "ozempic"]

def classify_drug(d):
    d = str(d).lower().strip()
    if any(k in d for k in DRUG_MOUNJARO_KEYS):
        return "Mounjaro"
    elif any(k in d for k in DRUG_WEGOVY_KEYS):
        return "Wegovy"
    else:
        return "Other"

df["Drug"] = df["drug_clean"].apply(classify_drug)

STAGE_ORDER  = ["Early-term", "Mid-term", "Long-term"]
STAGE_LABELS = {
    "Early-term": "Early-term",
    "Mid-term":   "Mid-term",
    "Long-term":  "Long-term",
}

# Mounjaro: 파란 계열 / Wegovy: 초록 계열
STAGE_COLORS_MOUNJARO = {
    "Early-term": "#1a4f7a",
    "Mid-term":   "#2874b5",
    "Long-term":  "#6db4e8",
}
STAGE_COLORS_WEGOVY = {
    "Early-term": "#1a5c38",
    "Mid-term":   "#2e8b57",
    "Long-term":  "#6db88a",
}

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


# ────────────────────────── Hero ──────────────────────────
st.markdown("""
<div class='page-hero'>
    <div class='page-hero-eyebrow'>Pharmacovigilance · Distribution of Side Effects by Drug &amp; Treatment Stage</div>
    <div class='page-hero-title'>📊 약물별 · 복용 기간별 부작용 분포 분석</div>
    <div class='page-hero-sub'>Mounjaro와 Wegovy의 복용 기간에 따른 주요 부작용 비중 변화를 각각 비교합니다.</div>
</div>
""", unsafe_allow_html=True)

# ────────────────────────── 데이터 분포 확인 ──────────────────────────
df_m = df[df["Drug"] == "Mounjaro"]
df_w = df[df["Drug"] == "Wegovy"]

other_cnt = len(df[df["Drug"] == "Other"])
st.markdown(f"""
<style>
.stat-card {{
    background:#fff; border:1.5px solid var(--border);
    border-left:4px solid var(--ewha);
    border-radius:var(--radius-md); padding:14px 20px;
    margin-bottom:1rem;
}}
.stat-label {{
    font-size:.78rem; font-weight:700; color:#00462A;
    letter-spacing:.03em; margin-bottom:4px;
}}
.stat-value {{
    font-family:'JetBrains Mono', monospace;
    font-size:.95rem; font-weight:500; color:#5a7a68;
}}
</style>
<div style='display:flex; gap:1rem; margin-bottom:1rem;'>
  <div class='stat-card' style='flex:1'>
    <div class='stat-label'>Mounjaro 전체 언급 수</div>
    <div class='stat-value'>{len(df_m):,}건</div>
  </div>
  <div class='stat-card' style='flex:1'>
    <div class='stat-label'>Wegovy 전체 언급 수</div>
    <div class='stat-value'>{len(df_w):,}건</div>
  </div>
  
</div>
""", unsafe_allow_html=True)

# ────────────────────────── Sidebar ──────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-size:1.05rem;font-weight:700;color:#d4ede2;margin:1rem 0 0.3rem'>⚙️ 분석 설정</div>
    <div style='height:1px;background:rgba(255,255,255,0.1);margin-bottom:1.2rem'></div>
    """, unsafe_allow_html=True)

    top_n = 15

    st.markdown("""
    <div style='font-size:0.62rem;letter-spacing:0.16em;text-transform:uppercase;
                color:#7aad95;margin-bottom:0.7rem;font-weight:700'>
        부작용 항목 선택
    </div>
    """, unsafe_allow_html=True)

    # 전체(Mounjaro+Wegovy) 기준 상위 N개 풀
    pool_df_all = df[df["Drug"].isin(["Mounjaro", "Wegovy"])]
    top_pool    = pool_df_all["side_effect"].value_counts().head(top_n).index.tolist()
    sorted_pool = pool_df_all[pool_df_all["side_effect"].isin(top_pool)]["side_effect"].value_counts().index.tolist()

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

# ────────────────────────── Y축 기준 선택 ──────────────────────────
st.markdown("<div class='section-title'>📐 비율 기준 선택</div>", unsafe_allow_html=True)

pct_mode = st.radio(
    "Y축 기준",
    ["전체 데이터 기준 비율 (%)", "선택 항목 기준 상대 비율 (%)"],
    index=0,
    horizontal=True,
    label_visibility="collapsed",
)

if not selected_ses:
    st.warning("⚠️ 사이드바에서 부작용을 1개 이상 선택해주세요.")
    st.stop()

if pct_mode == "전체 데이터 기준 비율 (%)":
    yaxis_label = "해당 기간 전체 언급 대비 비율 (%)"

else:
    yaxis_label = "선택 항목 합계 대비 비율 (%)"
    banner_msg  = "선택한 부작용들의 합계를 100%로 두고 각 항목의 상대 비중을 표시합니다."



# ────────────────────────── 공통 집계 함수 ──────────────────────────
def build_chart_data(drug_df: pd.DataFrame, selected: list[str], mode: str):
    """선택된 부작용 + 기간별 비율 집계"""
    pool_filtered = drug_df[drug_df["side_effect"].isin(top_pool)]
    stage_totals  = drug_df.groupby("Stage").size().reset_index(name="stage_total")
    counts = (
        pool_filtered.groupby(["Stage", "side_effect"])
        .size()
        .reset_index(name="count")
        .merge(stage_totals, on="Stage")
    )
    counts["percentage"] = counts["count"] / counts["stage_total"] * 100

    filtered = counts[counts["side_effect"].isin(selected)].copy()

    if mode == "선택 항목 기준 상대 비율 (%)":
        sel_totals = filtered.groupby("Stage")["count"].sum().reset_index(name="sel_total")
        filtered   = filtered.merge(sel_totals, on="Stage")
        filtered["percentage"] = filtered["count"] / filtered["sel_total"] * 100

    filtered["side_effect_label"] = filtered["side_effect"].apply(se_display_name)
    filtered["Stage_label"]       = filtered["Stage"].map(STAGE_LABELS)
    return filtered


def make_fig(filtered, stage_colors, title_suffix):
    order_base       = (filtered.groupby("side_effect_label")["count"].sum()
                        .sort_values(ascending=False).index.tolist())
    stage_label_order = [STAGE_LABELS[s] for s in STAGE_ORDER]
    stage_color_label = {STAGE_LABELS[k]: v for k, v in stage_colors.items()}

    fig = px.bar(
        filtered,
        x="side_effect_label",
        y="percentage",
        color="Stage_label",
        barmode="group",
        text_auto=".1f",
        category_orders={"Stage_label": stage_label_order, "side_effect_label": order_base},
        color_discrete_map=stage_color_label,
        template="plotly_white",
        labels={"Stage_label": "복용 기간", "side_effect_label": "부작용 항목"},
        title=title_suffix,
    )
    fig.update_layout(
        xaxis_title="부작용 항목",
        yaxis_title=yaxis_label,
        legend_title_text="복용 기간",
        legend_title_font=dict(color="#00462A", size=12, family="Noto Sans KR"),
        height=520,
        margin=dict(t=50, b=120, l=65, r=20),
        font=dict(family="Noto Sans KR", size=11, color="#1a2e24"),
        plot_bgcolor="#f9fcfa",
        paper_bgcolor="#ffffff",
        title_font=dict(size=14, color="#1a2e24", family="Noto Sans KR"),
        xaxis=dict(tickfont=dict(color="#1a2e24", size=9), title_font=dict(color="#1a2e24")),
        yaxis=dict(
            tickfont=dict(color="#1a2e24", size=10),
            title_font=dict(color="#1a2e24"),
            gridcolor="#e8f3ed",
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.9)", bordercolor="#cce0d6", borderwidth=1,
            font=dict(color="#1a2e24", size=11),
        ),
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#1a2e24", size=10, family="JetBrains Mono"),
        marker_line_color="white", marker_line_width=1.2,
        opacity=0.93, cliponaxis=False,
    )
    fig.update_xaxes(tickangle=-35)
    return fig


# ────────────────────────── 집계 ──────────────────────────
filtered_m = build_chart_data(df_m, selected_ses, pct_mode)
filtered_w = build_chart_data(df_w, selected_ses, pct_mode)

# ────────────────────────── 차트 (2열 나란히) ──────────────────────────
st.markdown(
    f"<div class='section-title'>📈 선택 부작용 {len(selected_ses)}개 · 약물별 복용 기간 비교</div>",
    unsafe_allow_html=True,
)

col_w, col_m = st.columns(2)

with col_w:
    st.markdown("<div class='drug-header drug-header-wegovy'>💉 Wegovy (Semaglutide)</div>",
                unsafe_allow_html=True)
    if filtered_w.empty:
        st.info("Wegovy 데이터에 선택된 부작용 데이터가 없습니다.")
    else:
        n_w = len(df_w)
        st.caption(f"총 {n_w:,}건 분석")
        fig_w = make_fig(filtered_w, STAGE_COLORS_WEGOVY, "Wegovy")
        st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar": False})

with col_m:
    st.markdown("<div class='drug-header drug-header-mounjaro'>💉 Mounjaro (Tirzepatide)</div>",
                unsafe_allow_html=True)
    if filtered_m.empty:
        st.info("Mounjaro 데이터에 선택된 부작용 데이터가 없습니다.")
    else:
        n_m = len(df_m)
        st.caption(f"총 {n_m:,}건 분석")
        fig_m = make_fig(filtered_m, STAGE_COLORS_MOUNJARO, "Mounjaro")
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})


# ────────────────────────── 상세 수치 표 (약물별) ──────────────────────────
def render_table(filtered, drug_name):
    if filtered.empty:
        return

    st.markdown(f"<div class='table-title-box'>📝 {drug_name} ·기간별 상세 수치</div>",
                unsafe_allow_html=True)

    pivot_df = (
        filtered.pivot(index="side_effect_label", columns="Stage", values="percentage")
        .reindex(columns=STAGE_ORDER)
        .fillna(0)
        .round(2)
    )
    pivot_df = pivot_df.loc[pivot_df.sum(axis=1).sort_values(ascending=False).index]

    col_headers = "".join(
        f"<th class='num-hd'>{STAGE_LABELS[c]}</th>"
        for c in pivot_df.columns if c in STAGE_LABELS
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
    background:#fff; border-radius:0 0 12px 12px; overflow:hidden;
    border:1.5px solid #cce0d6; border-top:none;
    margin-bottom:1rem; box-shadow:var(--shadow-sm);
}}
.htbl {{
    width:100%; border-collapse:collapse; table-layout:fixed;
    font-family:'Noto Sans KR', sans-serif; font-size:.82rem; color:#1a2e24;
}}
.htbl colgroup col.col-rank  {{ width:58px; }}
.htbl colgroup col.col-name  {{ width:220px; }}
.htbl colgroup col.col-num   {{ width:auto; }}
.htbl thead tr {{ background:#eef7f2; }}
.htbl thead th {{
    padding:9px 14px; font-size:.67rem; font-weight:700;
    letter-spacing:.08em; text-transform:uppercase; color:#00462A;
    border-bottom:2px solid #cce0d6; white-space:nowrap;
}}
.htbl thead th.num-hd {{ text-align:right; }}
.htbl tbody tr:nth-child(even) {{ background:#f7fbf9; }}
.htbl tbody tr:hover {{ background:#eef7f2; }}
.htbl tbody td {{
    padding:7px 14px; border-bottom:1px solid #e8f3ed;
    border-right:1px solid #e0ede6; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}}
.htbl tbody td:last-child {{ border-right:none; }}
.htbl thead th:not(:last-child) {{ border-right:1px solid #cce0d6; }}
..htbl .rank {{
    font-family:'JetBrains Mono', monospace; 
    color:#5a7a68;
    text-align:center;
    border-right:1px solid #e0ede6 !important; 
    font-weight:400;
    min-width:58px;
    padding-left:10px;
    padding-right:10px;
}}
.htbl .se-name {{ color:#1a2e24; font-weight:500; border-right:1px solid #e0ede6 !important; }}
.htbl .num {{
    font-family:'JetBrains Mono', monospace; color:#00462A;
    font-weight:400; text-align:right;
}}
/* 탭 글자 진한 초록 */
[data-testid="stTabs"] button[role="tab"] {{
    color:#00462A !important; font-weight:600 !important;
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    color:#00462A !important; font-weight:700 !important;
}}
</style>
<div class='htbl-wrap'>
  <table class='htbl'>
    <colgroup>
      <col class='col-rank'/>
      <col class='col-name'/>
      <col class='col-num'/><col class='col-num'/><col class='col-num'/>
    </colgroup>
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


st.markdown("<div class='section-title'>📝 약물별 기간별 상세 수치</div>", unsafe_allow_html=True)

tbl_w, tbl_m = st.columns(2)

with tbl_w:
    render_table(filtered_w, "Wegovy")

with tbl_m:
    render_table(filtered_m, "Mounjaro")