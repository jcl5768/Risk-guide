# pages.py — UI 렌더링 + 상관관계 시각화
#
# 업그레이드 포인트:
#   1. render_detail_page()에 "📈 상관 분석" 탭 추가
#   2. 거시지표 ↔ 종목 60일 상관계수 Bar 차트
#   3. breakdown 딕셔너리를 활용한 승률 계산 근거 공개
#   4. 지표 카드에 sensitivity(핵심/보조/참고) 배지 추가

import streamlit as st
import plotly.graph_objects as go
from config import SECTOR_CONFIG, MACRO_INDICATORS, SENSITIVITY_COLOR, SENSITIVITY_LABEL
from engine import (
    detect_sector, get_z_and_price, get_sector_analysis,
    get_price_history, get_news, get_macro_correlation,
    calc_win_rate, get_weighted_z,
    get_signal, zcolor, zdesc, corr_color,
)


# ── CSS ───────────────────────────────────────────────────────────────────────
def apply_custom_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp{background:#F7F8FA;color:#1A1D23;font-family:'Inter',sans-serif;}
    header[data-testid="stHeader"]{background:#FFFFFF;border-bottom:1px solid #E8EAED;}
    .stDeployButton{display:none;} #MainMenu{display:none;} footer{display:none;}
    section[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #E8EAED;}
    .macro-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:14px 18px;}
    .section-hdr{font-size:11px;font-weight:600;color:#6B7280;letter-spacing:1px;text-transform:uppercase;
                 margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #E8EAED;}
    .stock-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:16px 18px;}
    .badge-green{background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;border-radius:20px;
                 padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
    .badge-yellow{background:#FFFBEB;color:#D97706;border:1px solid #FDE68A;border-radius:20px;
                  padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
    .badge-red{background:#FEF2F2;color:#DC2626;border:1px solid #FECACA;border-radius:20px;
               padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
    .lv1{background:#EFF6FF;color:#2563EB;border:1px solid #BFDBFE;border-radius:6px;
         padding:2px 8px;font-size:10px;font-weight:700;}
    .lv2{background:#FFF7ED;color:#EA580C;border:1px solid #FED7AA;border-radius:6px;
         padding:2px 8px;font-size:10px;font-weight:700;}
    .lv3{background:#F5F3FF;color:#7C3AED;border:1px solid #DDD6FE;border-radius:6px;
         padding:2px 8px;font-size:10px;font-weight:700;}
    .news-pos{background:#ECFDF5;border-left:3px solid #059669;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
    .news-neg{background:#FEF2F2;border-left:3px solid #DC2626;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
    .news-neu{background:#F9FAFB;border-left:3px solid #D1D5DB;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
    .ind-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;
              padding:12px 16px;margin-bottom:8px;}
    .sensitivity-high{background:#FEF2F2;color:#DC2626;border:1px solid #FECACA;
                       border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
    .sensitivity-mid{background:#FFFBEB;color:#D97706;border:1px solid #FDE68A;
                      border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
    .sensitivity-low{background:#F9FAFB;color:#6B7280;border:1px solid #E8EAED;
                      border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
    div[data-testid="stButton"] button{background:#FFFFFF;color:#374151;border:1px solid #D1D5DB;
        border-radius:7px;font-size:12px;font-weight:500;padding:6px 16px;}
    div[data-testid="stButton"] button:hover{background:#F9FAFB;border-color:#9CA3AF;}
    div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{
        background:#FFFFFF !important;border:1px solid #D1D5DB !important;
        border-radius:7px !important;color:#1A1D23 !important;font-size:13px !important;}
    .stTabs [data-baseweb="tab-list"]{gap:2px;background:#F3F4F6;border-radius:8px;padding:3px;border:1px solid #E8EAED;}
    .stTabs [data-baseweb="tab"]{height:32px;font-size:12px;font-weight:500;color:#6B7280;border-radius:6px;padding:0 14px;}
    .stTabs [aria-selected="true"]{background:#FFFFFF !important;color:#1A1D23 !important;box-shadow:0 1px 3px rgba(0,0,0,0.1);}
    .stSlider > div > div > div{background:#2563EB !important;}
    .stSpinner > div{border-top-color:#2563EB !important;}
    </style>
    """, unsafe_allow_html=True)


# ── 메인 대시보드 ─────────────────────────────────────────────────────────────
def render_main_page():
    st.markdown("""
    <div style="margin-bottom:20px;">
        <h2 style="font-size:22px;font-weight:700;color:#1A1D23;margin:0;">📊 포트폴리오 현황</h2>
        <p style="font-size:13px;color:#6B7280;margin:4px 0 0;">섹터 드라이버 가중 Z-Score 기반 승률 분석</p>
    </div>
    """, unsafe_allow_html=True)

    # 거시 지표
    st.markdown('<div class="section-hdr">📡 주요 거시 지표</div>', unsafe_allow_html=True)
    mc = st.columns(5)
    for col, (label, sym, desc) in zip(mc, MACRO_INDICATORS):
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
    if not portfolio:
        st.markdown("""
        <div style="background:#FFFFFF;border:2px dashed #D1D5DB;border-radius:12px;
                    padding:48px;text-align:center;">
            <div style="font-size:36px;margin-bottom:10px;">📭</div>
            <div style="font-size:16px;font-weight:600;color:#374151;margin-bottom:6px;">
                아직 종목이 없습니다
            </div>
            <div style="font-size:13px;color:#9CA3AF;">
                왼쪽 사이드바에서 <b>➕ 종목 추가</b>를 눌러주세요.
            </div>
            <div style="font-size:11px;color:#D1D5DB;margin-top:8px;">
                예시: AAPL · TSLA · NVDA · XOM · JPM
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(
        '<div class="section-hdr">📈 보유 종목 분석 <span class="lv1" style="margin-left:6px;">Lv.1 / Lv.2</span></div>',
        unsafe_allow_html=True,
    )

    for rs in range(0, len(portfolio), 4):
        row  = portfolio[rs: rs + 4]
        cols = st.columns(len(row))
        for col, stock in zip(cols, row):
            with col:
                with st.spinner(""):
                    zs, price      = get_z_and_price(stock["ticker"])
                    _, cfg, inds   = get_sector_analysis(stock["ticker"])
                    nb, _          = get_news(stock["ticker"])
                    win, breakdown = calc_win_rate(zs, inds, nb)

                st_, sc_, sv_ = get_signal(win)
                pnl = ((price - stock["avg_price"]) / stock["avg_price"] * 100) if price and stock["avg_price"] > 0 else None
                pnl_text = f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "미입력"
                pc   = "#059669" if (pnl or 0) >= 0 else "#DC2626"
                ti   = max(inds, key=lambda x: abs(x["z"] * x["driver_weight"]))
                tc   = ti["z"] * ti["direction"]
                tclr = "#059669" if tc > 0 else "#DC2626"
                weighted_z = get_weighted_z(inds)

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
    <div style="display:flex;align-items:baseline;gap:4px;margin-bottom:2px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:700;
                     color:{sv_};line-height:1;">{win}%</span>
        <span style="font-size:10px;color:#9CA3AF;"
              title="{breakdown['explain']}">승률 ❔</span>
    </div>
    <div style="font-size:10px;color:#9CA3AF;margin-bottom:4px;">
        거시Z <span style="color:{zcolor(weighted_z)};font-weight:600;">{weighted_z:+.2f}</span>
        · 뉴스 <span style="color:{'#059669' if nb>0 else '#DC2626' if nb<0 else '#9CA3AF'};">{nb:+.0f}%</span>
    </div>
    <div style="font-size:10px;color:{tclr};margin-bottom:8px;">
        {'▲' if tc>0 else '▼'} {ti['name']} 핵심 드라이버
    </div>
    <div style="display:flex;justify-content:space-between;font-size:11px;
                padding-top:8px;border-top:1px solid #F3F4F6;">
        <span style="color:#6B7280;">${price:.1f}</span>
        <span style="color:{pc};font-weight:500;">{pnl_text}</span>
        <span style="color:#9CA3AF;">{stock['weight']}%</span>
    </div>
</div>""", unsafe_allow_html=True)
                st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                if st.button("상세 분석 →", key=f"go_{stock['ticker']}_{rs}"):
                    st.session_state.selected = stock["ticker"]
                    st.session_state.page     = "detail"
                    st.rerun()

    # 배분 차트
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-hdr">📊 포트폴리오 구성</div>', unsafe_allow_html=True)
    cc, bc = st.columns([1, 2])
    with cc:
        labels  = [s["ticker"] for s in portfolio]
        weights = [s["weight"] for s in portfolio]
        colors  = [SECTOR_CONFIG[detect_sector(s["ticker"])]["color"] for s in portfolio]
        fig = go.Figure(go.Pie(
            values=weights, labels=labels, hole=0.6,
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
            hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            margin=dict(t=10,b=10,l=10,r=10), height=200,
            annotations=[dict(text=f"<b>{sum(weights)}%</b>", x=0.5, y=0.5,
                font=dict(size=14, color="#1A1D23"), showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True)
    with bc:
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
                    <div style="height:100%;width:{min(s['weight'],100)}%;
                                background:{sc['color']};border-radius:2px;opacity:0.8;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── 상세 분석 페이지 ──────────────────────────────────────────────────────────
def render_detail_page():
    target = st.session_state.selected or ""
    if not target:
        st.session_state.page = "main"; st.rerun()

    if st.sidebar.button("← 대시보드로", use_container_width=True):
        st.session_state.page = "main"; st.rerun()

    si = next(
        (s for s in st.session_state.portfolio if s["ticker"] == target),
        {"name": target, "weight": "—", "avg_price": 0, "shares": 0},
    )

    with st.spinner(f"{target} 분석 중..."):
        zs, price        = get_z_and_price(target)
        sk, cfg, inds    = get_sector_analysis(target)
        nb, nd           = get_news(target)
        fw, breakdown    = calc_win_rate(zs, inds, nb)
        history          = get_price_history(target)
        weighted_z       = get_weighted_z(inds)

    st_, sc_, sv_ = get_signal(fw)
    pnl = ((price - si["avg_price"]) / si["avg_price"] * 100) if price and si["avg_price"] > 0 else 0
    pc  = "#059669" if pnl >= 0 else "#DC2626"

    # ── 헤더 ─────────────────────────────────────────────────────────
    hl, hr = st.columns([3, 1])
    with hl:
        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <div style="font-size:11px;color:#6B7280;letter-spacing:1px;
                        text-transform:uppercase;margin-bottom:4px;">
                {cfg['icon']} {cfg['label']} 섹터
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
                <h1 style="font-size:26px;font-weight:700;color:#1A1D23;margin:0;">{target}</h1>
                <div class="{sc_}">{st_}</div>
            </div>
            <div style="font-size:12px;color:#6B7280;">
                {si['name']} · 비중 {si['weight']}% · {si.get('shares',0)}주 · 평균 ${si['avg_price']:.2f}
            </div>
            <div style="font-size:11px;color:#9CA3AF;margin-top:3px;">
                📌 {cfg['cycle_note']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with hr:
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;
                    padding:18px;text-align:center;border-top:3px solid {sv_};">
            <div style="font-size:10px;color:#9CA3AF;letter-spacing:1px;
                        text-transform:uppercase;margin-bottom:4px;">오늘의 승률</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:42px;
                        font-weight:700;color:{sv_};line-height:1;">{fw}%</div>
            <div style="font-size:10px;color:#9CA3AF;margin-top:4px;"
                 title="{breakdown['explain']}">계산 근거 ❔</div>
            <div style="font-size:11px;color:#9CA3AF;margin-top:3px;">
                거시Z <b style="color:{zcolor(weighted_z)};">{weighted_z:+.2f}</b>
                · 뉴스 {nb:+.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 탭 ───────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌡️ 종합 기상도",
        f"{cfg['icon']} 섹터 지표",
        "📈 상관 분석",
        "📰 뉴스",
        "🧮 계산 근거",
    ])

    # ── TAB 1: 종합 기상도 ────────────────────────────────────────────
    with tab1:
        gl, gr = st.columns([1, 2])
        with gl:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=fw,
                number={"suffix":"%","font":{"family":"JetBrains Mono","size":28,"color":sv_}},
                gauge={
                    "axis":  {"range":[0,100],"tickfont":{"color":"#9CA3AF","size":10}},
                    "bar":   {"color":sv_,"thickness":0.28},
                    "bgcolor":"#FFFFFF","borderwidth":0,
                    "steps": [
                        {"range":[0,45],  "color":"rgba(220,38,38,0.05)"},
                        {"range":[45,60], "color":"rgba(217,119,6,0.05)"},
                        {"range":[60,100],"color":"rgba(5,150,105,0.05)"},
                    ],
                    "threshold":{"line":{"color":sv_,"width":2},"thickness":0.8,"value":fw},
                },
            ))
            gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font={"color":"#1A1D23"},
                margin=dict(t=10,b=10,l=10,r=10), height=200,
            )
            st.plotly_chart(gauge, use_container_width=True)

            # 한 줄 요약
            top_pos = sorted([x for x in inds if x["z"]*x["direction"]>0],
                             key=lambda x: abs(x["z"]*x["driver_weight"]), reverse=True)
            top_neg = sorted([x for x in inds if x["z"]*x["direction"]<0],
                             key=lambda x: abs(x["z"]*x["driver_weight"]), reverse=True)
            ps  = top_pos[0]["name"] if top_pos else "없음"
            ns2 = top_neg[0]["name"] if top_neg else "없음"
            st.markdown(f"""
            <div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:8px;padding:12px;">
                <div style="font-size:10px;color:#059669;font-weight:600;margin-bottom:4px;">
                    Lv.1 요약
                </div>
                <div style="font-size:12px;color:#374151;line-height:1.6;">
                    <span style="color:#059669;">▲ {ps}</span> 긍정 작용<br>
                    <span style="color:#DC2626;">▼ {ns2}</span> 리스크 요인
                </div>
            </div>
            """, unsafe_allow_html=True)

        with gr:
            if not history.empty and "Date" in history.columns:
                r, g, b = int(sv_[1:3],16), int(sv_[3:5],16), int(sv_[5:7],16)
                fh = go.Figure()
                fh.add_trace(go.Scatter(
                    x=history["Date"], y=history["Close"],
                    mode="lines", line=dict(color=sv_,width=2),
                    fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.06)",
                    name=target, hovertemplate="$%{y:.2f}  %{x|%m/%d}<extra></extra>",
                ))
                if len(history) >= 20:
                    ma20 = history["Close"].rolling(20).mean()
                    fh.add_trace(go.Scatter(
                        x=history["Date"], y=ma20, mode="lines",
                        line=dict(color="#D97706",width=1.5,dash="dash"), name="MA20",
                    ))
                fh.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#6B7280"),
                    xaxis=dict(showgrid=False, color="#D1D5DB"),
                    yaxis=dict(showgrid=True, gridcolor="#F3F4F6", color="#9CA3AF"),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
                    margin=dict(t=10,b=10,l=0,r=0), height=240, hovermode="x unified",
                )
                st.plotly_chart(fh, use_container_width=True)

            kc = st.columns(4)
            for col, (lbl, val, clr) in zip(kc, [
                ("현재가",   f"${price:.2f}",     "#1A1D23"),
                ("주가 Z",   f"{zs:+.2f}σ",       zcolor(zs)),
                ("거시 Z",   f"{weighted_z:+.2f}", zcolor(weighted_z)),
                ("수익률",   f"{'+'if pnl>=0 else ''}{pnl:.1f}%", pc),
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

    # ── TAB 2: 섹터 지표 ─────────────────────────────────────────────
    with tab2:
        st.markdown(f"""
        <div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;
                    padding:12px 16px;margin-bottom:16px;">
            <span class="lv2">Lv.2</span>
            <b style="font-size:13px;color:#1A1D23;margin-left:8px;">
                {cfg['icon']} {cfg['label']} — {len(inds)}개 드라이버
            </b>
            <div style="font-size:11px;color:#6B7280;margin-top:4px;">
                📌 {cfg['cycle_note']}
            </div>
            <div style="font-size:11px;color:#6B7280;margin-top:4px;">
                거시환경 가중 Z-Score:
                <b style="color:{zcolor(weighted_z)};font-family:'JetBrains Mono',monospace;">
                    {weighted_z:+.3f}σ
                </b>
                &nbsp;→ 승률 기여
                <b style="color:{zcolor(weighted_z)};">
                    {'+' if weighted_z*15 >= 0 else ''}{weighted_z*15:.1f}%p
                </b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for ind in inds:
            # 이 지표의 방향 반영 기여
            effective_z   = ind["z"] * ind["direction"]
            contribution  = effective_z * ind["driver_weight"] * 15
            cc2   = "#059669" if contribution > 0 else "#DC2626" if contribution < 0 else "#6B7280"
            wlbl  = f"호재(×{ind['driver_weight']:.0%})" if ind["direction"]==+1 else f"악재(×{ind['driver_weight']:.0%})"
            wclr  = "#059669" if ind["direction"]==+1 else "#DC2626"
            sens  = ind.get("sensitivity","mid")
            bs    = 50.0 if effective_z >= 0 else max(0.0, 50.0-min(50.0, abs(effective_z)/3*50))
            bw    = min(50.0, abs(effective_z)/3*50)

            st.markdown(f"""
            <div class="ind-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
                    <div>
                        <span style="font-size:13px;font-weight:600;color:#1A1D23;">{ind['name']}</span>
                        <span style="font-size:10px;color:#9CA3AF;margin-left:5px;">({ind['ticker']})</span>
                        <span class="sensitivity-{sens}" style="margin-left:6px;">
                            {SENSITIVITY_LABEL.get(sens,'')}
                        </span>
                        <div style="font-size:11px;color:#9CA3AF;margin-top:2px;">{ind['desc']}</div>
                    </div>
                    <div style="text-align:right;min-width:80px;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:15px;
                                    font-weight:700;color:{zcolor(ind['z'])};">{ind['z']:+.2f}σ</div>
                        <div style="font-size:10px;color:{zcolor(ind['z'])};">{zdesc(ind['z'])}</div>
                    </div>
                </div>
                <div style="height:5px;background:#F3F4F6;border-radius:3px;position:relative;margin-bottom:5px;">
                    <div style="position:absolute;top:0;left:49.5%;width:1px;height:100%;background:#E8EAED;"></div>
                    <div style="position:absolute;top:0;left:{bs}%;width:{bw}%;height:100%;
                                background:{zcolor(ind['z'])};border-radius:3px;opacity:0.8;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:11px;">
                    <span style="color:{wclr};">{wlbl}</span>
                    <span style="color:{cc2};font-weight:600;">
                        가중 기여 {'+' if contribution>0 else ''}{contribution:.1f}%p
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 드라이버 가중치 도넛 차트
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">드라이버 가중치 구성</div>', unsafe_allow_html=True)
        wc1, wc2 = st.columns([1, 2])
        with wc1:
            d_labels = [ind["name"] for ind in inds]
            d_vals   = [ind["driver_weight"] for ind in inds]
            d_colors = [SENSITIVITY_COLOR[ind.get("sensitivity","mid")] for ind in inds]
            wfig = go.Figure(go.Pie(
                values=d_vals, labels=d_labels, hole=0.5,
                marker=dict(colors=d_colors, line=dict(color="#FFFFFF",width=2)),
                textfont=dict(family="Inter",size=10),
                hovertemplate="<b>%{label}</b><br>가중치: %{percent}<extra></extra>",
            ))
            wfig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                margin=dict(t=10,b=10,l=10,r=10), height=200,
            )
            st.plotly_chart(wfig, use_container_width=True)
        with wc2:
            for ind in sorted(inds, key=lambda x: x["driver_weight"], reverse=True):
                sens  = ind.get("sensitivity","mid")
                s_clr = SENSITIVITY_COLOR[sens]
                bar_w = ind["driver_weight"] * 100
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                        <span style="font-size:12px;color:#1A1D23;">{ind['name']}</span>
                        <span style="font-size:12px;font-weight:600;color:{s_clr};">
                            {ind['driver_weight']:.0%}
                        </span>
                    </div>
                    <div style="height:4px;background:#F3F4F6;border-radius:2px;">
                        <div style="height:100%;width:{bar_w:.0f}%;background:{s_clr};
                                    border-radius:2px;opacity:0.7;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 3: 상관 분석 (★ 신규) ────────────────────────────────────
    with tab3:
        st.markdown(f"""
        <div style="background:#F8FAFF;border:1px solid #DBEAFE;border-radius:8px;
                    padding:12px 16px;margin-bottom:16px;">
            <span class="lv2">Lv.2</span>
            <b style="font-size:13px;color:#1A1D23;margin-left:8px;">
                {target} ↔ 거시 지표 60일 상관계수
            </b>
            <div style="font-size:11px;color:#6B7280;margin-top:4px;">
                상관계수 범위: -1(완전 역상관) ~ 0(무관) ~ +1(완전 동조)<br>
                <span style="color:#059669;">초록</span>: 이론 방향과 일치 &nbsp;
                <span style="color:#DC2626;">빨강</span>: 이론과 반대로 움직이는 중
                (시장 이상 신호일 수 있음)
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("상관계수 계산 중..."):
            corr_data = get_macro_correlation(target, inds)

        if not corr_data:
            st.info("상관계수 데이터를 불러올 수 없습니다.")
        else:
            # 상관계수 Bar 차트
            names  = [d["name"]      for d in corr_data]
            corrs  = [d["corr"]      for d in corr_data]
            clrs   = [corr_color(d["corr"], d["direction"]) for d in corr_data]
            dirs   = [d["direction"] for d in corr_data]

            bar_fig = go.Figure()
            bar_fig.add_trace(go.Bar(
                y=names, x=corrs,
                orientation="h",
                marker=dict(color=clrs, line=dict(color="#FFFFFF",width=0.5)),
                text=[f"{c:+.2f}" for c in corrs],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=11, color="#374151"),
                hovertemplate="<b>%{y}</b><br>상관계수: %{x:.3f}<extra></extra>",
            ))
            # 이론 방향 표시선 (direction × 점선)
            for i, (c, d) in enumerate(zip(corrs, dirs)):
                pass  # 텍스트로 충분

            bar_fig.add_vline(x=0, line_dash="dash", line_color="#E8EAED", line_width=1)
            bar_fig.add_vrect(x0=-0.15, x1=0.15, fillcolor="rgba(200,200,200,0.08)",
                              line_width=0, annotation_text="무상관 구간",
                              annotation_font_size=10, annotation_font_color="#9CA3AF")

            bar_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6B7280"),
                xaxis=dict(range=[-1.1, 1.1], showgrid=True, gridcolor="#F3F4F6",
                           zeroline=False, tickfont=dict(family="JetBrains Mono",size=10)),
                yaxis=dict(showgrid=False, tickfont=dict(size=12, color="#1A1D23")),
                margin=dict(t=10, b=10, l=10, r=60),
                height=50 + len(names) * 44,
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            # 상세 카드
            st.markdown('<div class="section-hdr" style="margin-top:8px;">지표별 상관 해석</div>',
                        unsafe_allow_html=True)
            for d in sorted(corr_data, key=lambda x: abs(x["corr"]), reverse=True):
                c     = d["corr"]
                clr   = corr_color(c, d["direction"])
                aligned = (c>0 and d["direction"]==+1) or (c<0 and d["direction"]==-1)
                interp = "이론 일치 ✓" if aligned else "이론 역방향 ⚠"
                dir_str = "상승 = 호재" if d["direction"]==+1 else "상승 = 악재"
                st.markdown(f"""
                <div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;
                            padding:10px 14px;margin-bottom:6px;display:flex;
                            justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-size:13px;font-weight:600;color:#1A1D23;">{d['name']}</span>
                        <span style="font-size:10px;color:#9CA3AF;margin-left:5px;">{dir_str}</span>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:16px;
                                    font-weight:700;color:{clr};">{c:+.3f}</div>
                        <div style="font-size:10px;color:{clr};">{interp}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 4: 뉴스 ──────────────────────────────────────────────────
    with tab4:
        if nd:
            for n in nd:
                css   = "news-pos" if n["sentiment"]=="Positive" else "news-neg" if n["sentiment"]=="Negative" else "news-neu"
                icon2 = "▲" if n["sentiment"]=="Positive" else "▼" if n["sentiment"]=="Negative" else "●"
                tc3   = "#059669" if n["sentiment"]=="Positive" else "#DC2626" if n["sentiment"]=="Negative" else "#9CA3AF"
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
            st.info("뉴스 데이터를 불러올 수 없습니다.")

    # ── TAB 5: 계산 근거 (투명성) ────────────────────────────────────
    with tab5:
        st.markdown("""
        <div style="background:#F8FAFF;border:1px solid #DBEAFE;border-radius:8px;
                    padding:14px 16px;margin-bottom:16px;">
            <b style="font-size:13px;color:#1A1D23;">승률 계산 공식 (Lv.1/2)</b>
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                        color:#374151;margin-top:8px;line-height:2;">
                weighted_Z = Σ(z_i × direction_i × driver_weight_i) / Σ(weight_i)<br>
                macro_score = weighted_Z × 15<br>
                z_penalty   = −z_stock × 3<br>
                final       = clamp(50 + z_penalty + macro_score + news_bonus, 5, 95)
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 구성 요소 Bar
        items = [
            ("기본값",       50.0,                      "#9CA3AF"),
            ("주가 위치",    breakdown["z_penalty"],    "#2563EB"),
            ("거시 환경",    breakdown["macro_score"],  zcolor(breakdown["macro_z"])),
            ("뉴스 감성",    breakdown["news_bonus"],   "#059669" if nb>0 else "#DC2626"),
        ]
        comp_fig = go.Figure()
        for lbl, val, clr in items:
            comp_fig.add_trace(go.Bar(
                name=lbl, x=[lbl], y=[val],
                marker_color=clr,
                text=[f"{val:+.1f}"],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=12),
            ))
        comp_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#374151")),
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6", range=[-25, 75]),
            margin=dict(t=20,b=10,l=0,r=0), height=220,
            barmode="group",
        )
        st.plotly_chart(comp_fig, use_container_width=True)

        # 수식 텍스트
        st.markdown(f"""
        <div style="background:#F9FAFB;border:1px solid #E8EAED;border-radius:8px;
                    padding:14px;font-family:'JetBrains Mono',monospace;font-size:12px;
                    color:#374151;line-height:2;">
            50.0 (기본)<br>
            {breakdown['z_penalty']:+.1f} (주가 Z={zs:+.2f} × −3)<br>
            {breakdown['macro_score']:+.1f} (거시 가중Z={breakdown['macro_z']:+.3f} × 15)<br>
            {breakdown['news_bonus']:+.1f} (뉴스 보정)<br>
            ──────────────<br>
            합계 {breakdown['total_raw']:+.1f} → clamp → <b style="color:{sv_};">{fw}%</b>
        </div>
        """, unsafe_allow_html=True)
