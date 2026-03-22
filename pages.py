# pages.py
import streamlit as st
import plotly.graph_objects as go
from config import SECTOR_CONFIG, MACRO_INDICATORS, SENSITIVITY_COLOR, SENSITIVITY_LABEL
from engine import (
    detect_sector, get_z_and_price, get_sector_analysis,
    get_price_history, get_news, get_korean_news,
    get_macro_correlation, get_chart_data, get_price_stats,
    calc_win_rate, get_weighted_z,
    get_signal, zcolor, zdesc, corr_color,
)


def apply_custom_style():
    st.markdown("""
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
.news-pos{background:#ECFDF5;border-left:3px solid #059669;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}
.news-neg{background:#FEF2F2;border-left:3px solid #DC2626;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}
.news-neu{background:#F9FAFB;border-left:3px solid #D1D5DB;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}
.ind-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:12px 16px;margin-bottom:8px;}
.sensitivity-high{background:#FEF2F2;color:#DC2626;border:1px solid #FECACA;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.sensitivity-mid{background:#FFFBEB;color:#D97706;border:1px solid #FDE68A;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.sensitivity-low{background:#F9FAFB;color:#6B7280;border:1px solid #E8EAED;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.stat-box{background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:10px;text-align:center;}
/* 기간 선택 버튼 — 선택된 것 강조 */
.period-btn-active button{background:#1A1D23 !important;color:#FFFFFF !important;border-color:#1A1D23 !important;font-weight:700 !important;}
/* 기간 버튼 전체 — 작고 심플 */
div[data-testid="stButton"][data-key^="p_"] button{font-size:11px !important;padding:3px 8px !important;height:28px !important;min-height:0 !important;}
/* Action Plan 테이블 */
.action-table{width:100%;border-collapse:collapse;font-size:12px;}
.action-table th{background:#F9FAFB;color:#6B7280;font-weight:600;padding:8px 12px;text-align:left;border-bottom:1px solid #E8EAED;}
.action-table td{padding:10px 12px;border-bottom:1px solid #F3F4F6;color:#374151;vertical-align:top;}
.action-table tr:last-child td{border-bottom:none;}
div[data-testid="stButton"] button{background:#FFFFFF;color:#374151;border:1px solid #D1D5DB;border-radius:7px;font-size:12px;font-weight:500;padding:6px 16px;}
div[data-testid="stButton"] button:hover{background:#F9FAFB;border-color:#9CA3AF;}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input,div[data-testid="stSelectbox"] div{background:#FFFFFF !important;border:1px solid #D1D5DB !important;border-radius:7px !important;color:#1A1D23 !important;font-size:13px !important;}
.stTabs [data-baseweb="tab-list"]{gap:2px;background:#F3F4F6;border-radius:8px;padding:3px;border:1px solid #E8EAED;}
.stTabs [data-baseweb="tab"]{height:32px;font-size:12px;font-weight:500;color:#6B7280;border-radius:6px;padding:0 14px;}
.stTabs [aria-selected="true"]{background:#FFFFFF !important;color:#1A1D23 !important;box-shadow:0 1px 3px rgba(0,0,0,0.1);}
.stSlider > div > div > div{background:#2563EB !important;}
.stSpinner > div{border-top-color:#2563EB !important;}
</style>
""", unsafe_allow_html=True)


# ── 승률 해석 텍스트 생성 ─────────────────────────────────────────────────────
def _win_rate_interpretation(fw, inds, zs, weighted_z):
    """
    승률 수치에 따른 상황 해석 텍스트 반환.
    핵심 리스크 드라이버 이름·설명도 포함.
    """
    # 가장 큰 부정 기여 지표 찾기
    neg_contribs = sorted(
        [ind for ind in inds if ind["z"] * ind["direction"] < 0],
        key=lambda x: abs(x["z"] * x["driver_weight"]),
        reverse=True
    )
    pos_contribs = sorted(
        [ind for ind in inds if ind["z"] * ind["direction"] > 0],
        key=lambda x: abs(x["z"] * x["driver_weight"]),
        reverse=True
    )

    top_neg = neg_contribs[0] if neg_contribs else None
    top_pos = pos_contribs[0] if pos_contribs else None

    if fw >= 70:
        bg, border, icon = "#F0FDF4", "#A7F3D0", "🟢"
        title = "통계적으로 매우 유리한 타점"
        pos_driver = f"<b>{top_pos['name']}</b>" if top_pos else "긍정 지표"
        body = (
            f"매크로 지표가 종목의 상승을 뒷받침하고 있으며, "
            f"주가는 역사적 평균 대비 저평가 구간({zs:+.2f}σ)에 위치합니다. "
            f"특히 {pos_driver}가 강한 호재로 작용 중입니다."
        )
        text_clr = "#059669"

    elif fw >= 45:
        bg, border, icon = "#FFFBEB", "#FDE68A", "🟡"
        title = "추세 유지 중 — 단기 변동성 주의"
        neg_driver = f"<b>{top_neg['name']}</b>({top_neg['desc']})" if top_neg else "일부 지표"
        body = (
            f"추세가 유지되고 있으나 {neg_driver}의 변화가 "
            f"단기 변동성을 높일 수 있습니다. "
            f"주요 매크로 지표의 변화를 주시하며 비중을 유지하는 것이 좋습니다."
        )
        text_clr = "#D97706"

    else:
        bg, border, icon = "#FEF2F2", "#FECACA", "🔴"
        title = "통계적 하락 압력 — 리스크 경고"
        neg_driver = (
            f"<b>{top_neg['name']}</b> ({top_neg['desc']})"
            if top_neg else "거시 지표 악화"
        )
        body = (
            f"현재 승률은 <b>{fw}%</b>로, 통계적 하락 압력이 강합니다. "
            f"주된 원인은 {neg_driver}입니다. "
            f"신규 진입을 자제하고 현금 비중 확대를 권고합니다."
        )
        text_clr = "#DC2626"

    return bg, border, icon, title, body, text_clr


