import streamlit as st
from app_logic import *
from app_ui import *

st.set_page_config(page_title="Pro Investor Hub", layout="wide")
apply_custom_style()

# 세션 상태 관리 (데이터 유지)
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"ticker": "NVDA", "weight": 23, "avg_price": 120.0},
        {"ticker": "TSLA", "weight": 7, "avg_price": 180.0}
    ]
if 'page' not in st.session_state: st.session_state.page = 'main'
if 'selected' not in st.session_state: st.session_state.selected = None

# --- 사이드바 ---
with st.sidebar:
    st.title("💼 My Wallet")
    for i, s in enumerate(st.session_state.portfolio):
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{s['ticker']}** ({s['weight']}%)")
        if col2.button("🗑️", key=f"del_{i}"):
            st.session_state.portfolio.pop(i)
            st.rerun()
    
    with st.expander("➕ 종목 추가"):
        t = st.text_input("티커").upper()
        w = st.number_input("비중", 1, 100, 10)
        p = st.number_input("평단가", 0.0)
        if st.button("포트폴리오에 추가"):
            st.session_state.portfolio.append({"ticker":t, "weight":w, "avg_price":p})
            st.rerun()

# --- 메인 화면 로직 ---
if st.session_state.page == 'main':
    st.header("📊 마켓 대시보드")
    m_cols = st.columns(3)
    for i, (l, t) in enumerate([("S&P 500", "^GSPC"), ("나스닥", "^IXIC"), ("공포지수", "^VIX")]):
        z, p = get_z_and_price(t)
        m_cols[i].markdown(f'<div class="macro-card"><small>{l}</small><h3>${p:,.2f}</h3></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔎 보유 종목 실시간 분석")
    p_cols = st.columns(2)
    for i, s in enumerate(st.session_state.portfolio):
        with p_cols[i % 2]:
            z, price = get_z_and_price(s['ticker'])
            sec, cfg, inds = get_sector_analysis(s['ticker'])
            ns, nd = get_news(s['ticker'])
            wr, exp = calc_win_rate(z, inds, ns)
            txt, b_cls, clr = get_signal_ui(wr)
            
            st.markdown(f"""
            <div class="stock-card" style="border-left: 5px solid {clr}">
                <div style="display:flex; justify-content:space-between;">
                    <span><b>{s['ticker']}</b> {cfg['icon']}</span>
                    <span class="{b_cls}">{txt}</span>
                </div>
                <h2 style="color:{clr}">{wr}%</h2>
                <small>{exp}</small>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{s['ticker']} 상세 리포트 보기", key=f"btn_{i}"):
                st.session_state.selected = s['ticker']
                st.session_state.page = 'detail'
                st.rerun()

elif st.session_state.page == 'detail':
    # 상세 페이지 코드 (뉴스 리스트 포함)
    target = st.session_state.selected
    if st.button("⬅️ 돌아가기"):
        st.session_state.page = 'main'
        st.rerun()
    
    st.title(f"🔍 {target} 정밀 분석 리포트")
    ns, nd = get_news(target)
    for n in nd:
        st.info(f"📰 {n['title']} (감성: {n['sentiment']})")
