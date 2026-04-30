import os
import json
import random
import ast
from itertools import combinations
from collections import defaultdict

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import gdown

# 파일별 Google Drive ID 입력
FILE_IDS = {
    "mounjaro_dc_2.jsonl":         "1faTMdwppHkiclwpSSx7au4qg6Zo61Bk6",
    "wegovy_dc_1.json":             "112zEwo4ju_S_oSD7dmP22dbS3d0WqFFD",
    "Reddit_v8.jsonl":              "1ojqRqcL5GnjY6mCqwztlSPwxtcCeDvgY",
}

def download_if_needed(filename, file_id):
    if not os.path.exists(filename):
        gdown.download(f"https://drive.google.com/uc?id={file_id}", filename, quiet=False)

for fname, fid in FILE_IDS.items():
    download_if_needed(fname, fid)

# ════════════════════════════════════════════════════════════════════
#  0. 페이지 설정
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="부작용 네트워크 분석",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════
#  1. 이화그린 테마 (#00462A)
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Noto+Sans+KR:wght@300;400;500;700&family=JetBrains+Mono:wght@500&display=swap');

/* ── 기본 변수 ── */
:root {
    --ewha:        #00462A;
    --ewha-light:  #1a7a50;
    --ewha-pale:   #d4ede2;
    --ewha-dark:   #002e1c;
    --ewha-faint:  #eef7f2;
    --gold:        #c9a84c;
    --bg:          #f2f6f4;
    --surface:     #ffffff;
    --border:      #cce0d6;
    --text:        #1a2e24;
    --muted:       #5a7a68;
    --radius-lg:   16px;
    --radius-md:   12px;
    --radius-sm:   8px;
    --shadow-sm:   0 2px 8px rgba(0,70,42,0.06);
    --shadow-md:   0 4px 20px rgba(0,70,42,0.09);
}

/* ── 전역 ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] > div {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #001f14 0%, var(--ewha-dark) 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #c8e0d4 !important; }
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
    padding: 0 4px;
}

/* ── 헤더 제거 ── */
[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── 메인 패딩 ── */
.block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1600px !important;
}

/* ════ 히어로 ════ */
.hero {
    background: linear-gradient(135deg, var(--ewha-dark) 0%, var(--ewha) 65%, #0a8c50 100%);
    border-radius: 20px;
    padding: 2.8rem 3.5rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 40px rgba(0,70,42,0.22);
}
.hero::before {
    content: '⬡';
    position: absolute;
    right: -2rem; top: -3rem;
    font-size: 18rem;
    color: rgba(255,255,255,0.03);
    line-height: 1;
    pointer-events: none;
}
.hero::after {
    content: '💊';
    position: absolute;
    right: 3.5rem; top: 50%;
    transform: translateY(-50%);
    font-size: 5.5rem;
    opacity: 0.14;
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--ewha-pale);
    opacity: 0.75;
    margin-bottom: 0.75rem;
}
.hero-title {
    font-family: 'Noto Sans KR', serif !important;
    font-size: clamp(1.5rem, 3vw, 2.6rem) !important;
    font-weight: 600 !important;
    color: #ffffff !important;
    line-height: 1.25 !important;
    margin: 0 0 0.5rem 0 !important;
}
.hero-title em {
    font-style: italic;
    font-weight: 400;
    color: var(--ewha-pale);
}
.hero-sub {
    font-size: 0.82rem;
    color: var(--ewha-pale);
    opacity: 0.68;
    margin-top: 0.4rem;
    letter-spacing: 0.04em;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--ewha-pale);
    margin-top: 1rem;
    letter-spacing: 0.06em;
}

/* ════ 메트릭 그룹 래퍼 ════ */
.metric-group {
    margin-bottom: 1.2rem;
}

/* ════ 메트릭 카드 그리드 ════ */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}
.metric-card {
    background: var(--ewha-faint);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 16px 12px;
    position: relative;
    overflow: hidden;
    box-shadow: none;
    transition: box-shadow 0.2s, transform 0.15s;
    min-width: 0;          /* grid 넘침 방지 */
}
.metric-card:hover {
    box-shadow: var(--shadow-sm);
    transform: translateY(-1px);
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--ewha) 0%, var(--ewha-light) 100%);
    border-radius: 0 0 var(--radius-md) var(--radius-md);
}
.metric-icon {
    font-size: 1.1rem;
    margin-bottom: 6px;
    display: block;
    line-height: 1;
}
.metric-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
    white-space: nowrap;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: clamp(1rem, 2vw, 1.45rem);  /* 뷰포트에 따라 자동 조절 */
    font-weight: 600;
    color: var(--ewha);
    line-height: 1.1;
    letter-spacing: -0.02em;
    white-space: nowrap;   /* 절대 줄바꿈 안 함 */
    overflow: hidden;
    text-overflow: ellipsis;
}
.metric-unit {
    font-size: 0.62rem;
    color: var(--muted);
    margin-top: 3px;
    letter-spacing: 0.04em;
}