# ── 리스크 드라이버 심화 분석 텍스트 ─────────────────────────────────────────
def _risk_driver_analysis(inds, fw):
    """
    가장 부정적으로 작용하는 지표를 골라 구체적 설명 생성.
    config.py의 desc 필드와 driver_weight를 활용.
    """
    # 방향 반영 기여 계산
    scored = []
    for ind in inds:
        eff = ind["z"] * ind["direction"]
        contrib = eff * ind["driver_weight"] * 15
        scored.append({**ind, "contrib": contrib, "eff_z": eff})

    # 부정 기여 top 2
    neg_sorted = sorted([x for x in scored if x["contrib"] < 0],
                        key=lambda x: x["contrib"])[:2]
    # 긍정 기여 top 1
    pos_sorted = sorted([x for x in scored if x["contrib"] > 0],
                        key=lambda x: -x["contrib"])[:1]

    blocks = []

    for ind in neg_sorted:
        z_str   = f"Z={ind['z']:+.2f}σ"
        w_pct   = f"{ind['driver_weight']:.0%}"
        contrib = f"{ind['contrib']:+.1f}%p"
        blocks.append(
            f'<div style="background:#FEF2F2;border-left:3px solid #DC2626;'
            f'border-radius:0 6px 6px 0;padding:10px 14px;margin-bottom:8px;">'
            f'<div style="font-size:11px;font-weight:700;color:#DC2626;margin-bottom:3px;">'
            f'▼ 리스크: {ind["name"]} ({ind["ticker"]})&nbsp;&nbsp;'
            f'<span style="font-family:\'JetBrains Mono\',monospace;">{z_str}</span>&nbsp;&nbsp;'
            f'<span style="color:#9CA3AF;font-weight:400;">가중치 {w_pct} · 승률 기여 {contrib}</span></div>'
            f'<div style="font-size:12px;color:#374151;line-height:1.6;">'
            f'{ind["desc"]} — 현재 이 지표가 하방 압력을 가하고 있습니다.</div></div>'
        )

    for ind in pos_sorted:
        z_str   = f"Z={ind['z']:+.2f}σ"
        w_pct   = f"{ind['driver_weight']:.0%}"
        contrib = f"{ind['contrib']:+.1f}%p"
        blocks.append(
            f'<div style="background:#ECFDF5;border-left:3px solid #059669;'
            f'border-radius:0 6px 6px 0;padding:10px 14px;margin-bottom:8px;">'
            f'<div style="font-size:11px;font-weight:700;color:#059669;margin-bottom:3px;">'
            f'▲ 호재: {ind["name"]} ({ind["ticker"]})&nbsp;&nbsp;'
            f'<span style="font-family:\'JetBrains Mono\',monospace;">{z_str}</span>&nbsp;&nbsp;'
            f'<span style="color:#9CA3AF;font-weight:400;">가중치 {w_pct} · 승률 기여 {contrib}</span></div>'
            f'<div style="font-size:12px;color:#374151;line-height:1.6;">'
            f'{ind["desc"]} — 현재 이 지표가 상방 모멘텀을 제공하고 있습니다.</div></div>'
        )

    return "".join(blocks)


# ── Action Plan 생성 ─────────────────────────────────────────────────────────
def _action_plan(fw):
    """승률 구간별 실전 대응 권장 행동 반환"""
    if fw >= 60:
        level_clr = "#059669"
        level_txt = f"높음 ({fw:.0f}%↑)"
        actions = [
            ("포지션 관리",   "기존 비중 유지 — 통계적 우위가 지속되는 동안 불필요한 매매를 줄입니다."),
            ("수익 극대화",   "분할 익절 전략: 수익이 +10%, +20% 도달 시 각 1/3씩 매도를 고려합니다."),
            ("추가 매수",     "승률 70% 이상 유지 시 소량 추가 매수 가능 (전체 비중 5% 이내 확대)."),
            ("손절선",        "매입 단가 대비 -8% ~ -10% 구간을 손절선으로 설정하고 유지합니다."),
        ]
    elif fw >= 45:
        level_clr = "#D97706"
        level_txt = f"보통 ({fw:.0f}%)"
        actions = [
            ("포지션 관리",   "비중 유지 — 추가 매수는 자제. 현재 보유량을 지키는 데 집중합니다."),
            ("익절 전략",     "예약 매도(지정가)를 통해 익절가를 현재가 +5~8% 수준으로 상향 조정합니다."),
            ("변수 모니터링", "핵심 드라이버 지표(위 리스크 항목)가 추가로 악화되면 비중 축소를 검토합니다."),
            ("손절선",        "매입 단가 대비 -7% 구간을 손절선으로 설정하고 이탈 시 즉시 실행합니다."),
        ]
    else:
        level_clr = "#DC2626"
        level_txt = f"낮음 ({fw:.0f}%↓)"
        actions = [
            ("추가 매수",     "⛔ 추가 매수 금지 — 하락 추세에서 평균 단가를 낮추는 물타기는 금물입니다."),
            ("손절 재점검",   "현재 보유 포지션의 손절선을 즉시 재확인하고, 기 설정된 손절선을 엄격히 준수합니다."),
            ("비중 축소",     "전체 포트폴리오 내 이 종목의 비중을 목표 비중의 50~70%까지 축소를 고려합니다."),
            ("현금 확보",     "축소한 비중만큼 현금으로 보유하며, 승률이 45% 이상 회복될 때까지 관망합니다."),
        ]

    rows = "".join(
        f'<tr><td style="font-weight:600;color:#374151;white-space:nowrap;">{a[0]}</td>'
        f'<td>{a[1]}</td></tr>'
        for a in actions
    )

    return level_clr, level_txt, rows


