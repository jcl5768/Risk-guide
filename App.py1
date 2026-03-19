import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════
# 1. 페이지 설정 & 화이트 테마 스타일
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Risk Guide",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* ── 전체 화이트 베이스 ── */
.stApp { background:#F7F8FA; color:#1A1D23; font-family:'Inter',sans-serif; }
header[data-testid="stHeader"] { background:#FFFFFF; border-bottom:1px solid #E8EAED; }
.stDeployButton { display:none; }
#MainMenu { display:none; }
footer { display:none; }

/* ── 사이드바 ── */
section[data-testid="stSidebar"] {
    background:#FFFFFF;
    border-right:1px solid #E8EAED;
}
section[data-testid="stSidebar"] .stMarkdown { color:#1A1D23; }

/* ── 상단 지표 카드 ── */
.macro-card {
    background:#FFFFFF;
    border:1px solid #E8EAED;
    border-radius:10px;
    padding:14px 18px;
    display:flex;
    flex-direction:column;
    gap:4px;
}
.macro-label { font-size:11px; color:#6B7280; font-weight:500; letter-spacing:0.5px; }
.macro-value { font-family:'JetBrains Mono',monospace; font-size:20px; font-weight:700; color:#1A1D23; }
.macro-sub   { font-size:11px; color:#9CA3AF; }

/* ── 종목 카드 (컴팩트) ── */
.stock-card {
    background:#FFFFFF;
    border:1px solid #E8EAED;
    border-radius:10px;
    padding:16px 18px;
    transition:box-shadow 0.15s;
}
.stock-card:hover { box-shadow:0 2px 12px rgba(0,0,0,0.08); }

/* ── 신호 배지 ── */
.badge-green  { background:#ECFDF5; color:#059669; border:1px solid #A7F3D0; border-radius:20px; padding:3px 10px; font-size:11px; font-weight:600; display:inline-block; }
.badge-yellow { background:#FFFBEB; color:#D97706; border:1px solid #FDE68A; border-radius:20px; padding:3px 10px; font-size:11px; font-weight:600; display:inline-block; }
.badge-red    { background:#FEF2F2; color:#DC2626; border:1px solid #FECACA; border-radius:20px; padding:3px 10px; font-size:11px; font-weight:600; display:inline-block; }

/* ── 섹션 헤더 ── */
.section-header {
    font-size:12px; font-weight:600; color:#6B7280;
    letter-spacing:1px; text-transform:uppercase;
    margin-bottom:12px; padding-bottom:8px;
    border-bottom:1px solid #E8EAED;
}

/* ── 포트폴리오 행 ── */
.portfolio-row {
    background:#FFFFFF; border:1px solid #E8EAED;
    border-radius:8px; padding:12px 16px; margin-bottom:6px;
}

/* ── 뉴스 카드 ── */
.news-pos { background:#ECFDF5; border-left:3px solid #059669; padding:10px 14px; border-radius:0 8px 8px 0; margin-bottom:8px; }
.news-neg { background:#FEF2F2; border-left:3px solid #DC2626; padding:10px 14px; border-radius:0 8px 8px 0; margin-bottom:8px; }
.news-neu { background:#F9FAFB; border-left:3px solid #D1D5DB; padding:10px 14px; border-radius:0 8px 8px 0; margin-bottom:8px; }

/* ── Streamlit 컴포넌트 오버라이드 ── */
.stTabs [data-baseweb="tab-list"] {
    gap:2px; background:#F3F4F6;
    border-radius:8px; padding:3px;
    border:1px solid #E8EAED;
}
.stTabs [data-baseweb="tab"] {
    height:32px; font-size:12px; font-weight:500;
    color:#6B7280; border-radius:6px; padding:0 14px;
    font-family:'Inter',sans-serif;
}
.stTabs [aria-selected="true"] {
    background:#FFFFFF !important;
    color:#1A1D23 !important;
    box-shadow:0 1px 3px rgba(0,0,0,0.1);
}
div[data-testid="stButton"] button {
    background:#FFFFFF; color:#374151;
    border:1px solid #D1D5DB; border-radius:7px;
    font-family:'Inter',sans-serif; font-size:12px;
    font-weight:500; padding:6px 16px;
    transition:all 0.15s;
}
div[data-testid="stButton"] button:hover {
    background:#F9FAFB; border-color:#9CA3AF; color:#111827;
}
div[data-testid="stButton"] button[kind="primary"] {
    background:#2563EB; color:#FFFFFF; border-color:#2563EB;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background:#1D4ED8;
}
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background:#FFFFFF !important;
    border:1px solid #D1D5DB !important;
    border-radius:7px !important;
    color:#1A1D23 !important;
    font-family:'Inter',sans-serif !important;
    font-size:13px !important;
}
div[data-testid="stSelectbox"] > div {
    background:#FFFFFF !important;
    border:1px solid #D1D5DB !important;
    border-radius:7px !important;
}
.stSlider > div > div > div { background:#2563EB !important; }
.stSpinner > div { border-top-color:#2563EB !important; }
div[data-testid="stExpander"] {
    background:#FFFFFF; border:1px solid #E8EAED; border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 2. 섹터별 거시지표 매핑
# ═══════════════════════════════════════════════════════════════════════════
SECTOR_CONFIG = {
    "Energy": {
        "icon":"🛢️", "color":"#D97706", "label":"에너지",
        "indicators":[
            {"name":"WTI 유가",    "ticker":"CL=F",     "weight":+12, "desc":"에너지주 매출과 직결"},
            {"name":"천연가스",    "ticker":"NG=F",      "weight":+6,  "desc":"LNG 사업 영향"},
            {"name":"달러 인덱스", "ticker":"DX-Y.NYB",  "weight":-4,  "desc":"달러 강세 = 원자재 하락 압력"},
            {"name":"10년물 금리", "ticker":"^TNX",      "weight":-3,  "desc":"금리 상승 = 고배당 매력 감소"},
            {"name":"VIX",         "ticker":"^VIX",      "weight":-5,  "desc":"공포 = 경기민감주 하락"},
        ]
    },
    "Technology": {
        "icon":"💻", "color":"#2563EB", "label":"기술주",
        "indicators":[
            {"name":"나스닥(QQQ)", "ticker":"QQQ",       "weight":+10, "desc":"기술주 섹터 흐름"},
            {"name":"10년물 금리", "ticker":"^TNX",      "weight":-12, "desc":"금리 상승 = 밸류에이션 직격"},
            {"name":"반도체(SOXX)","ticker":"SOXX",      "weight":+7,  "desc":"반도체 수요 선행지표"},
            {"name":"VIX",         "ticker":"^VIX",      "weight":-6,  "desc":"공포 구간 고PER 매도"},
            {"name":"달러 인덱스", "ticker":"DX-Y.NYB",  "weight":-4,  "desc":"달러 강세 = 해외 매출 역풍"},
        ]
    },
    "Consumer Cyclical": {
        "icon":"⚡", "color":"#DC2626", "label":"경기소비재/EV",
        "indicators":[
            {"name":"10년물 금리", "ticker":"^TNX",      "weight":-10, "desc":"금리 상승 = 할부금리 상승"},
            {"name":"나스닥(QQQ)", "ticker":"QQQ",       "weight":+8,  "desc":"기술 소비재 동조화"},
            {"name":"리튬ETF(LIT)","ticker":"LIT",       "weight":+6,  "desc":"배터리 원자재 가격"},
            {"name":"VIX",         "ticker":"^VIX",      "weight":-7,  "desc":"경기 불안 = 고가 소비 위축"},
            {"name":"달러 인덱스", "ticker":"DX-Y.NYB",  "weight":-3,  "desc":"수출 경쟁력 하락"},
        ]
    },
    "Consumer Defensive": {
        "icon":"🛒", "color":"#059669", "label":"필수소비재",
        "indicators":[
            {"name":"CPI 인플레",  "ticker":"RINF",      "weight":-8,  "desc":"인플레 = 실질구매력 하락"},
            {"name":"10년물 금리", "ticker":"^TNX",      "weight":-6,  "desc":"고금리 = 배당 매력 감소"},
            {"name":"VIX",         "ticker":"^VIX",      "weight":+5,  "desc":"공포 시 방어주 자금 유입"},
            {"name":"달러 인덱스", "ticker":"DX-Y.NYB",  "weight":-3,  "desc":"달러 강세 영향"},
            {"name":"S&P500(SPY)", "ticker":"SPY",       "weight":+4,  "desc":"전체 장 동반 상승"},
        ]
    },
    "Financial Services": {
        "icon":"🏦", "color":"#7C3AED", "label":"금융주",
        "indicators":[
            {"name":"10년물 금리", "ticker":"^TNX",      "weight":+12, "desc":"금리 상승 = 예대마진 확대"},
            {"name":"2년물 금리",  "ticker":"^IRX",      "weight":+5,  "desc":"단기금리 = 운용 수익"},
            {"name":"VIX",         "ticker":"^VIX",      "weight":-8,  "desc":"금융위기 공포 = 최대 타격"},
            {"name":"달러 인덱스", "ticker":"DX-Y.NYB",  "weight":+3,  "desc":"달러 강세 = 자산 가치 상승"},
            {"name":"S&P500(SPY)", "ticker":"SPY",       "weight":+5,  "desc":"강세장 = 수수료 수익 증가"},
        ]
    },
    "Healthcare": {
        "icon":"💊", "color":"#0891B2", "label":"헬스케어",
        "indicators":[
            {"name":"VIX",         "ticker":"^VIX",      "weight":+4,  "desc":"불안장 = 방어적 선호"},
            {"name":"10년물 금리", "ticker":"^TNX",      "weight":-5,  "desc":"신약개발 자금조달 비용"},
            {"name":"달러 인덱스", "ticker":"DX-Y.NYB",  "weight":-4,  "desc":"해외 매출 환산 손실"},
            {"name":"S&P500(SPY)", "ticker":"SPY",       "weight":+6,  "desc":"시장 흐름 동조"},
            {"name":"바이오(XBI)", "ticker":"XBI",       "weight":+5,  "desc":"바이오테크 투자심리"},
        ]
    },
    "Unknown": {
        "icon":"📊", "color":"#6B7280", "label":"기타",
        "indicators":[
            {"name":"S&P500(SPY)", "ticker":"SPY",       "weight":+8,  "desc":"전체 시장 흐름"},
            {"name":"VIX",         "ticker":"^VIX",      "weight":-6,  "desc":"시장 공포 지수"},
            {"name":"10년물 금리", "ticker":"^TNX",      "weight":-5,  "desc":"거시 금리 환경"},
            {"name":"달러 인덱스", "ticker":"DX-Y.NYB",  "weight":-3,  "desc":"달러 환경"},
            {"name":"나스닥(QQQ)", "ticker":"QQQ",       "weight":+5,  "desc":"성장주 흐름"},
        ]
    },
}

SECTOR_MAP = {
    "Energy":"Energy", "Technology":"Technology",
    "Consumer Cyclical":"Consumer Cyclical", "Consumer Defensive":"Consumer Defensive",
    "Financial Services":"Financial Services", "Healthcare":"Healthcare",
    "Industrials":"Unknown", "Basic Materials":"Unknown", "Real Estate":"Unknown",
    "Utilities":"Consumer Defensive", "Communication Services":"Technology",
}

ETF_MAP = {
    "XLE":"Energy",    "XOM":"Energy",    "CVX":"Energy",    "COP":"Energy",
    "XLK":"Technology","AAPL":"Technology","MSFT":"Technology","NVDA":"Technology",
    "META":"Technology","GOOGL":"Technology","AMZN":"Technology",
    "TSLA":"Consumer Cyclical","F":"Consumer Cyclical","GM":"Consumer Cyclical",
    "XLP":"Consumer Defensive","PG":"Consumer Defensive","KO":"Consumer Defensive",
    "WMT":"Consumer Defensive","COST":"Consumer Defensive",
    "XLF":"Financial Services","JPM":"Financial Services","BAC":"Financial Services",
    "GS":"Financial Services","MS":"Financial Services",
    "