/* ════ 탭 ════ */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--surface);
    border-radius: var(--radius-md);
    padding: 5px 6px;
    border: 1.5px solid var(--border);
    gap: 4px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.2rem;
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: var(--radius-sm) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    padding: 9px 22px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] [role="tab"]:hover:not([aria-selected="true"]) {
    background: var(--ewha-faint) !important;
    color: var(--ewha) !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, var(--ewha), var(--ewha-light)) !important;
    color: #ffffff !important;
    box-shadow: 0 3px 10px rgba(0,70,42,0.28) !important;
}

/* ════ 섹션 헤더 ════ */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--ewha-dark);
    margin: 1.8rem 0 0.9rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: 0.01em;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border) 0%, transparent 100%);
}

/* ════ 약물 헤더 ════ */
.drug-header {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 20px;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}
.drug-flag { font-size: 1.6rem; line-height: 1; }
.drug-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--ewha-dark);
}
.drug-sub { font-size: 0.72rem; color: var(--muted); margin-top: 1px; }
.drug-badge {
    margin-left: auto;
    background: var(--ewha-faint);
    border: 1px solid var(--ewha-pale);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.68rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--ewha);
    letter-spacing: 0.05em;
}

/* ════ 그래프 래퍼 ════ */
.graph-wrap {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-md);
    margin-bottom: 0.5rem;
}

/* ════ 범례 ════ */
.legend-wrap {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 12px;
    align-items: center;
}
.legend-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--ewha-faint);
    border: 1px solid var(--ewha-pale);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    color: var(--ewha);
    font-weight: 500;
}
.legend-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.legend-hint {
    margin-left: auto;
    font-size: 0.7rem;
    color: var(--muted);
    font-style: italic;
}

/* ════ 데이터프레임 — 흰 배경 + 진한 초록 글자 ════ */
[data-testid="stDataFrame"] {
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
    background: #ffffff !important;
}
/* iframe 내부 테이블 오버라이드 */
[data-testid="stDataFrame"] iframe {
    background: #ffffff !important;
}
/* 테이블 섹션 헤더/바디 흰 배경 */
.table-section { background: #ffffff !important; }
.table-section-header {
    background: #eef7f2 !important;
    color: var(--ewha-dark) !important;
    border-bottom: 1.5px solid var(--border) !important;
}
/* 섹션 타이틀 진한 초록 */
.section-title { color: var(--ewha-dark) !important; }
/* 빈도 순위 등 모든 테이블 래퍼 */
[data-testid="stDataFrame"] * {
    color: var(--ewha-dark) !important;
    background: transparent !important;
}
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] thead * {
    color: var(--ewha) !important;
    font-weight: 700 !important;
    background: var(--ewha-faint) !important;
}
[data-testid="stDataFrame"] td {
    color: var(--ewha-dark) !important;
}

/* ════ 사이드바 ════ */
.sb-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    color: #d4ede2 !important;
    font-weight: 600;
    margin: 1.2rem 0 0.3rem 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sb-divider {
    height: 1px;
    background: rgba(255,255,255,0.08);
    margin: 1rem 0;
}
.sb-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #7aad95 !important;
    margin: 1.2rem 0 0.6rem 0;
    display: block;
}
.sb-stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--radius-sm);
    padding: 9px 13px;
    margin: 4px 0;
    font-size: 0.79rem;
}
.sb-stat-key { color: #a0c8b4 !important; }
.sb-stat-val {
    font-family: 'JetBrains Mono', monospace;
    color: #e0f0e8 !important;
    font-size: 0.74rem;
    background: rgba(255,255,255,0.07);
    padding: 2px 8px;
    border-radius: 4px;
}
.sb-note {
    background: rgba(201,168,76,0.1);
    border-left: 3px solid #c9a84c;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 10px 13px;
    font-size: 0.76rem;
    color: #d4b96a !important;
    margin-top: 1rem;
    line-height: 1.55;
}

/* ════ 경고 / 노 데이터 ════ */
.no-data {
    text-align: center;
    padding: 4rem 2rem;
    background: var(--surface);
    border-radius: var(--radius-lg);
    border: 1.5px dashed var(--border);
    box-shadow: var(--shadow-sm);
}
.no-data-icon { font-size: 3rem; margin-bottom: 0.8rem; }
.no-data-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: var(--muted);
    margin-bottom: 0.3rem;
}
.no-data-desc { font-size: 0.8rem; color: #aaa; }

/* ════ 구분선 ════ */
.col-divider {
    width: 1px;
    background: var(--border);
    margin: 0 0.5rem;
    align-self: stretch;
    border-radius: 1px;
}

/* ════ 하단 테이블 컨테이너 ════ */
.table-section {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}
.table-section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 13px 18px;
    background: var(--ewha-faint);
    border-bottom: 1.5px solid var(--border);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--ewha-dark);
}
.table-section-body {
    padding: 12px 14px 14px;
}
.table-card-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

