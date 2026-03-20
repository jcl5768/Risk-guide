
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
# 2. 섹터별 거시지표 매핑 (이전과 동일, 핵심 엔진 유지)
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
    "XLV":"Healthcare","JNJ":"Healthcare","UNH":"Healthcare","PFE":"Healthcare",
    "QQQ":"Technology","SPY":"Unknown","IWM":"Unknown",
    "SOXX":"Technology","LIT":"Consumer Cyclical",
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. 세션 상태 — 포트폴리오 영구 보존
#    핵심: st.session_state에 portfolio를 저장하면 페이지 이동해도 유지됨
#    단, Replit 새로고침 시에는 초기화됨 (DB 연동은 추후)
# ═══════════════════════════════════════════════════════════════════════════
def init_session():
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = [
            {"ticker":"XOM",  "name":"Exxon Mobil",   "weight":23, "shares":250, "avg_price":105.0},
            {"ticker":"TSLA", "name":"Tesla",          "weight":10, "shares":50,  "avg_price":200.0},
            {"ticker":"XLP",  "name":"필수소비재 ETF","weight":15, "shares":100, "avg_price":72.0},
        ]
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if 'selected' not in st.session_state:
        st.session_state.selected = None
    if 'editing' not in st.session_state:
        st.session_state.editing = None   # 수정 중인 종목 인덱스
    if 'show_add' not in st.session_state:
        st.session_state.show_add = False

init_session()

# ═══════════════════════════════════════════════════════════════════════════
# 4. 분석 엔진
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def detect_sector(ticker):
    t = ticker.upper()
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
        data = yf.download(ticker, period="60d", interval="1d", progress=False)['Close']
        if len(data) < 21:
            return 0.0, 0.0
        cur  = float(data.iloc[-1])
        mean = float(data.tail(20).mean())
        std  = float(data.tail(20).std())
        if std == 0:
            return 0.0, round(cur, 2)
        return round((cur - mean) / std, 2), round(cur, 2)
    except:
        return 0.0, 0.0

@st.cache_data(ttl=300)
def get_sector_analysis(ticker):
    sector_key = detect_sector(ticker)
    cfg = SECTOR_CONFIG[sector_key]
    results = []
    for ind in cfg["indicators"]:
        z, price = get_z_and_price(ind["ticker"])
        results.append({**ind, "z": z, "price": price})
    return sector_key, cfg, results

@st.cache_data(ttl=300)
def get_price_history(ticker):
    try:
        data = yf.download(ticker, period="60d", interval="1d", progress=False)['Close']
        return data.reset_index()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_news(ticker):
    try:
        news_list = yf.Ticker(ticker).news[:5]
        pos_kw = ['buy','growth','up','positive','surge','profit','beat','record','strong','upgrade','bullish','soars']
        neg_kw = ['sell','fall','down','negative','drop','loss','risk','crisis','miss','weak','downgrade','bearish','cut']
        score, analyzed = 0, []
        for n in news_list:
            title = n.get('title','').lower()
            if any(w in title for w in pos_kw):
                score += 1; sentiment = "Positive"
            elif any(w in title for w in neg_kw):
                score -= 1; sentiment = "Negative"
            else:
                sentiment = "Neutral"
            analyzed.append({"title":n.get('title',''), "link":n.get('link','#'), "sentiment":sentiment})
        return score * 2.5, analyzed
    except:
        return 0.0, []

def calc_win_rate(z_stock, indicators, news_bonus):
    base = 50.0 - z_stock * 5
    for ind in indicators:
        base += ind["z"] * ind["weight"] * 0.5
    return round(max(5.0, min(95.0, base + news_bonus)), 1)

def get_signal(wr):
    if wr >= 60:   return "매수 우위", "badge-green",  "#059669"
    elif wr >= 45: return "중립 관망", "badge-yellow", "#D97706"
    else:          return "리스크 경고","badge-red",   "#DC2626"

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