# ── 메인 대시보드 ─────────────────────────────────────────────────────────────
def render_main_page():
    st.markdown(
        '<div style="margin-bottom:20px;">'
        '<h2 style="font-size:22px;font-weight:700;color:#1A1D23;margin:0;">📊 포트폴리오 현황</h2>'
        '<p style="font-size:13px;color:#6B7280;margin:4px 0 0;">섹터 드라이버 가중 Z-Score 기반 승률 분석</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # 거시 지표
    st.markdown('<div class="section-hdr">📡 주요 거시 지표</div>', unsafe_allow_html=True)
    mc = st.columns(5)
    for col, (label, sym, desc) in zip(mc, MACRO_INDICATORS):
        z, price = get_z_and_price(sym)
        arrow = "▲" if z > 0.2 else "▼" if z < -0.2 else "—"
        ac    = "#059669" if z > 0.2 else "#DC2626" if z < -0.2 else "#6B7280"
        col.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:8px 12px;">'
            f'<div style="font-size:9px;font-weight:600;color:#9CA3AF;margin-bottom:2px;letter-spacing:0.3px;">{label}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:14px;font-weight:700;color:{zcolor(z)};line-height:1.2;">'
            f'{price:,.2f} <span style="font-size:11px;color:{ac};">{arrow}</span></div>'
            f'<div style="font-size:9px;color:#B0B7C3;margin-top:2px;">Z {z:+.2f}σ</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    portfolio = st.session_state.portfolio

    if not portfolio:
        st.markdown(
            '<div style="background:#FFFFFF;border:2px dashed #D1D5DB;border-radius:12px;'
            'padding:48px;text-align:center;">'
            '<div style="font-size:36px;margin-bottom:10px;">📭</div>'
            '<div style="font-size:16px;font-weight:600;color:#374151;margin-bottom:6px;">아직 종목이 없습니다</div>'
            '<div style="font-size:13px;color:#9CA3AF;">왼쪽 사이드바에서 <b>➕ 종목 추가</b>를 눌러주세요.</div>'
            '<div style="font-size:11px;color:#D1D5DB;margin-top:8px;">예시: AAPL · TSLA · NVDA · XOM · JPM</div>'
            '</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown(
        '<div class="section-hdr">📈 보유 종목 분석 '
        '<span class="lv1" style="margin-left:6px;">Lv.1 / Lv.2</span></div>',
        unsafe_allow_html=True
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
                pnl = ((price - stock["avg_price"]) / stock["avg_price"] * 100) \
                      if price and stock["avg_price"] > 0 else None
                pnl_text = f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "미입력"
                pc   = "#059669" if (pnl or 0) >= 0 else "#DC2626"
                ti   = max(inds, key=lambda x: abs(x["z"] * x["driver_weight"]))
                tc   = ti["z"] * ti["direction"]
                tclr = "#059669" if tc > 0 else "#DC2626"
                weighted_z = get_weighted_z(inds)

                st.markdown(f"""
<div class="stock-card" style="border-top:3px solid {sv_};">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
        <div><span style="font-weight:700;font-size:15px;color:#1A1D23;">{stock['ticker']}</span>
        <span style="font-size:11px;color:{cfg['color']};margin-left:4px;">{cfg['icon']}</span>
        <div style="font-size:10px;color:#9CA3AF;">{stock['name']}</div></div>
        <div class="{sc_}">{st_}</div>
    </div>
    <div style="display:flex;align-items:baseline;gap:4px;margin-bottom:2px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:700;
                     color:{sv_};line-height:1;">{win}%</span>
        <span style="font-size:10px;color:#9CA3AF;" title="{breakdown['explain']}">승률 ❔</span>
    </div>
    <div style="font-size:10px;color:#9CA3AF;margin-bottom:4px;">
        거시Z <span style="color:{zcolor(weighted_z)};font-weight:600;">{weighted_z:+.2f}</span>
    </div>
    <div style="font-size:10px;color:{tclr};margin-bottom:8px;">
        {'▲' if tc>0 else '▼'} {ti['name']} 핵심 드라이버
    </div>
    <div style="display:flex;justify-content:space-between;font-size:11px;
                padding-top:8px;border-top:1px solid #F3F4F6;">
        <span style="color:#6B7280;">${price:.1f}</span>
        <span style="color:{pc};font-weight:500;">{pnl_text}</span>
        <span style="color:#9CA3AF;">{stock['weight']:.1f}%</span>
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
            hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10), height=200,
            annotations=[dict(
                text=f"<b>{sum(weights):.1f}%</b>", x=0.5, y=0.5,
                font=dict(size=14, color="#1A1D23"), showarrow=False
            )]
        )
        st.plotly_chart(fig, use_container_width=True)
    with bc:
        for s in portfolio:
            sc = SECTOR_CONFIG[detect_sector(s["ticker"])]
            st.markdown(
                f'<div style="margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                f'<span style="font-size:13px;font-weight:600;color:#1A1D23;">'
                f'{s["ticker"]} <span style="font-size:11px;color:{sc["color"]};">'
                f'{sc["icon"]} {sc["label"]}</span></span>'
                f'<span style="font-size:13px;font-weight:600;color:#2563EB;">{s["weight"]:.1f}%</span></div>'
                f'<div style="height:4px;background:#F3F4F6;border-radius:2px;">'
                f'<div style="height:100%;width:{min(s["weight"],100)}%;'
                f'background:{sc["color"]};border-radius:2px;opacity:0.8;"></div></div></div>',
                unsafe_allow_html=True
            )


# ── 상세 분석 페이지 ──────────────────────────────────────────────────────────
def render_detail_page():
    target = st.session_state.selected or ""
    if not target:
        st.session_state.page = "main"; st.rerun()

    if st.sidebar.button("← 대시보드로", use_container_width=True):
        st.session_state.page = "main"; st.rerun()

    si = next(
        (s for s in st.session_state.portfolio if s["ticker"] == target),
        {"name": target, "weight": "—", "avg_price": 0, "shares": 0}
    )

    with st.spinner(f"{target} 분석 중..."):
        zs, price        = get_z_and_price(target)
        sk, cfg, inds    = get_sector_analysis(target)
        nb, _            = get_news(target)
        fw, breakdown    = calc_win_rate(zs, inds, nb)
        weighted_z       = get_weighted_z(inds)

    st_, sc_, sv_ = get_signal(fw)
    pnl = ((price - si["avg_price"]) / si["avg_price"] * 100) \
          if price and si["avg_price"] > 0 else 0
    pc  = "#059669" if pnl >= 0 else "#DC2626"

    # ── 승률 해석 생성 ────────────────────────────────────────────────
    interp_bg, interp_border, interp_icon, interp_title, interp_body, interp_clr = \
        _win_rate_interpretation(fw, inds, zs, weighted_z)

    # ── 헤더 ─────────────────────────────────────────────────────────
    hl, hr = st.columns([3, 1])
    with hl:
        st.markdown(
            f'<div style="margin-bottom:12px;">'
            f'<div style="font-size:11px;color:#6B7280;letter-spacing:1px;'
            f'text-transform:uppercase;margin-bottom:4px;">{cfg["icon"]} {cfg["label"]} 섹터</div>'
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">'
            f'<h1 style="font-size:26px;font-weight:700;color:#1A1D23;margin:0;">{target}</h1>'
            f'<div class="{sc_}">{st_}</div></div>'
            f'<div style="font-size:12px;color:#6B7280;">'
            f'{si["name"]} · 비중 {si["weight"]}% · {si.get("shares",0)}주 · 평균 ${si["avg_price"]:.2f}</div>'
            f'<div style="font-size:11px;color:#9CA3AF;margin-top:3px;">📌 {cfg["cycle_note"]}</div></div>',
            unsafe_allow_html=True
        )
    with hr:
        # 승률 박스 + 해석 텍스트를 바로 아래에
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;'
            f'padding:16px;text-align:center;border-top:3px solid {sv_};">'
            f'<div style="font-size:10px;color:#9CA3AF;letter-spacing:1px;'
            f'text-transform:uppercase;margin-bottom:4px;">오늘의 승률</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:42px;'
            f'font-weight:700;color:{sv_};line-height:1;">{fw}%</div>'
            f'<div style="font-size:11px;color:{interp_clr};font-weight:600;margin-top:6px;">'
            f'{interp_icon} {interp_title}</div>'
            f'<div style="font-size:10px;color:#9CA3AF;margin-top:3px;">'
            f'거시Z <b style="color:{zcolor(weighted_z)};">{weighted_z:+.2f}</b> · 뉴스 {nb:+.0f}%</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # 승률 해석 상세 텍스트 (헤더 아래 전체 폭)
    st.markdown(
        f'<div style="background:{interp_bg};border:1px solid {interp_border};'
        f'border-radius:8px;padding:12px 16px;margin:8px 0 16px;">'
        f'<div style="font-size:12px;color:{interp_clr};font-weight:600;margin-bottom:4px;">'
        f'{interp_icon} {interp_title}</div>'
        f'<div style="font-size:12px;color:#374151;line-height:1.7;">{interp_body}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── 탭 ───────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 차트",
        f"{cfg['icon']} 섹터 지표 & 리스크",
        "🔗 상관 분석",
        "📰 뉴스 (한국어)",
        "🧮 계산 근거",
    ])

    # ── TAB 1: 차트 ────────────────────────────────────────────────── ─
    with tab1:
        pk = st.session_state.chart_period

        # 차트 데이터
        with st.spinner(""):
            df    = get_chart_data(target, pk)
            stats = get_price_stats(df)

        # 스탯 카드 6개 — 차트 바로 위
        s_cols = st.columns(6)
        stat_items = [
            ("기간 수익률",    f"{'+'if stats['period_ret']>=0 else ''}{stats['period_ret']:.1f}%",
             "#059669" if stats["period_ret"] >= 0 else "#DC2626"),
            ("최대 상승(봉)",  f"+{stats['max_gain']:.2f}%",  "#059669"),
            ("최대 하락(봉)",  f"{stats['max_loss']:.2f}%",   "#DC2626"),
            ("연환산 변동성",  f"{stats['volatility']:.1f}%", "#D97706"),
            ("기간 최고가",    f"${stats['high']:.2f}",        "#1A1D23"),
            ("기간 최저가",    f"${stats['low']:.2f}",         "#1A1D23"),
        ]
        for col, (lbl, val, clr) in zip(s_cols, stat_items):
            col.markdown(
                f'<div class="stat-box">'
                f'<div style="font-size:9px;color:#9CA3AF;font-weight:500;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:3px;">{lbl}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:13px;'
                f'font-weight:700;color:{clr};">{val}</div></div>',
                unsafe_allow_html=True
            )

        # 메인 차트 — 개선된 디자인
        if not df.empty and "Close" in df.columns:
            r, g, b = int(sv_[1:3], 16), int(sv_[3:5], 16), int(sv_[5:7], 16)

            if pk in ("1달", "1년") and all(c in df.columns for c in ["Open", "High", "Low", "Close"]):
                chart_fig = go.Figure()
                # 캔들스틱 — 더 세련된 색상
                chart_fig.add_trace(go.Candlestick(
                    x=df["Date"], open=df["Open"], high=df["High"],
                    low=df["Low"], close=df["Close"],
                    increasing_line_color="#10B981", decreasing_line_color="#EF4444",
                    increasing_fillcolor="rgba(16,185,129,0.85)",
                    decreasing_fillcolor="rgba(239,68,68,0.85)",
                    name=target,
                    hovertext=df.apply(
                        lambda row: f"O ${row['Open']:.2f}  H ${row['High']:.2f}<br>"
                                    f"L ${row['Low']:.2f}  C ${row['Close']:.2f}", axis=1
                    ),
                    hoverinfo="x+text",
                ))
                if len(df) >= 20:
                    ma20 = df["Close"].rolling(20).mean()
                    chart_fig.add_trace(go.Scatter(
                        x=df["Date"], y=ma20, mode="lines",
                        line=dict(color="#F59E0B", width=1.5, dash="dash"), name="MA20"
                    ))
                if len(df) >= 60:
                    ma60 = df["Close"].rolling(60).mean()
                    chart_fig.add_trace(go.Scatter(
                        x=df["Date"], y=ma60, mode="lines",
                        line=dict(color="#8B5CF6", width=1.2, dash="dot"), name="MA60"
                    ))
            else:
                chart_fig = go.Figure()
                # 라인 차트 — 그라디언트 영역 강화
                chart_fig.add_trace(go.Scatter(
                    x=df["Date"], y=df["Close"], mode="lines",
                    line=dict(color=sv_, width=2.5, shape="spline", smoothing=0.4),
                    fill="tozeroy",
                    fillcolor=f"rgba({r},{g},{b},0.10)",
                    name=target,
                    hovertemplate="<b>$%{y:.2f}</b>  %{x}<extra></extra>",
                ))
                # 최고가·최저가 마커
                if len(df) > 2:
                    idx_max = df["Close"].idxmax()
                    idx_min = df["Close"].idxmin()
                    chart_fig.add_trace(go.Scatter(
                        x=[df.loc[idx_max, "Date"]], y=[df.loc[idx_max, "Close"]],
                        mode="markers+text",
                        marker=dict(color="#10B981", size=8, symbol="circle"),
                        text=[f"H ${df.loc[idx_max,'Close']:.2f}"],
                        textposition="top center",
                        textfont=dict(size=9, color="#10B981"),
                        showlegend=False, hoverinfo="skip"
                    ))
                    chart_fig.add_trace(go.Scatter(
                        x=[df.loc[idx_min, "Date"]], y=[df.loc[idx_min, "Close"]],
                        mode="markers+text",
                        marker=dict(color="#EF4444", size=8, symbol="circle"),
                        text=[f"L ${df.loc[idx_min,'Close']:.2f}"],
                        textposition="bottom center",
                        textfont=dict(size=9, color="#EF4444"),
                        showlegend=False, hoverinfo="skip"
                    ))

            chart_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(248,250,252,0.6)",
                font=dict(color="#9CA3AF", size=11),
                xaxis=dict(
                    showgrid=True, gridcolor="rgba(226,232,240,0.5)", gridwidth=0.5,
                    color="#E8EAED",
                    rangeslider=dict(visible=False),
                    tickfont=dict(size=10, color="#9CA3AF"),
                    showline=True, linecolor="#E8EAED",
                ),
                yaxis=dict(
                    showgrid=True, gridcolor="rgba(226,232,240,0.5)",
                    gridwidth=0.5, color="#9CA3AF",
                    tickfont=dict(size=10),
                    showline=False,
                    tickprefix="$",
                    side="right",
                ),
                legend=dict(
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#E8EAED", borderwidth=1,
                    font=dict(size=10),
                    orientation="h", y=1.03, x=0
                ),
                margin=dict(t=10, b=4, l=0, r=50),
                height=360,
                hovermode="x unified",
            )
            st.plotly_chart(chart_fig, use_container_width=True)

            # 거래량 (여백 없이 바로 아래)
            if "Volume" in df.columns and df["Volume"].sum() > 0:
                vol_colors = [
                    "#10B981" if i > 0 and df["Close"].iloc[i] >= df["Close"].iloc[i-1]
                    else "#EF4444" if i > 0 else "#9CA3AF"
                    for i in range(len(df))
                ]
                vol_fig = go.Figure(go.Bar(
                    x=df["Date"], y=df["Volume"],
                    marker_color=vol_colors, opacity=0.5,
                    hovertemplate="%{x}<br>거래량: %{y:,.0f}<extra></extra>",
                ))
                vol_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,250,252,0.4)",
                    xaxis=dict(showgrid=False, tickfont=dict(size=9, color="#9CA3AF")),
                    yaxis=dict(showgrid=False, tickformat=".2s", tickfont=dict(size=9, color="#9CA3AF")),
                    margin=dict(t=0, b=4, l=0, r=50),
                    height=65, showlegend=False,
                )
                st.plotly_chart(vol_fig, use_container_width=True)

            # ── 기간 선택 버튼 — 차트 아래, 작게 ──────────────────────
            st.markdown(
                '<div style="display:flex;justify-content:center;gap:6px;margin-top:4px;margin-bottom:2px;">',
                unsafe_allow_html=True
            )
            period_cols = st.columns([3, 1, 1, 1, 1, 3])
            for idx, label in enumerate(["1일", "1주", "1달", "1년"]):
                with period_cols[idx + 1]:
                    is_active = pk == label
                    if st.button(
                        label,
                        key=f"p_{label}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary"
                    ):
                        st.session_state.chart_period = label
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("차트 데이터를 불러올 수 없습니다.")

        # KPI 4개 + 요약 (차트 아래)
        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
        kc = st.columns(4)
        for col, (lbl, val, clr) in zip(kc, [
            ("현재가",  f"${price:.2f}",     "#1A1D23"),
            ("주가 Z",  f"{zs:+.2f}σ",       zcolor(zs)),
            ("거시 Z",  f"{weighted_z:+.2f}", zcolor(weighted_z)),
            ("수익률",  f"{'+'if pnl>=0 else ''}{pnl:.1f}%", pc),
        ]):
            col.markdown(
                f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;'
                f'padding:10px;text-align:center;">'
                f'<div style="font-size:10px;color:#9CA3AF;font-weight:500;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:3px;">{lbl}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:16px;'
                f'font-weight:700;color:{clr};">{val}</div></div>',
                unsafe_allow_html=True
            )

    # ── TAB 2: 섹터 지표 & 리스크 드라이버 ──────────────────────────
    with tab2:
        macro_sign    = "+" if weighted_z * 15 >= 0 else ""
        macro_contrib = f"{macro_sign}{weighted_z*15:.1f}"

        st.markdown(
            f'<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;'
            f'padding:12px 16px;margin-bottom:16px;">'
            f'<span class="lv2">Lv.2</span>'
            f'<b style="font-size:13px;color:#1A1D23;margin-left:8px;">'
            f'{cfg["icon"]} {cfg["label"]} — {len(inds)}개 드라이버</b>'
            f'<div style="font-size:11px;color:#6B7280;margin-top:4px;">📌 {cfg["cycle_note"]}</div>'
            f'<div style="font-size:11px;color:#6B7280;margin-top:4px;">'
            f'거시환경 가중 Z-Score: <b style="color:{zcolor(weighted_z)};">{weighted_z:+.3f}σ</b>'
            f' → 승률 기여 <b style="color:{zcolor(weighted_z)};">{macro_contrib}%p</b></div></div>',
            unsafe_allow_html=True
        )

        # 지표 카드
        for ind in inds:
            eff_z   = ind["z"] * ind["direction"]
            contrib = eff_z * ind["driver_weight"] * 15
            cc2     = "#059669" if contrib > 0 else "#DC2626" if contrib < 0 else "#6B7280"
            wlbl    = f"호재(×{ind['driver_weight']:.0%})" if ind["direction"] == +1 else f"악재(×{ind['driver_weight']:.0%})"
            wclr    = "#059669" if ind["direction"] == +1 else "#DC2626"
            sens    = ind.get("sensitivity", "mid")
            bs      = 50.0 if eff_z >= 0 else max(0.0, 50.0 - min(50.0, abs(eff_z) / 3 * 50))
            bw      = min(50.0, abs(eff_z) / 3 * 50)

            st.markdown(f"""
<div class="ind-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
        <div>
            <span style="font-size:13px;font-weight:600;color:#1A1D23;">{ind['name']}</span>
            <span style="font-size:10px;color:#9CA3AF;margin-left:5px;">({ind['ticker']})</span>
            <span class="sensitivity-{sens}" style="margin-left:6px;">{SENSITIVITY_LABEL.get(sens,'')}</span>
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
        <span style="color:{cc2};font-weight:600;">가중 기여 {'+'if contrib>0 else ''}{contrib:.1f}%p</span>
    </div>
</div>""", unsafe_allow_html=True)

        # 레이더 차트
        rl  = [ind["name"] for ind in inds]
        rv  = [(min(3, max(-3, ind["z"])) + 3) / 6 for ind in inds]
        r2, g2, b2 = int(cfg["color"][1:3],16), int(cfg["color"][3:5],16), int(cfg["color"][5:7],16)
        radar = go.Figure(go.Scatterpolar(
            r=rv + [rv[0]], theta=rl + [rl[0]], fill="toself",
            fillcolor=f"rgba({r2},{g2},{b2},0.12)",
            line=dict(color=cfg["color"], width=2),
            marker=dict(size=5, color=cfg["color"])
        ))
        radar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            polar=dict(
                bgcolor="#FAFAFA",
                radialaxis=dict(visible=True, range=[0,1], showticklabels=False,
                                gridcolor="#E8EAED", linecolor="#E8EAED"),
                angularaxis=dict(tickfont=dict(color="#6B7280", size=11),
                                 gridcolor="#E8EAED", linecolor="#E8EAED"),
            ),
            showlegend=False,
            margin=dict(t=20, b=20, l=60, r=60), height=300
        )
        st.plotly_chart(radar, use_container_width=True)

        # ── 리스크 드라이버 심화 분석 ────────────────────────────────
        st.markdown(
            '<div class="section-hdr" style="margin-top:8px;">'
            '🔍 리스크 드라이버 심화 분석</div>',
            unsafe_allow_html=True
        )
        driver_html = _risk_driver_analysis(inds, fw)
        st.markdown(driver_html, unsafe_allow_html=True)

        # ── Action Plan ───────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        action_clr, action_level, action_rows = _action_plan(fw)

        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;'
            f'padding:16px 20px;">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
            f'<div style="font-size:13px;font-weight:700;color:#1A1D23;">📋 실전 대응 Action Plan</div>'
            f'<div style="background:{action_clr};color:#FFFFFF;font-size:11px;font-weight:600;'
            f'padding:3px 10px;border-radius:20px;">현재 승률 {action_level}</div>'
            f'</div>'
            f'<table class="action-table">'
            f'<thead><tr><th style="width:100px;">항목</th><th>권장 행동</th></tr></thead>'
            f'<tbody>{action_rows}</tbody>'
            f'</table></div>',
            unsafe_allow_html=True
        )

    # ── TAB 3: 상관 분석 ─────────────────────────────────────────────
    with tab3:
        st.markdown(
            f'<div style="background:#F8FAFF;border:1px solid #DBEAFE;border-radius:8px;'
            f'padding:12px 16px;margin-bottom:16px;">'
            f'<span class="lv2">Lv.2</span>'
            f'<b style="font-size:13px;color:#1A1D23;margin-left:8px;">'
            f'{target} ↔ 거시 지표 60일 상관계수</b>'
            f'<div style="font-size:11px;color:#6B7280;margin-top:4px;">'
            f'범위: -1(역상관) ~ 0(무관) ~ +1(동조)<br>'
            f'<span style="color:#059669;">초록</span>: 이론 방향 일치 &nbsp;'
            f'<span style="color:#DC2626;">빨강</span>: 이론 역방향 (이상 신호)</div></div>',
            unsafe_allow_html=True
        )
        with st.spinner("상관계수 계산 중..."):
            corr_data = get_macro_correlation(target, inds)

        if not corr_data:
            st.info("상관계수 데이터를 불러올 수 없습니다.")
        else:
            names = [d["name"] for d in corr_data]
            corrs = [d["corr"]  for d in corr_data]
            clrs  = [corr_color(d["corr"], d["direction"]) for d in corr_data]

            bar_fig = go.Figure()
            bar_fig.add_trace(go.Bar(
                y=names, x=corrs, orientation="h",
                marker=dict(color=clrs, line=dict(color="#FFFFFF", width=0.5)),
                text=[f"{c:+.2f}" for c in corrs],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=11, color="#374151"),
                hovertemplate="<b>%{y}</b><br>상관계수: %{x:.3f}<extra></extra>",
            ))
            bar_fig.add_vline(x=0, line_dash="dash", line_color="#E8EAED", line_width=1)
            bar_fig.add_vrect(
                x0=-0.15, x1=0.15,
                fillcolor="rgba(200,200,200,0.08)", line_width=0,
                annotation_text="무상관", annotation_font_size=9,
                annotation_font_color="#9CA3AF"
            )
            bar_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6B7280"),
                xaxis=dict(range=[-1.1,1.1], showgrid=True, gridcolor="#F3F4F6",
                           zeroline=False, tickfont=dict(family="JetBrains Mono", size=10)),
                yaxis=dict(showgrid=False, tickfont=dict(size=12, color="#1A1D23")),
                margin=dict(t=10, b=10, l=10, r=60),
                height=50 + len(names) * 44,
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            for d in sorted(corr_data, key=lambda x: abs(x["corr"]), reverse=True):
                c       = d["corr"]
                clr     = corr_color(c, d["direction"])
                aligned = (c > 0 and d["direction"] == +1) or (c < 0 and d["direction"] == -1)
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;'
                    f'padding:10px 14px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">'
                    f'<div><span style="font-size:13px;font-weight:600;color:#1A1D23;">{d["name"]}</span>'
                    f'<span style="font-size:10px;color:#9CA3AF;margin-left:5px;">'
                    f'{"상승=호재" if d["direction"]==+1 else "상승=악재"}</span></div>'
                    f'<div style="text-align:right;">'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:16px;'
                    f'font-weight:700;color:{clr};">{c:+.3f}</div>'
                    f'<div style="font-size:10px;color:{clr};">'
                    f'{"이론 일치 ✓" if aligned else "이론 역방향 ⚠"}</div></div></div>',
                    unsafe_allow_html=True
                )

    # ── TAB 4: 뉴스 (한국어) ─────────────────────────────────────────
    with tab4:
        st.markdown(
            f'<div style="background:#F8FAFF;border:1px solid #DBEAFE;border-radius:8px;'
            f'padding:10px 14px;margin-bottom:14px;font-size:12px;color:#6B7280;">'
            f'<b style="color:#1A1D23;">{target} ({si["name"]})</b>'
            f' 관련 한국어 뉴스 · Google News 실시간 수집</div>',
            unsafe_allow_html=True
        )

        with st.spinner("한국어 뉴스 수집 중..."):
            ko_bonus, ko_news = get_korean_news(target, si.get("name", ""))

        if ko_news:
            pos_c = sum(1 for n in ko_news if n["sentiment"] == "Positive")
            neg_c = sum(1 for n in ko_news if n["sentiment"] == "Negative")
            neu_c = sum(1 for n in ko_news if n["sentiment"] == "Neutral")
            nb_clr = "#059669" if ko_bonus > 0 else "#DC2626" if ko_bonus < 0 else "#9CA3AF"

            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;'
                f'padding:12px 16px;margin-bottom:14px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;">'
                f'<span style="font-size:11px;color:#6B7280;">감성 분포 ({len(ko_news)}건)</span>'
                f'<span style="color:#059669;font-size:12px;font-weight:600;">▲ 긍정 {pos_c}건</span>'
                f'<span style="color:#DC2626;font-size:12px;font-weight:600;">▼ 부정 {neg_c}건</span>'
                f'<span style="color:#9CA3AF;font-size:12px;">● 중립 {neu_c}건</span>'
                f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:12px;'
                f'color:{nb_clr};font-weight:700;margin-left:auto;">'
                f'뉴스 보정 {ko_bonus:+.1f}%</span></div>',
                unsafe_allow_html=True
            )

            for n in ko_news:
                css  = "news-pos" if n["sentiment"]=="Positive" else "news-neg" if n["sentiment"]=="Negative" else "news-neu"
                icon = "▲" if n["sentiment"]=="Positive" else "▼" if n["sentiment"]=="Negative" else "●"
                tc   = "#059669" if n["sentiment"]=="Positive" else "#DC2626" if n["sentiment"]=="Negative" else "#9CA3AF"
                pub  = f'<span style="color:#9CA3AF;font-size:10px;margin-left:8px;">{n.get("pub_date","")}</span>' if n.get("pub_date") else ""
                src  = f'<span style="color:#9CA3AF;font-size:10px;">{n.get("source","")}</span>' if n.get("source") else ""
                st.markdown(
                    f'<div class="{css}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">'
                    f'<span style="font-size:10px;color:{tc};font-weight:600;">{icon} {n["sentiment"].upper()}</span>'
                    f'<div>{src}{pub}</div></div>'
                    f'<a href="{n["link"]}" target="_blank" '
                    f'style="font-size:13px;color:#1A1D23;text-decoration:none;font-weight:500;line-height:1.5;">'
                    f'{n["title"]}</a></div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;'
                'padding:20px;text-align:center;">'
                '<div style="font-size:20px;margin-bottom:8px;">📰</div>'
                '<div style="font-size:13px;color:#D97706;font-weight:600;">뉴스를 불러올 수 없습니다</div>'
                '<div style="font-size:12px;color:#9CA3AF;margin-top:4px;">'
                '네트워크 연결을 확인하거나 잠시 후 다시 시도해주세요</div></div>',
                unsafe_allow_html=True
            )

    # ── TAB 5: 계산 근거 ─────────────────────────────────────────────
    with tab5:
        st.markdown(
            '<div style="background:#F8FAFF;border:1px solid #DBEAFE;border-radius:8px;'
            'padding:14px 16px;margin-bottom:16px;">'
            '<b style="font-size:13px;color:#1A1D23;">승률 계산 공식 (Lv.1/2)</b>'
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;'
            'color:#374151;margin-top:8px;line-height:2;">'
            'weighted_Z = Σ(z_i × direction_i × driver_weight_i) / Σ(weight_i)<br>'
            'macro_score = weighted_Z × 15<br>'
            'z_penalty   = −z_stock × 3<br>'
            'final       = clamp(50 + z_penalty + macro_score + news_bonus, 5, 95)'
            '</div></div>',
            unsafe_allow_html=True
        )

        items = [
            ("기본값",    50.0,                      "#9CA3AF"),
            ("주가 위치", breakdown["z_penalty"],    "#2563EB"),
            ("거시 환경", breakdown["macro_score"],  zcolor(breakdown["macro_z"])),
            ("뉴스 감성", breakdown["news_bonus"],   "#059669" if nb > 0 else "#DC2626"),
        ]
        comp_fig = go.Figure()
        for lbl, val, clr in items:
            comp_fig.add_trace(go.Bar(
                name=lbl, x=[lbl], y=[val], marker_color=clr,
                text=[f"{val:+.1f}"], textposition="outside",
                textfont=dict(family="JetBrains Mono", size=12)
            ))
        comp_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#374151")),
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6", range=[-25, 75]),
            margin=dict(t=20, b=10, l=0, r=0), height=220, barmode="group"
        )
        st.plotly_chart(comp_fig, use_container_width=True)

        st.markdown(
            f'<div style="background:#F9FAFB;border:1px solid #E8EAED;border-radius:8px;'
            f'padding:14px;font-family:\'JetBrains Mono\',monospace;font-size:12px;'
            f'color:#374151;line-height:2;">'
            f'50.0 (기본)<br>'
            f'{breakdown["z_penalty"]:+.1f} (주가 Z={zs:+.2f} × −3)<br>'
            f'{breakdown["macro_score"]:+.1f} (거시 가중Z={breakdown["macro_z"]:+.3f} × 15)<br>'
            f'{breakdown["news_bonus"]:+.1f} (뉴스 보정)<br>'
            f'──────────────<br>'
            f'합계 {breakdown["total_raw"]:+.1f} → clamp → '
            f'<b style="color:{sv_};">{fw}%</b></div>',
            unsafe_allow_html=True
        )