/* Streamlit warning 스타일 재정의 */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: 1.5px solid #f0c36d !important;
    background: #fffbf0 !important;
}

/* ════ 비율 기준 선택 radio 스타일 수정 ════ */
div[role="radiogroup"] label,
div[role="radiogroup"] label * {
    background: transparent !important;
    color: var(--ewha-dark) !important;
    font-weight: 700 !important;
}
div[role="radiogroup"] label:hover,
div[role="radiogroup"] label:hover * {
    background: transparent !important;
    color: var(--ewha) !important;
}

/* ════ 복용 단계 legend 제목 색상 수정 ════ */
.stage-title,
.dose-stage-title,
.legend-title,
.stage-legend-title {
    color: var(--ewha-dark) !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  2. 파일 경로 설정
# ════════════════════════════════════════════════════════════════════
def get_path(key, fallback=""):
    try:
        return st.secrets[key]
    except Exception:
        return fallback

FILE_PATHS = {
    "dc_wegovy":   "wegovy_dc_1.json",
    "dc_mounjaro": "mounjaro_dc_1.json",
    "reddit":      "Reddit_v8.jsonl",
}
SAMPLE_SIZE = 30_000

# ════════════════════════════════════════════════════════════════════
#  3. 한/영 부작용 매핑
# ════════════════════════════════════════════════════════════════════
SE_MAP = {
    "appetite_loss":            "식욕감소\nAppetite Loss",
    "nausea":                   "오심/메스꺼움\nNausea",
    "stomach_pain":             "복통\nStomach Pain",
    "diarrhea":                 "설사\nDiarrhea",
    "hypoglycemia":             "저혈당\nHypoglycemia",
    "insomnia":                 "불면증\nInsomnia",
    "acid_reflux":              "위식도역류\nAcid Reflux",
    "fatigue":                  "피로/무기력\nFatigue",
    "severe_gastrointestinal":  "심한위장장애\nSevere GI",
    "constipation":             "변비\nConstipation",
    "hair_loss":                "탈모\nHair Loss",
    "gallbladder_disease":      "담낭질환\nGallbladder",
    "heart_rate_increase":      "심박수증가\nTachycardia",
    "headache":                 "두통\nHeadache",
    "skin_changes":             "피부이상\nSkin Changes",
    "hypersensitivity":         "과민반응\nHypersensitivity",
    "pancreatitis":             "췌장염\nPancreatitis",
    "vomiting":                 "구토\nVomiting",
    "dizziness":                "어지러움\nDizziness",
    "aspiration_risk":          "흡인위험\nAspiration Risk",
    "thyroid_tumor":            "갑상선종양\nThyroid Tumor",
    "kidney_injury":            "신장손상\nKidney Injury",
    "retinopathy_aggravation":  "망막병증악화\nRetinopathy",
    "muscle_pain":              "근육통\nMuscle Pain",
    "burping":                  "트림\nBurping",
    "bloating":                 "고창/가스참\nBloating",
    "indigestion":              "소화불량\nIndigestion",
    "hypotension":              "저혈압\nHypotension",
    "구토":                     "구토\nVomiting",
    "오심(메스꺼움)":           "오심/메스꺼움\nNausea",
    "부작용 (명시되지 않음)":   "기타부작용\nOther SE",
    "설사":                     "설사\nDiarrhea",
    "피로/무기력":              "피로/무기력\nFatigue",
    "변비":                     "변비\nConstipation",
    "트림":                     "트림\nBurping",
    "두통":                     "두통\nHeadache",
    "어지러움":                 "어지러움\nDizziness",
    "소화불량":                 "소화불량\nIndigestion",
    "고창(가스참)":             "고창/가스참\nBloating",
    "위식도 역류":              "위식도역류\nAcid Reflux",
    "피부 이상":                "피부이상\nSkin Changes",
    "근육통":                   "근육통\nMuscle Pain",
    "탈모":                     "탈모\nHair Loss",
    "불면증":                   "불면증\nInsomnia",
    "복통":                     "복통\nStomach Pain",
    "저혈압":                   "저혈압\nHypotension",
    "저혈당":                   "저혈당\nHypoglycemia",
    "심박수 증가":              "심박수증가\nTachycardia",
    "담낭 질환":                "담낭질환\nGallbladder",
    "췌장염":                   "췌장염\nPancreatitis",
    "신장 손상":                "신장손상\nKidney Injury",
    "식욕감소":                 "식욕감소\nAppetite Loss",
}
EXCLUDE_SE_LABELS = {
    "기타부작용\nOther SE",
    "기타부작용 / Other SE",
    "부작용 (명시되지 않음)",
    "Other SE",
}

def normalize_se(raw: str) -> str:
    if not raw:
        return ""
    key = raw.strip().lower()
    if key in SE_MAP:
        return SE_MAP[key]
    raw_s = raw.strip()
    if raw_s in SE_MAP:
        return SE_MAP[raw_s]
    return raw_s
# ════════════════════════════════════════════════════════════════════
#  4. 데이터 로드
# ════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_dc(path: str, drug_label: str) -> list:
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    records = []
    for item in raw:
        se_raw = item.get("side_effects", "")
        if not se_raw:
            continue
        effects = [normalize_se(e) for e in str(se_raw).split(",") if e.strip()]
        effects = [e for e in effects if e]
        if effects:
            records.append({
                "uid": str(item.get("document_id", item.get("author", ""))),
                "drug": drug_label,
                "side_effects": effects,
            })
    return records


@st.cache_data(show_spinner=False)
def load_reddit(path: str) -> dict:
    result = {"wegovy": [], "mounjaro": []}
    if not path or not os.path.exists(path):
        return result
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue
            drug = item.get("drug", "").lower()
            if drug not in result:
                continue
            se_raw = item.get("side_effects", [])
            if isinstance(se_raw, str):
                try:
                    se_raw = ast.literal_eval(se_raw)
                except Exception:
                    se_raw = [e.strip() for e in se_raw.split(",") if e.strip()]
            effects = [normalize_se(e) for e in se_raw if e and str(e).strip()]
            effects = [e for e in effects if e]
            if effects:
                result[drug].append({
                    "uid": str(item.get("author", item.get("pk", ""))),
                    "drug": drug,
                    "side_effects": effects,
                })
    return result


@st.cache_data(show_spinner=False)
def get_all_data() -> dict:
    dc_w   = load_dc(FILE_PATHS["dc_wegovy"],   "wegovy")
    dc_m   = load_dc(FILE_PATHS["dc_mounjaro"], "mounjaro") if FILE_PATHS["dc_mounjaro"] else []
    reddit = load_reddit(FILE_PATHS["reddit"])
    return {
        "dc_wegovy":       dc_w,
        "dc_mounjaro":     dc_m,
        "reddit_wegovy":   reddit["wegovy"],
        "reddit_mounjaro": reddit["mounjaro"],
    }


def sample_records(records: list, n: int = SAMPLE_SIZE, seed: int = 42) -> list:
    if len(records) <= n:
        return records
    random.seed(seed)
    return random.sample(records, n)

# ════════════════════════════════════════════════════════════════════
#  5. 네트워크 분석
# ════════════════════════════════════════════════════════════════════
def build_network(records: list, top_n: int, min_weight: int):
    user_effects: dict = defaultdict(set)

    for r in records:
        filtered_effects = [
            e for e in r["side_effects"]
            if e and e not in EXCLUDE_SE_LABELS
        ]

        if filtered_effects:
            user_effects[r["uid"]].update(filtered_effects)

    effect_freq: dict = defaultdict(int)
    for effects in user_effects.values():
        for e in effects:
            effect_freq[e] += 1

    top_effects = set(
        e for e, _ in sorted(effect_freq.items(), key=lambda x: -x[1])[:top_n]
    )

    edge_weights: dict = defaultdict(int)
    for effects in user_effects.values():
        filtered = sorted(effects & top_effects)
        if len(filtered) > 1:
            for a, b in combinations(filtered, 2):
                edge_weights[(a, b)] += 1

    G = nx.Graph()
    for e in top_effects:
        freq = effect_freq.get(e, 0)
        G.add_node(e, freq=freq)

    for (a, b), w in edge_weights.items():
        if w >= min_weight:
            G.add_edge(a, b, weight=w)


    G.remove_nodes_from(list(nx.isolates(G)))
    return G, effect_freq, edge_weights


def freq_to_size(freq: int, freq_min: int, freq_max: int) -> float:
    SIZE_MIN, SIZE_MAX = 18, 70
    log_v   = np.log1p(freq)
    log_min = np.log1p(freq_min)
    log_max = np.log1p(freq_max)
    if log_max == log_min:
        return (SIZE_MIN + SIZE_MAX) / 2
    norm = (log_v - log_min) / (log_max - log_min)
    return SIZE_MIN + norm * (SIZE_MAX - SIZE_MIN)


def build_figure(G: nx.Graph) -> go.Figure | None:
    if not G.nodes:
        return None

    # 노드 수에 따라 k(반발력) 동적 조정 — 노드가 많을수록 더 넓게 배치
    n_nodes = len(G.nodes)
    k_val   = max(3.5, 5.0 / (n_nodes ** 0.35))
    pos = nx.spring_layout(G, k=k_val, iterations=300, seed=42, scale=2.5)

    weights = [d["weight"] for _, _, d in G.edges(data=True)]
    max_w = max(weights) if weights else 1
    min_w = min(weights) if weights else 1

    freqs    = [G.nodes[n]["freq"] for n in G.nodes()]
    freq_min = min(freqs)
    freq_max = max(freqs)

    # ── 엣지 ──
    edge_traces = []
    for u, v, d in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        norm_w = (d["weight"] - min_w) / (max_w - min_w + 1e-5)
        alpha  = 0.12 + norm_w * 0.45
        width  = 0.8 + norm_w * 7
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode="lines",
            line=dict(width=width, color=f"rgba(0,90,50,{alpha:.2f})"),
            hoverinfo="none",
        ))

    # ── 노드 ──
    node_x, node_y, node_labels = [], [], []
    node_sizes, node_colors, node_hover = [], [], []

    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        node_labels.append(n.replace("\n", "<br>"))

        freq = G.nodes[n]["freq"]
        node_sizes.append(freq_to_size(freq, freq_min, freq_max))
        node_colors.append(freq)

        node_hover.append(
            f"<b>{n.replace(chr(10), ' / ')}</b><br>"
            f"언급 빈도: <b>{freq:,}건</b><br>"
            f"연결 부작용: <b>{G.degree(n)}개</b>"
        )

    label_pos = {}
    coords = np.array([pos[n] for n in G.nodes()])
    center = coords.mean(axis=0)

    for idx, n in enumerate(G.nodes()):
        x, y = pos[n]
        vec = np.array([x, y]) - center
        norm = np.linalg.norm(vec)
        if norm < 1e-6:
            angle = 2 * np.pi * idx / max(1, n_nodes)
            vec = np.array([np.cos(angle), np.sin(angle)])
        else:
            vec = vec / norm

        # 빈도 높은 큰 노드일수록 라벨을 조금 더 바깥으로 밀어냄
        freq = G.nodes[n]["freq"]
        size_norm = (np.log1p(freq) - np.log1p(freq_min)) / (np.log1p(freq_max) - np.log1p(freq_min) + 1e-9)
        label_pos[n] = np.array([x, y]) + vec * (0.22 + 0.16 * size_norm)

    # 간단한 label repulsion: 라벨끼리 너무 가까우면 서로 밀어냄
    nodes = list(G.nodes())
    min_dist = 0.34
    for _ in range(120):
        moved = False
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                a, b = nodes[i], nodes[j]
                delta = label_pos[a] - label_pos[b]
                dist = np.linalg.norm(delta)
                if 1e-6 < dist < min_dist:
                    push = delta / dist * (min_dist - dist) * 0.5
                    label_pos[a] += push
                    label_pos[b] -= push
                    moved = True
        if not moved:
            break

    all_x = list(node_x) + [float(label_pos[n][0]) for n in nodes]
    all_y = list(node_y) + [float(label_pos[n][1]) for n in nodes]
    pad_x = (max(all_x) - min(all_x)) * 0.12 + 0.25
    pad_y = (max(all_y) - min(all_y)) * 0.12 + 0.25

    label_annotations = []
    for n in nodes:
        lx, ly = label_pos[n]
        label_annotations.append(dict(
            x=float(lx), y=float(ly),
            text=n.replace("\n", " / "),
            showarrow=False,
            font=dict(size=12, color="#002e1c", family="Noto Sans KR"),
            bgcolor="rgba(255,255,255,0.82)",
            bordercolor="rgba(204,224,214,0.95)",
            borderwidth=1,
            borderpad=3,
            opacity=0.98,
        ))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        text=node_labels,
        textposition="top center",
        hovertext=node_hover,
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale=[
                [0.00, "#d4ede2"],
                [0.25, "#7ec4a0"],
                [0.50, "#2e9060"],
                [0.75, "#1a6040"],
                [1.00, "#00462A"],
            ],
            color=node_colors,
            size=node_sizes,
            colorbar=dict(
                title=dict(
                    text="언급 빈도",
                    font=dict(color="#5a7a68", size=11, family="Noto Sans KR"),
                ),
                thickness=10,
                len=0.45,
                x=1.01,
                tickfont=dict(color="#5a7a68", size=9),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
            ),
            line=dict(width=2.5, color="#ffffff"),
            opacity=0.93,
        ),
    )

    fig = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            height=620,
            margin=dict(t=24, b=24, l=24, r=90),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f9fcfa",
            xaxis=dict(visible=False, showgrid=False, zeroline=False, range=[min(all_x)-pad_x, max(all_x)+pad_x]),
            yaxis=dict(visible=False, showgrid=False, zeroline=False, range=[min(all_y)-pad_y, max(all_y)+pad_y]),
            annotations=label_annotations,
            hovermode="closest",
            showlegend=False,
            font=dict(family="Noto Sans KR", color="#1a2e24"),
        ),
    )
    return fig

