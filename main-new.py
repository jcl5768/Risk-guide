import streamlit as st
from config import SECTOR_CONFIG, ETF_MAP
from engine import detect_sector, get_z_and_price, search_tickers, TICKER_NAME_MAP
from pages import apply_custom_style, render_main_page, render_detail_page

st.set_page_config(page_title="Risk Guide", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
apply_custom_style()

def init_session():
    if "portfolio" not in st.session_state: st.session_state.portfolio = []
    if "page" not in st.session_state: st.session_state.page = "main"
    if "selected" not in st.session_state: st.session_state.selected = None
    if "editing" not in st.session_state: st.session_state.editing = None
    if "show_add" not in st.session_state: st.session_state.show_add = True # 처음부터 켜둠
    if "chart_period" not in st.session_state: st.session_state.chart_period = "1달"

init_session()

# 사이드바 로직
with st.sidebar:
    st.markdown("### 📂 내 포트폴리오")
    # (종목 리스트 출력 로직...)
    for i, stock in enumerate(st.session_state.portfolio):
        st.write(f"**{stock['ticker']}** - {stock['weight']}%")
        if st.button("🔍 상세", key=f"det_{i}"):
            st.session_state.selected = stock["ticker"]
            st.session_state.page = "detail"
            st.rerun()
    
    st.markdown("---")
    # ── 종목 추가 입력창 (항상 표시되도록 고정) ──
    st.markdown("### ➕ 종목 추가")
    q = st.text_input("종목 검색", key="search_q")
    if q:
        sgs = search_tickers(q)
        if sgs:
            sel = st.selectbox("결과 선택", [f"{s['ticker']} - {s['name']}" for s in sgs])
            ticker_only = sel.split(" - ")[0]
            nw = st.number_input("비중", value=10.0)
            if st.button("포트폴리오에 추가"):
                st.session_state.portfolio.append({"ticker": ticker_only, "name": ticker_only, "weight": nw, "avg_price":0, "shares":0})
                # 여기서 False로 만드는 로직을 삭제함 -> 창이 계속 열려 있음
                st.rerun()

if st.session_state.page == "main": render_main_page()
elif st.session_state.page == "detail": render_detail_page()
