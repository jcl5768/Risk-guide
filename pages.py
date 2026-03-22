# pages.py
import streamlit as st
import plotly.graph_objects as go
from config import SECTOR_CONFIG, MACRO_INDICATORS, SENSITIVITY_COLOR, SENSITIVITY_LABEL
from engine import (
    detect_sector, get_z_and_price, get_sector_analysis,
    get_price_history, get_news, get_korean_news, get_yearly_top_news,
    get_macro_correlation, get_chart_data, get_price_stats,
    calc_win_rate, get_weighted_z,
    get_signal, zcolor, zdesc, corr_color,
)


# ── CSS ───────────────────────────────────────────────────────────────────────
def apply_custom_style():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* ── 전체 ── */
.stApp{background:#F2F4F7;color:#1A1D23;font-family:'Inter',sans-serif;}
header[data-testid="stHeader"]{background:#F2F4F7;border-bottom:none;}
.stDeployButton{display:none;} #MainMenu{display:none;} footer{display:none;}
section[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #E8EAED;}

/* ── 카드 ── */
.card{background:#FFFFFF;border-radius:14px;padding:16px 18px;margin-bottom:12px;
      box-shadow:0 1px 4px rgba(0,0,0,0.06);}
.card-sm{background:#FFFFFF;border-radius:10px;padding:12px 14px;margin-bottom:8px;
         box-shadow:0 1px 3px rgba(0,0,0,0.05);}

/* ── 거시 지표 카드 ── */
.macro-chip{background:#FFFFFF;border-radius:12px;padding:14px 16px;
            box-shadow:0 1px 4px rgba(0,0,0,0.06);}

/* ── 종목 카드 ── */
.stock-card{background:#FFFFFF;border-radius:14px;padding:16px 18px;margin-bottom:10px;
            box-shadow:0 1px 4px rgba(0,0,0,0.06);}

/* ── 배지 ── */
.badge-green{background:#E8FFF3;color:#059669;border-radius:20px;padding:4px 12px;font-size:11px;font-weight:700;display:inline-block;}
.badge-yellow{background:#FFFAEB;color:#D97706;border-radius:20px;padding:4px 12px;font-size:11px;font-weight:700;display:inline-block;}
.badge-red{background:#FFF1F1;color:#DC2626;border-radius:20px;padding:4px 12px;font-size:11px;font-weight:700;display:inline-block;}

/* ── 상세 헤더 ── */
.detail-header{background:#FFFFFF;border-radius:14px;padding:16px 20px;margin-bottom:12px;
               box-shadow:0 1px 4px rgba(0,0,0,0.06);}

/* ── KPI 박스 ── */
.kpi-box{background:#F8F9FB;border-radius:10px;padding:10px 12px;text-align:center;}

/* ── 뉴스 카드 ── */
.news-pos{background:#F0FDF4;border-left:3px solid #059669;padding:12px 14px;border-radius:0 10px 10px 0;margin-bottom:8px;}
.news-neg{background:#FEF2F2;border-left:3px solid #DC2626;padding:12px 14px;border-radius:0 10px 10px 0;margin-bottom:8px;}
.news-neu{background:#F9FAFB;border-left:3px solid #D1D5DB;padding:12px 14px;border-radius:0 10px 10px 0;margin-bottom:8px;}
.news-star{background:#FFFBEB;border-left:3px solid #F59E0B;padding:12px 14px;border-radius:0 10px 10px 0;margin-bottom:8px;}

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"]{gap:2px;background:#EBEBEB;border-radius:10px;padding:3px;border:none;}
.stTabs [data-baseweb="tab"]{height:34px;font-size:12px;font-weight:500;color:#6B7280;border-radius:8px;padding:0 14px;}
.stTabs [aria-selected="true"]{background:#FFFFFF !important;color:#1A1D23 !important;font-weight:600 !important;box-shadow:0 1px 4px rgba(0,0,0,0.08);}

/* ── 버튼 ── */
div[data-testid="stButton"] button{background:#FFFFFF;color:#374151;border:1px solid #E8EAED;
    border-radius:8px;font-size:12px;font-weight:500;padding:6px 14px;
    box-shadow:0 1px 2px rgba(0,0,0,0.04);}
div[data-testid="stButton"] button:hover{background:#F9FAFB;border-color:#D1D5DB;}
div[data-testid="stButton"] button[kind="primary"]{background:#1A1D23;color:#FFFFFF;border-color:#1A1D23;}
div[data-testid="stButton"] button[kind="primary"]:hover{background:#374151;}

/* ── 입력 ── */
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{
    background:#F8F9FB !important;border:1px solid #E8EAED !important;
    border-radius:8px !important;color:#1A1D23 !important;font-size:13px !important;}
div[data-testid="stSelectbox"]>div{background:#F8F9FB !important;border:1px solid #E8EAED !important;border-radius:8px !important;}

/* ── 기타 ── */
.stSpinner>div{border-top-color:#2563EB !important;}
.section-lbl{font-size:11px;font-weight:600;color:#6B7280;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:10px;}
.ind-card{background:#FFFFFF;border-radius:10px;padding:12px 14px;margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);}
.sensitivity-high{background:#FEF2F2;color:#DC2626;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.sensitivity-mid{background:#FFFBEB;color:#D97706;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.sensitivity-low{background:#F9FAFB;color:#6B7280;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.lv2{background:#FFF7ED;color:#EA580C;border:1px solid #FED7AA;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
</style>
""", unsafe_allow_html=True)


# ── 유틸 ─────────────────────────────────────────────────────────────────────
def _win_interpretation(fw, inds, zs):
    neg_inds = sorted([x for x in inds if x["z"]*x["direction"]<0],
                      key=lambda x: abs(x["z"]*x["driver_weight"]), reverse=True)
    pos_inds = sorted([x for x in inds if x["z"]*x["direction"]>0],
                      key=lambda x: abs(x["z"]*x["driver_weight"]), reverse=True)
    top_neg = neg_inds[0] if neg_inds else None
    top_pos = pos_inds[0] if pos_inds else None

    if fw >= 70:
        bg, brd, icon, clr = "#F0FDF4", "#A7F3D0", "🟢", "#059669"
        title = "통계적으로 매우 유리한 타점"
        p_drv = f"<b>{top_pos['name']}</b>" if top_pos else "긍정 지표"
        body  = (f"매크로 지표가 상승을 뒷받침하며 주가는 역사적 평균 대비 저평가 구간입니다. "
                 f"특히 {p_drv}가 강한 호재로 작용 중입니다.")
    elif fw >= 45:
        bg, brd, icon, clr = "#FFFBEB", "#FDE68A", "🟡", "#D97706"
        title = "추세 유지 — 단기 변동성 주의"
        n_drv = f"<b>{top_neg['name']}</b>" if top_neg else "일부 지표"
        body  = (f"{n_drv}의 흐름이 단기 변동성을 높일 수 있습니다. "
                 f"주요 매크로 변화를 주시하며 비중을 유지하는 것이 좋습니다.")
    else:
        bg, brd, icon, clr = "#FEF2F2", "#FECACA", "🔴", "#DC2626"
        title = "통계적 하락 압력 — 리스크 경고"
        n_drv = f"<b>{top_neg['name']}</b>({top_neg['desc']})" if top_neg else "거시 지표 악화"
        body  = (f"승률 <b>{fw}%</b> — 하락 압력이 강합니다. 주된 원인: {n_drv}. "
                 f"신규 진입을 자제하고 현금 비중 확대를 권고합니다.")

    return bg, brd, icon, clr, title, body


def _risk_driver_html(inds):
    scored = [
        {**ind, "contrib": ind["z"]*ind["direction"]*ind["driver_weight"]*15}
        for ind in inds
    ]
    neg2 = sorted([x for x in scored if x["contrib"]<0], key=lambda x: x["contrib"])[:2]
    pos1 = sorted([x for x in scored if x["contrib"]>0], key=lambda x: -x["contrib"])[:1]
    blocks = []
    for ind in neg2:
        blocks.append(
            f'<div class="news-neg" style="margin-bottom:8px;">'
            f'<div style="font-size:11px;font-weight:700;color:#DC2626;margin-bottom:3px;">'
            f'▼ 리스크: {ind["name"]} '
            f'<span style="font-family:\'JetBrains Mono\',monospace;">Z={ind["z"]:+.2f}σ</span>'
            f' <span style="color:#9CA3AF;font-weight:400;">가중치 {ind["driver_weight"]:.0%} · 기여 {ind["contrib"]:+.1f}%p</span></div>'
            f'<div style="font-size:12px;color:#374151;">{ind["desc"]}</div></div>'
        )
    for ind in pos1:
        blocks.append(
            f'<div class="news-pos" style="margin-bottom:8px;">'
            f'<div style="font-size:11px;font-weight:700;color:#059669;margin-bottom:3px;">'
            f'▲ 호재: {ind["name"]} '
            f'<span style="font-family:\'JetBrains Mono\',monospace;">Z={ind["z"]:+.2f}σ</span>'
            f' <span style="color:#9CA3AF;font-weight:400;">가중치 {ind["driver_weight"]:.0%} · 기여 {ind["contrib"]:+.1f}%p</span></div>'
            f'<div style="font-size:12px;color:#374151;">{ind["desc"]}</div></div>'
        )
    return "".join(blocks)


def _action_plan_html(fw):
    if fw >= 60:
        clr, lv = "#059669", f"높음 ({fw:.0f}%↑)"
        rows = [("포지션","기존 비중 유지 — 통계적 우위 지속 중. 불필요한 매매 자제"),
                ("수익 전략","분할 익절: +10%, +20% 도달 시 각 1/3씩 매도 고려"),
                ("추가 매수","승률 70% 이상 유지 시 소량 추가 가능 (비중 5% 이내)"),
                ("손절선","매입 단가 -8~-10% 구간 설정 후 엄격 유지")]
    elif fw >= 45:
        clr, lv = "#D97706", f"보통 ({fw:.0f}%)"
        rows = [("포지션","비중 유지 — 추가 매수 자제, 보유량 방어에 집중"),
                ("익절 전략","예약 매도로 익절가 현재가 +5~8%로 상향 조정"),
                ("모니터링","핵심 드라이버 지표 추가 악화 시 비중 축소 검토"),
                ("손절선","매입 단가 -7% 구간 설정, 이탈 시 즉시 실행")]
    else:
        clr, lv = "#DC2626", f"낮음 ({fw:.0f}%↓)"
        rows = [("추가 매수","⛔ 추가 매수 금지 — 하락 추세에서 물타기는 금물"),
                ("손절 재점검","현재 손절선 즉시 재확인 후 엄격히 준수"),
                ("비중 축소","목표 비중의 50~70%까지 축소 고려"),
                ("현금 확보","축소 비중만큼 현금 보유 — 승률 45% 회복 시까지 관망")]

    trs = "".join(
        f'<tr><td style="font-weight:600;color:#374151;font-size:12px;'
        f'white-space:nowrap;padding:9px 12px;border-bottom:1px solid #F3F4F6;">{r[0]}</td>'
        f'<td style="font-size:12px;color:#374151;padding:9px 12px;'
        f'border-bottom:1px solid #F3F4F6;">{r[1]}</td></tr>'
        for r in rows
    )
    return clr, lv, trs


# ── 메인 대시보드 ─────────────────────────────────────────────────────────────
def render_main_page():
    # ── 헤더 ──
    st.markdown(
        '<div style="padding:8px 0 16px;">'
        '<div style="font-size:11px;color:#9CA3AF;font-weight:500;margin-bottom:2px;">'
        'RISK GUIDE · 포트폴리오 분석</div>'
        '<div style="font-size:22px;font-weight:700;color:#1A1D23;">오늘의 포트폴리오 현황</div>'
        '<div style="font-size:13px;color:#6B7280;">섹터별 맞춤 거시지표 기반 통계적 승률 분석</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── 주요 거시 지표 (가로 스크롤 카드) ──
    st.markdown('<div class="section-lbl">📡 주요 거시 지표</div>', unsafe_allow_html=True)
    mc = st.columns(5)
    for col, (label, sym, desc) in zip(mc, MACRO_INDICATORS):
        z, price = get_z_and_price(sym)
        arrow = "▲" if z > 0.2 else "▼" if z < -0.2 else "—"
        ac    = "#059669" if z > 0.2 else "#DC2626" if z < -0.2 else "#6B7280"
        col.markdown(
            f'<div class="macro-chip">'
            f'<div style="font-size:10px;font-weight:600;color:#6B7280;margin-bottom:5px;">{label}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:18px;font-weight:700;color:{zcolor(z)};">'
            f'{price:,.2f} <span style="font-size:13px;color:{ac};">{arrow}</span></div>'
            f'<div style="font-size:10px;color:#9CA3AF;margin-top:3px;">Z {z:+.2f}σ</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 보유 종목 ──
    portfolio = st.session_state.portfolio
    if not portfolio:
        st.markdown(
            '<div style="background:#FFFFFF;border-radius:16px;padding:48px 24px;'
            'text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
            '<div style="font-size:40px;margin-bottom:12px;">📭</div>'
            '<div style="font-size:17px;font-weight:600;color:#374151;margin-bottom:6px;">'
            '아직 종목이 없습니다</div>'
            '<div style="font-size:13px;color:#9CA3AF;">'
            '아래 버튼으로 첫 종목을 추가해보세요</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="section-lbl">📈 보유 종목 분석</div>', unsafe_allow_html=True)

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
                    pnl  = ((price - stock["avg_price"]) / stock["avg_price"] * 100) \
                           if price and stock["avg_price"] > 0 else None
                    pnl_t = f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "미입력"
                    pc    = "#059669" if (pnl or 0) >= 0 else "#DC2626"
                    ti    = max(inds, key=lambda x: abs(x["z"] * x["driver_weight"]))
                    tc    = ti["z"] * ti["direction"]
                    tclr  = "#059669" if tc > 0 else "#DC2626"
                    wz    = get_weighted_z(inds)

                    st.markdown(f"""
<div class="stock-card" style="border-top:3px solid {sv_};">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
        <div>
            <span style="font-weight:700;font-size:16px;color:#1A1D23;">{stock['ticker']}</span>
            <span style="font-size:12px;color:{cfg['color']};margin-left:5px;">{cfg['icon']}</span>
            <div style="font-size:11px;color:#9CA3AF;margin-top:1px;">{stock['name']}</div>
        </div>
        <div class="{sc_}">{st_}</div>
    </div>
    <div style="display:flex;align-items:baseline;gap:5px;margin-bottom:4px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:34px;font-weight:700;
                     color:{sv_};line-height:1;">{win}%</span>
        <span style="font-size:11px;color:#9CA3AF;">승률</span>
    </div>
    <div style="font-size:11px;color:{tclr};margin-bottom:10px;">
        {'▲' if tc>0 else '▼'} {ti['name']} Z{ti['z']:+.1f}
    </div>
    <div style="display:flex;justify-content:space-between;font-size:12px;
                padding-top:10px;border-top:1px solid #F3F4F6;">
        <span style="color:#6B7280;font-weight:500;">${price:.1f}</span>
        <span style="color:{pc};font-weight:600;">{pnl_t}</span>
        <span style="color:#9CA3AF;">{stock['weight']:.1f}%</span>
    </div>
</div>""", unsafe_allow_html=True)
                    st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)
                    if st.button("상세 분석 →", key=f"go_{stock['ticker']}_{rs}"):
                        st.session_state.selected = stock["ticker"]
                        st.session_state.page     = "detail"
                        st.rerun()

        # 파이 차트
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-lbl">📊 포트폴리오 구성</div>', unsafe_allow_html=True)
        cc, bc = st.columns([1, 2])
        with cc:
            labels  = [s["ticker"] for s in portfolio]
            weights = [s["weight"] for s in portfolio]
            colors  = [SECTOR_CONFIG[detect_sector(s["ticker"])]["color"] for s in portfolio]
            fig = go.Figure(go.Pie(
                values=weights, labels=labels, hole=0.62,
                marker=dict(colors=colors, line=dict(color="#F2F4F7", width=3)),
                textfont=dict(family="Inter", size=11),
                hovertemplate="<b>%{label}</b>  %{value:.1f}%<extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                margin=dict(t=4,b=4,l=4,r=4), height=180,
                annotations=[dict(text=f"<b>{sum(weights):.1f}%</b>", x=0.5, y=0.5,
                    font=dict(size=14, color="#1A1D23"), showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
        with bc:
            for s in portfolio:
                sc = SECTOR_CONFIG[detect_sector(s["ticker"])]
                st.markdown(
                    f'<div style="margin-bottom:10px;">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                    f'<span style="font-size:13px;font-weight:600;color:#1A1D23;">{s["ticker"]}'
                    f' <span style="font-size:11px;color:{sc["color"]};">{sc["icon"]}</span></span>'
                    f'<span style="font-size:13px;font-weight:600;color:#2563EB;">{s["weight"]:.1f}%</span>'
                    f'</div>'
                    f'<div style="height:5px;background:#F2F4F7;border-radius:3px;">'
                    f'<div style="height:100%;width:{min(s["weight"],100)}%;'
                    f'background:{sc["color"]};border-radius:3px;opacity:0.85;"></div></div>'
                    f'<div style="font-size:11px;color:#9CA3AF;margin-top:2px;">{s["name"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    # ── 하단 "종목 추가" 버튼 (항상 하단에 고정) ──
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕  종목 추가", use_container_width=True, key="open_add", type="primary"):
        st.session_state.show_add = True
        st.rerun()


# ── 상세 분석 페이지 ──────────────────────────────────────────────────────────
def render_detail_page():
    target = st.session_state.selected or ""
    if not target: st.session_state.page = "main"; st.rerun()

    si = next(
        (s for s in st.session_state.portfolio if s["ticker"] == target),
        {"name": target, "weight": "—", "avg_price": 0, "shares": 0}
    )

    with st.spinner(f"{target} 분석 중..."):
        zs, price       = get_z_and_price(target)
        sk, cfg, inds   = get_sector_analysis(target)
        nb, _           = get_news(target)
        fw, breakdown   = calc_win_rate(zs, inds, nb)
        weighted_z      = get_weighted_z(inds)

    st_, sc_, sv_  = get_signal(fw)
    pnl  = ((price - si["avg_price"]) / si["avg_price"] * 100) if price and si["avg_price"] > 0 else 0
    pc   = "#059669" if pnl >= 0 else "#DC2626"

    # ── 앱 스타일 헤더 (3번째 사진처럼) ──────────────────────────────
    # 뒤로가기 + 티커 + 배지
    col_back, col_title, col_badge = st.columns([1, 4, 2])
    with col_back:
        if st.button("←", key="back_btn"):
            st.session_state.page = "main"; st.rerun()
    with col_title:
        st.markdown(
            f'<div style="padding:4px 0;">'
            f'<div style="font-size:20px;font-weight:700;color:#1A1D23;line-height:1.2;">'
            f'{target} <span style="font-size:14px;color:{cfg["color"]};">{cfg["icon"]}</span></div>'
            f'<div style="font-size:12px;color:#6B7280;">{cfg["label"]} 섹터</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col_badge:
        st.markdown(
            f'<div style="text-align:right;padding-top:6px;">'
            f'<div class="{sc_}">{st_}</div></div>',
            unsafe_allow_html=True
        )

    # 섹터 컬러 라인 (3번째 사진의 오렌지 라인)
    st.markdown(
        f'<div style="height:3px;background:{sv_};border-radius:2px;margin:8px 0 16px;"></div>',
        unsafe_allow_html=True
    )

    # ── 승률 헤더 카드 (3번째 사진 레이아웃) ─────────────────────────
    h_l, h_r = st.columns([2, 1])
    with h_l:
        st.markdown(
            f'<div>'
            f'<div style="font-size:11px;color:#9CA3AF;font-weight:500;margin-bottom:3px;">오늘의 승률</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:52px;'
            f'font-weight:700;color:{sv_};line-height:1;">{fw}%</div>'
            f'<div style="font-size:12px;color:#6B7280;margin-top:4px;">'
            f'뉴스 보정 <b style="color:{"#059669" if nb>0 else "#DC2626"};">{nb:+.1f}%</b>'
            f' · 수익률 <b style="color:{pc};">{"+"if pnl>=0 else ""}{pnl:.1f}%</b></div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with h_r:
        st.markdown(
            f'<div style="text-align:right;">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:22px;'
            f'font-weight:700;color:#1A1D23;">${price:.2f}</div>'
            f'<div style="font-size:13px;color:{zcolor(zs)};margin-top:2px;">'
            f'Z {zs:+.2f}σ</div>'
            f'<div style="font-size:11px;color:#9CA3AF;margin-top:2px;">'
            f'{si.get("shares",0)}주 · 평균 ${si["avg_price"]:.2f}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # 승률 해석 배너
    i_bg, i_brd, i_icon, i_clr, i_title, i_body = _win_interpretation(fw, inds, zs)
    st.markdown(
        f'<div style="background:{i_bg};border-left:4px solid {i_clr};'
        f'border-radius:0 10px 10px 0;padding:10px 14px;margin:12px 0;">'
        f'<div style="font-size:12px;font-weight:700;color:{i_clr};margin-bottom:3px;">'
        f'{i_icon} {i_title}</div>'
        f'<div style="font-size:12px;color:#374151;line-height:1.6;">{i_body}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── 탭 (3번째 사진: 기상도 / 지표 / 뉴스 / 시뮬) ─────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ 기상도", f"📊 지표", "📰 뉴스", "🔮 시뮬"])

    # ════════════════════════════════════════════════════
    # TAB 1: 기상도 (게이지 + 차트카드 + 기간버튼 차트 아래)
    # ════════════════════════════════════════════════════
    with tab1:
        # 게이지 + AI 요약 (3번째 사진처럼 가로 배치)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            g_l, g_r = st.columns([1, 1])
            with g_l:
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number", value=fw,
                    number={"suffix":"%","font":{"family":"JetBrains Mono","size":30,"color":sv_}},
                    gauge={
                        "axis":{"range":[0,100],"tickfont":{"color":"#9CA3AF","size":9},"tickwidth":1},
                        "bar":{"color":sv_,"thickness":0.32},
                        "bgcolor":"#FFFFFF","borderwidth":0,
                        "steps":[
                            {"range":[0,45],  "color":"rgba(220,38,38,0.06)"},
                            {"range":[45,60], "color":"rgba(217,119,6,0.06)"},
                            {"range":[60,100],"color":"rgba(5,150,105,0.06)"},
                        ],
                        "threshold":{"line":{"color":sv_,"width":3},"thickness":0.85,"value":fw},
                    }
                ))
                gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", font={"color":"#1A1D23"},
                    margin=dict(t=8,b=8,l=8,r=8), height=180
                )
                st.plotly_chart(gauge, use_container_width=True)

            with g_r:
                top_pos = sorted([x for x in inds if x["z"]*x["direction"]>0],
                                  key=lambda x: abs(x["z"]*x["driver_weight"]), reverse=True)
                top_neg = sorted([x for x in inds if x["z"]*x["direction"]<0],
                                  key=lambda x: abs(x["z"]*x["driver_weight"]), reverse=True)
                ps  = top_pos[0]["name"] if top_pos else "없음"
                ns2 = top_neg[0]["name"] if top_neg else "없음"
                st.markdown(
                    f'<div style="background:#F0FDF4;border-radius:10px;padding:14px;'
                    f'margin-top:16px;">'
                    f'<div style="font-size:11px;font-weight:700;color:#059669;margin-bottom:8px;">'
                    f'AI 요약</div>'
                    f'<div style="font-size:13px;color:#374151;line-height:1.7;">'
                    f'<span style="color:#059669;">▲ {ps}</span> 긍정적<br>'
                    f'<span style="color:#DC2626;">▼ {ns2}</span> 리스크</div></div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

        # 차트 카드 (3번째 사진: 카드 안에 차트, 기간 버튼 차트 아래)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # 차트 먼저
        pk = st.session_state.chart_period
        with st.spinner(""):
            df    = get_chart_data(target, pk)
            stats = get_price_stats(df)

        if not df.empty and "Close" in df.columns:
            r, g, b = int(sv_[1:3],16), int(sv_[3:5],16), int(sv_[5:7],16)
            if pk in ("1달","1년") and all(c in df.columns for c in ["Open","High","Low","Close"]):
                chart_fig = go.Figure()
                chart_fig.add_trace(go.Candlestick(
                    x=df["Date"], open=df["Open"], high=df["High"],
                    low=df["Low"], close=df["Close"],
                    increasing_line_color="#059669", decreasing_line_color="#DC2626",
                    increasing_fillcolor="rgba(5,150,105,0.85)",
                    decreasing_fillcolor="rgba(220,38,38,0.85)",
                    name=target,
                    hovertext=df.apply(
                        lambda row: f"O${row['Open']:.2f}  H${row['High']:.2f}  "
                                    f"L${row['Low']:.2f}  C${row['Close']:.2f}", axis=1),
                    hoverinfo="x+text",
                ))
                if len(df) >= 20:
                    ma20 = df["Close"].rolling(20).mean()
                    chart_fig.add_trace(go.Scatter(
                        x=df["Date"], y=ma20, mode="lines",
                        line=dict(color="#D97706", width=1.5, dash="dash"), name="MA20"
                    ))
            else:
                chart_fig = go.Figure()
                chart_fig.add_trace(go.Scatter(
                    x=df["Date"], y=df["Close"], mode="lines",
                    line=dict(color=sv_, width=2.5, shape="spline", smoothing=0.6),
                    fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.08)",
                    name=target, hovertemplate="$%{y:.2f}  %{x}<extra></extra>",
                ))

            chart_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#9CA3AF", size=11),
                xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#9CA3AF"),
                           rangeslider=dict(visible=False), color="#E8EAED"),
                yaxis=dict(showgrid=True, gridcolor="rgba(232,234,237,0.5)",
                           gridwidth=0.5, tickfont=dict(size=10, color="#9CA3AF")),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11),
                            orientation="h", y=1.04, x=0),
                margin=dict(t=6, b=0, l=0, r=0),
                height=260, hovermode="x unified",
            )
            st.plotly_chart(chart_fig, use_container_width=True)

            # 거래량 (작게)
            if "Volume" in df.columns and df["Volume"].sum() > 0:
                vc = [
                    "#059669" if i > 0 and df["Close"].iloc[i] >= df["Close"].iloc[i-1]
                    else "#DC2626" if i > 0 else "#9CA3AF"
                    for i in range(len(df))
                ]
                vf = go.Figure(go.Bar(
                    x=df["Date"], y=df["Volume"],
                    marker_color=vc, opacity=0.5,
                    hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"
                ))
                vf.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, tickfont=dict(size=9, color="#9CA3AF")),
                    yaxis=dict(showgrid=False, tickformat=".2s", tickfont=dict(size=9, color="#9CA3AF")),
                    margin=dict(t=0, b=2, l=0, r=0), height=52, showlegend=False,
                )
                st.plotly_chart(vf, use_container_width=True)
        else:
            st.info("차트 데이터를 불러올 수 없습니다.")

        # ── 기간 선택 버튼 (차트 아래, 작게) ── 3번째 사진 스타일
        p_cols = st.columns([1, 1, 1, 1, 4])
        for idx, label in enumerate(["일", "주", "달", "년"]):
            pk_map = {"일":"1일","주":"1주","달":"1달","년":"1년"}
            pk_key = pk_map[label]
            with p_cols[idx]:
                is_sel = (st.session_state.chart_period == pk_key)
                if st.button(
                    label, key=f"pk_{label}",
                    use_container_width=True,
                    type="primary" if is_sel else "secondary"
                ):
                    st.session_state.chart_period = pk_key; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # 스탯 행 (차트 카드 아래)
        s_cols = st.columns(4)
        stat_items = [
            ("기간 수익", f"{'+'if stats['period_ret']>=0 else ''}{stats['period_ret']:.1f}%",
             "#059669" if stats["period_ret"] >= 0 else "#DC2626"),
            ("최대 상승", f"+{stats['max_gain']:.2f}%", "#059669"),
            ("최대 하락", f"{stats['max_loss']:.2f}%",  "#DC2626"),
            ("변동성",    f"{stats['volatility']:.1f}%", "#D97706"),
        ]
        for col, (lbl, val, clr) in zip(s_cols, stat_items):
            col.markdown(
                f'<div class="kpi-box">'
                f'<div style="font-size:9px;color:#9CA3AF;font-weight:500;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:3px;">{lbl}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:14px;'
                f'font-weight:700;color:{clr};">{val}</div></div>',
                unsafe_allow_html=True
            )

        # KPI 4개
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        kc = st.columns(4)
        for col, (lbl, val, clr) in zip(kc, [
            ("현재가",  f"${price:.2f}", "#1A1D23"),
            ("주가 Z",  f"{zs:+.2f}σ",   zcolor(zs)),
            ("거시 Z",  f"{weighted_z:+.2f}", zcolor(weighted_z)),
            ("수익률",  f"{'+'if pnl>=0 else ''}{pnl:.1f}%", pc),
        ]):
            col.markdown(
                f'<div class="kpi-box">'
                f'<div style="font-size:9px;color:#9CA3AF;font-weight:500;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:3px;">{lbl}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:15px;'
                f'font-weight:700;color:{clr};">{val}</div></div>',
                unsafe_allow_html=True
            )

    # ════════════════════════════════════════════════════
    # TAB 2: 섹터 지표 & 리스크 드라이버 & Action Plan
    # ════════════════════════════════════════════════════
    with tab2:
        macro_sign    = "+" if weighted_z * 15 >= 0 else ""
        macro_contrib = f"{macro_sign}{weighted_z*15:.1f}"

        st.markdown(
            f'<div class="card-sm" style="margin-bottom:12px;">'
            f'<div style="font-size:12px;font-weight:700;color:#1A1D23;margin-bottom:3px;">'
            f'{cfg["icon"]} {cfg["label"]} — {len(inds)}개 드라이버</div>'
            f'<div style="font-size:11px;color:#6B7280;">📌 {cfg["cycle_note"]}</div>'
            f'<div style="font-size:11px;color:#6B7280;margin-top:3px;">'
            f'거시 가중 Z: <b style="color:{zcolor(weighted_z)};">{weighted_z:+.3f}σ</b>'
            f' → 승률 기여 <b style="color:{zcolor(weighted_z)};">{macro_contrib}%p</b></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        for ind in inds:
            eff_z   = ind["z"] * ind["direction"]
            contrib = eff_z * ind["driver_weight"] * 15
            cc2     = "#059669" if contrib > 0 else "#DC2626" if contrib < 0 else "#6B7280"
            wlbl    = f"호재×{ind['driver_weight']:.0%}" if ind["direction"]==+1 else f"악재×{ind['driver_weight']:.0%}"
            wclr    = "#059669" if ind["direction"]==+1 else "#DC2626"
            sens    = ind.get("sensitivity","mid")
            bs      = 50.0 if eff_z >= 0 else max(0.0, 50.0 - min(50.0, abs(eff_z)/3*50))
            bw      = min(50.0, abs(eff_z)/3*50)

            st.markdown(f"""
<div class="ind-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
        <div>
            <span style="font-size:13px;font-weight:600;color:#1A1D23;">{ind['name']}</span>
            <span style="font-size:10px;color:#9CA3AF;margin-left:5px;">({ind['ticker']})</span>
            <span class="sensitivity-{sens}" style="margin-left:5px;">{SENSITIVITY_LABEL.get(sens,'')}</span>
            <div style="font-size:11px;color:#9CA3AF;margin-top:2px;">{ind['desc']}</div>
        </div>
        <div style="text-align:right;min-width:72px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:14px;
                        font-weight:700;color:{zcolor(ind['z'])};">{ind['z']:+.2f}σ</div>
            <div style="font-size:9px;color:{zcolor(ind['z'])};">{zdesc(ind['z'])}</div>
        </div>
    </div>
    <div style="height:4px;background:#F2F4F7;border-radius:2px;position:relative;margin-bottom:5px;">
        <div style="position:absolute;top:0;left:49.5%;width:1px;height:100%;background:#E8EAED;"></div>
        <div style="position:absolute;top:0;left:{bs}%;width:{bw}%;height:100%;
                    background:{zcolor(ind['z'])};border-radius:2px;opacity:0.8;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:11px;">
        <span style="color:{wclr};">{wlbl}</span>
        <span style="color:{cc2};font-weight:600;">{'+'if contrib>0 else ''}{contrib:.1f}%p</span>
    </div>
</div>""", unsafe_allow_html=True)

        # 리스크 드라이버 심화
        st.markdown(
            '<div style="font-size:11px;font-weight:600;color:#6B7280;letter-spacing:0.8px;'
            'text-transform:uppercase;margin:14px 0 8px;">🔍 리스크 드라이버 심화</div>',
            unsafe_allow_html=True
        )
        st.markdown(_risk_driver_html(inds), unsafe_allow_html=True)

        # Action Plan
        st.markdown("<br>", unsafe_allow_html=True)
        ap_clr, ap_lv, ap_trs = _action_plan_html(fw)
        st.markdown(
            f'<div class="card">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
            f'<div style="font-size:13px;font-weight:700;color:#1A1D23;">📋 실전 Action Plan</div>'
            f'<div style="background:{ap_clr};color:#FFFFFF;font-size:11px;font-weight:600;'
            f'padding:3px 10px;border-radius:20px;">{ap_lv}</div></div>'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<thead><tr>'
            f'<th style="background:#F8F9FB;color:#6B7280;font-weight:600;font-size:11px;'
            f'padding:8px 12px;text-align:left;border-bottom:1px solid #E8EAED;width:90px;">항목</th>'
            f'<th style="background:#F8F9FB;color:#6B7280;font-weight:600;font-size:11px;'
            f'padding:8px 12px;text-align:left;border-bottom:1px solid #E8EAED;">권장 행동</th>'
            f'</tr></thead><tbody>{ap_trs}</tbody></table></div>',
            unsafe_allow_html=True
        )

    # ════════════════════════════════════════════════════
    # TAB 3: 뉴스 — 연간 주요 + 최근 뉴스
    # ════════════════════════════════════════════════════
    with tab3:
        nl, nr = st.columns([2, 1])
        with nl:
            # ── 섹션 1: 연간 주요 뉴스 ──
            st.markdown(
                '<div style="font-size:11px;font-weight:600;color:#6B7280;letter-spacing:0.8px;'
                'text-transform:uppercase;margin-bottom:8px;">⭐ 연간 주요 뉴스 (임팩트 높은 순)</div>',
                unsafe_allow_html=True
            )
            with st.spinner("연간 주요 뉴스 수집 중..."):
                yearly_news = get_yearly_top_news(target, si.get("name",""))

            if yearly_news:
                for n in yearly_news:
                    css = (
                        "news-star"    if n["impact"] >= 2 else
                        "news-pos"     if n["sentiment"]=="Positive" else
                        "news-neg"     if n["sentiment"]=="Negative" else
                        "news-neu"
                    )
                    icon = "⭐" if n["impact"] >= 2 else ("▲" if n["sentiment"]=="Positive" else "▼" if n["sentiment"]=="Negative" else "●")
                    tc = "#F59E0B" if n["impact"] >= 2 else ("#059669" if n["sentiment"]=="Positive" else "#DC2626" if n["sentiment"]=="Negative" else "#9CA3AF")
                    st.markdown(
                        f'<div class="{css}">'
                        f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
                        f'<span style="font-size:10px;font-weight:700;color:{tc};">'
                        f'{icon} {n["sentiment"].upper()} · 임팩트 {"★"*min(n["impact"],3)}</span>'
                        f'<div style="font-size:10px;color:#9CA3AF;">'
                        f'{n.get("source","")} {n.get("pub_date","")}</div></div>'
                        f'<a href="{n["link"]}" target="_blank" '
                        f'style="font-size:13px;font-weight:500;color:#1A1D23;'
                        f'text-decoration:none;line-height:1.5;">{n["title"]}</a></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div style="color:#9CA3AF;font-size:12px;">연간 주요 뉴스를 불러올 수 없습니다.</div>', unsafe_allow_html=True)

            # ── 섹션 2: 최근 뉴스 ──
            st.markdown(
                '<div style="font-size:11px;font-weight:600;color:#6B7280;letter-spacing:0.8px;'
                'text-transform:uppercase;margin:16px 0 8px;">📅 최근 주요 뉴스 (실시간)</div>',
                unsafe_allow_html=True
            )
            with st.spinner("최근 뉴스 수집 중..."):
                ko_bonus, recent_news = get_korean_news(target, si.get("name",""))

            if recent_news:
                for n in recent_news:
                    css  = "news-pos" if n["sentiment"]=="Positive" else "news-neg" if n["sentiment"]=="Negative" else "news-neu"
                    icon = "▲" if n["sentiment"]=="Positive" else "▼" if n["sentiment"]=="Negative" else "●"
                    tc   = "#059669" if n["sentiment"]=="Positive" else "#DC2626" if n["sentiment"]=="Negative" else "#9CA3AF"
                    st.markdown(
                        f'<div class="{css}">'
                        f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
                        f'<span style="font-size:10px;font-weight:700;color:{tc};">{icon} {n["sentiment"].upper()}</span>'
                        f'<div style="font-size:10px;color:#9CA3AF;">'
                        f'{n.get("source","")} {n.get("pub_date","")}</div></div>'
                        f'<a href="{n["link"]}" target="_blank" '
                        f'style="font-size:13px;font-weight:500;color:#1A1D23;'
                        f'text-decoration:none;line-height:1.5;">{n["title"]}</a></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div style="color:#9CA3AF;font-size:12px;">최근 뉴스를 불러올 수 없습니다.</div>', unsafe_allow_html=True)

        with nr:
            # 감성 도넛
            all_news_combined = yearly_news + recent_news if yearly_news else recent_news
            if all_news_combined:
                pos_c = sum(1 for n in all_news_combined if n["sentiment"]=="Positive")
                neg_c = sum(1 for n in all_news_combined if n["sentiment"]=="Negative")
                neu_c = sum(1 for n in all_news_combined if n["sentiment"]=="Neutral")
                sf = go.Figure(go.Pie(
                    values=[max(pos_c,0.01), max(neg_c,0.01), max(neu_c,0.01)],
                    labels=["긍정","부정","중립"], hole=0.62,
                    marker=dict(colors=["#059669","#DC2626","#D1D5DB"],
                                line=dict(color="#F2F4F7",width=3)),
                    textfont=dict(family="Inter",size=10),
                ))
                nb_clr = "#059669" if ko_bonus > 0 else "#DC2626" if ko_bonus < 0 else "#9CA3AF"
                sf.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                    legend=dict(font=dict(color="#6B7280",size=11),bgcolor="rgba(0,0,0,0)"),
                    margin=dict(t=0,b=0,l=0,r=0), height=160,
                    annotations=[dict(text=f"<b>{ko_bonus:+.0f}%</b>",x=0.5,y=0.5,
                        font=dict(size=16,color=nb_clr,family="JetBrains Mono"),showarrow=False)]
                )
                st.plotly_chart(sf, use_container_width=True)
                st.markdown(
                    f'<div class="kpi-box" style="text-align:center;">'
                    f'<div style="font-size:10px;color:#9CA3AF;margin-bottom:4px;">뉴스 승률 보정</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:18px;'
                    f'font-weight:700;color:{nb_clr};">{ko_bonus:+.1f}%</div></div>',
                    unsafe_allow_html=True
                )

    # ════════════════════════════════════════════════════
    # TAB 4: 시뮬레이션
    # ════════════════════════════════════════════════════
    with tab4:
        st.markdown(
            f'<div style="font-size:13px;color:#6B7280;margin-bottom:16px;">'
            f'{cfg["icon"]} <b>{cfg["label"]}</b> 섹터 지표를 직접 조정하여 승률 변화를 시뮬레이션합니다.</div>',
            unsafe_allow_html=True
        )
        sim_inds = []
        for ind in inds:
            d = st.slider(
                f"{ind['name']}  ({ind['ticker']})",
                -3.0, 3.0, float(ind["z"]), 0.1,
                key=f"sim_{ind['ticker']}"
            )
            sim_inds.append({**ind, "z": d})
        sn  = st.slider("📰 뉴스 보정(%)", -15.0, 15.0, float(nb), 0.5)
        sw, _ = calc_win_rate(zs, sim_inds, sn)
        dw  = sw - fw
        ss_, sc2_, sv2_ = get_signal(sw)
        dw_clr = "#059669" if dw > 0 else "#DC2626" if dw < 0 else "#6B7280"

        st.markdown(
            f'<div class="card" style="text-align:center;border-top:3px solid {sv2_};">'
            f'<div style="font-size:11px;color:#9CA3AF;margin-bottom:4px;">시뮬레이션 결과</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:48px;'
            f'font-weight:700;color:{sv2_};line-height:1;">{sw}%</div>'
            f'<div style="font-size:13px;margin-top:8px;font-weight:600;color:{dw_clr};">'
            f'{"▲" if dw>0 else "▼" if dw<0 else "—"} 현재 대비 {dw:+.1f}%p</div>'
            f'<div class="{sc2_}" style="margin-top:10px;display:inline-block;">{ss_}</div></div>',
            unsafe_allow_html=True
        )
