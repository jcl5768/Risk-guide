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
/* 매크로 지표 크기 축소 (패딩과 폰트 크기 조절) */
.macro-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:8px 12px;}
.section-hdr{font-size:11px;font-weight:600;color:#6B7280;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #E8EAED;}
.stock-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:16px 18px;}
.badge-green{background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.badge-yellow{background:#FFFBEB;color:#D97706;border:1px solid #FDE68A;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.badge-red{background:#FEF2F2;color:#DC2626;border:1px solid #FECACA;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}
.lv1{background:#EFF6FF;color:#2563EB;border:1px solid #BFDBFE;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
.lv2{background:#FFF7ED;color:#EA580C;border:1px solid #FED7AA;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}
.news-pos{background:#ECFDF5;border-left:3px solid #059669;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}
.news-neg{background:#FEF2F2;border-left:3px solid #DC2626;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}
.news-neu{background:#F9FAFB;border-left:3px solid #D1D5DB;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}
.ind-card{background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:12px 16px;margin-bottom:8px;}
.sensitivity-high{background:#FEF2F2;color:#DC2626;border:1px solid #FECACA;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.sensitivity-mid{background:#FFFBEB;color:#D97706;border:1px solid #FDE68A;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.sensitivity-low{background:#F9FAFB;color:#6B7280;border:1px solid #E8EAED;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}
.stat-box{background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:10px;text-align:center;}
.action-table{width:100%;border-collapse:collapse;font-size:12px;}
.action-table th{background:#F9FAFB;color:#6B7280;font-weight:600;padding:8px 12px;text-align:left;border-bottom:1px solid #E8EAED;}
.action-table td{padding:10px 12px;border-bottom:1px solid #F3F4F6;color:#374151;vertical-align:top;}
div[data-testid="stButton"] button{background:#FFFFFF;color:#374151;border:1px solid #D1D5DB;border-radius:7px;font-size:12px;font-weight:500;padding:6px 16px;}
div[data-testid="stButton"] button:hover{background:#F9FAFB;border-color:#9CA3AF;}
.stTabs [data-baseweb="tab-list"]{gap:2px;background:#F3F4F6;border-radius:8px;padding:3px;border:1px solid #E8EAED;}
.stTabs [data-baseweb="tab"]{height:32px;font-size:12px;font-weight:500;color:#6B7280;border-radius:6px;padding:0 14px;}
.stTabs [aria-selected="true"]{background:#FFFFFF !important;color:#1A1D23 !important;box-shadow:0 1px 3px rgba(0,0,0,0.1);}
/* 작아진 기간 선택 버튼 스타일 강제 */
button[kind="primary"]{background:#1A1D23 !important;color:#FFFFFF !important;border-color:#1A1D23 !important;font-weight:700 !important; padding:4px 8px !important; font-size:11px !important;}
button[kind="secondary"]{padding:4px 8px !important; font-size:11px !important;}
</style>
""", unsafe_allow_html=True)

# ── 승률 해석 텍스트 생성 (기존과 동일) ─────────────────────────────────
def _win_rate_interpretation(fw, inds, zs, weighted_z):
    neg_contribs = sorted([ind for ind in inds if ind["z"] * ind["direction"] < 0], key=lambda x: abs(x["z"] * x["driver_weight"]), reverse=True)
    pos_contribs = sorted([ind for ind in inds if ind["z"] * ind["direction"] > 0], key=lambda x: abs(x["z"] * x["driver_weight"]), reverse=True)
    top_neg = neg_contribs[0] if neg_contribs else None
    top_pos = pos_contribs[0] if pos_contribs else None

    if fw >= 70:
        bg, border, icon, title = "#F0FDF4", "#A7F3D0", "🟢", "통계적으로 매우 유리한 타점"
        pos_driver = f"<b>{top_pos['name']}</b>" if top_pos else "긍정 지표"
        body = f"매크로 지표가 종목의 상승을 뒷받침하고 있으며, 주가는 역사적 평균 대비 저평가 구간({zs:+.2f}σ)에 위치합니다. 특히 {pos_driver}가 강한 호재로 작용 중입니다."
        text_clr = "#059669"
    elif fw >= 45:
        bg, border, icon, title = "#FFFBEB", "#FDE68A", "🟡", "추세 유지 중 — 단기 변동성 주의"
        neg_driver = f"<b>{top_neg['name']}</b>({top_neg['desc']})" if top_neg else "일부 지표"
        body = f"추세가 유지되고 있으나 {neg_driver}의 변화가 단기 변동성을 높일 수 있습니다. 주요 매크로 지표의 변화를 주시하며 비중을 유지하는 것이 좋습니다."
        text_clr = "#D97706"
    else:
        bg, border, icon, title = "#FEF2F2", "#FECACA", "🔴", "통계적 하락 압력 — 리스크 경고"
        neg_driver = f"<b>{top_neg['name']}</b> ({top_neg['desc']})" if top_neg else "거시 지표 악화"
        body = f"현재 승률은 <b>{fw}%</b>로, 통계적 하락 압력이 강합니다. 주된 원인은 {neg_driver}입니다. 신규 진입을 자제하고 현금 비중 확대를 권고합니다."
        text_clr = "#DC2626"
    return bg, border, icon, title, body, text_clr

def _risk_driver_analysis(inds, fw):
    scored = []
    for ind in inds:
        eff = ind["z"] * ind["direction"]
        contrib = eff * ind["driver_weight"] * 15
        scored.append({**ind, "contrib": contrib, "eff_z": eff})
    neg_sorted = sorted([x for x in scored if x["contrib"] < 0], key=lambda x: x["contrib"])[:2]
    pos_sorted = sorted([x for x in scored if x["contrib"] > 0], key=lambda x: -x["contrib"])[:1]
    blocks = []
    for ind in neg_sorted:
        blocks.append(f'<div style="background:#FEF2F2;border-left:3px solid #DC2626;padding:10px 14px;margin-bottom:8px;"><div style="font-size:11px;font-weight:700;color:#DC2626;">▼ 리스크: {ind["name"]} ({ind["ticker"]})</div><div style="font-size:12px;color:#374151;">{ind["desc"]}</div></div>')
    for ind in pos_sorted:
        blocks.append(f'<div style="background:#ECFDF5;border-left:3px solid #059669;padding:10px 14px;margin-bottom:8px;"><div style="font-size:11px;font-weight:700;color:#059669;">▲ 호재: {ind["name"]} ({ind["ticker"]})</div><div style="font-size:12px;color:#374151;">{ind["desc"]}</div></div>')
    return "".join(blocks)

def _action_plan(fw):
    if fw >= 60: return "#059669", f"높음 ({fw:.0f}%↑)", "<tr><td>포지션 관리</td><td>기존 비중 유지</td></tr><tr><td>수익 극대화</td><td>분할 익절 전략</td></tr>"
    elif fw >= 45: return "#D97706", f"보통 ({fw:.0f}%)", "<tr><td>포지션 관리</td><td>비중 유지</td></tr><tr><td>익절 전략</td><td>예약 매도 조정</td></tr>"
    else: return "#DC2626", f"낮음 ({fw:.0f}%↓)", "<tr><td>비중 축소</td><td>포트폴리오 비중 축소</td></tr><tr><td>현금 확보</td><td>관망</td></tr>"

# ── 메인 대시보드 ─────────────────────────────────────────────────────────────
def render_main_page():
    st.markdown('<div style="margin-bottom:20px;"><h2 style="font-size:22px;font-weight:700;color:#1A1D23;margin:0;">📊 포트폴리오 현황</h2></div>', unsafe_allow_html=True)

    # 상단 매크로 지표 크기 축소 반영
    st.markdown('<div class="section-hdr">📡 주요 거시 지표</div>', unsafe_allow_html=True)
    mc = st.columns(5)
    for col, (label, sym, desc) in zip(mc, MACRO_INDICATORS):
        z, price = get_z_and_price(sym)
        arrow = "▲" if z > 0.2 else "▼" if z < -0.2 else "—"
        ac    = "#059669" if z > 0.2 else "#DC2626" if z < -0.2 else "#6B7280"
        col.markdown(
            f'<div class="macro-card">'
            f'<div style="font-size:9px;font-weight:600;color:#6B7280;margin-bottom:2px;">{label}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:15px;font-weight:700;color:{zcolor(z)};">'
            f'{price:,.2f} <span style="font-size:11px;color:{ac};">{arrow}</span></div>'
            f'<div style="font-size:9px;color:#9CA3AF;margin-top:1px;">Z {z:+.2f}σ · {desc}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    portfolio = st.session_state.portfolio

    if not portfolio:
        st.markdown('<div style="background:#FFFFFF;border:2px dashed #D1D5DB;border-radius:12px;padding:48px;text-align:center;">📭 아직 종목이 없습니다</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="section-hdr">📈 보유 종목 분석</div>', unsafe_allow_html=True)
    for rs in range(0, len(portfolio), 4):
        row  = portfolio[rs: rs + 4]
        cols = st.columns(len(row))
        for col, stock in zip(cols, row):
            with col:
                with st.spinner(""):
                    zs, price = get_z_and_price(stock["ticker"])
                    _, cfg, inds = get_sector_analysis(stock["ticker"])
                    nb, _ = get_news(stock["ticker"])
                    win, breakdown = calc_win_rate(zs, inds, nb)
                st_, sc_, sv_ = get_signal(win)
                st.markdown(f'<div class="stock-card" style="border-top:3px solid {sv_};"><b>{stock["ticker"]}</b><br><span style="font-size:24px;color:{sv_};font-weight:bold;">{win}%</span></div>', unsafe_allow_html=True)
                if st.button("상세 분석 →", key=f"go_{stock['ticker']}_{rs}"):
                    st.session_state.selected = stock["ticker"]
                    st.session_state.page     = "detail"
                    st.rerun()

# ── 상세 분석 페이지 ──────────────────────────────────────────────────────────
def render_detail_page():
    target = st.session_state.selected or ""
    if not target:
        st.session_state.page = "main"; st.rerun()

    if st.sidebar.button("← 대시보드로", use_container_width=True):
        st.session_state.page = "main"; st.rerun()

    si = next((s for s in st.session_state.portfolio if s["ticker"] == target), {"name": target, "weight": "—", "avg_price": 0, "shares": 0})

    with st.spinner(f"{target} 분석 중..."):
        zs, price = get_z_and_price(target)
        sk, cfg, inds = get_sector_analysis(target)
        nb, _ = get_news(target)
        fw, breakdown = calc_win_rate(zs, inds, nb)
        weighted_z = get_weighted_z(inds)

    st_, sc_, sv_ = get_signal(fw)
    interp_bg, interp_border, interp_icon, interp_title, interp_body, interp_clr = _win_rate_interpretation(fw, inds, zs, weighted_z)

    st.markdown(f"<h2>{target} 분석</h2>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 차트", "지표 & 리스크", "뉴스"])

    # ── TAB 1: 차트 ──────────────────────────────────────────────────
    with tab1:
        pk = st.session_state.chart_period

        with st.spinner("차트 로딩 중..."):
            df    = get_chart_data(target, pk)
            stats = get_price_stats(df)

        # 메인 차트 (디자인 개선)
        if not df.empty and "Close" in df.columns:
            chart_fig = go.Figure()
            if pk in ("1달", "1년") and all(c in df.columns for c in ["Open", "High", "Low", "Close"]):
                chart_fig.add_trace(go.Candlestick(
                    x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                    increasing_line_color="#10B981", decreasing_line_color="#EF4444", # 캔들 색상 모던하게 변경
                    increasing_fillcolor="rgba(16, 185, 129, 0.7)", decreasing_fillcolor="rgba(239, 68, 68, 0.7)",
                    name=target
                ))
            else:
                chart_fig.add_trace(go.Scatter(
                    x=df["Date"], y=df["Close"], mode="lines",
                    line=dict(color=sv_, width=2.5, shape="spline", smoothing=1.2), # 선 더 부드럽고 굵게
                    fill="tozeroy", fillcolor=f"rgba(37,99,235,0.05)",
                    name=target
                ))

            chart_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6B7280", size=10),
                xaxis=dict(showgrid=True, gridcolor="rgba(232,234,237,0.4)", rangeslider=dict(visible=False)),
                yaxis=dict(showgrid=True, gridcolor="rgba(232,234,237,0.8)", gridwidth=1, side="right"), # Y축을 우측으로 이동시켜 전문적인 느낌 부여
                margin=dict(t=15, b=5, l=0, r=0), height=320, hovermode="x unified",
            )
            st.plotly_chart(chart_fig, use_container_width=True)

        # ── 기간 선택 버튼 (차트 밑으로 이동 및 크기 축소) ────────────────
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        # 1:1:1:1:8 비율로 설정하여 버튼들이 좌측에 작게 뭉치도록 유도
        p_cols = st.columns([1, 1, 1, 1, 8]) 
        for idx, label in enumerate(["1일", "1주", "1달", "1년"]):
            with p_cols[idx]:
                if st.button(label, key=f"p_{label}", use_container_width=True, type="primary" if pk == label else "secondary"):
                    st.session_state.chart_period = label
                    st.rerun()

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        
        # 하단 요약 스탯
        kc = st.columns(4)
        for col, (lbl, val, clr) in zip(kc, [("현재가", f"${price:.2f}", "#1A1D23"), ("주가 Z", f"{zs:+.2f}σ", zcolor(zs)), ("거시 Z", f"{weighted_z:+.2f}", zcolor(weighted_z)), ("수익률", f"{stats['period_ret']}%", "#059669")]):
            col.markdown(f'<div class="stat-box"><div style="font-size:10px;color:#9CA3AF;">{lbl}</div><div style="font-size:14px;font-weight:bold;color:{clr};">{val}</div></div>', unsafe_allow_html=True)

    with tab2:
        st.write("리스크 분석 탭")
    with tab3:
        st.write("뉴스 탭")
