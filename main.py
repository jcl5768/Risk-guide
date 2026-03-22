# main.py
import streamlit as st
from config import SECTOR_CONFIG, ETF_MAP
from engine import detect_sector, get_z_and_price, search_tickers, TICKER_NAME_MAP
from pages import apply_custom_style, render_main_page, render_detail_page

st.set_page_config(
    page_title="Risk Guide", page_icon="📊",
    layout="wide", initial_sidebar_state="collapsed"   # 모바일 친화적: 사이드바 기본 닫힘
)
apply_custom_style()


# ── 세션 초기화 (페이지 이동 시 portfolio 절대 초기화 안 함) ────────────────
def init_session():
    if "portfolio"    not in st.session_state: st.session_state.portfolio    = []
    if "page"         not in st.session_state: st.session_state.page         = "main"
    if "selected"     not in st.session_state: st.session_state.selected     = None
    if "editing"      not in st.session_state: st.session_state.editing      = None
    if "show_add"     not in st.session_state: st.session_state.show_add     = False
    if "chart_period" not in st.session_state: st.session_state.chart_period = "1달"

init_session()


# ── 사이드바 (포트폴리오 관리) ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 포트폴리오 관리")

    total_w = sum(s["weight"] for s in st.session_state.portfolio)
    bar_pct = min(total_w, 100)
    bar_clr = "#059669" if total_w <= 100 else "#DC2626"
    st.markdown(
        f'<div style="margin-bottom:12px;">'
        f'<div style="display:flex;justify-content:space-between;font-size:12px;'
        f'color:{bar_clr};margin-bottom:4px;">'
        f'<span>총 비중 {total_w:.1f}% {"✓" if total_w<=100 else "⚠ 초과"}</span>'
        f'<span>{len(st.session_state.portfolio)}개 종목</span></div>'
        f'<div style="height:5px;background:#E8EAED;border-radius:3px;">'
        f'<div style="height:100%;width:{bar_pct}%;background:{bar_clr};border-radius:3px;"></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    if not st.session_state.portfolio:
        st.markdown(
            '<div style="text-align:center;padding:14px 8px;color:#9CA3AF;font-size:12px;">'
            '📭 종목이 없습니다</div>',
            unsafe_allow_html=True
        )

    # 종목 목록
    for i, stock in enumerate(st.session_state.portfolio):
        sec = detect_sector(stock["ticker"])
        cfg = SECTOR_CONFIG[sec]

        if st.session_state.editing == i:
            st.markdown(f"**✏️ {stock['ticker']} 수정**")
            nn = st.text_input("종목명",       value=stock["name"],                          key=f"en_{i}")
            nw = st.number_input("비중(%)",     value=float(stock["weight"]),
                                 min_value=0.1, max_value=100.0, step=0.1, format="%.1f",   key=f"ew_{i}")
            ns = st.number_input("수량(주)",    value=float(stock.get("shares", 1)),
                                 min_value=0.01, max_value=1000000.0, step=0.01, format="%.2f", key=f"es_{i}")
            na = st.number_input("평균단가($)", value=float(stock["avg_price"]),
                                 min_value=1.0, max_value=999999.0, format="%.2f",           key=f"ea_{i}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 저장", key=f"save_{i}", use_container_width=True):
                    st.session_state.portfolio[i].update(
                        {"name": nn, "weight": round(nw,1), "shares": round(ns,2), "avg_price": na}
                    )
                    st.session_state.editing = None; st.rerun()
            with c2:
                if st.button("✕ 취소", key=f"cancel_{i}", use_container_width=True):
                    st.session_state.editing = None; st.rerun()
        else:
            _, cur_price = get_z_and_price(stock["ticker"])
            pnl = ((cur_price - stock["avg_price"]) / stock["avg_price"] * 100) \
                  if cur_price and stock["avg_price"] > 0 else None
            pnl_str = f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "—"
            pnl_clr = "#059669" if (pnl or 0) >= 0 else "#DC2626"
            shares  = stock.get("shares", 0)
            value   = f"${cur_price * shares:,.0f}" if cur_price and shares else "—"

            st.markdown(
                f'<div style="padding:8px 0;">'
                f'<div style="display:flex;justify-content:space-between;">'
                f'<div><b style="font-size:14px;">{stock["ticker"]}</b>'
                f' <span style="color:{cfg["color"]};font-size:11px;">{cfg["icon"]}</span>'
                f'<div style="font-size:10px;color:#9CA3AF;">{stock["name"]}</div></div>'
                f'<div style="text-align:right;">'
                f'<div style="font-weight:700;color:#2563EB;">{stock["weight"]:.1f}%</div>'
                f'<div style="font-size:10px;color:{pnl_clr};">{pnl_str}</div>'
                f'</div></div>'
                f'<div style="font-size:10px;color:#9CA3AF;margin-top:2px;">'
                f'${cur_price:.1f} · {shares}주 · 평가 {value}</div></div>',
                unsafe_allow_html=True
            )
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("✏️ 수정", key=f"edit_{i}", use_container_width=True):
                    st.session_state.editing = i; st.rerun()
            with cb2:
                if st.button("🗑 삭제", key=f"del_{i}", use_container_width=True):
                    st.session_state.portfolio.pop(i)
                    if st.session_state.editing == i: st.session_state.editing = None
                    st.rerun()

        st.markdown("<hr style='margin:6px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("⚙️ 설정"):
        if st.button("🔄 전체 초기화", use_container_width=True):
            st.session_state.portfolio = []; st.session_state.editing = None; st.rerun()


# ── 종목 추가 오버레이 (메인 영역에 표시) ─────────────────────────────────────
def render_add_stock():
    """종목 검색 → 선택 → 입력 → 추가 플로우 (단일 검색창, 종목명 입력 제거)"""
    st.markdown("### 🔍 종목 추가")
    st.markdown("---")

    # 통합 검색창 하나만
    query = st.text_input(
        "",
        placeholder="예: AAPL, Apple, 반도체, 나스닥…",
        key="add_search",
        label_visibility="collapsed"
    ).strip()

    sel_ticker = st.session_state.get("_add_ticker", "")
    sel_name   = st.session_state.get("_add_name",   "")
    sel_price  = st.session_state.get("_add_price",  0.0)

    # 연관 검색 결과
    if query:
        suggestions = search_tickers(query)
        if suggestions:
            st.markdown(
                '<div style="font-size:11px;color:#9CA3AF;margin:8px 0 4px;">연관 종목</div>',
                unsafe_allow_html=True
            )
            for sg in suggestions:
                cfg2 = SECTOR_CONFIG.get(sg["sector"], SECTOR_CONFIG["Unknown"])
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    if st.button(sg["ticker"], key=f"pick_{sg['ticker']}", use_container_width=True):
                        _, px = get_z_and_price(sg["ticker"])
                        st.session_state["_add_ticker"] = sg["ticker"]
                        st.session_state["_add_name"]   = sg["name"]
                        st.session_state["_add_price"]  = px
                        st.rerun()
                with col_b:
                    st.markdown(
                        f'<div style="padding:5px 0;font-size:12px;">'
                        f'<b>{sg["name"]}</b>'
                        f' <span style="color:{cfg2["color"]};font-size:11px;">'
                        f'{cfg2["icon"]} {cfg2["sector_label"]}</span></div>',
                        unsafe_allow_html=True
                    )
        elif len(query) >= 1:
            # 직접 티커로 시도
            sel_ticker = query.upper()
            _, px2 = get_z_and_price(sel_ticker)
            sel_name  = TICKER_NAME_MAP.get(sel_ticker, sel_ticker)
            sel_price = px2

    # 선택된 종목 미리보기
    if sel_ticker:
        sec3 = detect_sector(sel_ticker)
        cfg3 = SECTOR_CONFIG.get(sec3, SECTOR_CONFIG["Unknown"])
        st.markdown(
            f'<div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:10px;'
            f'padding:14px 16px;margin:12px 0;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<div style="font-size:18px;font-weight:700;color:#1A1D23;">{sel_ticker}</div>'
            f'<div style="font-size:12px;color:#6B7280;">{sel_name}</div>'
            f'<div style="font-size:11px;color:{cfg3["color"]};margin-top:2px;">'
            f'{cfg3["icon"]} {cfg3["label"]}</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:22px;font-weight:700;color:#1A1D23;">${sel_price:.2f}</div>'
            f'<div style="font-size:10px;color:#059669;">현재가 ✓</div>'
            f'</div></div></div>',
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # 입력 폼 — 종목명 입력칸 없음 (자동 설정됨)
        col1, col2 = st.columns(2)
        with col1:
            nw = st.number_input("비중(%)",   min_value=0.1, max_value=100.0,
                                 value=10.0, step=0.1, format="%.1f", key="add_nw")
        with col2:
            ns = st.number_input("수량(주)",  min_value=0.01, max_value=1000000.0,
                                 value=1.0, step=0.01, format="%.2f", key="add_ns")   # ← 소수점 허용

        na = st.number_input(
            "평균단가($)", min_value=1.0, max_value=999999.0,
            value=max(1.0, round(float(sel_price), 2)),
            format="%.2f", key="add_na"
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 추가하기", key="confirm_add", use_container_width=True, type="primary"):
                st.session_state.portfolio.append({
                    "ticker":    sel_ticker,
                    "name":      sel_name or sel_ticker,
                    "weight":    round(nw, 1),
                    "shares":    round(ns, 2),
                    "avg_price": na,
                })
                # 임시 상태 정리
                for k in ("_add_ticker", "_add_name", "_add_price"):
                    st.session_state.pop(k, None)
                st.session_state.show_add = False
                st.rerun()
        with c2:
            if st.button("✕ 취소", key="cancel_add", use_container_width=True):
                for k in ("_add_ticker", "_add_name", "_add_price"):
                    st.session_state.pop(k, None)
                st.session_state.show_add = False
                st.rerun()
    else:
        # 아직 미선택
        if st.button("✕ 닫기", key="cancel_add_empty", use_container_width=True):
            st.session_state.show_add = False
            st.rerun()


# ── 라우팅 ─────────────────────────────────────────────────────────────────────
if st.session_state.show_add:
    render_add_stock()
elif st.session_state.page == "main":
    render_main_page()
elif st.session_state.page == "detail":
    render_detail_page()
