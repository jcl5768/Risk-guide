# =============================================================================
# pages.py — UI 렌더링 (대시보드 페이지 + 상세 분석 페이지)
#
# ✅ 이 파일을 수정하는 경우:
#   - 화면 레이아웃 변경     → show_dashboard() / show_detail()
#   - 새 탭 추가             → show_detail() 내 st.tabs() 수정
#   - 카드 디자인 변경       → 각 st.markdown() 블록
#   - Lv.3 탭 내용 채우기   → show_lv3_tab() 함수
#
# 데이터/계산 로직은 engine.py에 있습니다.
# 섹터·지표 설정은 config.py에 있습니다.
# =============================================================================

import streamlit as st
import plotly.graph_objects as go

from config import SECTOR_CONFIG, MACRO_INDICATORS, LV3_ROADMAP
from engine import (
    get_z_and_price, get_sector_analysis,
    get_price_history, get_news,
    calc_win_rate, get_signal, zcolor, zdesc, detect_sector,
)


# ── 공통 CSS 스타일 ───────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
.stApp{background:#F7F8FA;color:#1A1D23;font-family:'Inter',sans-serif;}
header[data-testid="stHeader"]{background:#FFFFFF;border-bottom:1px solid #E8EAED;}
.stDeployButton{display:none;} #MainMenu{display:none;} footer{display:none;}
section[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #E8EAED;}
.macro-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:14px 18px;}
.section-hdr{font-size:11px;font-weight:600;color:#6B7280;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #E8EAED;}
.stock-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:16px 18px;}
.badge-green{background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.badge-yellow{background:#FFFBEB;color:#D97706;border:1px solid #FDE68A;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.badge-red{background:#FEF2F2;color:#DC2626;border:1px solid #FECACA;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.lv1{background:#EFF6FF;color:#2563EB;border:1px solid #BFDBFE;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
.lv2{background:#FFF7ED;color:#EA580C;border:1px solid #FED7AA;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
.lv3{background:#F5F3FF;color:#7C3AED;border:1px solid #DDD6FE;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
.news-pos{background:#ECFDF5;border-left:3px solid #059669;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
.news-neg{background:#FEF2F2;border-left:3px solid #DC2626;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
.news-neu{background:#F9FAFB;border-left:3px solid #D1D5DB;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
.stTabs [data-baseweb="tab-list"]{gap:2px;background:#F3F4F6;border-radius:8px;padding:3px;border:1px solid #E8EAED;}
.stTabs [data-baseweb="tab"]{height:32px;font-size:12px;font-weight:500;color:#6B7280;border-radius:6px;padding:0 14px;}
.stTabs [aria-selected="true"]{background:#FFFFFF !important;color:#1A1D23 !important;box-shadow:0 1px 3px rgba(0,0,0,0.1);}
div[data-testid="stButton"] button{background:#FFFFFF;color:#374151;border:1px solid #D1D5DB;border-radius:7px;font-size:12px;font-weight:500;padding:6px 16px;}
div[data-testid="stButton"] button:hover{background:#F9FAFB;border-color:#9CA3AF;}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{background:#FFFFFF !important;border:1px solid #D1D5DB !important;border-radius:7px !important;color:#1A1D23 !important;font-size:13px !important;}
.stSlider > div > div > div{background:#2563EB !important;}
.stSpinner > div{border-top-color:#2563EB !important;}
div[data-testid="stExpander"]{background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# 메인 대시보드
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard():
    """메인 대시보드 페이지 렌더링"""

    # 타이틀
    st.markdown("""
    <div style="margin-bottom:20px;">
        <h2 style="font-size:22px;font-weight:700;color:#1A1D23;margin:0;">📊 포트폴리오 현황</h2>
        <p style="font-size:13px;color:#6B7280;margin:4px 0 0;">섹터별 맞춤 거시지표 기반 통계적 승률 분석</p>
    </div>
    """, unsafe_allow_html=True)

    # Level 안내 배너
    st.markdown("""
    <div style="background:#F8FAFF;border:1px solid #DBEAFE;border-radius:10px;padding:12px 18px;margin-bottom:18px;">
        <div style="font-size:11px;font-weight:600;color:#2563EB;letter-spacing:1px;margin-bottom:6px;">분석 레벨 안내</div>
        <div style="display:flex;gap:20px;flex-wrap:wrap;font-size:12px;color:#374151;">
            <div><span class="lv1">Lv.1</span> <b>직관</b> — 승률% · 신호등 · 한줄 요약</div>
            <div><span class="lv2">Lv.2</span> <b>분석</b> — 섹터 지표별 점수 · 뉴스 감성 (현재)</div>
            <div><span class="lv3">Lv.3</span> <b style="color:#9CA3AF;">심화</b> — 상관계수 · 몬테카를로 (예정)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 주요 거시 지표
    st.markdown('<div class="section-hdr">📡 주요 거시 지표</div>', unsafe_allow_html=True)
    cols = st.columns(len(MACRO_INDICATORS))
    for col, (label, sym, desc) in zip(cols, MACRO_INDICATORS):
        z, price = get_z_and_price(sym)
        arrow = "▲" if z > 0.2 else "▼" if z < -0.2 else "—"
        ac    = "#059669" if z > 0.2 else "#DC2626" if z < -0.2 else "#6B7280"
        col.markdown(f"""
        <div class="macro-card">
            <div style="font-size:10px;font-weight:600;color:#6B7280;margin-bottom:4px;">{label}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:19px;font-weight:700;color:{zcolor(z)};">
                {price:,.2f} <span style="font-size:13px;color:{ac};">{arrow}</span>
            </div>
            <div style="font-size:10px;color:#9CA3AF;margin-top:2px;">Z {z:+.2f}σ · {desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    portfolio = st.session_state.portfolio

    # 포트폴리오가 비어있을 때
    if not portfolio:
        st.markdown("""
        <div style="background:#FFFFFF;border:2px dashed #D1D5DB;border-radius:12px;padding:48px;text-align:center;">
            <div style="font-size:36px;margin-bottom:10px;">📭</div>
            <div style="font-size:16px;font-weight:600;color:#374151;margin-bottom:6px;">아직 종목이 없습니다</div>
            <div style="font-size:13px;color:#9CA3AF;">
                왼쪽 사이드바에서 <b>➕ 종목 추가</b>를 눌러 첫 종목을 추가해보세요.
            </div>
            <div style="font-size:11px;color:#D1D5DB;margin-top:8px;">
                예시: AAPL · TSLA · NVDA · XOM · JPM
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # 종목 카드 (4개씩 한 행)
    st.markdown(
        '<div class="section-hdr">📈 보유 종목 분석 <span class="lv1" style="margin-left:6px;">Lv.1</span></div>',
        unsafe_allow_html=True,
    )
    for row_start in range(0, len(portfolio), 4):
        row = portfolio[row_start: row_start + 4]
        cols = st.columns(len(row))
        for col, stock in zip(cols, row):
            with col:
                _render_stock_card(stock)

    # 포트폴리오 구성 차트
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-hdr">📊 포트폴리오 구성</div>', unsafe_allow_html=True)
    chart_col, bar_col = st.columns([1, 2])
    with chart_col:
        _render_pie_chart(portfolio)
    with bar_col:
        _render_allocation_bars(portfolio)


def _render_stock_card(stock: dict):
    """종목 카드 한 개 렌더링 + 상세 분석 버튼"""
    with st.spinner(""):
        zs, price        = get_z_and_price(stock["ticker"])
        _, cfg, inds     = get_sector_analysis(stock["ticker"])
        nb, _            = get_news(stock["ticker"])
        win              = calc_win_rate(zs, inds, nb)

    st_, sc_, sv_ = get_signal(win)
    pnl  = ((price - stock["avg_price"]) / stock["avg_price"] * 100) if price and stock["avg_price"] else 0
    pc   = "#059669" if pnl >= 0 else "#DC2626"
    ti   = max(inds, key=lambda x: abs(x["z"] * x["weight"]))
    tc   = ti["z"] * ti["weight"] * 0.5
    tclr = "#059669" if tc > 0 else "#DC2626"

    st.markdown(f"""
    <div class="stock-card" style="border-top:3px solid {sv_};">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
            <div>
                <span style="font-weight:700;font-size:15px;color:#1A1D23;">{stock['ticker']}</span>
                <span style="font-size:11px;color:{cfg['color']};margin-left:4px;">{cfg['icon']}</span>
                <div style="font-size:10px;color:#9CA3AF;">{stock['name']}</div>
            </div>
            <div class="{sc_}">{st_}</div>
        </div>
        <div style="display:flex;align-items:baseline;gap:3px;margin-bottom:2px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:700;color:{sv_};line-height:1;">{win}%</span>
            <span style="font-size:10px;color:#9CA3AF;">승률</span>
        </div>
        <div style="font-size:10px;color:{tclr};margin-bottom:8px;">
            {'▲' if tc>0 else '▼'} {ti['name']} Z{ti['z']:+.1f}
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;padding-top:8px;border-top:1px solid #F3F4F6;">
            <span style="color:#6B7280;">${price:.1f}</span>
            <span style="color:{pc};font-weight:500;">{'+'if pnl>=0 else ''}{pnl:.1f}%</span>
            <span style="color:#9CA3AF;">{stock['weight']}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    if st.button("상세 분석 →", key=f"go_{stock['ticker']}_{id(stock)}"):
        st.session_state.selected = stock["ticker"]
        st.session_state.page     = "detail"
        st.rerun()


def _render_pie_chart(portfolio: list):
    labels  = [s["ticker"] for s in portfolio]
    weights = [s["weight"] for s in portfolio]
    colors  = [SECTOR_CONFIG[detect_sector(s["ticker"])]["color"] for s in portfolio]
    fig = go.Figure(go.Pie(
        values=weights, labels=labels, hole=0.6,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textfont=dict(family="Inter", size=11),
        hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10), height=200,
        annotations=[dict(
            text=f"<b>{sum(weights)}%</b>", x=0.5, y=0.5,
            font=dict(size=14, color="#1A1D23", family="Inter"),
            showarrow=False,
        )],
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_allocation_bars(portfolio: list):
    for s in portfolio:
        sc = SECTOR_CONFIG[detect_sector(s["ticker"])]
        st.markdown(f"""
        <div style="margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                <span style="font-size:13px;font-weight:600;color:#1A1D23;">
                    {s['ticker']}
                    <span style="font-size:11px;color:{sc['color']};">{sc['icon']} {sc['label']}</span>
                </span>
                <span style="font-size:13px;font-weight:600;color:#2563EB;">{s['weight']}%</span>
            </div>
            <div style="height:4px;background:#F3F4F6;border-radius:2px;">
                <div style="height:100%;width:{min(s['weight'],100)}%;background:{sc['color']};border-radius:2px;opacity:0.8;"></div>
            </div>
            <div style="font-size:11px;color:#9CA3AF;margin-top:2px;">
                {s['name']} · {s['shares']}주 · 평균 ${s['avg_price']:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 상세 분석 페이지
# ─────────────────────────────────────────────────────────────────────────────
def show_detail():
    """상세 분석 페이지 렌더링"""
    target = st.session_state.selected or ""
    if not target:
        st.session_state.page = "main"
        st.rerun()

    if st.sidebar.button("← 대시보드로", use_container_width=True):
        st.session_state.page = "main"
        st.rerun()

    # 포트폴리오에서 종목 정보 찾기
    si = next(
        (s for s in st.session_state.portfolio if s["ticker"] == target),
        {"name": target, "weight": "—", "avg_price": 0, "shares": 0},
    )

    # 데이터 로드
    with st.spinner(f"{target} 분석 중..."):
        zs, price       = get_z_and_price(target)
        sk, cfg, inds   = get_sector_analysis(target)
        nb, nd          = get_news(target)
        fw              = calc_win_rate(zs, inds, nb)
        history         = get_price_history(target)

    st_, sc_, sv_ = get_signal(fw)
    pnl = ((price - si["avg_price"]) / si["avg_price"] * 100) if price and si["avg_price"] else 0
    pc  = "#059669" if pnl >= 0 else "#DC2626"

    # 헤더
    hl, hr = st.columns([3, 1])
    with hl:
        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <div style="font-size:11px;color:#6B7280;font-weight:500;letter-spacing:1px;
                        text-transform:uppercase;margin-bottom:4px;">
                {cfg['icon']} {cfg['label']} 섹터
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
                <h1 style="font-size:26px;font-weight:700;color:#1A1D23;margin:0;">{target}</h1>
                <div class="{sc_}">{st_}</div>
            </div>
            <div style="font-size:12px;color:#6B7280;">
                {si['name']} · 비중 {si['weight']}% · {si['shares']}주 · 평균 ${si['avg_price']:.2f}
            </div>
            <div style="font-size:11px;color:#9CA3AF;margin-top:4px;">📌 {cfg['cycle_note']}</div>
        </div>
        """, unsafe_allow_html=True)
    with hr:
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;
                    padding:18px;text-align:center;border-top:3px solid {sv_};">
            <div style="font-size:10px;color:#9CA3AF;font-weight:500;letter-spacing:1px;
                        text-transform:uppercase;margin-bottom:4px;">
                오늘의 승률 <span class="lv1">Lv.1</span>
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:42px;
                        font-weight:700;color:{sv_};line-height:1;">{fw}%</div>
            <div style="font-size:11px;color:#9CA3AF;margin-top:4px;">
                뉴스 보정 {nb:+.1f}% ·
                <span style="color:{pc};">{'+'if pnl>=0 else ''}{pnl:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 탭
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌡️  종합 기상도 (Lv.1)",
        f"{cfg['icon']}  섹터 지표 (Lv.2)",
        "📰  뉴스 감성 (Lv.2)",
        "🔮  시나리오 시뮬",
        "🔒  심화 분석 (Lv.3)",
    ])

    with tab1:
        _show_tab_overview(zs, inds, nb, fw, sv_, history, target, price, pnl)
    with tab2:
        _show_tab_indicators(cfg, inds)
    with tab3:
        _show_tab_news(nd, nb)
    with tab4:
        _show_tab_simulator(zs, inds, nb, fw, sv_, cfg)
    with tab5:
        _show_tab_lv3()


# ── 탭 1: 종합 기상도 ────────────────────────────────────────────────────────
def _show_tab_overview(zs, inds, nb, fw, sv_, history, target, price, pnl):
    gl, gr = st.columns([1, 2])
    with gl:
        # 게이지
        gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=fw,
            number={"suffix": "%", "font": {"family": "JetBrains Mono", "size": 28, "color": sv_}},
            gauge={
                "axis":  {"range": [0, 100], "tickfont": {"color": "#9CA3AF", "size": 10}},
                "bar":   {"color": sv_, "thickness": 0.28},
                "bgcolor": "#FFFFFF", "borderwidth": 0,
                "steps": [
                    {"range": [0,  45], "color": "rgba(220,38,38,0.05)"},
                    {"range": [45, 60], "color": "rgba(217,119,6,0.05)"},
                    {"range": [60,100], "color": "rgba(5,150,105,0.05)"},
                ],
                "threshold": {"line": {"color": sv_, "width": 2}, "thickness": 0.8, "value": fw},
            },
        ))
        gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font={"color": "#1A1D23"},
            margin=dict(t=10, b=10, l=10, r=10), height=200,
        )
        st.plotly_chart(gauge, use_container_width=True)

        # 한 줄 요약
        top_pos = sorted([x for x in inds if x["z"] * x["weight"] > 0],
                         key=lambda x: x["z"] * x["weight"], reverse=True)
        top_neg = sorted([x for x in inds if x["z"] * x["weight"] < 0],
                         key=lambda x: x["z"] * x["weight"])
        ps  = top_pos[0]["name"] if top_pos else "없음"
        ns2 = top_neg[0]["name"] if top_neg else "없음"
        st.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:8px;padding:12px 14px;">
            <div style="font-size:10px;color:#059669;font-weight:600;letter-spacing:1px;margin-bottom:4px;">
                Lv.1 요약
            </div>
            <div style="font-size:12px;color:#374151;line-height:1.6;">
                <span style="color:#059669;">▲ {ps}</span> 긍정<br>
                <span style="color:#DC2626;">▼ {ns2}</span> 리스크
            </div>
        </div>
        """, unsafe_allow_html=True)

    with gr:
        # 60일 차트
        if not history.empty and "Date" in history.columns:
            r, g, b = int(sv_[1:3], 16), int(sv_[3:5], 16), int(sv_[5:7], 16)
            fh = go.Figure()
            fh.add_trace(go.Scatter(
                x=history["Date"], y=history["Close"],
                mode="lines", line=dict(color=sv_, width=2),
                fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.06)",
                name=target, hovertemplate="$%{y:.2f}<br>%{x|%m/%d}<extra></extra>",
            ))
            if len(history) >= 20:
                ma20 = history["Close"].rolling(20).mean()
                fh.add_trace(go.Scatter(
                    x=history["Date"], y=ma20, mode="lines",
                    line=dict(color="#D97706", width=1.5, dash="dash"), name="MA20",
                ))
            fh.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6B7280"),
                xaxis=dict(showgrid=False, color="#D1D5DB"),
                yaxis=dict(showgrid=True, gridcolor="#F3F4F6", color="#9CA3AF"),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
                margin=dict(t=10, b=10, l=0, r=0), height=240, hovermode="x unified",
            )
            st.plotly_chart(fh, use_container_width=True)

        # KPI 4개
        pc = "#059669" if pnl >= 0 else "#DC2626"
        kc = st.columns(4)
        for col, (lbl, val, clr) in zip(kc, [
            ("현재가",  f"${price:.2f}",     "#1A1D23"),
            ("주가 Z",  f"{zs:+.2f}σ",       zcolor(zs)),
            ("뉴스",    f"{nb:+.1f}%",        "#059669" if nb > 0 else "#DC2626"),
            ("수익률",  f"{'+'if pnl>=0 else ''}{pnl:.1f}%", pc),
        ]):
            col.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;
                        padding:12px;text-align:center;">
                <div style="font-size:10px;color:#9CA3AF;font-weight:500;
                            letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{lbl}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:17px;
                            font-weight:700;color:{clr};">{val}</div>
            </div>
            """, unsafe_allow_html=True)


# ── 탭 2: 섹터 지표 분석 ─────────────────────────────────────────────────────
def _show_tab_indicators(cfg, inds):
    r2, g2, b2 = int(cfg["color"][1:3], 16), int(cfg["color"][3:5], 16), int(cfg["color"][5:7], 16)
    st.markdown(f"""
    <div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;
                padding:12px 16px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <span class="lv2">Lv.2</span>
            <b style="font-size:13px;color:#1A1D23;">{cfg['icon']} {cfg['label']} — {len(inds)}개 지표</b>
        </div>
        <div style="font-size:12px;color:#6B7280;">📌 {cfg['cycle_note']}</div>
    </div>
    """, unsafe_allow_html=True)

    for ind in inds:
        contrib = ind["z"] * ind["weight"] * 0.5
        cc2  = "#059669" if contrib > 0 else "#DC2626" if contrib < 0 else "#6B7280"
        wl   = f"호재 +{ind['weight']}" if ind["weight"] > 0 else f"악재 {ind['weight']}"
        wc2  = "#059669" if ind["weight"] > 0 else "#DC2626"
        bs   = 50.0 if ind["z"] >= 0 else max(0.0, 50.0 - min(50.0, abs(ind["z"]) / 3 * 50))
        bw   = min(50.0, abs(ind["z"]) / 3 * 50)

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;
                    padding:14px 18px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                <div>
                    <span style="font-size:13px;font-weight:600;color:#1A1D23;">{ind['name']}</span>
                    <span style="font-size:10px;color:#9CA3AF;margin-left:6px;">({ind['ticker']})</span>
                    <div style="font-size:11px;color:#9CA3AF;margin-top:2px;">{ind['desc']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:15px;
                                font-weight:700;color:{zcolor(ind['z'])};">{ind['z']:+.2f}σ</div>
                    <div style="font-size:10px;color:{zcolor(ind['z'])};">{zdesc(ind['z'])}</div>
                </div>
            </div>
            <div style="height:5px;background:#F3F4F6;border-radius:3px;position:relative;margin-bottom:6px;">
                <div style="position:absolute;top:0;left:49.5%;width:1px;height:100%;background:#E8EAED;"></div>
                <div style="position:absolute;top:0;left:{bs}%;width:{bw}%;height:100%;
                            background:{zcolor(ind['z'])};border-radius:3px;opacity:0.8;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:11px;">
                <span style="color:{wc2};">{wl}</span>
                <span style="color:{cc2};font-weight:600;">
                    승률 기여 {'+'if contrib>0 else ''}{contrib:.1f}%p
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 레이더 차트
    rl = [ind["name"] for ind in inds]
    rv = [(min(3, max(-3, ind["z"])) + 3) / 6 for ind in inds]
    radar = go.Figure(go.Scatterpolar(
        r=rv + [rv[0]], theta=rl + [rl[0]], fill="toself",
        fillcolor=f"rgba({r2},{g2},{b2},0.12)",
        line=dict(color=cfg["color"], width=2),
        marker=dict(size=5, color=cfg["color"]),
    ))
    radar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="#FAFAFA",
            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False,
                            gridcolor="#E8EAED", linecolor="#E8EAED"),
            angularaxis=dict(tickfont=dict(color="#6B7280", size=11),
                             gridcolor="#E8EAED", linecolor="#E8EAED"),
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=60, r=60), height=300,
    )
    st.plotly_chart(radar, use_container_width=True)


# ── 탭 3: 뉴스 감성 ──────────────────────────────────────────────────────────
def _show_tab_news(nd, nb):
    nl, nr = st.columns([2, 1])
    with nl:
        st.markdown('<div class="section-hdr">뉴스 감성 분석 <span class="lv2">Lv.2</span></div>',
                    unsafe_allow_html=True)
        if nd:
            for n in nd:
                css   = "news-pos" if n["sentiment"] == "Positive" else "news-neg" if n["sentiment"] == "Negative" else "news-neu"
                icon2 = "▲" if n["sentiment"] == "Positive" else "▼" if n["sentiment"] == "Negative" else "●"
                tc3   = "#059669" if n["sentiment"] == "Positive" else "#DC2626" if n["sentiment"] == "Negative" else "#9CA3AF"
                st.markdown(f"""
                <div class="{css}">
                    <div style="font-size:10px;color:{tc3};font-weight:600;margin-bottom:4px;">
                        {icon2} {n['sentiment'].upper()}
                    </div>
                    <a href="{n['link']}" target="_blank"
                       style="font-size:12px;color:#374151;text-decoration:none;line-height:1.5;">
                        {n['title']}
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("뉴스 데이터 없음")

    with nr:
        pc2 = sum(1 for n in nd if n["sentiment"] == "Positive")
        nc2 = sum(1 for n in nd if n["sentiment"] == "Negative")
        nc3 = sum(1 for n in nd if n["sentiment"] == "Neutral")
        if nd:
            sf = go.Figure(go.Pie(
                values=[max(pc2, 0.01), max(nc2, 0.01), max(nc3, 0.01)],
                labels=["긍정", "부정", "중립"], hole=0.6,
                marker=dict(colors=["#059669", "#DC2626", "#D1D5DB"],
                            line=dict(color="#FFFFFF", width=2)),
                textfont=dict(family="Inter", size=11),
            ))
            nb_color = "#059669" if nb > 0 else "#DC2626" if nb < 0 else "#6B7280"
            sf.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                legend=dict(font=dict(color="#6B7280", size=11), bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=0, b=0, l=0, r=0), height=180,
                annotations=[dict(text=f"<b>{nb:+.0f}%</b>", x=0.5, y=0.5,
                    font=dict(size=18, color=nb_color, family="JetBrains Mono"),
                    showarrow=False)],
            )
            st.plotly_chart(sf, use_container_width=True)

        nb_color2 = "#059669" if nb > 0 else "#DC2626" if nb < 0 else "#9CA3AF"
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:14px;">
            <div style="font-size:10px;color:#9CA3AF;font-weight:600;letter-spacing:1px;margin-bottom:10px;">감성 스코어</div>
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="font-size:12px;color:#059669;">▲ 긍정</span>
                <b style="font-size:12px;color:#059669;">{pc2}건</b>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="font-size:12px;color:#DC2626;">▼ 부정</span>
                <b style="font-size:12px;color:#DC2626;">{nc2}건</b>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                <span style="font-size:12px;color:#9CA3AF;">● 중립</span>
                <b style="font-size:12px;color:#9CA3AF;">{nc3}건</b>
            </div>
            <div style="border-top:1px solid #E8EAED;padding-top:10px;
                        display:flex;justify-content:space-between;">
                <span style="font-size:12px;color:#6B7280;">승률 보정</span>
                <b style="font-family:'JetBrains Mono',monospace;font-size:14px;color:{nb_color2};">
                    {nb:+.1f}%
                </b>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── 탭 4: 시나리오 시뮬레이션 ────────────────────────────────────────────────
def _show_tab_simulator(zs, inds, nb, fw, sv_, cfg):
    st.markdown(f"""
    <p style="font-size:13px;color:#6B7280;margin-bottom:16px;">
        {cfg['icon']} <b>{cfg['label']}</b> 섹터 지표를 직접 조정하여 승률 변화를 시뮬레이션합니다.
    </p>
    """, unsafe_allow_html=True)

    sl, sr = st.columns([1, 1])
    with sl:
        sim_inds = []
        for ind in inds:
            d = st.slider(f"{ind['name']}", -3.0, 3.0, float(ind["z"]), 0.1,
                          key=f"sim_{ind['ticker']}")
            sim_inds.append({**ind, "z": d})
        sn  = st.slider("📰 뉴스 보정(%)", -15.0, 15.0, float(nb), 0.5)
        sw  = calc_win_rate(zs, sim_inds, sn)
        dw  = sw - fw
        ss_, sc2_, sv2_ = get_signal(sw)

    with sr:
        dwc = "#059669" if dw > 0 else "#DC2626" if dw < 0 else "#6B7280"
        st.markdown(f"""
        <div style="background:#FFFFFF;border:2px solid {sv2_};border-radius:10px;
                    padding:24px;text-align:center;margin-bottom:16px;">
            <div style="font-size:10px;color:#9CA3AF;font-weight:500;letter-spacing:1px;
                        text-transform:uppercase;margin-bottom:6px;">시뮬레이션 결과</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:46px;
                        font-weight:700;color:{sv2_};line-height:1;">{sw}%</div>
            <div style="font-size:13px;margin-top:8px;font-weight:600;color:{dwc};">
                {'▲' if dw>0 else '▼' if dw<0 else '—'} 현재 대비 {dw:+.1f}%p
            </div>
            <div class="{sc2_}" style="margin-top:10px;display:inline-block;">{ss_}</div>
        </div>
        """, unsafe_allow_html=True)

        cmp = go.Figure(go.Bar(
            x=["현재 승률", "시뮬 승률"], y=[fw, sw],
            marker=dict(color=[sv_, sv2_], line=dict(color="#FFFFFF", width=1)),
            text=[f"{fw}%", f"{sw}%"],
            textfont=dict(family="JetBrains Mono", size=13, color="#1A1D23"),
            textposition="outside",
        ))
        cmp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#6B7280")),
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6", range=[0, 105]),
            margin=dict(t=20, b=10, l=0, r=0), height=200,
        )
        st.plotly_chart(cmp, use_container_width=True)


# ── 탭 5: Lv.3 심화 (로드맵) ─────────────────────────────────────────────────
def _show_tab_lv3():
    """
    Lv.3 기능 로드맵 표시.
    추후 각 기능 구현 시 이 함수 내에 st.tabs() 또는 섹션을 추가.
    """
    st.markdown("""
    <div style="background:#F5F3FF;border:1px solid #DDD6FE;border-radius:10px;
                padding:18px 22px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span class="lv3">Lv.3 심화</span>
            <span style="font-size:14px;font-weight:600;color:#1A1D23;">개발 진행 중</span>
        </div>
        <p style="font-size:13px;color:#6B7280;margin:0;line-height:1.6;">
            현재 Lv.2까지 구현되어 있습니다. 아래 기능들이 순서대로 추가됩니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    for icon3, title, desc, status in LV3_ROADMAP:
        is_next  = (status == "다음 개발")
        bg       = "#EDE9FE" if is_next else "#F3F4F6"
        clr      = "#7C3AED" if is_next else "#9CA3AF"
        card_bg  = "#F5F3FF" if is_next else "#F9FAFB"
        st.markdown(f"""
        <div style="background:{card_bg};border:1px solid #E8EAED;border-radius:8px;
                    padding:14px 18px;margin-bottom:8px;display:flex;gap:14px;align-items:flex-start;">
            <div style="font-size:22px;">{icon3}</div>
            <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
                    <span style="font-size:13px;font-weight:600;color:#1A1D23;">{title}</span>
                    <span style="font-size:10px;color:{clr};font-weight:600;
                                 background:{bg};padding:2px 8px;border-radius:4px;">{status}</span>
                </div>
                <div style="font-size:12px;color:#6B7280;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