# ════════════════════════════════════════════════════════════════════
#  6. 탭 렌더링
# ════════════════════════════════════════════════════════════════════
def render_tab(records: list, top_n: int, min_weight: int, source_label: str = ""):
    if not records:
        st.markdown("""
        <div class='no-data'>
            <div class='no-data-icon'>📂</div>
            <div class='no-data-title'>데이터 없음</div>
            <div class='no-data-desc'>secrets.toml 에서 파일 경로를 확인해주세요.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    sampled = sample_records(records, SAMPLE_SIZE)
    G, effect_freq, edge_weights = build_network(sampled, top_n, min_weight)
    n_users = len(set(r["uid"] for r in sampled))

    # ── 메트릭 카드 ──
    icons  = ["📄", "👤", "⬡", "🔗"]
    labels = ["분석 데이터", "고유 유저", "부작용 노드", "연결 엣지"]
    values = [f"{len(sampled):,}", f"{n_users:,}", str(len(G.nodes)), str(len(G.edges))]
    units  = ["건", "명", "개", "개"]

    inner = "".join(
        f"<div class='metric-card'>"
        f"<span class='metric-icon'>{icon}</span>"
        f"<div class='metric-label'>{label}</div>"
        f"<div class='metric-value'>{val}</div>"
        f"<div class='metric-unit'>{unit}</div>"
        f"</div>"
        for icon, label, val, unit in zip(icons, labels, values, units)
    )
    st.markdown(
        f"<div class='metric-group'><div class='metric-row'>{inner}</div></div>",
        unsafe_allow_html=True,
    )

    if not G.nodes:
        st.warning("⚠️ 조건에 맞는 노드가 없습니다. 사이드바에서 최소 연결 강도를 낮춰보세요.")
        return

    # ── 범례 ──
    st.markdown("""
    <div class='legend-wrap'>
        <div class='legend-chip'>
            <span class='legend-dot' style='background:#d4ede2;border:1.5px solid #7ec4a0'></span>낮은 빈도
        </div>
        <div class='legend-chip'>
            <span class='legend-dot' style='background:#2e9060'></span>중간 빈도
        </div>
        <div class='legend-chip'>
            <span class='legend-dot' style='background:#00462A'></span>높은 빈도
        </div>
        <span class='legend-hint'>노드 크기 · 색상 = 언급 빈도 &nbsp;|&nbsp; 선 굵기 = 동시 언급 강도</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 네트워크 그래프 ──
    fig = build_figure(G)
    if fig:
        st.markdown("<div class='graph-wrap'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 하단 테이블 ──
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin:1.8rem 0 1rem'>
      <span style='font-family:"Playfair Display",serif;font-size:1rem;font-weight:600;color:#002e1c;letter-spacing:0.01em'>
        📋 상세 분석 테이블
      </span>
      <span style='flex:1;height:1px;background:linear-gradient(90deg,#cce0d6,transparent)'></span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    # ── 공통 HTML 테이블 스타일 ──
    TBL_STYLE = """
    <style>
    .htbl {
        width: 100%; border-collapse: collapse;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.82rem;
        background: #ffffff;
        color: #002e1c;
        border-radius: 10px;
        overflow: hidden;
    }
    .htbl thead tr {
        background: #eef7f2;
    }
    .htbl thead th {
        padding: 10px 14px;
        text-align: left;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #00462A;
        border-bottom: 2px solid #cce0d6;
        white-space: nowrap;
    }
    .htbl tbody tr:nth-child(even) { background: #f7fbf9; }
    .htbl tbody tr:hover            { background: #eef7f2; }
    .htbl tbody td {
        padding: 9px 14px;
        color: #002e1c;
        border-bottom: 1px solid #e8f3ed;
        font-size: 0.81rem;
    }
    .htbl .num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #1a6040;
        font-weight: 400;
        text-align: right;
    }
    .htbl .rank {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #5a7a68;
        text-align: center;
        width: 28px;
    }
    /* 영향력 바 */
    .bar-wrap {
        display: flex; align-items: center; gap: 8px;
    }
    .bar-bg {
        flex: 1; height: 8px;
        background: #e8f3ed;
        border-radius: 4px; overflow: hidden;
    }
    .bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #1a7a50, #00462A);
        border-radius: 4px;
    }
    .bar-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #00462A;
        font-weight: 600;
        min-width: 38px;
        text-align: right;
    }
    </style>
    """

    def make_edge_table(edge_list):
        rows = ""
        for i, row in enumerate(edge_list, 1):
            rows += (
                f"<tr><td class='rank'>{i}</td>"
                f"<td>{row['부작용 A']}</td>"
                f"<td>{row['부작용 B']}</td>"
                f"<td class='num'>{row['동시 언급']:,}건</td></tr>"
            )
        return (
            f"<table class='htbl'><thead><tr>"
            f"<th>#</th><th>부작용 A</th><th>부작용 B</th><th>동시 언급</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>"
        )

    def make_hub_table(c_df):
        rows = ""
        for i, row in c_df.iterrows():
            pct = row["영향력 점수"]
            rows += (
                f"<tr><td class='rank'>{i}</td>"
                f"<td>{row['부작용']}</td>"
                f"<td><div class='bar-wrap'>"
                f"<div class='bar-bg'><div class='bar-fill' style='width:{pct}%'></div></div>"
                f"<span class='bar-val'>{pct:.1f}</span>"
                f"</div></td></tr>"
            )
        return (
            f"<table class='htbl'><thead><tr>"
            f"<th>#</th><th>부작용</th><th>영향력</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>"
        )

    def make_freq_table(freq_df):
        rows = ""
        for i, row in freq_df.iterrows():
            rows += (
                f"<tr><td class='rank'>{i}</td>"
                f"<td>{row['부작용']}</td>"
                f"<td class='num'>{int(row['실제 언급 수']):,}건</td>"
                f"<td class='num'>{row['로그 보정 크기']:.2f}</td></tr>"
            )
        return (
            f"<table class='htbl'><thead><tr>"
            f"<th>#</th><th>부작용</th><th>실제 언급 수</th><th>로그 보정</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>"
        )

    # ── 강한 연결 TOP 10 ──
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin:0.4rem 0 0.8rem'>
      <span style='font-family:"Playfair Display",serif;font-size:0.95rem;font-weight:600;color:#002e1c;letter-spacing:0.01em'>
        🔗 강한 연결 TOP 10
      </span>
      <span style='flex:1;height:1px;background:linear-gradient(90deg,#cce0d6,transparent)'></span>
    </div>
    """, unsafe_allow_html=True)

    edge_list = sorted(
        [
            {"부작용 A": a.replace("\n", " / "), "부작용 B": b.replace("\n", " / "), "동시 언급": w}
            for (a, b), w in edge_weights.items() if G.has_edge(a, b)
        ],
        key=lambda x: -x["동시 언급"],
    )[:10]
    if edge_list:
        st.markdown(TBL_STYLE + make_edge_table(edge_list), unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='no-data' style='padding:1.5rem'>"
            "<div class='no-data-title'>표시할 강한 연결이 없습니다</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    # ── 핵심 허브 TOP 10 ──
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin:1.2rem 0 0.8rem'>
      <span style='font-family:"Playfair Display",serif;font-size:0.95rem;font-weight:600;color:#002e1c;letter-spacing:0.01em'>
        🏆 핵심 허브 부작용 TOP 10
      </span>
      <span style='flex:1;height:1px;background:linear-gradient(90deg,#cce0d6,transparent)'></span>
    </div>
    """, unsafe_allow_html=True)

    for u, v, d in G.edges(data=True):
        d["distance"] = 1.0 / (d["weight"] + 1e-5)
    between = nx.betweenness_centrality(G, weight="distance")
    if sum(between.values()) == 0:
        between = nx.degree_centrality(G)

    c_df = pd.DataFrame(between.items(), columns=["부작용", "중심성"])
    c_df["부작용"] = c_df["부작용"].apply(lambda x: x.replace("\n", " / "))
    total_val = c_df["중심성"].sum()
    c_df["영향력 점수"] = c_df["중심성"].apply(
        lambda x: round(x / total_val * 100, 1) if total_val > 0 else 0
    )
    c_df = c_df.sort_values("영향력 점수", ascending=False).head(10).reset_index(drop=True)
    c_df.index = c_df.index + 1
    st.markdown(TBL_STYLE + make_hub_table(c_df), unsafe_allow_html=True)

    # ── 빈도 순위 TOP 10 ──
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin:1.8rem 0 1rem'>
      <span style='font-family:"Playfair Display",serif;font-size:1rem;font-weight:600;color:#002e1c;letter-spacing:0.01em'>
        📊 부작용 빈도 순위 <span style='font-size:0.75rem;font-weight:400;color:#5a7a68;font-family:"Noto Sans KR",sans-serif'>실제 언급 수 기준 TOP 10</span>
      </span>
      <span style='flex:1;height:1px;background:linear-gradient(90deg,#cce0d6,transparent)'></span>
    </div>
    """, unsafe_allow_html=True)
    freq_df = pd.DataFrame(effect_freq.items(), columns=["부작용", "실제 언급 수"])
    freq_df["부작용"] = freq_df["부작용"].apply(lambda x: x.replace("\n", " / "))
    freq_df["로그 보정 크기"] = freq_df["실제 언급 수"].apply(lambda x: round(np.log1p(x), 2))
    freq_df = freq_df.sort_values("실제 언급 수", ascending=False).head(10).reset_index(drop=True)
    freq_df.index = freq_df.index + 1
    st.markdown(
        "<div class='table-section'><div class='table-section-body'>"
        + TBL_STYLE + make_freq_table(freq_df)
        + "</div></div>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════
#  7. 메인 레이아웃
# ════════════════════════════════════════════════════════════════════

# ── 히어로 ──
st.markdown("""
<div class='hero'>
    <div class='hero-eyebrow'>Pharmacovigilance · Side Effect Network Analysis</div>
    <h1 class='hero-title'>위고비 &amp; 마운자로<br><em>부작용 네트워크 비교 분석</em></h1>
    <p class='hero-sub'>DC인사이드 (KR) vs Reddit (US) — 플랫폼 간 부작용 패턴 비교</p>
</div>
""", unsafe_allow_html=True)

with st.spinner("📡 데이터를 불러오는 중입니다…"):
    all_data = get_all_data()


# ── 사이드바 ──
with st.sidebar:
    st.markdown("""
    <div class='sb-logo'>⚙️ 분석 설정</div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)
    st.markdown("<span class='sb-section'>네트워크 파라미터</span>", unsafe_allow_html=True)

    adj_weight = st.slider(
        "연결 강도 보정",
        min_value=-10, max_value=50, value=0, step=1,
        help="기본값(DC: 25, Reddit: 50)에 더해지는 보정값입니다.",
    )
    top_n = st.slider(
        "상위 부작용 노드 수",
        min_value=5, max_value=12, value=12, step=1,
        help="네트워크에 표시할 최다 언급 부작용의 개수입니다.",
    )

    st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)
    st.markdown("<span class='sb-section'>데이터 현황</span>", unsafe_allow_html=True)

    stats = [
        ("🇰🇷 국내 위고비",   len(all_data["dc_wegovy"])),
        ("🇰🇷 국내 마운자로", len(all_data["dc_mounjaro"]) if all_data["dc_mounjaro"] else "미업로드"),
        ("🇺🇸 해외 위고비",   len(all_data["reddit_wegovy"])),
        ("🇺🇸 해외 마운자로", len(all_data["reddit_mounjaro"])),
    ]
    for label, val in stats:
        val_str = f"{val:,}건" if isinstance(val, int) else val
        st.markdown(
            f"<div class='sb-stat'>"
            f"<span class='sb-stat-key'>{label}</span>"
            f"<span class='sb-stat-val'>{val_str}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    


# ── 비교 렌더링 함수 ──
def render_side_by_side(
    left_records, right_records,
    left_flag, left_name, left_sub,
    right_flag, right_name, right_sub,
    top_n, base_dc, base_reddit, adj,
):
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            f"<div class='drug-header'>"
            f"<span class='drug-flag'>{left_flag}</span>"
            f"<div><div class='drug-name'>{left_name}</div>"
            f"<div class='drug-sub'>{left_sub}</div></div>"
            f"<span class='drug-badge'>DC인사이드 · KR</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        render_tab(left_records, top_n, max(1, base_dc + adj), source_label="dc")

    with col2:
        st.markdown(
            f"<div class='drug-header'>"
            f"<span class='drug-flag'>{right_flag}</span>"
            f"<div><div class='drug-name'>{right_name}</div>"
            f"<div class='drug-sub'>{right_sub}</div></div>"
            f"<span class='drug-badge'>Reddit · US</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        render_tab(right_records, top_n, max(1, base_reddit + adj), source_label="reddit")


# ── 약물 탭 ──
tab_wegovy, tab_mounjaro = st.tabs(["💉 Wegovy 비교 분석", "💉 Mounjaro 비교 분석"])

with tab_wegovy:
    render_side_by_side(
        all_data["dc_wegovy"],
        all_data["reddit_wegovy"],
        "🇰🇷", "위고비 (국내)", "DC인사이드 커뮤니티 데이터",
        "🇺🇸", "Wegovy (해외)", "Reddit r/Semaglutide 등",
        top_n, 25, 50, adj_weight,
    )

with tab_mounjaro:
    if not all_data["dc_mounjaro"]:
        st.markdown(
            "<div class='no-data'>"
            "<div class='no-data-icon'>📂</div>"
            "<div class='no-data-title'>국내 마운자로 데이터 없음</div>"
            "<div class='no-data-desc'>DC 마운자로 파일 경로를 secrets.toml 에서 설정해주세요.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top:1.5rem'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='drug-header'>"
            "<span class='drug-flag'>🇺🇸</span>"
            "<div><div class='drug-name'>Mounjaro (해외)</div>"
            "<div class='drug-sub'>Reddit 커뮤니티 데이터</div></div>"
            "<span class='drug-badge'>Reddit · US</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        render_tab(all_data["reddit_mounjaro"], top_n, max(1, 50 + adj_weight))
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        render_side_by_side(
            all_data["dc_mounjaro"],
            all_data["reddit_mounjaro"],
            "🇰🇷", "마운자로 (국내)", "DC인사이드 커뮤니티 데이터",
            "🇺🇸", "Mounjaro (해외)", "Reddit 커뮤니티 데이터",
            top_n, 25, 50, adj_weight,
        )