# ═══════════════════════════════════════════════════════════════════════════
# 5. 사이드바 — 포트폴리오 CRUD
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 📂 내 포트폴리오")
    st.markdown("---")

    # ── 종목 목록 ──────────────────────────────────────────────────────
    for i, stock in enumerate(st.session_state.portfolio):
        sec   = detect_sector(stock['ticker'])
        cfg   = SECTOR_CONFIG[sec]
        is_editing = (st.session_state.editing == i)

        with st.container():
            if is_editing:
                # ── 수정 모드 ──────────────────────────────────────────
                st.markdown(f"**{stock['ticker']} 수정**")
                new_name   = st.text_input("종목명",   value=stock['name'],      key=f"e_name_{i}")
                new_weight = st.number_input("비중(%)", value=int(stock['weight']),
                                             min_value=1, max_value=100,         key=f"e_weight_{i}")
                new_shares = st.number_input("수량",    value=int(stock['shares']),
                                             min_value=1, max_value=100000,      key=f"e_shares_{i}")
                new_avg    = st.number_input("평균단가($)", value=float(stock['avg_price']),
                                             min_value=0.1, max_value=100000.0,  key=f"e_avg_{i}",
                                             format="%.2f")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("✅ 저장", key=f"save_{i}"):
                        st.session_state.portfolio[i].update({
                            "name": new_name, "weight": new_weight,
                            "shares": new_shares, "avg_price": new_avg
                        })
                        st.session_state.editing = None
                        st.rerun()
                with col_cancel:
                    if st.button("✕ 취소", key=f"cancel_{i}"):
                        st.session_state.editing = None
                        st.rerun()
            else:
                # ── 일반 표시 모드 ─────────────────────────────────────
                col_info, col_pct, col_btns = st.columns([3, 1, 2])
                with col_info:
                    st.markdown(f"""
                    <div style='line-height:1.4;'>
                        <span style='font-weight:700;font-size:14px;color:#1A1D23;'>{stock['ticker']}</span>
                        <span style='font-size:11px;color:{cfg["color"]};margin-left:4px;'>{cfg["icon"]}</span><br>
                        <span style='font-size:11px;color:#6B7280;'>{stock['name']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_pct:
                    st.markdown(f"""
                    <div style='font-weight:700;font-size:16px;color:#2563EB;text-align:right;padding-top:4px;'>
                        {stock['weight']}%
                    </div>
                    """, unsafe_allow_html=True)
                with col_btns:
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✏️", key=f"edit_{i}", help="수정"):
                            st.session_state.editing = i
                            st.rerun()
                    with b2:
                        if st.button("🗑️", key=f"del_{i}", help="삭제"):
                            st.session_state.portfolio.pop(i)
                            if st.session_state.editing == i:
                                st.session_state.editing = None
                            st.rerun()

            st.markdown("<hr style='margin:8px 0;border-color:#E8EAED;'>", unsafe_allow_html=True)

    # ── 종목 추가 ──────────────────────────────────────────────────────
    st.markdown("")
    if st.button("➕  종목 추가", use_container_width=True):
        st.session_state.show_add = not st.session_state.show_add

    if st.session_state.show_add:
        st.markdown("**새 종목 추가**")
        new_ticker = st.text_input("티커 심볼", placeholder="예: AAPL", key="add_ticker").upper()
        new_name   = st.text_input("종목명",    placeholder="예: Apple Inc",   key="add_name")
        new_weight = st.number_input("비중(%)",  min_value=1,   max_value=100, value=10, key="add_weight")
        new_shares = st.number_input("수량",     min_value=1,   max_value=100000, value=10, key="add_shares")
        new_avg    = st.number_input("평균단가($)", min_value=0.1, max_value=100000.0,
                                     value=100.0, format="%.2f", key="add_avg")

        # 섹터 자동 감지 미리보기
        if new_ticker:
            detected = detect_sector(new_ticker)
            dcfg = SECTOR_CONFIG[detected]
            st.markdown(f"""
            <div style='background:#F0FDF4;border:1px solid #A7F3D0;border-radius:6px;
                        padding:6px 10px;font-size:12px;color:#059669;margin-bottom:8px;'>
                {dcfg["icon"]} 감지된 섹터: <b>{dcfg["label"]}</b>
            </div>
            """, unsafe_allow_html=True)

        col_add, col_close = st.columns(2)
        with col_add:
            if st.button("✅ 추가", key="confirm_add", use_container_width=True):
                if new_ticker:
                    st.session_state.portfolio.append({
                        "ticker":    new_ticker,
                        "name":      new_name or new_ticker,
                        "weight":    new_weight,
                        "shares":    new_shares,
                        "avg_price": new_avg,
                    })
                    st.session_state.show_add = False
                    st.rerun()
        with col_close:
            if st.button("✕ 닫기", key="close_add", use_container_width=True):
                st.session_state.show_add = False
                st.rerun()

    st.markdown("---")

    # ── 포트폴리오 초기화 ──────────────────────────────────────────────
    with st.expander("⚙️ 설정"):
        if st.button("🔄 기본값으로 초기화", use_container_width=True):
            del st.session_state['portfolio']
            st.session_state.editing = None
            st.rerun()
        total_w = sum(s['weight'] for s in st.session_state.portfolio)
        color = "#059669" if total_w <= 100 else "#DC2626"
        st.markdown(f"""
        <div style='font-size:12px;color:{color};margin-top:8px;'>
            총 비중: <b>{total_w}%</b>
            {'✓' if total_w <= 100 else ' ⚠ 100% 초과'}
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 6. 메인 대시보드
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.page == 'main':

    # ── 타이틀 (추후 수정 예정) ────────────────────────────────────────
    st.markdown("""
    <div style='margin-bottom:20px;'>
        <h2 style='font-size:22px;font-weight:700;color:#1A1D23;margin:0;'>오늘의 포트폴리오 현황</h2>
        <p style='font-size:13px;color:#6B7280;margin:4px 0 0;'>
            섹터별 맞춤 거시지표 기반 통계적 승률 분석
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── 주요 거시 지표 5개 ─────────────────────────────────────────────
    # 기존 VIX/TLT/달러 → 더 핵심적인 지표로 교체
    st.markdown('<div class="section-header">📡 주요 거시 지표</div>', unsafe_allow_html=True)

    macro_tickers = [
        ("S&P 500",    "^GSPC",     "시장 전체 흐름"),
        ("나스닥 100", "^NDX",      "기술·성장주 흐름"),
        ("10년물 금리","^TNX",      "금리 환경 — 전 섹터 영향"),
        ("VIX 공포",   "^VIX",      "시장 불안 수준"),
        ("WTI 유가",   "CL=F",      "에너지·인플레 선행지표"),
    ]
    m_cols = st.columns(5)
    for col, (label, sym, desc) in zip(m_cols, macro_tickers):
        z, price = get_z_and_price(sym)
        arrow = "▲" if z > 0.2 else "▼" if z < -0.2 else "—"
        a_color = "#059669" if z > 0.2 else "#DC2626" if z < -0.2 else "#6B7280"
        col.markdown(f"""
        <div class="macro-card">
            <div class="macro-label">{label}</div>
            <div class="macro-value" style="color:{zcolor(z)};">
                {price:,.2f}
                <span style='font-size:14px;color:{a_color};'>{arrow}</span>
            </div>
            <div class="macro-sub">Z {z:+.2f}σ &nbsp;·&nbsp; {desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 포트폴리오 종목 카드 (컴팩트) ────────────────────────────────
    if not st.session_state.portfolio:
        st.info("포트폴리오가 비어있습니다. 사이드바에서 종목을 추가해주세요.")
    else:
        st.markdown('<div class="section-header">📈 보유 종목 분석</div>', unsafe_allow_html=True)

        # 한 행에 최대 4개
        chunk_size = 4
        portfolio  = st.session_state.portfolio
        for row_start in range(0, len(portfolio), chunk_size):
            row_stocks = portfolio[row_start : row_start + chunk_size]
            cols = st.columns(len(row_stocks))

            for col, stock in zip(cols, row_stocks):
                with col:
                    with st.spinner(""):
                        z_stock, price     = get_z_and_price(stock['ticker'])
                        _, cfg, inds       = get_sector_analysis(stock['ticker'])
                        news_bonus, _      = get_news(stock['ticker'])
                        win = calc_win_rate(z_stock, inds, news_bonus)

                    sig_text, sig_class, sig_color = get_signal(win)
                    pnl = ((price - stock['avg_price']) / stock['avg_price'] * 100) if price and stock['avg_price'] else 0
                    pnl_color = "#059669" if pnl >= 0 else "#DC2626"
                    pnl_str   = f"{'+'if pnl>=0 else ''}{pnl:.1f}%"

                    # 가장 영향 큰 지표 1개
                    top_ind = max(inds, key=lambda x: abs(x["z"] * x["weight"]))
                    top_contrib = top_ind["z"] * top_ind["weight"] * 0.5
                    top_color   = "#059669" if top_contrib > 0 else "#DC2626"

                    st.markdown(f"""
                    <div class="stock-card" style="border-top:3px solid {sig_color};">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div>
                                <span style="font-weight:700;font-size:15px;color:#1A1D23;">{stock['ticker']}</span>
                                <span style="font-size:11px;color:{cfg['color']};margin-left:5px;">{cfg['icon']}</span>
                                <div style="font-size:11px;color:#9CA3AF;margin-top:1px;">{stock['name']}</div>
                            </div>
                            <div class="{sig_class}" style="font-size:10px;">{sig_text}</div>
                        </div>

                        <div style="display:flex;align-items:baseline;gap:4px;margin-bottom:2px;">
                            <span style="font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:700;color:{sig_color};line-height:1;">{win}%</span>
                            <span style="font-size:11px;color:#9CA3AF;">승률</span>
                        </div>

                        <div style="font-size:11px;color:{top_color};margin-bottom:10px;">
                            {'▲' if top_contrib>0 else '▼'} {top_ind['name']} Z{top_ind['z']:+.1f}
                        </div>

                        <div style="display:flex;justify-content:space-between;font-size:12px;padding-top:8px;border-top:1px solid #F3F4F6;">
                            <span style="color:#6B7280;">${price:.1f}</span>
                            <span style="color:{pnl_color};font-weight:500;">{pnl_str}</span>
                            <span style="color:#9CA3AF;">{stock['weight']}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
                    if st.button(f"상세 분석 →", key=f"go_{stock['ticker']}_{row_start}"):
                        st.session_state.selected = stock['ticker']
                        st.session_state.page     = 'detail'
                        st.rerun()

        # ── 포트폴리오 배분 요약 ───────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 포트폴리오 구성</div>', unsafe_allow_html=True)

        chart_col, bar_col = st.columns([1, 2])
        with chart_col:
            labels  = [s['ticker']  for s in st.session_state.portfolio]
            weights = [s['weight']  for s in st.session_state.portfolio]
            colors  = [SECTOR_CONFIG[detect_sector(s['ticker'])]["color"] for s in st.session_state.portfolio]
            fig = go.Figure(go.Pie(
                values=weights, labels=labels, hole=0.6,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                textfont=dict(family="Inter", size=11),
                hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>"
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                margin=dict(t=10,b=10,l=10,r=10), height=200,
                annotations=[dict(text=f"<b>{sum(weights)}%</b>",
                    x=0.5, y=0.5, font=dict(size=14, color="#1A1D23", family="Inter"),
                    showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)

        with bar_col:
            for s in st.session_state.portfolio:
                sc = SECTOR_CONFIG[detect_sector(s['ticker'])]
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="font-size:13px;font-weight:600;color:#1A1D23;">
                            {s['ticker']}
                            <span style="font-size:11px;color:{sc['color']};margin-left:4px;">{sc['icon']} {sc['label']}</span>
                        </span>
                        <span style="font-size:13px;font-weight:600;color:#2563EB;">{s['weight']}%</span>
                    </div>
                    <div style="height:5px;background:#F3F4F6;border-radius:3px;">
                        <div style="height:100%;width:{s['weight']}%;background:{sc['color']};border-radius:3px;opacity:0.8;"></div>
                    </div>
                    <div style="font-size:11px;color:#9CA3AF;margin-top:2px;">
                        {s['name']} · {s['shares']}주 · 평균 ${s['avg_price']:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 7. 상세 분석 페이지
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == 'detail':
    target = st.session_state.selected or 'XOM'

    # ── 뒤로 가기 (포트폴리오 유지) ──────────────────────────────────
    if st.sidebar.button("← 대시보드로 돌아가기", use_container_width=True):
        st.session_state.page = 'main'
        st.rerun()

    # 포트폴리오에서 종목 정보 찾기 (없으면 기본값)
    stock_info = next(
        (s for s in st.session_state.portfolio if s['ticker'] == target),
        {"name": target, "weight": "—", "avg_price": 0, "shares": 0}
    )

    # ── 데이터 로드 ──────────────────────────────────────────────────
    with st.spinner(f"{target} 데이터 수집 중..."):
        z_stock, price       = get_z_and_price(target)
        sector_key, cfg, inds = get_sector_analysis(target)
        news_bonus, news_data = get_news(target)
        final_win             = calc_win_rate(z_stock, inds, news_bonus)
        history               = get_price_history(target)

    sig_text, sig_class, sig_color = get_signal(final_win)
    pnl = ((price - stock_info['avg_price']) / stock_info['avg_price'] * 100) if price and stock_info['avg_price'] else 0

    # ── 헤더 ─────────────────────────────────────────────────────────
    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_l:
        st.markdown(f"""
        <div style="margin-bottom:20px;">
            <div style="font-size:11px;color:#6B7280;font-weight:500;
                        letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                {cfg['icon']} {cfg['label']} 섹터
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
                <h1 style="font-size:28px;font-weight:700;color:#1A1D23;margin:0;">{target}</h1>
                <div class="{sig_class}">{sig_text}</div>
            </div>
            <div style="font-size:13px;color:#6B7280;">
                {stock_info['name']}
                &nbsp;·&nbsp; 비중 {stock_info['weight']}%
                &nbsp;·&nbsp; {stock_info['shares']}주 보유
                &nbsp;·&nbsp; 평균단가 ${stock_info['avg_price']:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hdr_r:
        pnl_color = "#059669" if pnl >= 0 else "#DC2626"
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;
                    padding:20px;text-align:center;border-top:3px solid {sig_color};">
            <div style="font-size:10px;color:#9CA3AF;font-weight:500;
                        letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">
                오늘의 승률
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:44px;
                        font-weight:700;color:{sig_color};line-height:1;">{final_win}%</div>
            <div style="font-size:11px;color:#9CA3AF;margin-top:6px;">
                뉴스 보정 {news_bonus:+.1f}%
                &nbsp;·&nbsp;
                수익률 <span style="color:{pnl_color};">{'+'if pnl>=0 else ''}{pnl:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 탭 ───────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️  종합 기상도",
        f"{cfg['icon']}  섹터 지표 분석",
        "📰  뉴스 감성",
        "🔮  시나리오 시뮬",
    ])

    # ── TAB 1: 종합 기상도 ────────────────────────────────────────────
    with tab1:
        g_left, g_right = st.columns([1, 2])

        with g_left:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=final_win,
                number={"suffix":"%","font":{"family":"JetBrains Mono","size":32,"color":sig_color}},
                gauge={
                    "axis":{"range":[0,100],"tickcolor":"#E8EAED",
                            "tickfont":{"color":"#9CA3AF","size":10}},
                    "bar":{"color":sig_color,"thickness":0.28},
                    "bgcolor":"#FFFFFF","borderwidth":0,
                    "steps":[
                        {"range":[0,45],  "color":"rgba(220,38,38,0.06)"},
                        {"range":[45,60], "color":"rgba(217,119,6,0.06)"},
                        {"range":[60,100],"color":"rgba(5,150,105,0.06)"},
                    ],
                    "threshold":{"line":{"color":sig_color,"width":2},"thickness":0.8,"value":final_win},
                }
            ))
            gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color":"#1A1D23"},
                margin=dict(t=10,b=10,l=10,r=10), height=200
            )
            st.plotly_chart(gauge, use_container_width=True)

            # 한 줄 요약
            top_pos = sorted([x for x in inds if x["z"]*x["weight"]>0], key=lambda x: x["z"]*x["weight"], reverse=True)
            top_neg = sorted([x for x in inds if x["z"]*x["weight"]<0], key=lambda x: x["z"]*x["weight"])
            pos_str = top_pos[0]["name"] if top_pos else "없음"
            neg_str = top_neg[0]["name"] if top_neg else "없음"
            st.markdown(f"""
            <div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:8px;padding:12px 14px;margin-top:8px;">
                <div style="font-size:10px;color:#059669;font-weight:600;letter-spacing:1px;margin-bottom:4px;">AI 요약</div>
                <div style="font-size:12px;color:#374151;line-height:1.6;">
                    <span style="color:#059669;">▲ {pos_str}</span> 긍정적 &nbsp;|&nbsp;
                    <span style="color:#DC2626;">▼ {neg_str}</span> 리스크
                </div>
            </div>
            """, unsafe_allow_html=True)

        with g_right:
            if not history.empty:
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Scatter(
                    x=history['Date'], y=history['Close'],
                    mode='lines',
                    line=dict(color=sig_color, width=2),
                    fill='tozeroy',
                    fillcolor=f'rgba({int(sig_color[1:3],16)},{int(sig_color[3:5],16)},{int(sig_color[5:7],16)},0.06)',
                    name=target,
                    hovertemplate="$%{y:.2f}<br>%{x|%m/%d}<extra></extra>"
                ))
                if len(history) >= 20:
                    ma20 = history['Close'].rolling(20).mean()
                    fig_hist.add_trace(go.Scatter(
                        x=history['Date'], y=ma20, mode='lines',
                        line=dict(color="#D97706", width=1.5, dash='dash'),
                        name="MA20", hovertemplate="MA20 $%{y:.2f}<extra></extra>"
                    ))
                fig_hist.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#6B7280", family="Inter"),
                    xaxis=dict(showgrid=False, color="#D1D5DB", showline=False),
                    yaxis=dict(showgrid=True, gridcolor="#F3F4F6", color="#9CA3AF"),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
                    margin=dict(t=10,b=10,l=0,r=0), height=240, hovermode="x unified"
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            # KPI 4개
            kc = st.columns(4)
            for col, (lbl, val, clr) in zip(kc, [
                ("현재가",  f"${price:.2f}",       "#1A1D23"),
                ("주가 Z",  f"{z_stock:+.2f}σ",    zcolor(z_stock)),
                ("뉴스",    f"{news_bonus:+.1f}%",  "#059669" if news_bonus>0 else "#DC2626"),
                ("수익률",  f"{'+'if pnl>=0 else ''}{pnl:.1f}%", "#059669" if pnl>=0 else "#DC2626"),
            ]):
                col.markdown(f"""
                <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;
                            padding:12px;text-align:center;">
                    <div style="font-size:10px;color:#9CA3AF;font-weight:500;
                                letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{lbl}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:18px;
                                font-weight:700;color:{clr};">{val}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2: 섹터 지표 분석 ─────────────────────────────────────────
    with tab2:
        st.markdown(f"""
        <div style="background:#F9FAFB;border:1px solid #E8EAED;border-radius:8px;
                    padding:12px 16px;margin-bottom:16px;font-size:12px;color:#6B7280;">
            <b style="color:{cfg['color']};">{cfg['icon']} {cfg['label']} 섹터</b>에 맞는
            <b style="color:#1A1D23;">{len(inds)}개 지표</b>를 자동 선택하여 승률에 반영합니다.
            가중치(+/-)는 해당 지표가 이 종목에 미치는 방향과 강도입니다.
        </div>
        """, unsafe_allow_html=True)

        for ind in inds:
            contrib = ind["z"] * ind["weight"] * 0.5
            c_color = "#059669" if contrib > 0 else "#DC2626" if contrib < 0 else "#6B7280"
            w_label = f"호재 +{ind['weight']}" if ind["weight"] > 0 else f"악재 {ind['weight']}"
            w_color = "#059669" if ind["weight"] > 0 else "#DC2626"

            # Z-Score 바
            if ind["z"] >= 0:
                bs, bw = 50.0, min(50.0, ind["z"]/3*50)
            else:
                bw = min(50.0, abs(ind["z"])/3*50)
                bs = 50.0 - bw

            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;
                        padding:14px 18px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                    <div>
                        <span style="font-size:13px;font-weight:600;color:#1A1D23;">{ind['name']}</span>
                        <span style="font-size:11px;color:#9CA3AF;margin-left:6px;">({ind['ticker']})</span>
                        <div style="font-size:11px;color:#9CA3AF;margin-top:2px;">{ind['desc']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:16px;
                                    font-weight:700;color:{zcolor(ind['z'])};">{ind['z']:+.2f}σ</div>
                        <div style="font-size:10px;color:{zcolor(ind['z'])};">{zdesc(ind['z'])}</div>
                    </div>
                </div>
                <div style="height:5px;background:#F3F4F6;border-radius:3px;position:relative;margin-bottom:6px;">
                    <div style="position:absolute;top:0;left:49.5%;width:1px;height:100%;background:#E8EAED;"></div>
                    <div style="position:absolute;top:0;left:{bs}%;width:{bw}%;height:100%;
                                background:{zcolor(ind['z'])};border-radius:3px;opacity:0.7;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:11px;">
                    <span style="color:{w_color};">{w_label}</span>
                    <span style="color:{c_color};font-weight:600;">
                        승률 기여 {'+'if contrib>0 else ''}{contrib:.1f}%p
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 레이더 차트
        st.markdown("<br>", unsafe_allow_html=True)
        r_labels = [ind["name"] for ind in inds]
        r_vals   = [(min(3, max(-3, ind["z"])) + 3) / 6 for ind in inds]
        radar = go.Figure(go.Scatterpolar(
            r=r_vals+[r_vals[0]], theta=r_labels+[r_labels[0]],
            fill='toself',
            fillcolor=f'rgba({int(cfg["color"][1:3],16)},{int(cfg["color"][3:5],16)},{int(cfg["color"][5:7],16)},0.12)',
            line=dict(color=cfg["color"], width=2),
            marker=dict(size=5, color=cfg["color"]),
        ))
        radar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            polar=dict(
                bgcolor="#FAFAFA",
                radialaxis=dict(visible=True, range=[0,1], showticklabels=False,
                                gridcolor="#E8EAED", linecolor="#E8EAED"),
                angularaxis=dict(tickfont=dict(color="#6B7280",size=11,family="Inter"),
                                 gridcolor="#E8EAED", linecolor="#E8EAED"),
            ),
            showlegend=False,
            margin=dict(t=20,b=20,l=60,r=60), height=300
        )
        st.plotly_chart(radar, use_container_width=True)

    # ── TAB 3: 뉴스 감성 ─────────────────────────────────────────────
    with tab3:
        nl, nr = st.columns([2, 1])
        with nl:
            st.markdown('<div class="section-header">최신 뉴스 감성 분석</div>', unsafe_allow_html=True)
            if news_data:
                for n in news_data:
                    css  = "news-pos" if n['sentiment']=="Positive" else "news-neg" if n['sentiment']=="Negative" else "news-neu"
                    icon = "▲" if n['sentiment']=="Positive" else "▼" if n['sentiment']=="Negative" else "●"
                    tc   = "#059669" if n['sentiment']=="Positive" else "#DC2626" if n['sentiment']=="Negative" else "#9CA3AF"
                    st.markdown(f"""
                    <div class="{css}">
                        <div style="font-size:10px;color:{tc};font-weight:600;margin-bottom:4px;">
                            {icon} {n['sentiment'].upper()}
                        </div>
                        <a href="{n['link']}" target="_blank"
                           style="font-size:12px;color:#374151;text-decoration:none;line-height:1.5;">
                            {n['title']}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#9CA3AF;font-size:13px;'>뉴스 데이터 없음</p>", unsafe_allow_html=True)

        with nr:
            pos_c = sum(1 for n in news_data if n['sentiment']=='Positive')
            neg_c = sum(1 for n in news_data if n['sentiment']=='Negative')
            neu_c = sum(1 for n in news_data if n['sentiment']=='Neutral')
            if news_data:
                sf = go.Figure(go.Pie(
                    values=[pos_c, neg_c, neu_c], labels=["긍정","부정","중립"], hole=0.6,
                    marker=dict(colors=["#059669","#DC2626","#D1D5DB"],
                                line=dict(color="#FFFFFF",width=2)),
                    textfont=dict(family="Inter",size=11),
                ))
                sf.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                    legend=dict(font=dict(color="#6B7280",size=11),bgcolor="rgba(0,0,0,0)"),
                    margin=dict(t=0,b=0,l=0,r=0), height=180,
                    annotations=[dict(
                        text=f"<b>{news_bonus:+.0f}%</b>", x=0.5, y=0.5,
                        font=dict(size=18, color="#059669" if news_bonus>0 else "#DC2626", family="JetBrains Mono"),
                        showarrow=False
                    )]
                )
                st.plotly_chart(sf, use_container_width=True)

            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:14px;">
                <div style="font-size:10px;color:#9CA3AF;font-weight:500;
                            letter-spacing:1px;margin-bottom:10px;">SENTIMENT SCORE</div>
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:12px;color:#059669;">▲ 긍정</span>
                    <span style="font-size:12px;color:#059669;font-weight:600;">{pos_c}건</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:12px;color:#DC2626;">▼ 부정</span>
                    <span style="font-size:12px;color:#DC2626;font-weight:600;">{neg_c}건</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                    <span style="font-size:12px;color:#9CA3AF;">● 중립</span>
                    <span style="font-size:12px;color:#9CA3AF;font-weight:600;">{neu_c}건</span>
                </div>
                <div style="border-top:1px solid #E8EAED;padding-top:10px;
                            display:flex;justify-content:space-between;">
                    <span style="font-size:12px;color:#6B7280;">승률 보정</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700;
                                 color:{'#059669' if news_bonus>0 else '#DC2626' if news_bonus<0 else '#9CA3AF'};">
                        {news_bonus:+.1f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 4: 시나리오 시뮬레이션 ───────────────────────────────────
    with tab4:
        st.markdown(f"""
        <p style="font-size:13px;color:#6B7280;margin-bottom:16px;">
            {cfg['icon']} <b>{cfg['label']}</b> 섹터 지표를 직접 조정해서 승률 변화를 시뮬레이션합니다.
        </p>
        """, unsafe_allow_html=True)

        sim_l, sim_r = st.columns([1, 1])
        with sim_l:
            sim_inds = []
            for ind in inds:
                delta = st.slider(
                    f"{ind['name']} Z-Score",
                    -3.0, 3.0, float(ind["z"]), 0.1,
                    key=f"sim_{ind['ticker']}"
                )
                sim_inds.append({**ind, "z": delta})
            sim_news = st.slider("📰 뉴스 감성 보정(%)", -15.0, 15.0, float(news_bonus), 0.5)
            sim_win  = calc_win_rate(z_stock, sim_inds, sim_news)
            dw = sim_win - final_win
            sim_sig, sim_class, sim_color = get_signal(sim_win)

        with sim_r:
            dw_color = "#059669" if dw > 0 else "#DC2626" if dw < 0 else "#6B7280"
            st.markdown(f"""
            <div style="background:#FFFFFF;border:2px solid {sim_color};border-radius:10px;
                        padding:24px;text-align:center;margin-bottom:16px;">
                <div style="font-size:10px;color:#9CA3AF;font-weight:500;
                            letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">
                    시뮬레이션 승률
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:48px;
                            font-weight:700;color:{sim_color};line-height:1;">{sim_win}%</div>
                <div style="font-size:13px;margin-top:8px;font-weight:600;color:{dw_color};">
                    {'▲' if dw>0 else '▼' if dw<0 else '—'} 현재 대비 {dw:+.1f}%p
                </div>
                <div class="{sim_class}" style="margin-top:10px;display:inline-block;">{sim_sig}</div>
            </div>
            """, unsafe_allow_html=True)

            cmp = go.Figure(go.Bar(
                x=["현재 승률", "시뮬 승률"], y=[final_win, sim_win],
                marker=dict(
                    color=[sig_color, sim_color],
                    line=dict(color="#FFFFFF", width=1)
                ),
                text=[f"{final_win}%", f"{sim_win}%"],
                textfont=dict(family="JetBrains Mono", size=13, color="#1A1D23"),
                textposition="outside",
            ))
            cmp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont=dict(family="Inter",size=12,color="#6B7280")),
                yaxis=dict(showgrid=True, gridcolor="#F3F4F6", range=[0,105]),
                margin=dict(t=20,b=10,l=0,r=0), height=200
            )
            st.plotly_chart(cmp, use_container_width=True)
