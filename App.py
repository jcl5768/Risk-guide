
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════
# 1. 페이지 설정 & 화이트 테마 스타일 (기존 코드 유지)
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Risk Guide",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* CSS 스타일 생략 (사용자가 제공한 스타일과 동일) */
.stApp { background:#F7F8FA; color:#1A1D23; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 2. 섹터 및 지표 설정 (기존 데이터 유지)
# ═══════════════════════════════════════════════════════════════════════════
SECTOR_CONFIG = {
    "Energy": {
        "icon":"🛢️", "color":"#D97706", "label":"에너지",
        "indicators":[
            {"name":"WTI 유가",    "ticker":"CL=F",     "weight":+12},
            {"name":"달러 인덱스", "ticker":"DX-Y.NYB",  "weight":-4},
        ]
    },
    "Consumer Defensive": {
        "icon":"🛒", "color":"#059669", "label":"필수소비재",
        "indicators":[
            {"name":"CPI 인플레",  "ticker":"RINF",      "weight":-8},
            {"name":"VIX",         "ticker":"^VIX",      "weight":+5},
        ]
    },
    # ... 다른 섹터 생략 (사용자 원본 데이터 참조)
}

ETF_MAP = {
    "XLE":"Energy", "XOM":"Energy", "CVX":"Energy",
    "XLP":"Consumer Defensive", "PG":"Consumer Defensive",
    "VOO":"Unknown", "GOOGL":"Technology", "TSLA":"Consumer Cyclical"
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. 핵심 함수: 데이터 로드 및 리스크 계산
# ═══════════════════════════════════════════════════════════════════════════

def get_market_data(ticker):
    """KeyError: 'Date' 방지를 위해 reset_index() 적용"""
    try:
        data = yf.download(ticker, period="5d", interval="1d", progress=False)
        if data.empty: return None
        # 데이터프레임 구조를 평탄화하여 'Date'를 일반 컬럼으로 변환
        data = data.reset_index()
        return data
    except:
        return None

def calculate_risk_score(ticker, sector_name):
    """거시 지표 변화율에 따른 리스크 점수 계산"""
    config = SECTOR_CONFIG.get(sector_name, SECTOR_CONFIG["Unknown"])
    total_score = 50  # 기본 점수 (중립)
    
    for ind in config.get("indicators", []):
        df = get_market_data(ind["ticker"])
        if df is not None and len(df) >= 2:
            # 최근 2거래일 종가 기준 변화율 계산
            change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
            total_score += float(change * ind["weight"])
            
    return max(0, min(100, total_score)) # 0~100 사이로 제한

# ═══════════════════════════════════════════════════════════════════════════
# 4. 메인 화면: 내 포트폴리오 리스크 가이드
# ═══════════════════════════════════════════════════════════════════════════

st.title("📊 My Risk Guide")

# 사용자 실제 포트폴리오 데이터
my_portfolio = [
    {"name": "Energy Sector", "ticker": "XOM", "weight": 23, "sector": "Energy"},
    {"name": "Consumer Defensive", "ticker": "PG", "weight": 7, "sector": "Consumer Defensive"},
    {"name": "Core Holdings (VOO/TSLA/GOOG)", "ticker": "VOO", "weight": 60, "sector": "Unknown"}
]

cols = st.columns(len(my_portfolio))

for i, stock in enumerate(my_portfolio):
    with cols[i]:
        risk = calculate_risk_score(stock["ticker"], stock["sector"])
        
        # 리스크 등급 결정
        if risk < 40: status, color = "리스크 낮음", "green"
        elif risk < 70: status, color = "중립 관망", "yellow"
        else: status, color = "리스크 경고", "red"
        
        st.markdown(f"""
        <div class="stock-card">
            <div class="macro-label">{stock['name']} ({stock['weight']}%)</div>
            <div class="macro-value">{risk:.1f} pts</div>
            <div class="badge-{color}">{status}</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 5. 상세 차트 (예시: 에너지 섹터)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("### 📈 Sector Detail: Energy (23%)")
energy_data = get_market_data("XOM")

if energy_data is not None:
    fig = go.Figure(data=[go.Scatter(x=energy_data['Date'], y=energy_data['Close'], line=dict(color='#D97706'))])
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
