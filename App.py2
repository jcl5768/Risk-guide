# Risk Guide v4.1 — 수익률 버그 수정 + 승률 공식 단순화 + 툴팁 추가
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Risk Guide", page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
.stApp{background:#F7F8FA;color:#1A1D23;font-family:'Inter',sans-serif;}
header[data-testid="stHeader"]{background:#FFFFFF;border-bottom:1px solid #E8EAED;}
.stDeployButton{display:none;} #MainMenu{display:none;} footer{display:none;}
section[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #E8EAED;}
.macro-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:14px 18px;}
.section-hdr{font-size:11px;font-weight:600;color:#6B7280;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #E8EAED;}
.stock-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:16px 18px;}
.badge-green{background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.badge-yellow{background:#FFFBEB;color:#D97706;border:1px solid #FDE68A;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.badge-red{background:#FEF2F2;color:#DC2626;border:1px solid #FECACA;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.lv1{background:#EFF6FF;color:#2563EB;border:1px solid #BFDBFE;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
.lv2{background:#FFF7ED;color:#EA580C;border:1px solid #FED7AA;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
.lv3{background:#F5F3FF;color:#7C3AED;border:1px solid #DDD6FE;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
.news-pos{background:#ECFDF5;border-left:3px solid #059669;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
.news-neg{background:#FEF2F2;border-left:3px solid #DC2626;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
.news-neu{background:#F9FAFB;border-left:3px solid #D1D5DB;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
.stTabs [data-baseweb="tab-list"]{gap:2px;background:#F3F4F6;border-radius:8px;padding:3px;border:1px solid #E8EAED;}
.stTabs [data-baseweb="tab"]{height:32px;font-size:12px;font-weight:500;color:#6B7280;border-radius:6px;padding:0 14px;}
.stTabs [aria-selected="true"]{background:#FFFFFF !important;color:#1A1D23 !important;box-shadow:0 1px 3px rgba(0,0,0,0.1);}
div[data-testid="stButton"] button{background:#FFFFFF;color:#374151;border:1px solid #D1D5DB;border-radius:7px;font-size:12px;font-weight:500;padding:6px 16px;}
div[data-testid="stButton"] button:hover{background:#F9FAFB;border-color:#9CA3AF;}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{background:#FFFFFF !important;border:1px solid #D1D5DB !important;border-radius:7px !important;color:#1A1D23 !important;font-size:13px !important;}
.stSlider > div > div > div{background:#2563EB !important;}
.stSpinner > div{border-top-color:#2563EB !important;}
div[data-testid="stExpander"]{background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ── 섹터 설정 ─────────────────────────────────────────────────────────────
SECTOR_CONFIG = {
    "Energy": {
        "icon":"🛢️","color":"#D97706","label":"에너지",
        "cycle_note":"유가 사이클 — OPEC 결정·지정학 리스크·달러 강세에 연동",
        "indicators":[
            {"name":"WTI 유가",       "ticker":"CL=F",     "weight":+14,"desc":"매출·마진 직결. 유가 1% 상승 ≈ EPS 2~3% 개선"},
            {"name":"천연가스",       "ticker":"NG=F",      "weight":+6, "desc":"LNG·가스 사업 비중 종목에 직접 영향"},
            {"name":"에너지ETF(XLE)", "ticker":"XLE",       "weight":+8, "desc":"섹터 전반 기관 자금 흐름 반영"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-5, "desc":"달러 강세 = 원자재 가격 하락 압력"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-4, "desc":"고배당 에너지주 vs 채권 경쟁"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-5, "desc":"경기침체 공포 = 원자재 수요 감소"},
        ]
    },
    "Technology": {
        "icon":"💻","color":"#2563EB","label":"기술주",
        "cycle_note":"금리 사이클 — DCF 할인율 직결. 금리 1%p 상승 시 고PER 기술주 밸류에이션 ~15% 하락",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-14,"desc":"가장 중요. 미래 현금흐름 할인율 직접 영향"},
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+10,"desc":"기술주 섹터 모멘텀 — 기관 수급 반영"},
            {"name":"반도체(SOXX)",   "ticker":"SOXX",      "weight":+7, "desc":"빅테크 AI 인프라 투자 선행지표"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-7, "desc":"공포 구간 = 고PER 종목 먼저 청산"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-4, "desc":"해외 매출 비중 높은 빅테크 역풍"},
            {"name":"2년물 금리",     "ticker":"^IRX",      "weight":-5, "desc":"단기 유동성 비용 — 성장주 자금조달"},
        ]
    },
    "Semiconductor": {
        "icon":"🔬","color":"#0891B2","label":"반도체",
        "cycle_note":"재고 사이클 (18~36개월) — 공급과잉/부족 사이클. SOX 지수·PC/서버 수요가 핵심",
        "indicators":[
            {"name":"반도체(SOXX)",   "ticker":"SOXX",      "weight":+14,"desc":"섹터 사이클 직접 반영. 재고 조정 신호"},
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+8, "desc":"AI·클라우드 수요 — 반도체 end-demand"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-10,"desc":"CAPEX 비용 — 파운드리 설비 확장에 영향"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-6, "desc":"TSMC 등 아시아 공급망 원가·환율"},
            {"name":"구리 선물",      "ticker":"HG=F",      "weight":+5, "desc":"전자부품 원자재 + 경기 선행지표"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-5, "desc":"리스크오프 = 사이클주 집중 매도"},
        ]
    },
    "Consumer Cyclical": {
        "icon":"🛍️","color":"#DC2626","label":"경기소비재/EV",
        "cycle_note":"경기+금리 복합 사이클 — 소비자 구매력(금리·고용)과 EV는 배터리 원가 사이클에 추가 연동",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-11,"desc":"자동차 할부금리 직결 — 금리 1%p = 월납부 증가"},
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+8, "desc":"소비·기술 복합 종목(TSLA 등) 동조화"},
            {"name":"리튬ETF(LIT)",   "ticker":"LIT",       "weight":+7, "desc":"배터리 핵심 원자재 — EV 마진 직접 영향"},
            {"name":"임의소비(XLY)",  "ticker":"XLY",       "weight":+6, "desc":"소비심리 선행지표 — 기관 섹터 수급"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-7, "desc":"불안 = 고가 내구재 소비 위축"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-3, "desc":"글로벌 판매 환율 효과"},
        ]
    },
    "Consumer Defensive": {
        "icon":"🛒","color":"#059669","label":"필수소비재",
        "cycle_note":"경기 방어 섹터 — VIX 상승(공포장)에서 역발상 수혜. 인플레이션 구매력 훼손이 핵심 리스크",
        "indicators":[
            {"name":"CPI 인플레",     "ticker":"RINF",      "weight":-9, "desc":"인플레 심화 = 실질 구매력 하락"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-6, "desc":"고금리 = 고배당 방어주 상대 매력 감소"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":+6, "desc":"공포 시 안전자산 수요 → 방어주 유입"},
            {"name":"필수소비(XLP)",  "ticker":"XLP",       "weight":+7, "desc":"섹터 기관 자금 흐름"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-3, "desc":"수입 원자재·식품 원가 영향"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+4, "desc":"전체 장 상승 시 동반 상승"},
        ]
    },
    "Financial Services": {
        "icon":"🏦","color":"#7C3AED","label":"금융주",
        "cycle_note":"금리 사이클 — 장단기 스프레드(예대마진)가 핵심. 금리 인상기 수혜, 역전 시 압박",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":+13,"desc":"대출 금리 기준 — 예대마진 확대 직접 호재"},
            {"name":"2년물 금리",     "ticker":"^IRX",      "weight":+6, "desc":"단기 조달 비용 — 금리 스프레드 핵심"},
            {"name":"금융ETF(XLF)",   "ticker":"XLF",       "weight":+7, "desc":"섹터 기관 수급 반영"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-9, "desc":"금융위기 공포 = 모든 금융주 동시 하락"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":+3, "desc":"글로벌 금융사 달러 자산 가치 상승"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+4, "desc":"경제 성장 = 대출 수요 증가"},
        ]
    },
    "Healthcare": {
        "icon":"💊","color":"#0891B2","label":"헬스케어",
        "cycle_note":"방어+성장 복합 — FDA 규제·바이오 사이클이 개별 종목 변동성 높임",
        "indicators":[
            {"name":"바이오(XBI)",    "ticker":"XBI",       "weight":+8, "desc":"신약 파이프라인 투자심리 선행지표"},
            {"name":"헬스케어(XLV)",  "ticker":"XLV",       "weight":+6, "desc":"섹터 기관 자금 흐름"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":+5, "desc":"불안장 = 방어적 헬스케어 선호 증가"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-6, "desc":"신약 R&D 자금조달 비용 상승"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-4, "desc":"해외 판매 환율 — 글로벌 제약사"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+5, "desc":"전체 강세장 수혜"},
        ]
    },
    "Industrials": {
        "icon":"🏭","color":"#374151","label":"산업재",
        "cycle_note":"경기 사이클 — ISM 제조업 지수와 높은 상관. 인프라 지출·무역정책·달러에 민감",
        "indicators":[
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+9, "desc":"경기 확장 = 설비투자·인프라 수요 직결"},
            {"name":"구리 선물",      "ticker":"HG=F",      "weight":+8, "desc":"닥터 코퍼 — 산업 수요 경기 선행지표"},
            {"name":"산업재(XLI)",    "ticker":"XLI",       "weight":+6, "desc":"섹터 자금 흐름"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-6, "desc":"자본재 투자 비용 상승"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-7, "desc":"수출 제조업 경쟁력 하락"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"경기 불안 = 설비 발주 취소"},
        ]
    },
    "Real Estate": {
        "icon":"🏢","color":"#065F46","label":"부동산(REIT)",
        "cycle_note":"금리 사이클 — 모기지 금리와 직결. 금리 상승 시 가장 큰 타격 받는 섹터",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-15,"desc":"모기지 금리 기준 — REIT 밸류에이션 직격"},
            {"name":"2년물 금리",     "ticker":"^IRX",      "weight":-8, "desc":"단기 자금조달 비용 상승"},
            {"name":"부동산(XLRE)",   "ticker":"XLRE",      "weight":+7, "desc":"섹터 전반 기관 수급"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"경기침체 = 공실률 상승 우려"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-3, "desc":"해외 부동산 보유 REIT 환율"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+4, "desc":"경제 성장 = 임대 수요 증가"},
        ]
    },
    "Utilities": {
        "icon":"⚡","color":"#0369A1","label":"유틸리티",
        "cycle_note":"금리·배당 사이클 — 채권 대체 자산. AI 전력 수요가 신규 성장 변수로 부상",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-12,"desc":"채권 대비 배당 매력 — 금리 상승 = 경쟁"},
            {"name":"유틸리티(XLU)",  "ticker":"XLU",       "weight":+8, "desc":"섹터 자금 흐름"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":+5, "desc":"불안장 = 방어적 유틸리티 자금 유입"},
            {"name":"천연가스",       "ticker":"NG=F",       "weight":-5, "desc":"발전 원가 — 가스 발전 비중 유틸리티"},
            {"name":"2년물 금리",     "ticker":"^IRX",      "weight":-6, "desc":"단기 부채 비용 — 자본 집약적 사업"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+3, "desc":"전체 장 약세 시 방어적 수요"},
        ]
    },
    "Basic Materials": {
        "icon":"⛏️","color":"#92400E","label":"소재/원자재",
        "cycle_note":"달러·원자재 사이클 — 달러 약세 + 중국 경기 회복 + 인프라 수요가 삼각 동력",
        "indicators":[
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-10,"desc":"달러 약세 = 원자재 가격 상승 (역상관)"},
            {"name":"구리 선물",      "ticker":"HG=F",      "weight":+10,"desc":"글로벌 제조·건설 수요 척도"},
            {"name":"소재ETF(XLB)",   "ticker":"XLB",       "weight":+6, "desc":"섹터 기관 수급"},
            {"name":"금 선물",        "ticker":"GC=F",      "weight":+5, "desc":"인플레·불확실성 헷지 수요"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"경기침체 = 원자재 수요 감소"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-4, "desc":"달러 강세 압력 간접 경로"},
        ]
    },
    "Communication Services": {
        "icon":"📡","color":"#1D4ED8","label":"통신/미디어",
        "cycle_note":"기술+경기 복합 — 광고 수익(경기 민감) + 구독 수익(방어적) 혼재",
        "indicators":[
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+10,"desc":"빅테크 동조 — 광고·플랫폼 연계"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-9, "desc":"성장주 밸류에이션 할인율 영향"},
            {"name":"통신ETF(XLC)",   "ticker":"XLC",       "weight":+5, "desc":"섹터 자금 흐름"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+6, "desc":"광고 수익 = 경기와 직결"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"불안 = 디지털 광고 지출 감소"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-4, "desc":"해외 매출 환율 — 글로벌 플랫폼"},
        ]
    },
    "Unknown": {
        "icon":"📊","color":"#6B7280","label":"기타",
        "cycle_note":"섹터를 특정할 수 없어 범용 지표를 적용합니다.",
        "indicators":[
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+8, "desc":"전체 시장 흐름"},
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+5, "desc":"성장주 흐름"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-5, "desc":"거시 금리 환경"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"시장 공포 수준"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-3, "desc":"달러 강세/약세"},
        ]
    },
}

SECTOR_MAP = {
    "Energy":"Energy","Technology":"Technology","Consumer Cyclical":"Consumer Cyclical",
    "Consumer Defensive":"Consumer Defensive","Financial Services":"Financial Services",
    "Healthcare":"Healthcare","Industrials":"Industrials","Basic Materials":"Basic Materials",
    "Real Estate":"Real Estate","Utilities":"Utilities",
    "Communication Services":"Communication Services",
}

ETF_MAP = {
    "XLE":"Energy","XOM":"Energy","CVX":"Energy","COP":"Energy","SLB":"Energy",
    "XLK":"Technology","AAPL":"Technology","MSFT":"Technology","CRM":"Technology","ADBE":"Technology","ORCL":"Technology",
    "NVDA":"Semiconductor","AMD":"Semiconductor","INTC":"Semiconductor","QCOM":"Semiconductor",
    "MU":"Semiconductor","SOXX":"Semiconductor","SMH":"Semiconductor","AMAT":"Semiconductor",
    "LRCX":"Semiconductor","ASML":"Semiconductor","TSM":"Semiconductor","AVGO":"Semiconductor","ARM":"Semiconductor",
    "TSLA":"Consumer Cyclical","F":"Consumer Cyclical","GM":"Consumer Cyclical","RIVN":"Consumer Cyclical",
    "AMZN":"Consumer Cyclical","HD":"Consumer Cyclical","NKE":"Consumer Cyclical","XLY":"Consumer Cyclical","LIT":"Consumer Cyclical",
    "XLP":"Consumer Defensive","PG":"Consumer Defensive","KO":"Consumer Defensive",
    "WMT":"Consumer Defensive","COST":"Consumer Defensive","PEP":"Consumer Defensive","MCD":"Consumer Defensive",
    "XLF":"Financial Services","JPM":"Financial Services","BAC":"Financial Services",
    "GS":"Financial Services","MS":"Financial Services","WFC":"Financial Services","V":"Financial Services","MA":"Financial Services",
    "XLV":"Healthcare","JNJ":"Healthcare","UNH":"Healthcare","PFE":"Healthcare",
    "MRK":"Healthcare","ABBV":"Healthcare","LLY":"Healthcare","TMO":"Healthcare",
    "XLI":"Industrials","CAT":"Industrials","DE":"Industrials","BA":"Industrials","GE":"Industrials","UPS":"Industrials",
    "XLRE":"Real Estate","AMT":"Real Estate","PLD":"Real Estate","EQIX":"Real Estate",
    "XLU":"Utilities","NEE":"Utilities","DUK":"Utilities","SO":"Utilities",
    "XLB":"Basic Materials","FCX":"Basic Materials","NEM":"Basic Materials","GLD":"Basic Materials",
    "XLC":"Communication Services","META":"Communication Services","GOOGL":"Communication Services",
    "NFLX":"Communication Services","DIS":"Communication Services","VZ":"Communication Services","T":"Communication Services",
    "QQQ":"Technology","SPY":"Unknown","IWM":"Unknown","DIA":"Unknown","ARKK":"Technology",
}


# ── 세션 상태 — 빈 포트폴리오로 시작 ─────────────────────────────────────
def init_session():
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if 'selected' not in st.session_state:
        st.session_state.selected = None
    if 'editing' not in st.session_state:
        st.session_state.editing = None
    if 'show_add' not in st.session_state:
        st.session_state.show_add = False

init_session()

# ── 분석 엔진 ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def detect_sector(ticker):
    t = ticker.upper().strip()
    if t in ETF_MAP:
        return ETF_MAP[t]
    try:
        info = yf.Ticker(ticker).info
        return SECTOR_MAP.get(info.get("sector","Unknown"), "Unknown")
    except:
        return "Unknown"

@st.cache_data(ttl=300)
def get_z_and_price(ticker):
    try:
        raw = yf.download(ticker, period="60d", interval="1d", progress=False)
        if raw.empty: return 0.0, 0.0
        if isinstance(raw.columns, pd.MultiIndex):
            data = raw['Close'].iloc[:,0] if 'Close' in raw.columns.get_level_values(0) else raw.iloc[:,0]
        else:
            data = raw['Close'] if 'Close' in raw.columns else raw.iloc[:,0]
        data = data.dropna()
        if len(data) < 21: return 0.0, float(data.iloc[-1]) if len(data) > 0 else 0.0
        cur = float(data.iloc[-1])
        mean = float(data.tail(20).mean())
        std = float(data.tail(20).std())
        if std == 0: return 0.0, round(cur,2)
        return round((cur-mean)/std,2), round(cur,2)
    except:
        return 0.0, 0.0

@st.cache_data(ttl=300)
def get_sector_analysis(ticker):
    sk = detect_sector(ticker)
    cfg = SECTOR_CONFIG[sk]
    results = []
    for ind in cfg["indicators"]:
        z, price = get_z_and_price(ind["ticker"])
        results.append({**ind, "z":z, "price":price})
    return sk, cfg, results

@st.cache_data(ttl=300)
def get_price_history(ticker):
    try:
        raw = yf.download(ticker, period="60d", interval="1d", progress=False)
        if raw.empty: return pd.DataFrame()
        if isinstance(raw.columns, pd.MultiIndex):
            data = raw['Close'].iloc[:,0] if 'Close' in raw.columns.get_level_values(0) else raw.iloc[:,0]
        else:
            data = raw['Close'] if 'Close' in raw.columns else raw.iloc[:,0]
        df = data.dropna().reset_index()
        df.columns = ['Date','Close']
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_news(ticker):
    try:
        news_list = yf.Ticker(ticker).news[:5]
        pos_kw = ['buy','growth','up','positive','surge','profit','beat','record','strong','upgrade','bullish','soars','rises','rally']
        neg_kw = ['sell','fall','down','negative','drop','loss','risk','crisis','miss','weak','downgrade','bearish','cut','slump','plunge']
        score, analyzed = 0, []
        for n in news_list:
            title = n.get('title','').lower()
            if any(w in title for w in pos_kw):
                score += 1; sentiment = "Positive"
            elif any(w in title for w in neg_kw):
                score -= 1; sentiment = "Negative"
            else:
                sentiment = "Neutral"
            analyzed.append({"title":n.get('title',''),"link":n.get('link','#'),"sentiment":sentiment})
        return score*2.5, analyzed
    except:
        return 0.0, []

def calc_win_rate(z_stock, indicators, news_bonus):
    """직관적인 승률 계산 공식 (100점 만점)"""
    base = 50.0  # 1. 기본 점수 (중립)
    
    # 2. 과열 페널티 (현재 주가가 너무 높으면 승률 깎임)
    z_penalty = round(-(z_stock * 3.0), 1) 
    
    # 3. 거시 지표 점수
    macro_score = round(sum([ind["z"] * (ind["weight"] / 5.0) for ind in indicators]), 1)
    
    total = base + z_penalty + macro_score + news_bonus
    final_win = round(max(5.0, min(95.0, total)), 1)
    
    # 설명 텍스트 (물음표 툴팁용)
    explain = f"기본(50) {'+' if z_penalty>=0 else ''}{z_penalty}(가격위치) {'+' if macro_score>=0 else ''}{macro_score}(거시지표) {'+' if news_bonus>=0 else ''}{news_bonus}(뉴스) = {final_win}%"
    
    return final_win, explain

def get_signal(wr):
    if wr >= 60:   return "매수 우위","badge-green","#059669"
    elif wr >= 45: return "중립 관망","badge-yellow","#D97706"
    else:          return "리스크 경고","badge-red","#DC2626"

def zcolor(z):
    if z > 1.5:    return "#DC2626"
    elif z > 0.5:  return "#D97706"
    elif z < -1.5: return "#059669"
    elif z < -0.5: return "#2563EB"
    else:          return "#6B7280"

def zdesc(z):
    if z > 2.0:    return "극단 과열"
    elif z > 1.0:  return "과매수"
    elif z > 0.3:  return "평균 이상"
    elif z > -0.3: return "중립"
    elif z > -1.0: return "평균 이하"
    elif z > -2.0: return "과매도"
    else:          return "극단 과매도"


# ── 사이드바 — 포트폴리오 CRUD ────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 내 포트폴리오")
    total_w = sum(s['weight'] for s in st.session_state.portfolio)
    wc = "#059669" if total_w <= 100 else "#DC2626"
    st.markdown(f'<div style="font-size:12px;color:{wc};margin-bottom:12px;">총 비중: <b>{total_w}%</b> {"✓" if total_w<=100 else "⚠ 초과"} · 종목 {len(st.session_state.portfolio)}개</div>', unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.portfolio:
        st.markdown('<div style="text-align:center;padding:16px 8px;color:#9CA3AF;font-size:12px;">아직 종목이 없어요.<br>아래 버튼으로 추가해보세요!</div>', unsafe_allow_html=True)

    for i, stock in enumerate(st.session_state.portfolio):
        sec = detect_sector(stock['ticker'])
        cfg = SECTOR_CONFIG[sec]
        if st.session_state.editing == i:
            st.markdown(f"**✏️ {stock['ticker']} 수정**")
            nn = st.text_input("종목명",       value=stock['name'],             key=f"en_{i}")
            nw = st.number_input("비중(%)",     value=int(stock['weight']),      min_value=1,   max_value=100,    key=f"ew_{i}")
            ns = st.number_input("수량(주)",    value=int(stock['shares']),      min_value=1,   max_value=100000, key=f"es_{i}")
            na = st.number_input("평균단가($)", value=float(stock['avg_price']), min_value=0.0, max_value=999999.0,format="%.2f",key=f"ea_{i}")
            c1,c2 = st.columns(2)
            with c1:
                if st.button("✅ 저장", key=f"save_{i}", use_container_width=True):
                    st.session_state.portfolio[i].update({"name":nn,"weight":nw,"shares":ns,"avg_price":na})
                    st.session_state.editing = None
                    st.rerun()
            with c2:
                if st.button("✕ 취소", key=f"cancel_{i}", use_container_width=True):
                    st.session_state.editing = None
                    st.rerun()
        else:
            ci,cp,cb = st.columns([3,1,2])
            with ci:
                st.markdown(f'<div style="line-height:1.5;"><b style="font-size:14px;color:#1A1D23;">{stock["ticker"]}</b> <span style="font-size:11px;color:{cfg["color"]};">{cfg["icon"]}</span><br><span style="font-size:11px;color:#9CA3AF;">{stock["name"]}</span></div>', unsafe_allow_html=True)
            with cp:
                st.markdown(f'<div style="font-weight:700;font-size:15px;color:#2563EB;text-align:right;padding-top:6px;">{stock["weight"]}%</div>', unsafe_allow_html=True)
            with cb:
                b1,b2 = st.columns(2)
                with b1:
                    if st.button("✏️", key=f"edit_{i}", help="수정"):
                        st.session_state.editing = i
                        st.rerun()
                with b2:
                    if st.button("🗑", key=f"del_{i}", help="삭제"):
                        st.session_state.portfolio.pop(i)
                        if st.session_state.editing == i:
                            st.session_state.editing = None
                        st.rerun()
        st.markdown("<hr style='margin:6px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)

    if st.button("➕  종목 추가", use_container_width=True, key="toggle_add"):
        st.session_state.show_add = not st.session_state.show_add

    if st.session_state.show_add:
        st.markdown("**새 종목 추가**")
        nt = st.text_input("티커 심볼", placeholder="예: AAPL", key="add_t").upper().strip()
        nn = st.text_input("종목명",    placeholder="예: Apple Inc",  key="add_n")
        nw = st.number_input("비중(%)", min_value=1, max_value=100, value=10, key="add_w")
        ns = st.number_input("수량(주)",min_value=1, max_value=100000, value=10, key="add_s")
        na = st.number_input("평균단가($)", min_value=0.0, max_value=999999.0, value=0.0, format="%.2f", key="add_a")
        if nt:
            dsec = detect_sector(nt)
            dcfg = SECTOR_CONFIG[dsec]
            st.markdown(f'<div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:6px;padding:6px 10px;font-size:12px;color:#059669;margin:4px 0;">{dcfg["icon"]} 감지 섹터: <b>{dcfg["label"]}</b></div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("✅ 추가", key="do_add", use_container_width=True):
                if nt:
                    st.session_state.portfolio.append({"ticker":nt,"name":nn or nt,"weight":nw,"shares":ns,"avg_price":na})
                    st.session_state.show_add = False
                    st.rerun()
        with c2:
            if st.button("✕ 닫기", key="close_add", use_container_width=True):
                st.session_state.show_add = False
                st.rerun()

    st.markdown("---")
    if st.sidebar.button("🔄 전체 초기화", use_container_width=True):
        st.session_state.portfolio = []
        st.session_state.editing = None
        st.rerun()


# ── 메인 대시보드 ──────────────────────────────────────────────────────────
if st.session_state.page == 'main':
    st.markdown('<div style="margin-bottom:20px;"><h2 style="font-size:22px;font-weight:700;color:#1A1D23;margin:0;">📊 포트폴리오 현황</h2></div>', unsafe_allow_html=True)

    # 주요 거시 지표
    st.markdown('<div class="section-hdr">📡 주요 거시 지표</div>', unsafe_allow_html=True)
    macro_list = [("S&P 500","^GSPC","시장 전체"),("나스닥 100","^NDX","기술·성장주"),
                  ("10년물 금리","^TNX","금리 환경"),("VIX 공포","^VIX","시장 불안"),("WTI 유가","CL=F","에너지·인플레")]
    mc = st.columns(5)
    for col,(label,sym,desc) in zip(mc, macro_list):
        z,price = get_z_and_price(sym)
        arrow = "▲" if z>0.2 else "▼" if z<-0.2 else "—"
        ac = "#059669" if z>0.2 else "#DC2626" if z<-0.2 else "#6B7280"
        col.markdown(f'<div class="macro-card"><div style="font-size:10px;font-weight:600;color:#6B7280;margin-bottom:4px;">{label}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:19px;font-weight:700;color:{zcolor(z)};">{price:,.2f} <span style="font-size:13px;color:{ac};">{arrow}</span></div><div style="font-size:10px;color:#9CA3AF;margin-top:2px;">Z {z:+.2f}σ · {desc}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.portfolio:
        st.markdown('<div style="background:#FFFFFF;border:2px dashed #D1D5DB;border-radius:12px;padding:48px;text-align:center;"><div style="font-size:36px;margin-bottom:10px;">📭</div><div style="font-size:16px;font-weight:600;color:#374151;margin-bottom:6px;">아직 종목이 없습니다</div><div style="font-size:13px;color:#9CA3AF;">왼쪽 사이드바에서 <b>➕ 종목 추가</b>를 눌러주세요.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="section-hdr">📈 보유 종목 분석 <span class="lv1" style="margin-left:6px;">Lv.1</span></div>', unsafe_allow_html=True)
        chunk = 4
        for rs in range(0, len(st.session_state.portfolio), chunk):
            row = st.session_state.portfolio[rs:rs+chunk]
            cols = st.columns(len(row))
            for col, stock in zip(cols, row):
                with col:
                    with st.spinner(""):
                        zs, price = get_z_and_price(stock['ticker'])
                        _, cfg, inds = get_sector_analysis(stock['ticker'])
                        nb, _ = get_news(stock['ticker'])
                        win, explain_text = calc_win_rate(zs, inds, nb)
                    st_,sc_,sv_ = get_signal(win)
                    
                    if stock.get('avg_price', 0) > 0:
                        pnl = ((price-stock['avg_price'])/stock['avg_price']*100)
                        pnl_text = f"{'+'if pnl>=0 else ''}{pnl:.1f}%"
                        pc = "#059669" if pnl>=0 else "#DC2626"
                    else:
                        pnl_text = "미입력"; pc = "#9CA3AF"
                        
                    ti = max(inds, key=lambda x: abs(x["z"]*x["weight"]))
                    tc2 = ti["z"]*ti["weight"]*0.5
                    tclr = "#059669" if tc2>0 else "#DC2626"
                    
                    st.markdown(f"""
<div class="stock-card" style="border-top:3px solid {sv_};">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
        <div>
            <span style="font-weight:700;font-size:15px;color:#1A1D23;">{stock['ticker']}</span>
            <span style="font-size:11px;color:{cfg['color']};margin-left:4px;">{cfg['icon']}</span>
            <div style="font-size:10px;color:#9CA3AF;">{stock['name']}</div>
        </div>
        <div class="{sc_}">{st_}</div>
    </div>
    <div style="display:flex;align-items:baseline;gap:4px;margin-bottom:2px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:700;color:{sv_};line-height:1;">{win}%</span>
        <span style="font-size:10px;color:#9CA3AF;">승률 <span title="{explain_text}" style="cursor:help;font-size:12px;background:#F3F4F6;padding:2px 4px;border-radius:10px;">❔</span></span>
    </div>
    <div style="font-size:10px;color:{tclr};margin-bottom:8px;">{'▲' if tc2>0 else '▼'} {ti['name']} Z{ti['z']:+.1f}</div>
    <div style="display:flex;justify-content:space-between;font-size:11px;padding-top:8px;border-top:1px solid #F3F4F6;">
        <span style="color:#6B7280;">${price:.1f}</span>
        <span style="color:{pc};font-weight:500;">{pnl_text}</span>
        <span style="color:#9CA3AF;">{stock['weight']}%</span>
    </div>
</div>""", unsafe_allow_html=True)
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                    if st.button("상세 분석 →", key=f"go_{stock['ticker']}_{rs}"):
                        st.session_state.selected = stock['ticker']
                        st.session_state.page = 'detail'; st.rerun()

        # 배분 차트
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">📊 포트폴리오 구성</div>', unsafe_allow_html=True)
        cc, bc = st.columns([1,2])
        with cc:
            labels  = [s['ticker'] for s in st.session_state.portfolio]
            weights = [s['weight'] for s in st.session_state.portfolio]
            colors  = [SECTOR_CONFIG[detect_sector(s['ticker'])]["color"] for s in st.session_state.portfolio]
            fig = go.Figure(go.Pie(values=weights,labels=labels,hole=0.6, marker=dict(colors=colors,line=dict(color="#FFFFFF",width=2))))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",showlegend=False, margin=dict(t=10,b=10,l=10,r=10),height=200, annotations=[dict(text=f"<b>{sum(weights)}%</b>",x=0.5,y=0.5,showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)
        with bc:
            for s in st.session_state.portfolio:
                sc = SECTOR_CONFIG[detect_sector(s['ticker'])]
                st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="font-size:13px;font-weight:600;color:#1A1D23;">{s["ticker"]} <span style="font-size:11px;color:{sc["color"]};">{sc["icon"]} {sc["label"]}</span></span><span style="font-size:13px;font-weight:600;color:#2563EB;">{s["weight"]}%</span></div><div style="height:4px;background:#F3F4F6;border-radius:2px;"><div style="height:100%;width:{min(s["weight"],100)}%;background:{sc["color"]};border-radius:2px;opacity:0.8;"></div></div></div>', unsafe_allow_html=True)


# ── 상세 분석 페이지 ──────────────────────────────────────────────────────
elif st.session_state.page == 'detail':
    target = st.session_state.selected or ''
    if not target: st.session_state.page = 'main'; st.rerun()
    if st.sidebar.button("← 대시보드로", use_container_width=True): st.session_state.page = 'main'; st.rerun()

    si = next((s for s in st.session_state.portfolio if s['ticker']==target), {"name":target,"weight":"—","avg_price":0,"shares":0})

    with st.spinner(f"{target} 분석 중..."):
        zs, price = get_z_and_price(target)
        sk, cfg, inds = get_sector_analysis(target)
        nb, nd = get_news(target)
        fw, explain_text = calc_win_rate(zs, inds, nb)
        history = get_price_history(target)

    st_, sc_, sv_ = get_signal(fw)
    pnl = ((price-si['avg_price'])/si['avg_price']*100) if price and si['avg_price'] > 0 else 0
    pc = "#059669" if pnl>=0 else "#DC2626"

    # 헤더
    hl,hr = st.columns([3,1])
    with hl:
        st.markdown(f'<div style="margin-bottom:16px;"><div style="font-size:11px;color:#6B7280;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{cfg["icon"]} {cfg["label"]} 섹터</div><div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;"><h1 style="font-size:26px;font-weight:700;color:#1A1D23;margin:0;">{target}</h1><div class="{sc_}">{st_}</div></div><div style="font-size:12px;color:#6B7280;">{si["name"]} · 비중 {si["weight"]}% · 평균 ${si["avg_price"]:.2f}</div></div>', unsafe_allow_html=True)
    with hr:
        st.markdown(f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:18px;text-align:center;border-top:3px solid {sv_};"><div style="font-size:10px;color:#9CA3AF;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">오늘의 승률</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:42px;font-weight:700;color:{sv_};line-height:1;">{fw}%</div><div style="font-size:11px;color:#9CA3AF;margin-top:4px;" title="{explain_text}">계산 근거 확인 ❔</div></div>', unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["🌡️ 종합 기상도", f"{cfg['icon']} 섹터 지표", "📰 뉴스 분석"])
    
    with tab1:
        gl,gr = st.columns([1,2])
        with gl:
            gauge = go.Figure(go.Indicator(mode="gauge+number",value=fw, number={"suffix":"%","font":{"family":"JetBrains Mono","size":28,"color":sv_}}, gauge={"axis":{"range":[0,100]}, "bar":{"color":sv_}, "steps":[{"range":[0,45],"color":"rgba(220,38,38,0.05)"},{"range":[45,60],"color":"rgba(217,119,6,0.05)"},{"range":[60,100],"color":"rgba(5,150,105,0.05)"}]}))
            gauge.update_layout(height=200, margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(gauge, use_container_width=True)
        with gr:
            if not history.empty:
                fh = go.Figure(go.Scatter(x=history['Date'],y=history['Close'],mode='lines', line=dict(color=sv_,width=2),fill='tozeroy'))
                fh.update_layout(height=240, margin=dict(t=10,b=10,l=0,r=0))
                st.plotly_chart(fh, use_container_width=True)

    with tab2:
        for ind in inds:
            contrib = ind["z"]*(ind["weight"]/5.0)
            st.markdown(f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:14px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;"><b>{ind["name"]}</b> <span>{ind["z"]:+.2f}σ</span></div><div style="font-size:11px;color:#9CA3AF;">{ind["desc"]}</div><div style="font-size:11px;color:{"#059669" if contrib>0 else "#DC2626"};margin-top:4px;">승률 기여 {contrib:+.1f}%p</div></div>', unsafe_allow_html=True)

    with tab3:
        if nd:
            for n in nd:
                css="news-pos" if n['sentiment']=="Positive" else "news-neg" if n['sentiment']=="Negative" else "news-neu"
                st.markdown(f'<div class="{css}"><a href="{n["link"]}" target="_blank" style="font-size:12px;color:#374151;text-decoration:none;">{n["title"]}</a></div>', unsafe_allow_html=True)
        else: st.info("데이터가 없습니다.")
