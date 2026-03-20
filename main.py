# main.py — 진입점, 세션 관리, 개선된 포트폴리오 입력 UX
#
# 업그레이드 포인트:
#   1. 종목 추가 시 티커 입력하면 종목명·섹터·현재가 자동 조회
#   2. 빠른 추가(Quick Add) — 자주 쓰는 종목 원클릭 추가
#   3. 비중 합계 시각적 프로그레스 바
#   4. 포트폴리오 카드뷰에서 수익률·보유금액 즉시 표시

import streamlit as st
from config import SECTOR_CONFIG, ETF_MAP
from engine import detect_sector, get_z_and_price
from pages import apply_custom_style, render_main_page, render_detail_page

st.set_page_config(
    page_title="Risk Guide",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_style()


# ── 세션 초기화 ───────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "portfolio": [],
        "page":      "main",
        "selected":  None,
        "editing":   None,
        "show_add":  False,
        "add_ticker_lookup": {},  # 자동 조회 캐시 {ticker: {name, sector, price}}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── 티커 자동 조회 ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def lookup_ticker(ticker: str) -> dict:
    """티커 입력 시 종목명·섹터·현재가 자동 조회"""
    import yfinance as yf
    try:
        info  = yf.Ticker(ticker).info
        name  = info.get("shortName") or info.get("longName") or ticker
        sec   = detect_sector(ticker)
        _, px = get_z_and_price(ticker)
        return {"name": name, "sector": sec, "price": px, "found": True}
    except Exception:
        return {"name": ticker, "sector": "Unknown", "price": 0.0, "found": False}


# ── 빠른 추가 종목 목록 ────────────────────────────────────────────────────────
QUICK_ADD_LIST = [
    ("AAPL", "Apple"),    ("MSFT", "Microsoft"), ("NVDA", "NVIDIA"),
    ("TSLA", "Tesla"),    ("AMZN", "Amazon"),    ("GOOGL", "Alphabet"),
    ("META", "Meta"),     ("JPM",  "JPMorgan"),  ("XOM",  "Exxon"),
]


# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 내 포트폴리오")

    # 비중 프로그레스 바
    total_w = sum(s["weight"] for s in st.session_state.portfolio)
    bar_pct  = min(total_w, 100)
    bar_clr  = "#059669" if total_w <= 100 else "#DC2626"
    st.markdown(f"""
    <div style="margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;font-size:12px;
                    color:{bar_clr};margin-bottom:4px;">
            <span>총 비중 {total_w}% {"✓" if total_w<=100 else "⚠ 초과"}</span>
            <span>{len(st.session_state.portfolio)}개 종목</span>
        </div>
        <div style="height:5px;background:#E8EAED;border-radius:3px;">
            <div style="height:100%;width:{bar_pct}%;background:{bar_clr};
                        border-radius:3px;transition:width 0.3s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # 종목 없을 때
    if not st.session_state.portfolio:
        st.markdown("""
        <div style="text-align:center;padding:14px 8px;color:#9CA3AF;font-size:12px;
                    background:#F9FAFB;border-radius:8px;margin-bottom:10px;">
            📭 아직 종목이 없어요<br>
            <span style="font-size:11px;">아래에서 추가해보세요</span>
        </div>
        """, unsafe_allow_html=True)

    # ── 종목 목록 ────────────────────────────────────────────────────────
    for i, stock in enumerate(st.session_state.portfolio):
        sec = detect_sector(stock["ticker"])
        cfg = SECTOR_CONFIG[sec]

        if st.session_state.editing == i:
            # 수정 모드
            st.markdown(f"**✏️ {stock['ticker']} 수정**")
            nn = st.text_input("종목명",       value=stock["name"],              key=f"en_{i}")
            nw = st.number_input("비중(%)",     value=int(stock["weight"]),       min_value=1,   max_value=100,     key=f"ew_{i}")
            ns = st.number_input("수량(주)",    value=int(stock.get("shares",1)), min_value=1,   max_value=1000000, key=f"es_{i}")
            na = st.number_input("평균단가($)", value=float(stock["avg_price"]),  min_value=0.0, max_value=999999.0, format="%.2f", key=f"ea_{i}")
            c1, c2 = st.columns(2)
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
            # 일반 표시
            _, cur_price = get_z_and_price(stock["ticker"])
            pnl = ((cur_price - stock["avg_price"]) / stock["avg_price"] * 100) if cur_price and stock["avg_price"] > 0 else None
            pnl_str = f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "—"
            pnl_clr = "#059669" if (pnl or 0) >= 0 else "#DC2626"
            value_str = f"${cur_price * stock.get('shares',0):,.0f}" if cur_price and stock.get("shares") else "—"

            st.markdown(f"""
            <div style="padding:8px 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-weight:700;font-size:14px;color:#1A1D23;">{stock['ticker']}</span>
                        <span style="font-size:11px;color:{cfg['color']};margin-left:4px;">{cfg['icon']}</span>
                        <div style="font-size:10px;color:#9CA3AF;">{stock['name']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-weight:700;font-size:14px;color:#2563EB;">{stock['weight']}%</div>
                        <div style="font-size:10px;color:{pnl_clr};">{pnl_str}</div>
                    </div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:10px;
                            color:#9CA3AF;margin-top:2px;">
                    <span>${cur_price:.1f} · {stock.get('shares',0)}주</span>
                    <span>평가 {value_str}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

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

    # ── 종목 추가 섹션 ──────────────────────────────────────────────────
    if st.button("➕  종목 추가", use_container_width=True, key="toggle_add"):
        st.session_state.show_add = not st.session_state.show_add

    if st.session_state.show_add:

        # 빠른 추가
        st.markdown('<div style="font-size:11px;color:#9CA3AF;margin-bottom:6px;">⚡ 빠른 추가</div>',
                    unsafe_allow_html=True)
        qa_cols = st.columns(3)
        for idx, (qticker, qname) in enumerate(QUICK_ADD_LIST):
            with qa_cols[idx % 3]:
                if st.button(qticker, key=f"qa_{qticker}", use_container_width=True,
                             help=qname):
                    if not any(s["ticker"] == qticker for s in st.session_state.portfolio):
                        info = lookup_ticker(qticker)
                        _, px = get_z_and_price(qticker)
                        st.session_state.portfolio.append({
                            "ticker":    qticker,
                            "name":      info["name"],
                            "weight":    10,
                            "shares":    1,
                            "avg_price": round(px, 2) if px else 0.0,
                        })
                        st.session_state.show_add = False
                        st.rerun()

        st.markdown("---")

        # 직접 입력
        st.markdown('<div style="font-size:11px;color:#9CA3AF;margin-bottom:6px;">직접 입력</div>',
                    unsafe_allow_html=True)

        nt = st.text_input(
            "티커 심볼", placeholder="예: AAPL",
            key="add_t",
            help="미국 주식 티커를 입력하면 종목명·섹터·현재가를 자동으로 불러옵니다"
        ).upper().strip()

        # 자동 조회 미리보기
        auto_name, auto_price = "", 0.0
        if nt:
            info = lookup_ticker(nt)
            auto_name  = info["name"]
            auto_price = info["price"]
            dsec  = info["sector"]
            dcfg  = SECTOR_CONFIG[dsec]
            status_color = "#059669" if info["found"] else "#D97706"
            status_text  = "조회 완료" if info["found"] else "수동 입력 필요"
            st.markdown(f"""
            <div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:8px;
                        padding:10px 12px;margin:6px 0;font-size:12px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-weight:600;color:#1A1D23;">{auto_name}</span>
                    <span style="color:{status_color};font-size:10px;">{status_text}</span>
                </div>
                <div style="color:#6B7280;">
                    {dcfg['icon']} {dcfg['label']}
                    &nbsp;·&nbsp;
                    현재가 <b>${auto_price:.2f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        nn = st.text_input("종목명",      value=auto_name, placeholder="자동 입력", key="add_n")
        nw = st.number_input("비중(%)",   min_value=1, max_value=100, value=10, key="add_w")
        ns = st.number_input("수량(주)",  min_value=1, max_value=1000000, value=1, key="add_s")
        na = st.number_input(
            "평균단가($)",
            min_value=0.0, max_value=999999.0,
            value=round(float(auto_price), 2) if auto_price else 0.0,
            format="%.2f", key="add_a",
            help="0 입력 시 수익률 계산 생략"
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 추가", key="do_add", use_container_width=True):
                if nt:
                    st.session_state.portfolio.append({
                        "ticker":    nt,
                        "name":      nn or nt,
                        "weight":    nw,
                        "shares":    ns,
                        "avg_price": na,
                    })
                    st.session_state.show_add = False
                    st.rerun()
        with c2:
            if st.button("✕ 닫기", key="close_add", use_container_width=True):
                st.session_state.show_add = False
                st.rerun()

    st.markdown("---")

    # 설정
    with st.expander("⚙️ 설정"):
        if st.button("🔄 전체 초기화", use_container_width=True):
            st.session_state.portfolio = []
            st.session_state.editing   = None
            st.rerun()
        st.markdown(f"""
        <div style="font-size:11px;color:#9CA3AF;margin-top:8px;line-height:1.6;">
            세션이 종료되면 포트폴리오가 초기화됩니다.<br>
            (Lv.3에서 로컬 저장 기능 추가 예정)
        </div>
        """, unsafe_allow_html=True)


# ── 페이지 라우팅 ─────────────────────────────────────────────────────────────
if st.session_state.page == "main":
    render_main_page()
elif st.session_state.page == "detail":
    render_detail_page()
