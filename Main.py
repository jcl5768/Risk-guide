import streamlit as st
import plotly.graph_objects as go
from app_logic import *
from app_ui import *

st.set_page_config(page_title="Risk Guide", page_icon="📊", layout="wide")
apply_custom_style()

# 세션 초기화
if 'portfolio' not in st.session_state: st.session_state.portfolio = []
if 'page' not in st.session_state: st.session_state.page = 'main'
if 'selected' not in st.session_state: st.session_state.selected = None

# --- 사이드바 ---
with st.sidebar:
    st.title("📂 포트폴리오")
    # 간단한 추가 로직
    with st.expander("➕ 종목 추가"):
        t = st.text_input("티커(예: AAPL)").upper()
        w = st.number_input("비중(%)", 0, 100, 10)
        a = st.number_input("평단가($)", 0.0)
        if st.button("추가하기"):
            st.session_state.portfolio.append({"ticker":t, "weight":w, "avg_price":a, "name":t})
            st.rerun()
    
    if st.button("🔄 전체 초기화"):
        st.session_state.portfolio = []
        st.rerun()

# --- 메인 화면 ---
if st.session_state.page == 'main':
    st.header("📊 대시보드")
    
    if not st.session_state.portfolio:
        st.info("왼쪽에서 종목을 추가해주세요.")
    else:
        cols = st.columns(min(len(st.session_state.portfolio), 4))
        for i, stock in enumerate(st.session_state.portfolio):
            with cols[i % 4]:
                z, price = get_z_and_price(stock['ticker'])
                sk, cfg, inds = get_sector_analysis(stock['ticker'])
                nb, _ = get_news(stock['ticker'])
                win, _ = calc_win_rate(z, inds, nb)
                msg, badge, color = get_signal_ui(win)
                
                st.markdown(f"""
                <div class="stock-card" style="border-top:3px solid {color};">
                    <h4>{stock['ticker']} {cfg['icon']}</h4>
                    <h2 style="color:{color}">{win}%</h2>
                    <div class="{badge}">{msg}</div>
                    <p style="font-size:12px; margin-top:10px;">현재가: ${price}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"{stock['ticker']} 상세", key=f"btn_{i}"):
                    st.session_state.selected = stock['ticker']
                    st.session_state.page = 'detail'
                    st.rerun()

elif st.session_state.page == 'detail':
    target = st.session_state.selected
    if st.button("← 돌아가기"):
        st.session_state.page = 'main'
        st.rerun()
    st.subheader(f"🔍 {target} 상세 분석")
    # 상세 분석 로직...
