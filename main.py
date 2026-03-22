st.error("신규 코드 반영 테스트 중!") 

# main.py
import streamlit as st
from config import SECTOR_CONFIG, ETF_MAP
from engine import detect_sector, get_z_and_price, search_tickers, TICKER_NAME_MAP
from pages import apply_custom_style, render_main_page, render_detail_page

st.set_page_config(
    page_title="Risk Guide", page_icon="📊",
    layout="wide", initial_sidebar_state="expanded"
)
apply_custom_style()

# ── 세션 초기화 — 페이지 이동 시에도 portfolio 절대 초기화 안 함 ──────────────
def init_session():
    if "portfolio"     not in st.session_state: st.session_state.portfolio     = []
    if "page"          not in st.session_state: st.session_state.page          = "main"
    if "selected"      not in st.session_state: st.session_state.selected      = None
    if "editing"       not in st.session_state: st.session_state.editing       = None
    if "show_add"      not in st.session_state: st.session_state.show_add      = False
    if "chart_period"  not in st.session_state: st.session_state.chart_period  = "1달"

init_session()

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 내 포트폴리오")

    # 비중 프로그레스 바
    total_w = sum(s["weight"] for s in st.session_state.portfolio)
    bar_pct  = min(total_w, 100)
    bar_clr  = "#059669" if total_w <= 100 else "#DC2626"
    st.markdown(
        f'<div style="margin-bottom:12px;">'
        f'<div style="display:flex;justify-content:space-between;font-size:12px;color:{bar_clr};margin-bottom:4px;">'
        f'<span>총 비중 {total_w:.1f}% {"✓" if total_w<=100 else "⚠ 초과"}</span>'
        f'<span>{len(st.session_state.portfolio)}개 종목</span></div>'
        f'<div style="height:5px;background:#E8EAED;border-radius:3px;">'
        f'<div style="height:100%;width:{bar_pct}%;background:{bar_clr};border-radius:3px;"></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    # 종목 없을 때 안내
    if not st.session_state.portfolio:
        st.markdown(
            '<div style="text-align:center;padding:14px 8px;color:#9CA3AF;font-size:12px;'
            'background:#F9FAFB;border-radius:8px;margin-bottom:10px;">'
            '📭 아직 종목이 없어요<br>'
            '<span style="font-size:11px;">아래에서 추가해보세요</span></div>',
            unsafe_allow_html=True
        )

    # ── 종목 목록 ────────────────────────────────────────────────────────
    for i, stock in enumerate(st.session_state.portfolio):
        sec = detect_sector(stock["ticker"])
        cfg = SECTOR_CONFIG[sec]

        if st.session_state.editing == i:
            st.markdown(f"**✏️ {stock['ticker']} 수정**")
            nw = st.number_input("비중(%)",     value=float(stock["weight"]), min_value=0.1, max_value=100.0, step=0.1, format="%.1f",   key=f"ew_{i}")
            ns = st.number_input("수량(주)",    value=float(stock.get("shares", 1)), min_value=0.001, max_value=float(1000000), step=0.001, format="%.3f", key=f"es_{i}")
            na = st.number_input("평균단가($)", value=float(stock["avg_price"]), min_value=0.0001, max_value=999999.0, format="%.4f", key=f"ea_{i}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 저장", key=f"save_{i}", use_container_width=True):
                    st.session_state.portfolio[i].update({"weight": round(nw, 1), "shares": round(ns, 3), "avg_price": na})
                    st.session_state.editing = None
                    st.rerun()
            with c2:
                if st.button("✕ 취소", key=f"cancel_{i}", use_container_width=True):
                    st.session_state.editing = None
                    st.rerun()
        else:
            _, cur_price = get_z_and_price(stock["ticker"])
            pnl = ((cur_price - stock["avg_price"]) / stock["avg_price"] * 100) if cur_price and stock["avg_price"] > 0 else None
            pnl_str = f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "—"
            pnl_clr = "#059669" if (pnl or 0) >= 0 else "#DC2626"
            value_str = f"${cur_price * stock.get('shares', 0):,.0f}" if cur_price and stock.get("shares") else "—"

            st.markdown(
                f'<div style="padding:8px 0;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><span style="font-weight:700;font-size:14px;color:#1A1D23;">{stock["ticker"]}</span>'
                f' <span style="font-size:11px;color:{cfg["color"]};">{cfg["icon"]}</span>'
                f'<div style="font-size:10px;color:#9CA3AF;">{stock["name"]}</div></div>'
                f'<div style="text-align:right;">'
                f'<div style="font-weight:700;font-size:14px;color:#2563EB;">{stock["weight"]:.1f}%</div>'
                f'<div style="font-size:10px;color:{pnl_clr};">{pnl_str}</div>'
                f'</div></div>'
                f'<div style="display:flex;justify-content:space-between;font-size:10px;color:#9CA3AF;margin-top:2px;">'
                f'<span>${cur_price:.1f} · {stock.get("shares",0)}주</span>'
                f'<span>평가 {value_str}</span></div></div>',
                unsafe_allow_html=True
            )
            cb1, cb2 = st.columns([1, 1])
            with cb1:
                if st.button("✏️ 수정", key=f"edit_{i}", use_container_width=True):
                    st.session_state.editing = i
                    st.rerun()
            with cb2:
                if st.button("🗑 삭제", key=f"del_{i}", use_container_width=True):
                    st.session_state.portfolio.pop(i)
                    if st.session_state.editing == i:
                        st.session_state.editing = None
                    st.rerun()

        st.markdown("<hr style='margin:6px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)

    # ── 통합 종목 검색 & 추가 (연속 추가 가능하도록 수정) ─────────────────
    if st.button("➕  종목 추가", use_container_width=True, key="toggle_add"):
        st.session_state.show_add = not st.session_state.show_add

    if st.session_state.show_add:
        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px;">🔍 종목 검색</div>',
            unsafe_allow_html=True
        )

        query = st.text_input("티커 또는 종목명", placeholder="예: AAPL, Apple...", key="search_q", label_visibility="collapsed").strip()
        sel_ticker, sel_name, sel_price = "", "", 0.0

        if query:
            suggestions = search_tickers(query)
            if suggestions:
                options = ["선택하세요…"] + [f"{sg['ticker']}  —  {sg['name']}  {sg['sector_icon']}" for sg in suggestions]
                chosen = st.selectbox("연관 종목", options=options, key="sg_select", label_visibility="collapsed")
                if chosen != "선택하세요…":
                    sel_ticker = chosen.split("  —  ")[0].strip()
                    sel_name   = TICKER_NAME_MAP.get(sel_ticker, sel_ticker)
                    _, sel_price = get_z_and_price(sel_ticker)
            else:
                sel_ticker = query.upper().strip()
                _, sel_price = get_z_and_price(sel_ticker)
                sel_name = TICKER_NAME_MAP.get(sel_ticker, sel_ticker)

        final_ticker, auto_name, auto_price = sel_ticker, sel_name, sel_price

        st.markdown("---")
        nw = st.number_input("비중(%)", min_value=0.1, max_value=100.0, value=10.0, step=0.1, format="%.1f", key="add_w")
        ns = st.number_input("수량(주)", min_value=0.001, max_value=float(1000000), value=1.0, step=0.001, format="%.3f", key="add_s")
        na = st.number_input("평균단가($)", min_value=0.0001, max_value=999999.0, value=max(0.0001, round(float(auto_price), 4)) if auto_price else 1.0, format="%.4f", key="add_a")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 추가", key="do_add", use_container_width=True):
                if final_ticker:
                    st.session_state.portfolio.append({
                        "ticker":    final_ticker,
                        "name":      auto_name or final_ticker,
                        "weight":    round(nw, 1),
                        "shares":    round(ns, 3),
                        "avg_price": na,
                    })
                    # show_add = False를 제거하여 종목 추가 후에도 창이 유지되도록 함
                    st.rerun()
        with c2:
            if st.button("✕ 닫기", key="close_add", use_container_width=True):
                st.session_state.show_add = False
                st.rerun()

    st.markdown("---")
    with st.expander("⚙️ 설정"):
        if st.button("🔄 전체 초기화", use_container_width=True):
            st.session_state.portfolio = []
            st.session_state.editing   = None
            st.rerun()
        st.markdown('<div style="font-size:11px;color:#9CA3AF;margin-top:8px;line-height:1.6;">세션 종료 시 포트폴리오가 초기화됩니다.</div>', unsafe_allow_html=True)

if st.session_state.page == "main":
    render_main_page()
elif st.session_state.page == "detail":
    render_detail_page()
