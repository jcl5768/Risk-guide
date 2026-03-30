# main.py
import streamlit as st
import json
from config import SECTOR_CONFIG, ETF_MAP
from engine import detect_sector, get_z_and_price, search_tickers, TICKER_NAME_MAP
from pages import apply_custom_style, render_main_page, render_detail_page

st.set_page_config(
    page_title="Signum", page_icon="🔭",
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
    if "chart_period"  not in st.session_state: st.session_state.chart_period  = "1개월"
    if "open_sidebar"  not in st.session_state: st.session_state.open_sidebar  = False
    if "invest_mode"   not in st.session_state: st.session_state.invest_mode   = "단기"

init_session()


# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 내 포트폴리오")

    # open_sidebar 플래그 → 검색창 자동 열기
    if st.session_state.get("open_sidebar"):
        st.session_state.show_add    = True
        st.session_state.open_sidebar = False

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
            # 수정 모드
            st.markdown(f"**✏️ {stock['ticker']} 수정**")
            nw = st.number_input("비중(%)",     value=float(stock["weight"]),
                                 min_value=0.1, max_value=100.0, step=0.1, format="%.1f",   key=f"ew_{i}")
            ns = st.number_input("수량(주)",    value=float(stock.get("shares", 1)),
                                 min_value=0.001, max_value=float(1000000),
                                 step=1.0, format="%g",                                      key=f"es_{i}")
            na = st.number_input("평균단가($)", value=float(stock["avg_price"]),
                                 min_value=0.01, max_value=999999.0, step=1.0, format="%g",  key=f"ea_{i}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 저장", key=f"save_{i}", use_container_width=True):
                    st.session_state.portfolio[i].update(
                        {"weight": round(nw, 1), "shares": round(ns, 3), "avg_price": na}
                    )
                    st.session_state.editing = None
                    st.rerun()
            with c2:
                if st.button("✕ 취소", key=f"cancel_{i}", use_container_width=True):
                    st.session_state.editing = None
                    st.rerun()

        else:
            # 일반 표시
            _, cur_price = get_z_and_price(stock["ticker"])
            pnl = ((cur_price - stock["avg_price"]) / stock["avg_price"] * 100) \
                  if cur_price and stock["avg_price"] > 0 else None
            pnl_str = f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "—"
            pnl_clr = "#059669" if (pnl or 0) >= 0 else "#DC2626"
            value_str = f"${cur_price * stock.get('shares', 0):,.0f}" \
                        if cur_price and stock.get("shares") else "—"

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
                f'<div style="display:flex;justify-content:space-between;font-size:10px;'
                f'color:#9CA3AF;margin-top:2px;">'
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

    # ── 통합 종목 검색 & 추가 ────────────────────────────────────────────
    if st.button("➕  종목 추가", use_container_width=True, key="toggle_add"):
        st.session_state.show_add = not st.session_state.show_add

    if st.session_state.show_add:
        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px;">'
            '🔍 종목 검색</div>',
            unsafe_allow_html=True
        )

        # ── 통합 검색창: 티커 + 종목명 동시 검색 ────────────────────────
        query = st.text_input(
            "티커 또는 종목명",
            placeholder="예: AAPL, Apple, 반도체, 나스닥…",
            key="search_q",
            label_visibility="collapsed"
        ).strip()

        # 연관 검색 결과 → selectbox로 통합
        sel_ticker = ""
        sel_name   = ""
        sel_price  = 0.0

        if query:
            suggestions = search_tickers(query)
            if suggestions:
                # selectbox 옵션: "TICKER — 종목명 (섹터)" 형식
                options = ["선택하세요…"] + [
                    f"{sg['ticker']}  —  {sg['name']}  {sg['sector_icon']}"
                    for sg in suggestions
                ]
                chosen = st.selectbox(
                    "연관 종목",
                    options=options,
                    key="sg_select",
                    label_visibility="collapsed"
                )
                if chosen != "선택하세요…":
                    # 선택된 티커 추출
                    sel_ticker = chosen.split("  —  ")[0].strip()
                    sel_name   = TICKER_NAME_MAP.get(sel_ticker, sel_ticker)
                    _, sel_price = get_z_and_price(sel_ticker)

                    # 미리보기 카드
                    sec2  = detect_sector(sel_ticker)
                    cfg2  = SECTOR_CONFIG.get(sec2, SECTOR_CONFIG["Unknown"])
                    st.markdown(
                        f'<div style="background:#F0FDF4;border:1px solid #A7F3D0;'
                        f'border-radius:8px;padding:10px 12px;margin:6px 0;font-size:12px;">'
                        f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                        f'<span style="font-weight:700;color:#1A1D23;">{sel_ticker} — {sel_name}</span>'
                        f'<span style="color:#059669;font-size:10px;">선택됨 ✓</span></div>'
                        f'<div style="color:#6B7280;">{cfg2["icon"]} {cfg2["label"]}'
                        f' · 현재가 <b>${sel_price:.2f}</b></div></div>',
                        unsafe_allow_html=True
                    )
            else:
                # 검색 결과 없음 → 티커 직접 시도
                st.markdown(
                    f'<div style="font-size:11px;color:#D97706;padding:4px 0;">'
                    f'"{query}" — ETF_MAP에 없음. 직접 티커로 추가합니다.</div>',
                    unsafe_allow_html=True
                )
                sel_ticker = query.upper().strip()
                _, sel_price = get_z_and_price(sel_ticker)
                sel_name = TICKER_NAME_MAP.get(sel_ticker, sel_ticker)

        # 최종 티커 / 이름 / 가격 결정
        final_ticker = sel_ticker
        auto_name    = sel_name
        auto_price   = sel_price

        st.markdown("---")

        # 입력 폼 (종목명 자동 처리 — 텍스트박스 없음)
        nw = st.number_input(
            "비중(%)",
            min_value=0.1, max_value=100.0,
            value=10.0, step=0.1, format="%.1f",
            key="add_w"
        )
        ns = st.number_input(
            "수량(주)",
            min_value=0.001, max_value=float(1000000),
            value=1.0, step=1.0, format="%g",
            key="add_s"
        )
        na = st.number_input(
            "평균단가($)",
            min_value=0.01, max_value=999999.0,
            value=max(1.0, round(float(auto_price), 2)) if auto_price else 1.0,
            step=1.0, format="%g",
            key="add_a",
            help="현재가로 자동 입력됩니다. 직접 수정 가능"
        )

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
                    # 검색창·선택값 완전 초기화
                    for k in ("_sel_ticker", "_sel_name", "search_q", "sg_select",
                              "add_w", "add_s", "add_a"):
                        st.session_state.pop(k, None)
                    st.rerun()
        with c2:
            if st.button("✕ 닫기", key="close_add", use_container_width=True):
                st.session_state.show_add = False
                for k in ("_sel_ticker", "_sel_name"):
                    st.session_state.pop(k, None)
                st.rerun()

    st.markdown("---")
    with st.expander("⚙️ 설정"):
        # ── 투자 모드 선택 ──────────────────────────────────────────
        mode_options = ["단기", "스윙", "장기"]
        mode_desc = {
            "단기": "수일~수주 · 타점·리스크 경고 중심",
            "스윙": "수주~수개월 · 균형 분석",
            "장기": "수개월~수년 · 모멘텀·추세 중심",
        }
        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px;">'
            '📐 투자 기간 모드</div>',
            unsafe_allow_html=True
        )
        cur_idx = mode_options.index(st.session_state.get("invest_mode", "단기"))
        selected_mode = st.radio(
            "투자 모드",
            options=mode_options,
            index=cur_idx,
            horizontal=True,
            label_visibility="collapsed",
            key="mode_radio"
        )
        if selected_mode != st.session_state.get("invest_mode", "단기"):
            st.session_state.invest_mode = selected_mode
            st.rerun()
        st.markdown(
            f'<div style="font-size:10px;color:#6B7280;padding:2px 0 10px;">'
            f'{mode_desc[st.session_state.get("invest_mode","단기")]}</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")

        # ── 포트폴리오 저장 (인라인 방식) ───────────────────────────────
        if st.session_state.portfolio:
            portfolio_json = json.dumps(
                st.session_state.portfolio, ensure_ascii=False, indent=2
            )
            st.markdown(
                '<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:4px;">💾 포트폴리오 저장</div>'
                '<div style="font-size:11px;color:#6B7280;margin-bottom:6px;">아래 텍스트를 전체 복사해서 메모장에 저장하세요</div>',
                unsafe_allow_html=True
            )
            st.text_area(
                "저장 데이터",
                value=portfolio_json,
                height=120,
                key="export_json",
                label_visibility="collapsed",
                help="전체 선택(Ctrl+A) 후 복사(Ctrl+C)하여 저장"
            )
        else:
            st.markdown(
                '<div style="font-size:11px;color:#9CA3AF;text-align:center;'
                'padding:6px 0;">종목 추가 후 저장 가능합니다</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ── 포트폴리오 불러오기 (인라인 방식) ──────────────────────────
        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:4px;">📂 포트폴리오 불러오기</div>'
            '<div style="font-size:11px;color:#6B7280;margin-bottom:6px;">저장해둔 텍스트를 아래에 붙여넣고 불러오기를 누르세요</div>',
            unsafe_allow_html=True
        )
        import_text = st.text_area(
            "불러오기 데이터",
            placeholder='저장한 JSON 텍스트를 여기에 붙여넣으세요…',
            height=100,
            key="import_json",
            label_visibility="collapsed"
        )
        if st.button("📂 불러오기", use_container_width=True, key="do_import"):
            if import_text.strip():
                try:
                    loaded = json.loads(import_text.strip())
                    if isinstance(loaded, list) and len(loaded) > 0:
                        st.session_state.portfolio = loaded
                        st.session_state.editing   = None
                        st.success(f"✅ {len(loaded)}개 종목 불러오기 완료!")
                        st.rerun()
                    else:
                        st.error("올바른 포트폴리오 데이터가 아닙니다.")
                except Exception:
                    st.error("텍스트를 읽을 수 없습니다. 저장한 내용을 그대로 붙여넣으세요.")
            else:
                st.warning("텍스트를 먼저 붙여넣어 주세요.")

        st.markdown("---")
        if st.button("🔄 전체 초기화", use_container_width=True):
            st.session_state.portfolio = []
            st.session_state.editing   = None
            st.rerun()
        st.markdown(
            '<div style="font-size:11px;color:#9CA3AF;margin-top:8px;line-height:1.6;">'
            '세션 종료 시 포트폴리오가 초기화됩니다.<br>'
            '💾 저장 텍스트를 메모장에 복사해두세요!</div>',
            unsafe_allow_html=True
        )


# ── 페이지 라우팅 ─────────────────────────────────────────────────────────────
if st.session_state.page == "main":
    render_main_page()
elif st.session_state.page == "detail":
    render_detail_page()
