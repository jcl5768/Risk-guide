# main.py
import streamlit as st
from config import *
from engine import *
from pages import *

# 페이지 기본 설정
st.set_page_config(page_title="Risk Guide", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
apply_custom_style()

# 세션 상태 초기화
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

# 사이드바 (포트폴리오 관리)
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
            ns = st.number_input("수량(주)",    value=int(stock.get('shares', 10)),      min_value=1,   max_value=100000, key=f"es_{i}")
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
    if st.button("🔄 전체 초기화", use_container_width=True):
        st.session_state.portfolio = []
        st.session_state.editing = None
        st.rerun()

# 메인 라우팅 (페이지 이동)
if st.session_state.page == 'main':
    render_main_page()
elif st.session_state.page == 'detail':
    render_detail_page()
