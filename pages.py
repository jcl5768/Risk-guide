# pages.py
import streamlit as st
import plotly.graph_objects as go
from config import SECTOR_CONFIG, MACRO_INDICATORS, SENSITIVITY_COLOR, SENSITIVITY_LABEL
from engine import (
    detect_sector, get_z_and_price, get_sector_analysis,
    get_price_history, get_korean_news,
    get_macro_correlation, get_chart_data, get_price_stats,
    calc_win_rate, get_weighted_z, run_backtest,
    get_signal, zcolor, zdesc, corr_color,
    get_fear_greed, get_portfolio_lv1,
    calc_var, calc_portfolio_var, calc_monte_carlo, calc_bayesian_update,
    get_portfolio_correlation_matrix, simulate_portfolio_history,
    get_batch_portfolio_data,
    get_relative_momentum,
)


def apply_custom_style():
    dark = st.session_state.get("dark_mode", False)

    # ── 라이트 / 다크 토큰 ───────────────────────────────────────────
    if dark:
        bg        = "#0F1117"   # 앱 배경
        bg2       = "#1A1D23"   # 카드 배경
        bg3       = "#22262F"   # 서브 카드 / hover
        border    = "#2D3139"   # 구분선
        txt_main  = "#F0F2F5"   # 본문 텍스트
        txt_sub   = "#9CA3AF"   # 보조 텍스트
        txt_muted = "#6B7280"   # 흐린 텍스트
        header_bg = "#1A1D23"
        sidebar_bg= "#1A1D23"
        input_bg  = "#22262F"
        tab_bg    = "#22262F"
        tab_sel   = "#2D3139"
        action_th = "#22262F"
        news_neu  = "#22262F"
        news_neu_border = "#374151"
        btn_bg    = "#22262F"
        btn_border= "#374151"
        btn_txt   = "#D1D5DB"
        btn_hover = "#2D3139"
        lv1_bg="#1E3A5F"; lv1_txt="#60A5FA"; lv1_bdr="#1D4ED8"
        lv2_bg="#3B1F0A"; lv2_txt="#FB923C"; lv2_bdr="#92400E"
        lv3_bg="#2E1065"; lv3_txt="#A78BFA"; lv3_bdr="#5B21B6"
        badge_g_bg="#022C22"; badge_g_bdr="#065F46"
        badge_y_bg="#2D1B00"; badge_y_bdr="#92400E"
        badge_r_bg="#2D0A0A"; badge_r_bdr="#991B1B"
        sns_h_bg="#2D0A0A"; sns_m_bg="#2D1B00"; sns_l_bg="#1F2937"
        stat_bg   = "#22262F"
    else:
        bg        = "#F7F8FA"
        bg2       = "#FFFFFF"
        bg3       = "#F9FAFB"
        border    = "#E8EAED"
        txt_main  = "#1A1D23"
        txt_sub   = "#6B7280"
        txt_muted = "#9CA3AF"
        header_bg = "#FFFFFF"
        sidebar_bg= "#FFFFFF"
        input_bg  = "#FFFFFF"
        tab_bg    = "#F3F4F6"
        tab_sel   = "#FFFFFF"
        action_th = "#F9FAFB"
        news_neu  = "#F9FAFB"
        news_neu_border = "#D1D5DB"
        btn_bg    = "#FFFFFF"
        btn_border= "#D1D5DB"
        btn_txt   = "#374151"
        btn_hover = "#F9FAFB"
        lv1_bg="#EFF6FF"; lv1_txt="#2563EB"; lv1_bdr="#BFDBFE"
        lv2_bg="#FFF7ED"; lv2_txt="#EA580C"; lv2_bdr="#FED7AA"
        lv3_bg="#F5F3FF"; lv3_txt="#7C3AED"; lv3_bdr="#DDD6FE"
        badge_g_bg="#ECFDF5"; badge_g_bdr="#A7F3D0"
        badge_y_bg="#FFFBEB"; badge_y_bdr="#FDE68A"
        badge_r_bg="#FEF2F2"; badge_r_bdr="#FECACA"
        sns_h_bg="#FEF2F2"; sns_m_bg="#FFFBEB"; sns_l_bg="#F9FAFB"
        stat_bg   = "#FFFFFF"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* ── 기본 배경 / 텍스트 ── */
.stApp{{background:{bg};color:{txt_main};font-family:'Inter',sans-serif;}}
header[data-testid="stHeader"]{{background:{header_bg};border-bottom:1px solid {border};}}
.stDeployButton{{display:none;}} #MainMenu{{display:none;}} footer{{display:none;}}
section[data-testid="stSidebar"]{{background:{sidebar_bg};border-right:1px solid {border};}}
/* 사이드바 내부 콘텐츠 좌우 여백 — 입력칸 잘림 방지 */
section[data-testid="stSidebar"] > div:first-child{{
  padding-left:16px !important;
  padding-right:16px !important;
  padding-top:20px !important;
  padding-bottom:20px !important;
}}

/* ── 카드 컴포넌트 ── */
.macro-card{{background:{bg2};border:1px solid {border};border-radius:10px;padding:14px 18px;}}
.section-hdr{{font-size:11px;font-weight:600;color:{txt_sub};letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid {border};}}
.stock-card{{background:{bg2};border:1px solid {border};border-radius:10px;padding:16px 18px;}}
.ind-card{{background:{bg2};border:1px solid {border};border-radius:8px;padding:12px 16px;margin-bottom:8px;}}
.stat-box{{background:{stat_bg};border:1px solid {border};border-radius:8px;padding:10px;text-align:center;}}

/* ── 배지 ── */
.badge-green{{background:{badge_g_bg};color:#059669;border:1px solid {badge_g_bdr};border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}}
.badge-yellow{{background:{badge_y_bg};color:#D97706;border:1px solid {badge_y_bdr};border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}}
.badge-red{{background:{badge_r_bg};color:#DC2626;border:1px solid {badge_r_bdr};border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;display:inline-block;}}

/* ── Lv 배지 ── */
.lv1{{background:{lv1_bg};color:{lv1_txt};border:1px solid {lv1_bdr};border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}}
.lv2{{background:{lv2_bg};color:{lv2_txt};border:1px solid {lv2_bdr};border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}}
.lv3{{background:{lv3_bg};color:{lv3_txt};border:1px solid {lv3_bdr};border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;}}

/* ── 뉴스 카드 ── */
.news-pos{{background:{"#022C22" if dark else "#ECFDF5"};border-left:3px solid #059669;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}}
.news-neg{{background:{"#2D0A0A" if dark else "#FEF2F2"};border-left:3px solid #DC2626;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}}
.news-neu{{background:{news_neu};border-left:3px solid {news_neu_border};padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:10px;}}

/* ── Sensitivity 배지 ── */
.sensitivity-high{{background:{sns_h_bg};color:#DC2626;border:1px solid #FECACA;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}}
.sensitivity-mid{{background:{sns_m_bg};color:#D97706;border:1px solid #FDE68A;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}}
.sensitivity-low{{background:{sns_l_bg};color:{txt_sub};border:1px solid {border};border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;}}

/* ── 기간 버튼 ── */
.period-btn-active button{{background:{txt_main} !important;color:{bg} !important;border-color:{txt_main} !important;font-weight:700 !important;}}
div[data-testid="stButton"][data-key^="p_"] > button{{font-size:11px !important;padding:2px 4px !important;height:26px !important;min-height:0 !important;}}

/* ── Action Plan 테이블 ── */
.action-table{{width:100%;border-collapse:collapse;font-size:12px;}}
.action-table th{{background:{action_th};color:{txt_sub};font-weight:600;padding:8px 12px;text-align:left;border-bottom:1px solid {border};}}
.action-table td{{padding:10px 12px;border-bottom:1px solid {border};color:{txt_main};vertical-align:top;}}
.action-table tr:last-child td{{border-bottom:none;}}

/* ── Streamlit 기본 버튼 ── */
div[data-testid="stButton"] button{{background:{btn_bg};color:{btn_txt};border:1px solid {btn_border};border-radius:7px;font-size:12px;font-weight:500;padding:6px 16px;}}
div[data-testid="stButton"] button:hover{{background:{btn_hover};border-color:{txt_muted};}}

/* ── 입력창 ── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div{{background:{input_bg} !important;border:1px solid {btn_border} !important;border-radius:7px !important;color:{txt_main} !important;font-size:13px !important;}}
div[data-testid="stTextArea"] textarea{{background:{input_bg} !important;border:1px solid {btn_border} !important;color:{txt_main} !important;font-size:12px !important;border-radius:7px !important;}}

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"]{{gap:2px;background:{tab_bg};border-radius:8px;padding:3px;border:1px solid {border};}}
.stTabs [data-baseweb="tab"]{{height:32px;font-size:12px;font-weight:500;color:{txt_sub};border-radius:6px;padding:0 14px;}}
.stTabs [aria-selected="true"]{{background:{tab_sel} !important;color:{txt_main} !important;box-shadow:0 1px 3px rgba(0,0,0,{"0.3" if dark else "0.1"});}}

/* ── 기타 ── */
.stSlider > div > div > div{{background:#2563EB !important;}}
.stSpinner > div{{border-top-color:#2563EB !important;}}

/* ── expander ── */
div[data-testid="stExpander"]{{background:{bg2};border:1px solid {border} !important;border-radius:8px;}}
div[data-testid="stExpander"] summary{{color:{txt_main};}}

/* ── st.info / st.success / st.error ── */
div[data-testid="stAlert"]{{background:{bg2} !important;border-color:{border} !important;color:{txt_main} !important;}}

/* ── 기본 여백 (데스크탑/모바일 공통) ── */
.block-container{{
  padding-left:20px !important;
  padding-right:20px !important;
  padding-top:32px !important;
  padding-bottom:48px !important;
  max-width:100% !important;
}}

/* 요소 간 세로 여백 */
div[data-testid="stVerticalBlock"] > div{{
  margin-bottom:6px;
}}

/* 카드 간 여백 */
.stock-card{{margin-bottom:16px;}}
.ind-card{{margin-bottom:12px;}}

/* 사이드바 너비 */
section[data-testid="stSidebar"]{{
  min-width:280px !important;
  max-width:300px !important;
}}

/* ── number_input 잘림 방지 (사이드바 포함 전체) ── */
div[data-testid="stNumberInput"]{{
  width:100% !important;
}}
div[data-testid="stNumberInput"] > div{{
  display:flex !important;
  align-items:center !important;
  width:100% !important;
  gap:4px !important;
}}
div[data-testid="stNumberInput"] input{{
  flex:1 1 auto !important;
  min-width:0 !important;        /* flex 잘림 방지 핵심 */
  width:100% !important;
  box-sizing:border-box !important;
}}
/* +/- 버튼은 shrink 금지 */
div[data-testid="stNumberInput"] button{{
  flex:0 0 36px !important;
  width:36px !important;
  min-width:36px !important;
}}

@media (max-width: 768px) {{
  /* 여백 */
  .block-container{{
    padding-left:16px !important;
    padding-right:16px !important;
    padding-top:28px !important;
    padding-bottom:56px !important;
  }}

  /* 사이드바 내부 모바일 패딩 */
  section[data-testid="stSidebar"] > div:first-child{{
    padding-left:14px !important;
    padding-right:14px !important;
  }}

  /* 카드 */
  .stock-card{{padding:14px !important;border-radius:10px !important;margin-bottom:14px !important;}}
  .ind-card{{padding:12px !important;margin-bottom:10px !important;}}
  .macro-card{{padding:12px !important;}}

  /* 버튼 터치 영역 */
  div[data-testid="stButton"] button{{
    min-height:46px !important;
    font-size:13px !important;
    padding:10px 12px !important;
  }}

  /* 탭 */
  .stTabs [data-baseweb="tab-list"]{{
    gap:1px !important;
    padding:2px !important;
  }}
  .stTabs [data-baseweb="tab"]{{
    padding:0 7px !important;
    font-size:10px !important;
    height:32px !important;
  }}

  /* 테이블 */
  .action-table td{{padding:10px 8px !important;font-size:11px !important;}}
  .action-table th{{padding:8px !important;font-size:11px !important;}}

  /* 승률 큰 숫자 */
  .win-big{{font-size:38px !important;}}

  /* 사이드바 */
  section[data-testid="stSidebar"]{{
    min-width:260px !important;
    max-width:285px !important;
  }}

  /* 입력창 — iOS 자동 줌 방지(16px), 터치 크기 확보 */
  div[data-testid="stNumberInput"] input,
  div[data-testid="stTextInput"] input{{
    font-size:16px !important;
    min-height:42px !important;
    padding:8px 10px !important;
  }}

  /* selectbox */
  div[data-testid="stSelectbox"] > div{{
    min-height:42px !important;
    font-size:14px !important;
  }}

  /* expander */
  div[data-testid="stExpander"]{{padding:6px !important;}}

  /* plotly 터치 스크롤 */
  .js-plotly-plot{{touch-action:pan-y !important;}}

  /* 섹션 헤더 */
  .section-hdr{{
    font-size:10px !important;
    margin-bottom:10px !important;
    margin-top:6px !important;
  }}

  /* 배지 */
  .badge-green,.badge-yellow,.badge-red{{
    padding:3px 8px !important;
    font-size:9px !important;
  }}

  /* stat-box */
  .stat-box{{padding:10px 6px !important;}}

  /* 카드 간 여백 */
  .stock-card{{margin-bottom:16px !important;}}
  .ind-card{{margin-bottom:12px !important;}}

  /* 섹션 사이 여백 */
  .section-hdr{{margin-top:20px !important;}}
}}

/* 아이폰 노치/홈바 대응 */
@supports (padding-bottom: env(safe-area-inset-bottom)) {{
  .block-container{{
    padding-bottom: calc(40px + env(safe-area-inset-bottom)) !important;
  }}
}}
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
        '<h2 style="font-size:22px;font-weight:700;color:#1A1D23;margin:0 0 4px;">🔭 Signum</h2>'
        '<p style="font-size:13px;color:#6B7280;margin:0 0 12px;">시장 신호 기반 종목 분석</p>',
        unsafe_allow_html=True
    )

    # ── 앱 사용법 안내 (접이식) ──────────────────────────────────
    with st.expander('📖 이 앱을 어떻게 쓰면 좋을까요?', expanded=False):
        st.markdown(
            '<div style="font-size:12px;color:#374151;line-height:1.9;">'
            '<b style="font-size:13px;">Signum은 매수 타이밍을 알려주는 앱이 아닙니다.</b><br>'
            '주가 위치 · 거시 환경 · 모멘텀 · 뉴스를 종합해 '
            '<b>지금 이 종목의 환경이 유리한지 불리한지</b>를 수치로 보여주는 도구예요.<br><br>'
            '<b>✅ 이렇게 쓰면 효과적입니다</b><br>'
            '· 이미 보유한 종목에서 <b>비중을 늘릴지, 줄일지, 유지할지</b> 판단할 때<br>'
            '· 승률이 낮은 종목이 있다면 → 추가 매수 자제, 손절 라인 점검<br>'
            '· 승률이 높은 종목이 있다면 → 분할 매수 고려 (확신은 금물)<br>'
            '· 포트폴리오 전체를 보면서 <b>가장 취약한 종목</b>을 파악할 때<br><br>'
            '<b>⚠ 이것만은 주의하세요</b><br>'
            '· 승률 수치는 <b>과거 통계 기반</b>이에요. 미래를 예측하지 않아요.<br>'
            '· 전쟁 휴전, 금리 발표 같은 <b>돌발 이벤트는 어떤 지표도 예측 못 해요.</b><br>'
            '· 승률이 낮다고 반드시 떨어지는 것도, 높다고 반드시 오르는 것도 아니에요.<br>'
            '· 이 앱은 <b>가속 페달이 아니라 브레이크</b>예요. 리스크 관리 도구로 쓰세요.<br><br>'
            '<span style="color:#9CA3AF;font-size:11px;">'
            '백테스트 탭에서 이 앱의 과거 신호 적중률을 직접 확인할 수 있어요.</span>'
            '</div>',
            unsafe_allow_html=True
        )

    # 거시 지표
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-hdr">📡 주요 거시 지표</div>', unsafe_allow_html=True)
    cards_html = ""
    for (label, sym, desc) in MACRO_INDICATORS:
        z, price = get_z_and_price(sym)
        arrow = "▲" if z > 0.2 else "▼" if z < -0.2 else "—"
        ac    = "#059669" if z > 0.2 else "#DC2626" if z < -0.2 else "#6B7280"
        cards_html += (
            f'<div style="flex:0 0 30%;min-width:100px;max-width:130px;'
            f'background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:8px 12px;">'
            f'<div style="font-size:9px;font-weight:600;color:#9CA3AF;margin-bottom:2px;'
            f'letter-spacing:0.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{label}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:14px;font-weight:700;'
            f'color:{zcolor(z)};line-height:1.2;">'
            f'{price:,.2f} <span style="font-size:11px;color:{ac};">{arrow}</span></div>'
            f'<div style="font-size:9px;color:#B0B7C3;margin-top:2px;">Z {z:+.2f}σ</div></div>'
        )
    st.markdown(
        f'<div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:6px;'
        f'-webkit-overflow-scrolling:touch;scrollbar-width:none;">'
        f'{cards_html}</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    portfolio = st.session_state.portfolio

    # ── Lv.1: 포트폴리오 날씨 ────────────────────────────────────────
    if portfolio:
        fg_score, fg_label, fg_clr = get_fear_greed()
        _lv1_ph = st.empty()
        _lv1_ph.markdown(
            '<div style="background:#F9FAFB;border:1px solid #E8EAED;border-radius:8px;'
            'padding:8px 14px;font-size:12px;color:#9CA3AF;">⏳ 포트폴리오 날씨 계산 중...</div>',
            unsafe_allow_html=True
        )
        avg_win, w_icon, w_label, w_clr, w_summary = get_portfolio_lv1(portfolio)
        _lv1_ph.empty()
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:12px;'
            f'padding:14px 18px;margin-bottom:16px;">'
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:10px;">'
            f'<span class="lv1">Lv.1</span>'
            f'<span style="font-size:12px;font-weight:600;color:#1A1D23;">오늘 내 계좌 날씨</span>'
            f'</div>'
            f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">'
            f'<div style="text-align:center;min-width:70px;">'
            f'<div style="font-size:36px;line-height:1;">{w_icon}</div>'
            f'<div style="font-size:11px;font-weight:700;color:{w_clr};margin-top:4px;">{w_label}</div>'
            f'</div>'
            f'<div style="flex:1;min-width:140px;">'
            f'<div style="display:flex;justify-content:space-between;font-size:11px;'
            f'color:#6B7280;margin-bottom:4px;">'
            f'<span>포트폴리오 평균 승률</span>'
            f'<span style="font-weight:700;color:{w_clr};">{avg_win:.0f}%</span></div>'
            f'<div style="height:8px;background:#F3F4F6;border-radius:4px;">'
            f'<div style="height:100%;width:{avg_win}%;background:{w_clr};border-radius:4px;'
            f'transition:width 0.3s;"></div></div>'
            f'<div style="font-size:11px;color:#6B7280;margin-top:6px;">{w_summary}</div>'
            f'</div>'
            f'<div style="text-align:center;min-width:60px;">'
            f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:2px;">공포·탐욕</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:20px;'
            f'font-weight:700;color:{fg_clr};">{fg_score}</div>'
            f'<div style="font-size:10px;color:{fg_clr};font-weight:600;">{fg_label}</div>'
            f'</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

        # ── 포트폴리오 전체 VaR ──────────────────────────────────────
        _var_ph = st.empty()
        _var_ph.markdown(
            '<div style="background:#F9FAFB;border:1px solid #E8EAED;border-radius:8px;'
            'padding:8px 14px;font-size:12px;color:#9CA3AF;">⏳ 리스크(VaR) 계산 중...</div>',
            unsafe_allow_html=True
        )
        pvar = calc_portfolio_var(portfolio, confidence=0.95)
        _var_ph.empty()
        if pvar:
            v_clr = "#DC2626" if pvar["var_7d"] < -5 else "#D97706" if pvar["var_7d"] < -3 else "#059669"
            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:12px;'
                f'padding:12px 18px;margin-bottom:16px;">'
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">'
                f'<span class="lv3">Lv.3</span>'
                f'<span style="font-size:12px;font-weight:600;color:#1A1D23;">'
                f'포트폴리오 전체 리스크 (VaR {pvar["confidence"]}%)</span>'
                f'</div>'
                f'<div style="display:flex;gap:10px;flex-wrap:wrap;">'
                f'<div style="flex:1;min-width:70px;background:#F9FAFB;border-radius:8px;padding:10px;text-align:center;">'
                f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:3px;">7일 최대손실</div>'
                f'<div style="font-size:16px;font-weight:700;color:{v_clr};">{pvar["var_7d"]:+.2f}%</div>'
                f'</div>'
                f'<div style="flex:1;min-width:70px;background:#F9FAFB;border-radius:8px;padding:10px;text-align:center;">'
                f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:3px;">1달 최대손실</div>'
                f'<div style="font-size:16px;font-weight:700;color:{v_clr};">{pvar["var_1mo"]:+.2f}%</div>'
                f'</div>'
                f'<div style="flex:1;min-width:70px;background:#F9FAFB;border-radius:8px;padding:10px;text-align:center;">'
                f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:3px;">1년 최대손실</div>'
                f'<div style="font-size:16px;font-weight:700;color:{v_clr};">{pvar["var_1y"]:+.2f}%</div>'
                f'</div>'
                f'<div style="flex:1;min-width:70px;background:#FEF2F2;border-radius:8px;padding:10px;text-align:center;">'
                f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:3px;">7일 예상손실액</div>'
                f'<div style="font-size:16px;font-weight:700;color:#DC2626;">${pvar["amount_7d"]:,.0f}</div>'
                f'</div>'
                f'</div>'
                f'<div style="font-size:10px;color:#B0B7C3;margin-top:8px;">'
                f'총 평가금액 ${pvar["total_value"]:,.0f} 기준 · 과거 1년 수익률 기반 참고치</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    if not portfolio:
        st.markdown(
            '<div style="background:#FFFFFF;border:2px dashed #D1D5DB;border-radius:12px;'
            'padding:48px;text-align:center;">'
            '<div style="font-size:36px;margin-bottom:10px;">📭</div>'
            '<div style="font-size:16px;font-weight:600;color:#374151;margin-bottom:6px;">아직 종목이 없습니다</div>'
            '<div style="font-size:13px;color:#9CA3AF;">아래 버튼을 눌러 첫 종목을 추가해보세요.</div>'
            '<div style="font-size:11px;color:#D1D5DB;margin-top:8px;">예시: AAPL · TSLA · NVDA · XOM · JPM</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("➕ 종목 추가하기", use_container_width=True, key="empty_add_btn", type="primary"):
            st.session_state.show_add   = True
            st.session_state.open_sidebar = True
            st.rerun()

        # 버튼 클릭 후 show_add가 켜진 상태면 메인화면에서 바로 검색창 표시
        if st.session_state.get('show_add'):
            st.markdown('---')
            st.markdown(
                '<div style="font-size:14px;font-weight:600;color:#1A1D23;margin-bottom:8px;">'
                '🔍 종목 검색 — 사이드바에서도 추가할 수 있어요</div>',
                unsafe_allow_html=True
            )
            st.info('← 왼쪽 상단 > 버튼으로 사이드바를 열어 종목을 추가하세요. 📱 모바일에서는 화면 왼쪽 끝을 오른쪽으로 스와이프해도 열려요.')
        return

    st.markdown(
        '<div class="section-hdr" style="margin-top:20px;">📈 보유 종목 분석 '
        '<span class="lv1" style="margin-left:6px;">Lv.1 / Lv.2</span></div>',
        unsafe_allow_html=True
    )

    # ── 배치 로딩 — 종목별 실시간 진행 표시 ─────────────────────────
    _tickers_t = tuple(s["ticker"] for s in portfolio)
    _n = len(portfolio)

    # 캐시 히트 여부: get_batch_portfolio_data는 ttl=600 캐시
    # 첫 로딩(캐시 미스)이면 종목당 약 3~5초 소요 안내
    _load_placeholder = st.empty()
    _prog_placeholder = st.empty()

    if _n > 0:
        _load_placeholder.markdown(
            f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;'
            f'padding:10px 14px;margin-bottom:8px;font-size:12px;color:#2563EB;">'
            f'📡 {_n}개 종목 시장 데이터 수집 중'
            f'<span style="color:#9CA3AF;font-size:11px;margin-left:8px;">'
            f'처음 로딩 시 {_n * 3}~{_n * 5}초 소요 · 이후 빠르게 캐시 제공</span></div>',
            unsafe_allow_html=True
        )
        _prog_placeholder.progress(0, text="준비 중...")

    _batch = get_batch_portfolio_data(_tickers_t)

    # 로딩 완료 — 안내 메시지 제거
    _load_placeholder.empty()
    _prog_placeholder.empty()

    for rs in range(0, len(portfolio), 2):
        row  = list(enumerate(portfolio[rs: rs + 2], start=rs))
        cols = st.columns(len(row))
        for col, (pi, stock) in zip(cols, row):
            with col:
                _d        = _batch.get(stock["ticker"], {})
                zs        = _d.get("z", 0.0)
                price     = _d.get("price", 0.0)
                cfg       = _d.get("cfg", SECTOR_CONFIG["Unknown"])
                inds      = _d.get("inds", [])
                win       = _d.get("win", 50.0)
                breakdown = _d.get("breakdown", {})

                st_, sc_, sv_ = get_signal(win)
                pnl = ((price - stock["avg_price"]) / stock["avg_price"] * 100) \
                      if price and stock["avg_price"] > 0 else None
                pnl_text = f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "—"
                pc   = "#059669" if (pnl or 0) >= 0 else "#DC2626"
                ti   = max(inds, key=lambda x: abs(x["z"] * x["driver_weight"])) if inds else {"name": "—", "direction": 1, "z": 0.0}
                tc   = ti["z"] * ti["direction"]
                tclr = "#059669" if tc > 0 else "#DC2626"
                weighted_z = get_weighted_z(inds)

                # 평가손익 금액
                shares    = stock.get("shares", 0)
                eval_val  = price * shares if price and shares else 0
                cost_val  = stock["avg_price"] * shares if shares else 0
                pnl_amt   = eval_val - cost_val
                pnl_amt_str = f"{'+'if pnl_amt>=0 else ''}${pnl_amt:,.0f}" if shares > 0 else "—"
                pnl_amt_clr = "#059669" if pnl_amt >= 0 else "#DC2626"

                # 비중 경고
                weight_warn = ""
                if win < 45 and stock["weight"] > 20:
                    weight_warn = f'<div style="font-size:10px;color:#DC2626;margin-top:3px;">⚠ 승률 낮은데 비중 {stock["weight"]:.0f}% — 축소 고려</div>'
                elif win < 45 and stock["weight"] > 10:
                    weight_warn = f'<div style="font-size:10px;color:#D97706;margin-top:3px;">⚠ 승률 낮음 — 비중 주의</div>'

                # 직관적 거시환경 표현
                if weighted_z > 0.3:    macro_txt = "📈 시장 환경 유리"
                elif weighted_z < -0.3: macro_txt = "📉 시장 환경 불리"
                else:                   macro_txt = "➡ 시장 환경 중립"
                macro_clr = "#059669" if weighted_z > 0.3 else "#DC2626" if weighted_z < -0.3 else "#6B7280"

                # 실적/가이던스 배지 (메인 카드용 — 감지된 경우만 표시)
                eg_card_html = ""
                eg_signals_card = breakdown.get("earnings_guidance_signals", [])
                if eg_signals_card:
                    badges = []
                    for sig in eg_signals_card[:2]:   # 최대 2개만 카드에 표시
                        is_pos = sig["direction"] == "긍정"
                        b_bg  = "#ECFDF5" if is_pos else "#FEF2F2"
                        b_txt = "#065F46" if is_pos else "#991B1B"
                        badges.append(
                            f'<span style="background:{b_bg};color:{b_txt};'
                            f'font-size:9px;font-weight:600;padding:2px 6px;'
                            f'border-radius:4px;margin-right:3px;">{sig["badge"]}</span>'
                        )
                    eg_card_html = (
                        f'<div style="margin-top:4px;margin-bottom:2px;">{"".join(badges)}</div>'
                    )

                st.markdown(f"""
<div class="stock-card" style="border-top:3px solid {sv_};">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
        <div><span style="font-weight:700;font-size:15px;color:#1A1D23;">{stock['ticker']}</span>
        <span style="font-size:11px;color:{cfg['color']};margin-left:4px;">{cfg['icon']}</span>
        <div style="font-size:10px;color:#9CA3AF;">{stock['name']}</div></div>
        <div class="{sc_}">{st_}</div>
    </div>
    <div style="display:flex;align-items:baseline;gap:4px;margin-bottom:4px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:700;
                     color:{sv_};line-height:1;">{win}%</span>
        <span style="font-size:10px;color:#9CA3AF;">상승 가능성</span>
    </div>
    <div style="font-size:10px;color:{macro_clr};margin-bottom:4px;">{macro_txt}</div>
    {eg_card_html}
    <div style="font-size:10px;color:{tclr};margin-bottom:6px;">
        {'▲' if tc>0 else '▼'} {ti['name']} 주요 변수
    </div>
    <div style="display:flex;justify-content:space-between;font-size:11px;
                padding-top:8px;border-top:1px solid #F3F4F6;margin-top:4px;">
        <span style="color:#6B7280;">${price:.1f}</span>
        <span style="color:{pc};font-weight:500;">{pnl_text}</span>
        <span style="color:{pnl_amt_clr};font-weight:600;">{pnl_amt_str}</span>
    </div>
</div>""", unsafe_allow_html=True)
                if weight_warn:
                    st.markdown(weight_warn, unsafe_allow_html=True)
                st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                if st.button("상세 분석 →", key=f"go_{stock['ticker']}_{pi}"):
                    st.session_state.selected = stock["ticker"]
                    st.session_state.page     = "detail"
                    st.rerun()

    # 배분 차트
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-hdr">📊 포트폴리오 구성</div>', unsafe_allow_html=True)
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
        margin=dict(t=10, b=10, l=10, r=10), height=180,
        annotations=[dict(
            text=f"<b>{sum(weights):.1f}%</b>", x=0.5, y=0.5,
            font=dict(size=14, color="#1A1D23"), showarrow=False
        )]
    )
    st.plotly_chart(fig, use_container_width=True)
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
    # ── 섹션 B: 포트폴리오 수익률 시뮬레이션 (6개월) ─────────────────────────
    if len(portfolio) >= 2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">📈 포트폴리오 6개월 수익률 시뮬레이션</div>', unsafe_allow_html=True)
        with st.spinner("수익률 시뮬레이션 계산 중..."):
            port_snap = tuple((s["ticker"], s["weight"]) for s in portfolio)
            sim = simulate_portfolio_history(port_snap)

        if sim:
            final = sim["final_ret"]
            spy_f = sim["spy_final_ret"]
            mdd   = sim["max_drawdown"]
            alpha = round(final - spy_f, 2)
            f_clr = "#059669" if final >= 0 else "#DC2626"
            s_clr = "#059669" if spy_f >= 0 else "#DC2626"
            a_clr = "#059669" if alpha >= 0 else "#DC2626"
            m_clr = "#DC2626" if mdd < -10 else "#D97706" if mdd < -5 else "#059669"

            # KPI 행
            kpi_html = (
                f'<div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;">'
                f'<div style="flex:1;min-width:70px;background:#F9FAFB;border-radius:8px;padding:10px;text-align:center;">'
                f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:2px;">내 포트폴리오</div>'
                f'<div style="font-size:18px;font-weight:700;color:{f_clr};">{final:+.2f}%</div></div>'
                f'<div style="flex:1;min-width:70px;background:#F9FAFB;border-radius:8px;padding:10px;text-align:center;">'
                f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:2px;">S&P500 벤치마크</div>'
                f'<div style="font-size:18px;font-weight:700;color:{s_clr};">{spy_f:+.2f}%</div></div>'
                f'<div style="flex:1;min-width:70px;background:#F9FAFB;border-radius:8px;padding:10px;text-align:center;">'
                f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:2px;">초과수익(α)</div>'
                f'<div style="font-size:18px;font-weight:700;color:{a_clr};">{alpha:+.2f}%</div></div>'
                f'<div style="flex:1;min-width:70px;background:#FEF2F2;border-radius:8px;padding:10px;text-align:center;">'
                f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:2px;">최대 낙폭(MDD)</div>'
                f'<div style="font-size:18px;font-weight:700;color:{m_clr};">{mdd:.2f}%</div></div>'
                f'</div>'
            )

            # 라인 차트
            sim_fig = go.Figure()
            sim_fig.add_trace(go.Scatter(
                x=sim["dates"], y=sim["portfolio_returns"],
                mode="lines", name="내 포트폴리오",
                line=dict(color="#2563EB", width=2.5),
                fill="tozeroy",
                fillcolor="rgba(37,99,235,0.08)",
                hovertemplate="<b>포트폴리오</b>: %{y:+.2f}%<extra></extra>",
            ))
            sim_fig.add_trace(go.Scatter(
                x=sim["dates"], y=sim["spy_returns"],
                mode="lines", name="S&P500",
                line=dict(color="#9CA3AF", width=1.5, dash="dot"),
                hovertemplate="<b>S&P500</b>: %{y:+.2f}%<extra></extra>",
            ))
            sim_fig.add_hline(y=0, line_dash="dash", line_color="#E8EAED", line_width=1)
            sim_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(248,250,252,0.5)",
                margin=dict(t=10, b=4, l=0, r=10), height=200,
                legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#E8EAED",
                            borderwidth=1, font=dict(size=10), orientation="h", y=1.04, x=0),
                xaxis=dict(showgrid=False, tickfont=dict(size=9, color="#9CA3AF")),
                yaxis=dict(showgrid=True, gridcolor="#F3F4F6", ticksuffix="%",
                           tickfont=dict(size=9, color="#9CA3AF"), side="right"),
                hovermode="x unified",
            )

            # 종목별 수익 바 차트
            if sim["stock_rets"]:
                sr_items = sorted(sim["stock_rets"].items(), key=lambda x: -x[1])
                sr_labels = [x[0] for x in sr_items]
                sr_vals   = [x[1] for x in sr_items]
                sr_colors = ["#059669" if v >= 0 else "#DC2626" for v in sr_vals]
                bar_fig = go.Figure(go.Bar(
                    x=sr_labels, y=sr_vals,
                    marker_color=sr_colors, opacity=0.85,
                    text=[f"{v:+.1f}%" for v in sr_vals],
                    textposition="outside",
                    textfont=dict(size=10),
                    hovertemplate="<b>%{x}</b>: %{y:+.2f}%<extra></extra>",
                ))
                bar_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=0, l=0, r=0), height=150,
                    xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                    yaxis=dict(showgrid=False, ticksuffix="%", tickfont=dict(size=9)),
                    showlegend=False,
                )

            best_t, best_r = sim["best_stock"]
            worst_t, worst_r = sim["worst_stock"]

            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:12px;padding:14px 16px;">'
                f'<div style="font-size:11px;color:#9CA3AF;margin-bottom:10px;">'
                f'6개월 전 현재 비중대로 구성했다면 (과거 데이터 기반 참고치)</div>'
                f'{kpi_html}',
                unsafe_allow_html=True
            )
            st.plotly_chart(sim_fig, use_container_width=True)
            if sim["stock_rets"]:
                st.markdown('<div style="font-size:10px;color:#9CA3AF;margin:4px 0 2px;padding:0 2px;">종목별 6개월 수익률</div>', unsafe_allow_html=True)
                st.plotly_chart(bar_fig, use_container_width=True)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;font-size:11px;color:#6B7280;padding:0 2px 8px;">'
                f'<span>🏆 최고: <b style="color:#059669;">{best_t} {best_r:+.1f}%</b></span>'
                f'<span>📉 최저: <b style="color:#DC2626;">{worst_t} {worst_r:+.1f}%</b></span></div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("시뮬레이션 데이터를 불러올 수 없습니다. (종목당 최소 20거래일 데이터 필요)")

    # ── 섹션 C: 종목 간 상관관계 히트맵 ─────────────────────────────────────
    if len(portfolio) >= 2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">🔗 종목 간 상관관계 히트맵</div>', unsafe_allow_html=True)
        with st.spinner("상관계수 계산 중..."):
            tickers_t = tuple(s["ticker"] for s in portfolio)
            corr_mat, warnings = get_portfolio_correlation_matrix(tickers_t)

        if corr_mat is not None:
            # 경고 배너
            if warnings:
                warn_html = ""
                for w in warnings[:3]:
                    clr = "#DC2626" if w["type"] == "동조" else "#7C3AED"
                    warn_html += (
                        f'<span style="background:#FEF2F2;border:1px solid #FECACA;'
                        f'border-radius:4px;padding:2px 8px;font-size:11px;color:{clr};'
                        f'font-weight:600;margin-right:6px;margin-bottom:4px;display:inline-block;">'
                        f'⚠ {w["t1"]}↔{w["t2"]} r={w["r"]:+.2f} ({w["type"]})</span>'
                    )
                st.markdown(
                    f'<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;'
                    f'padding:10px 14px;margin-bottom:10px;">'
                    f'<div style="font-size:11px;font-weight:700;color:#D97706;margin-bottom:6px;">'
                    f'⚠ 고상관 종목 감지 (분산 효과 감소)</div>'
                    f'{warn_html}'
                    f'<div style="font-size:10px;color:#9CA3AF;margin-top:6px;">'
                    f'r ≥ 0.75이면 두 종목이 거의 같이 움직입니다. 진정한 분산을 위해 종목을 조정하세요.</div></div>',
                    unsafe_allow_html=True
                )

            tickers_list = corr_mat.columns.tolist()
            z_vals = corr_mat.values.tolist()

            # 색상 구성: 대각선=회색, 양=파랑, 음=빨강
            heatmap_fig = go.Figure(go.Heatmap(
                z=z_vals,
                x=tickers_list,
                y=tickers_list,
                colorscale=[
                    [0.0,  "#DC2626"],
                    [0.4,  "#FCA5A5"],
                    [0.5,  "#F3F4F6"],
                    [0.6,  "#93C5FD"],
                    [1.0,  "#1D4ED8"],
                ],
                zmin=-1, zmax=1,
                text=[[f"{v:.2f}" for v in row] for row in z_vals],
                texttemplate="%{text}",
                textfont=dict(size=11, color="#1A1D23"),
                hovertemplate="<b>%{x} ↔ %{y}</b><br>상관계수: %{z:.3f}<extra></extra>",
                showscale=True,
                colorbar=dict(
                    thickness=10, len=0.8,
                    tickvals=[-1, -0.5, 0, 0.5, 1],
                    ticktext=["-1", "-0.5", "0", "+0.5", "+1"],
                    tickfont=dict(size=9),
                )
            ))
            n = len(tickers_list)
            cell_size = max(50, min(80, 400 // n))
            heatmap_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=60),
                height=max(200, n * cell_size + 60),
                xaxis=dict(tickfont=dict(size=11, color="#374151"), side="bottom"),
                yaxis=dict(tickfont=dict(size=11, color="#374151"), autorange="reversed"),
            )
            st.plotly_chart(heatmap_fig, use_container_width=True)
            st.markdown(
                '<div style="font-size:10px;color:#9CA3AF;margin-top:2px;">'
                '최근 3개월 일별 수익률 기반 · 파랑=동조 / 빨강=역방향 / 회색=무관</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("상관계수 데이터를 불러올 수 없습니다. (종목당 최소 20거래일 데이터 필요)")


# ── 상세 분석 페이지 ──────────────────────────────────────────────────────────
def render_detail_page():
    target = st.session_state.selected or ""
    if not target:
        st.session_state.page = "main"; st.rerun()

    if st.sidebar.button("← 대시보드로", use_container_width=True):
        st.session_state.page = "main"; st.rerun()

    if st.button("← 홈으로 돌아가기", key="btn_home_top"):
        st.session_state.page = "main"; st.rerun()

    si = next(
        (s for s in st.session_state.portfolio if s["ticker"] == target),
        {"name": target, "weight": "—", "avg_price": 0, "shares": 0}
    )

    _detail_load = st.empty()
    _detail_load.markdown(
        f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;'
        f'padding:10px 14px;margin-bottom:8px;font-size:12px;color:#2563EB;">'
        f'🔍 <b>{target}</b> 분석 중'
        f'<span style="color:#9CA3AF;font-size:11px;margin-left:8px;">'
        f'주가 · 거시환경 · 뉴스 · 승률 계산 중...</span></div>',
        unsafe_allow_html=True
    )

    zs, price        = get_z_and_price(target)
    sk, cfg, inds    = get_sector_analysis(target)
    nb, news_items   = get_korean_news(target, si.get("name", ""))
    fw_raw, breakdown = calc_win_rate(zs, inds, nb, stock_ticker=target, news_items=news_items)

    # ── 3일 이동평균 스무딩 (session_state — 캐시 함수 밖에서 안전하게 처리) ──
    _skey  = f"_win_hist_{target}"
    _shist = st.session_state.get(_skey, [])
    _shist.append(fw_raw)
    if len(_shist) > 3:
        _shist = _shist[-3:]
    st.session_state[_skey] = _shist
    fw = round(sum(_shist) / len(_shist), 1)
    # breakdown에도 반영 (Lv.2 표시용)
    breakdown["raw_final"] = fw_raw
    breakdown["final"]     = fw

    weighted_z       = get_weighted_z(inds, breakdown.get("dynamic_weights"))

    _detail_load.empty()

    st_, sc_, sv_ = get_signal(fw)
    pnl = ((price - si["avg_price"]) / si["avg_price"] * 100) \
          if price and si["avg_price"] > 0 else 0
    pc  = "#059669" if pnl >= 0 else "#DC2626"

    # ── 승률 해석 생성 ────────────────────────────────────────────────
    interp_bg, interp_border, interp_icon, interp_title, interp_body, interp_clr = \
        _win_rate_interpretation(fw, inds, zs, weighted_z)

    # 상세 헤더에 필요한 직관적 표현 계산
    # 가격 위치
    pct_val = breakdown.get("percentile", 50)
    if pct_val <= 20:   price_pos = "1년 저점 근처 🟢"
    elif pct_val <= 40: price_pos = "비교적 저렴한 구간"
    elif pct_val <= 60: price_pos = "중간 가격대"
    elif pct_val <= 80: price_pos = "비교적 비싼 구간"
    else:               price_pos = "1년 고점 근처 🔴"

    # 평가손익
    shares   = si.get("shares", 0)
    eval_val = price * shares if price and shares else 0
    cost_val = si["avg_price"] * shares if shares else 0
    pnl_amt  = eval_val - cost_val
    pnl_amt_str = f"({'+'if pnl_amt>=0 else ''}${pnl_amt:,.0f})" if shares > 0 else ""
    pnl_amt_clr = "#059669" if pnl_amt >= 0 else "#DC2626"

    # 손익분기점
    bep_pct = ((si["avg_price"] - price) / price * 100) if price and si["avg_price"] > 0 and price < si["avg_price"] else 0
    bep_txt = f"본전까지 +{bep_pct:.1f}% 필요" if bep_pct > 0 else ""
    # 상단: 종목명 + 섹터 + 신호 배지
    st.markdown(
        f'<div style="background:#FFFFFF;border-bottom:1px solid #E8EAED;'
        f'padding:16px 4px 14px;margin-bottom:0;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<div>'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:22px;font-weight:700;color:#1A1D23;">{target}</span>'
        f'<span style="font-size:16px;">{cfg["icon"]}</span>'
        f'</div>'
        f'<div style="font-size:11px;color:#9CA3AF;margin-top:2px;">{cfg["label"]} 섹터</div>'
        f'</div>'
        f'<div class="{sc_}" style="font-size:12px;">{st_}</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    # 승률 + 현재가 큰 숫자 행
    st.markdown(
        f'<div style="background:#FFFFFF;padding:16px 4px 14px;'
        f'border-bottom:3px solid {sv_};margin-bottom:16px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
        f'<div>'
        f'<div style="font-size:10px;color:#9CA3AF;margin-bottom:2px;">상승 가능성</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:44px;'
        f'font-weight:700;color:{sv_};line-height:1;" class="win-big">{fw:.1f}%</div>'
    f'<div style="font-size:11px;color:#9CA3AF;margin-top:2px;">'
    f'±{breakdown.get("confidence_range", 8.0):.0f}%p 불확실성 범위</div>'
        f'<div style="font-size:11px;color:#6B7280;margin-top:4px;">'
        f'{price_pos} · 수익률 '
        f'<span style="color:{pc};font-weight:600;">{("+" if pnl>=0 else "")}{pnl:.1f}%</span>'
        f'</div>'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:22px;'
        f'font-weight:700;color:#1A1D23;">${price:.2f}</div>'
        f'<div style="font-size:11px;color:{pnl_amt_clr};font-weight:600;margin-top:2px;">'
        f'{pnl_amt_str}</div>'
        f'<div style="font-size:11px;color:#9CA3AF;margin-top:2px;">'
        f'{si.get("shares",0)}주 · 평균 ${si["avg_price"]:.2f}</div>'
        f'</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )
    if bep_txt:
        st.markdown(
            f'<div style="font-size:10px;color:#D97706;padding:0 4px 8px;">{bep_txt}</div>',
            unsafe_allow_html=True
        )
    # AI 요약 한 줄 (핵심 드라이버 기반)
    top_pos_inds = sorted([i for i in inds if i["z"]*i["direction"]>0.3],
                          key=lambda x: abs(x["z"]*x["driver_weight"]), reverse=True)
    top_neg_inds = sorted([i for i in inds if i["z"]*i["direction"]<-0.3],
                          key=lambda x: abs(x["z"]*x["driver_weight"]), reverse=True)
    ai_items = ""
    for ind in top_pos_inds[:2]:
        ai_items += f'<div style="font-size:12px;color:#059669;">▲ {ind["name"]} 긍정적</div>'
    for ind in top_neg_inds[:2]:
        ai_items += f'<div style="font-size:12px;color:#DC2626;">▼ {ind["name"]} 리스크</div>'
    if not ai_items:
        ai_items = '<div style="font-size:12px;color:#9CA3AF;">주요 드라이버 신호 없음</div>'
    st.markdown(
        f'<div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:8px;'
        f'padding:10px 14px;margin-bottom:12px;">'
        f'<div style="font-size:10px;font-weight:700;color:#059669;margin-bottom:4px;">AI 요약</div>'
        f'{ai_items}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── 섹터 대비 상대 모멘텀 카드 ──────────────────────────────────────
    with st.spinner(''):
        _rel = get_relative_momentum(target, sk)
    _rel_clr = '#059669' if _rel['rel_20'] > 1 else '#DC2626' if _rel['rel_20'] < -1 else '#6B7280'
    _rel_bg  = '#F0FDF4' if _rel['rel_20'] > 1 else '#FEF2F2' if _rel['rel_20'] < -1 else '#F9FAFB'
    st.markdown(
        f'<div style="background:{_rel_bg};border:1px solid #E8EAED;border-radius:8px;'
        f'padding:10px 14px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">'
        f'<div>'
        f'<div style="font-size:10px;font-weight:700;color:#6B7280;margin-bottom:2px;">📊 섹터 상대 강도</div>'
        f'<div style="font-size:12px;color:{_rel_clr};font-weight:600;">{_rel["label"]}</div>'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<div style="font-size:14px;font-weight:700;color:{_rel_clr};">'
        f'{"+" if _rel["rel_20"]>=0 else ""}{_rel["rel_20"]}%</div>'
        f'<div style="font-size:10px;color:#9CA3AF;">20일 상대수익률</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    # ── 탭 ───────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 차트",
        f"{cfg['icon']} 섹터/리스크",
        "🔗 상관",
        "📰 뉴스",
        "🧪 백테스트",
    ])

    # ── TAB 1: 차트 ────────────────────────────────────────────────── ─
    with tab1:
        pk = st.session_state.chart_period

        # 차트 데이터
        with st.spinner(""):
            df    = get_chart_data(target, pk)
            stats = get_price_stats(df)

        # 스탯 카드 6개 — 차트 바로 위
        s_cols = st.columns(3)
        stat_items = [
            ("기간 수익률",    f"{'+'if stats['period_ret']>=0 else ''}{stats['period_ret']:.1f}%",
             "#059669" if stats["period_ret"] >= 0 else "#DC2626"),
            ("최대 상승(봉)",  f"+{stats['max_gain']:.2f}%",  "#059669"),
            ("최대 하락(봉)",  f"{stats['max_loss']:.2f}%",   "#DC2626"),
            ("연환산 변동성",  f"{stats['volatility']:.1f}%", "#D97706"),
            ("기간 최고가",    f"${stats['high']:.2f}",        "#1A1D23"),
            ("기간 최저가",    f"${stats['low']:.2f}",         "#1A1D23"),
        ]
        for idx, (lbl, val, clr) in enumerate(stat_items):
            col = s_cols[idx % 3]
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

            if pk in ("1개월", "3개월", "1년", "5년") and all(c in df.columns for c in ["Open", "High", "Low", "Close"]):
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

            # ── 평단가 수평선 ─────────────────────────────────────────────
            avg_p = si.get("avg_price", 0)
            if avg_p and avg_p > 0 and not df.empty:
                _avg_clr = "#059669" if price >= avg_p else "#DC2626"
                # annotation 분리: add_hline은 선만, 레이블은 add_annotation으로
                chart_fig.add_hline(
                    y=avg_p,
                    line=dict(color=_avg_clr, width=1.5, dash="dot"),
                )
                chart_fig.add_annotation(
                    x=0, xref="paper",
                    y=avg_p, yref="y",
                    text=f"평단 ${avg_p:.2f}",
                    showarrow=False,
                    font=dict(size=10, color=_avg_clr),
                    bgcolor="rgba(255,255,255,0.85)",
                    bordercolor=_avg_clr,
                    borderwidth=1,
                    borderpad=3,
                    xanchor="left",
                )

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
                    fixedrange=False,   # 축소 허용
                ),
                yaxis=dict(
                    showgrid=True, gridcolor="rgba(226,232,240,0.5)",
                    gridwidth=0.5, color="#9CA3AF",
                    tickfont=dict(size=10),
                    showline=False,
                    tickprefix="$",
                    side="right",
                    fixedrange=False,   # 축소 허용
                ),
                legend=dict(
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#E8EAED", borderwidth=1,
                    font=dict(size=10),
                    orientation="h", y=1.03, x=0
                ),
                margin=dict(t=10, b=4, l=0, r=50),
                height=240,
                hovermode="x unified",
            )
            # scrollZoom: 핀치로 확대·축소, doubleclick으로 원상복구
            _chart_cfg = {
                "scrollZoom": True,
                "displayModeBar": True,
                "modeBarButtonsToRemove": [
                    "select2d", "lasso2d", "autoScale2d",
                    "hoverClosestCartesian", "hoverCompareCartesian",
                    "toggleSpikelines",
                ],
                "modeBarButtonsToAdd": ["resetScale2d"],
                "displaylogo": False,
                "toImageButtonOptions": {"format": "png", "scale": 2},
            }
            st.plotly_chart(chart_fig, use_container_width=True, config=_chart_cfg)

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

            # ── 기간 선택 버튼 — 4개 균등, 한 줄 전체 너비 ──────────
            period_cols = st.columns(4)
            for idx, label in enumerate(["1개월", "3개월", "1년", "5년"]):
                with period_cols[idx]:
                    if st.button(
                        label,
                        key=f"p_{label}",
                        use_container_width=True,
                        type="primary" if pk == label else "secondary"
                    ):
                        st.session_state.chart_period = label
                        st.rerun()

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

        # ── Lv.1 / Lv.2 / Lv.3 패널 ─────────────────────────────────
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        lv_tab1, lv_tab2, lv_tab3 = st.tabs(["☀️ Lv.1 직관", "📊 Lv.2 분석", "🔬 Lv.3 심화"])

        # ── Lv.1: 직관 ───────────────────────────────────────────────
        with lv_tab1:
            fg_score, fg_label, fg_clr = get_fear_greed()
            pct = breakdown.get("percentile", 50.0)

            # 날씨 신호등
            if fw >= 65:   w_icon, w_label, w_clr = "☀️", "맑음 — 매수 우위",  "#059669"
            elif fw >= 50: w_icon, w_label, w_clr = "⛅", "구름 — 중립 관망",  "#D97706"
            else:          w_icon, w_label, w_clr = "🌧️", "비 — 리스크 경고", "#DC2626"

            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;'
                f'padding:16px;margin-bottom:10px;">'
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:12px;">'
                f'<span class="lv1">Lv.1</span>'
                f'<span style="font-size:12px;font-weight:600;color:#1A1D23;">직관 요약</span>'
                f'</div>'
                f'<div style="background:#EFF6FF;border-radius:6px;padding:8px 12px;margin-bottom:12px;font-size:11px;color:#2563EB;line-height:1.6;">'
                f'📌 <b>승률이란?</b> 현재 시장 환경에서 이 종목이 <b>앞으로 상승할 통계적 가능성</b>입니다.<br>'
                f'주가 위치(1년 백분위) + 거시 지표 흐름 + 뉴스 감성을 종합해 계산하며,'
                f' <b>오늘 이 순간 기준의 확률</b>입니다. 내일 주가를 예측하는 게 아니라,'
                f' 지금 매수했을 때 유리한 환경인지 불리한 환경인지를 나타냅니다.</div>'
                # 날씨
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">'
                f'<div style="font-size:40px;">{w_icon}</div>'
                f'<div>'
                f'<div style="font-size:14px;font-weight:700;color:{w_clr};">{w_label}</div>'
                f'<div style="font-size:12px;color:#6B7280;margin-top:2px;">'
                f'오늘의 승률 <b style="color:{sv_};">{fw:.0f}%</b></div>'
                f'</div></div>'
                # 승률 게이지
                f'<div style="margin-bottom:12px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:11px;'
                f'color:#9CA3AF;margin-bottom:4px;"><span>0%</span><span>50%</span><span>100%</span></div>'
                f'<div style="height:10px;background:#F3F4F6;border-radius:5px;position:relative;">'
                f'<div style="position:absolute;top:0;left:50%;width:1px;height:100%;background:#D1D5DB;"></div>'
                f'<div style="height:100%;width:{fw}%;background:{sv_};border-radius:5px;opacity:0.85;"></div>'
                f'</div></div>'
                # 1년 중 가격 위치
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'background:#F9FAFB;border-radius:8px;padding:10px 12px;margin-bottom:10px;">'
                f'<span style="font-size:12px;color:#6B7280;">1년 중 가격 위치</span>'
                f'<span style="font-size:14px;font-weight:700;color:{zcolor(zs)};">'
                f'하위 {pct:.0f}%</span></div>'
                # 공포탐욕
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'background:#F9FAFB;border-radius:8px;padding:10px 12px;">'
                f'<span style="font-size:12px;color:#6B7280;">시장 공포·탐욕 지수</span>'
                f'<span style="font-size:14px;font-weight:700;color:{fg_clr};">'
                f'{fg_score} · {fg_label}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # ── Lv.2: 분석 (기존 로직 요약) ─────────────────────────────
        with lv_tab2:
            macro_sign    = "+" if weighted_z * 15 >= 0 else ""
            macro_contrib = f"{macro_sign}{weighted_z * 15:.1f}"
            news_adj      = breakdown.get("news_bonus", 0)
            pos_score     = breakdown.get("position_score", 0)

            mom_score  = breakdown.get("momentum_score", 0.0)
            mom_meta   = breakdown.get("momentum_meta", {})
            mom_offset = breakdown.get("momentum_offset", 0.0)
            mom_clr    = "#059669" if mom_score > 0 else "#DC2626" if mom_score < 0 else "#6B7280"
            mom_vol    = mom_meta.get("vol_label", "")
            mom_high   = mom_meta.get("high_label", "")
            mom_20d    = mom_meta.get("mom_20", 0.0)
            mom_60d    = mom_meta.get("mom_60", 0.0)
            mom_vol_mult = mom_meta.get("vol_multiplier", 1.0)
            mom_pct_from_high = mom_meta.get("pct_from_high", 0.0)
            mom_detail = f"20일 {mom_20d:+.1f}% / 60일 {mom_60d:+.1f}%"
            if mom_vol:    mom_detail += f" · 거래량 {mom_vol}"
            if mom_high:   mom_detail += f" · {mom_high}"

            # 거래량 상세 문구 (Lv.2 모멘텀 행 서브텍스트용)
            _vol_ratio_txt = ""
            if mom_vol_mult >= 1.5:
                _vol_clr = "#059669"
                _vol_ratio_txt = f"최근 5일 거래량: 평균 대비 약 {mom_vol_mult:.1f}배 (폭발 🔥)"
            elif mom_vol_mult >= 1.2:
                _vol_clr = "#059669"
                _vol_ratio_txt = f"최근 5일 거래량: 평균 대비 약 {mom_vol_mult:.1f}배 (증가 ↑)"
            elif mom_vol_mult <= 0.4:
                _vol_clr = "#DC2626"
                _vol_ratio_txt = f"최근 5일 거래량: 평균 대비 약 {mom_vol_mult:.1f}배 (급감 ↓ — 모멘텀 신뢰도 약화)"
            elif mom_vol_mult <= 0.7:
                _vol_clr = "#D97706"
                _vol_ratio_txt = f"최근 5일 거래량: 평균 대비 약 {mom_vol_mult:.1f}배 (감소)"
            else:
                _vol_clr = "#9CA3AF"
                _vol_ratio_txt = f"최근 5일 거래량: 평균 수준 (×{mom_vol_mult:.1f})"

            # 신고가 서브텍스트
            _high_txt = ""
            if mom_high:
                _high_txt = f" · 신고가 대비 {mom_pct_from_high:+.1f}% ({mom_high})"

            lv2_rows = ""
            for lbl, val, c, sub in [
                ("📍 가격 위치 (1년 %ile)", f"{breakdown.get('percentile',50):.0f}%ile → {pos_score:+.1f}점", zcolor(zs), ""),
                ("📡 거시 환경 (동적 가중Z)", f"{weighted_z:+.3f}σ → {macro_contrib}%p", zcolor(weighted_z), ""),
                ("📰 뉴스 감성 (감쇠 적용)", f"{news_adj:+.1f}점", "#059669" if news_adj >= 0 else "#DC2626", ""),
                ("🚀 모멘텀 (추세+거래량+신고가)", f"{mom_score:+.1f}점", mom_clr, f'<div style="font-size:10px;color:{_vol_clr};margin-top:3px;">{_vol_ratio_txt}{_high_txt}</div>'),
                ("📊 섹터 상대 강도", f"{_rel['rel_20']:+.1f}% (20일)", _rel_clr, ""),
            ]:
                lv2_rows += (
                    f'<div style="padding:8px 12px;background:#F9FAFB;border-radius:7px;margin-bottom:6px;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                    f'<span style="font-size:12px;color:#374151;">{lbl}</span>'
                    f'<span style="font-size:13px;font-weight:700;color:{c};">{val}</span></div>'
                    f'{sub}'
                    f'</div>'
                )

            # ── 실적/가이던스 감지 배지 ────────────────────────────────
            eg_signals = breakdown.get("earnings_guidance_signals", [])
            eg_html = ""
            if eg_signals:
                eg_items = ""
                for sig in eg_signals:
                    is_pos = sig["direction"] == "긍정"
                    badge_bg  = "#ECFDF5" if is_pos else "#FEF2F2"
                    badge_bdr = "#A7F3D0" if is_pos else "#FECACA"
                    badge_txt = "#065F46" if is_pos else "#991B1B"
                    contrib_str = f"{sig['contrib']:+.1f}점" if sig['contrib'] != 0 else "반영 중"
                    eg_items += (
                        f'<div style="background:{badge_bg};border:1px solid {badge_bdr};'
                        f'border-radius:7px;padding:8px 12px;margin-bottom:6px;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                        f'<div>'
                        f'<span style="font-size:12px;font-weight:700;color:{badge_txt};">{sig["badge"]}</span>'
                        f'<div style="font-size:10px;color:{badge_txt};opacity:0.8;margin-top:2px;">'
                        f'{sig["note"]}'
                        f'{"  ·  " + sig["elapsed"] if sig.get("elapsed") else ""}'
                        f'</div>'
                        f'<div style="font-size:10px;color:#6B7280;margin-top:3px;word-break:break-all;">'
                        f'{sig["title"]}{"..." if len(sig["title"]) >= 60 else ""}</div>'
                        f'</div>'
                        f'<span style="font-size:12px;font-weight:700;color:{badge_txt};white-space:nowrap;margin-left:8px;">'
                        f'약 {contrib_str}</span>'
                        f'</div>'
                        f'</div>'
                    )
                eg_html = (
                    f'<div style="margin-top:10px;">'
                    f'<div style="font-size:11px;font-weight:600;color:#374151;margin-bottom:6px;">'
                    f'📋 실적 · 가이던스 감지</div>'
                    f'<div style="font-size:10px;color:#9CA3AF;margin-bottom:6px;">'
                    f'점수는 키워드 기반 추정값으로, 방향 참고용입니다.</div>'
                    f'{eg_items}'
                    f'</div>'
                )

            adj_pos_lv2   = breakdown.get("adj_position",    0)
            adj_mom_lv2   = breakdown.get("adj_momentum",    0)
            regime_lv2    = breakdown.get("regime_adj",      0)
            mom_off_lv2   = breakdown.get("momentum_offset", 0)
            raw_final_lv2 = breakdown.get("raw_final",       fw)
            _off_lv2      = f" {mom_off_lv2:+.1f}(오프셋)" if mom_off_lv2 != 0 else ""
            # 스무딩 여부 표시 (raw와 표시값이 다를 때만)
            _smooth_note  = (
                f' <span style="font-size:10px;color:#9CA3AF;">'
                f'(오늘 원본 {raw_final_lv2:.0f}% · 3일 평균으로 표시)</span>'
            ) if abs(raw_final_lv2 - fw) >= 1.0 else ""

            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;'
                f'padding:16px;margin-bottom:10px;">'
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:12px;">'
                f'<span class="lv2">Lv.2</span>'
                f'<span style="font-size:12px;font-weight:600;color:#1A1D23;">분석 근거</span>'
                f'</div>'
                f'<div style="background:#FFF7ED;border-radius:6px;padding:8px 12px;margin-bottom:10px;font-size:11px;color:#92400E;line-height:1.6;">'
                f'📌 <b>Lv.2는 승률을 5가지 근거로 분해</b>해서 보여줍니다.<br>'
                f'① <b>가격 위치</b>: 현재가가 1년 중 어느 위치인지 (낮을수록 저점 매수 유리, ×0.7 적용)<br>'
                f'② <b>거시 환경</b>: 금리·달러·VIX 등 시장 지표들이 이 종목에 유리한지 불리한지<br>'
                f'③ <b>뉴스 감성</b>: 최근 뉴스의 긍정/부정 비율 (오래된 뉴스는 감쇠 적용)<br>'
                f'④ <b>모멘텀</b>: 추세 지속성 + 거래량 + 52주 신고가 근접도 (×1.3 적용)<br>'
                f'⑤ <b>시장 국면</b>: 전체 시장이 Quiet/Trending/Volatile 중 어느 상태인지</div>'
                f'<div style="font-size:12px;color:#6B7280;margin-bottom:12px;">'
                f'승률 <b style="color:{sv_};">{fw:.0f}%</b>{_smooth_note} = '
                f'50(기본) {adj_pos_lv2:+.1f}(가격) {breakdown.get("macro_score", weighted_z*15):+.1f}(거시)'
                f' {news_adj:+.1f}(뉴스) {adj_mom_lv2:+.1f}(모멘텀){_off_lv2} {regime_lv2:+.1f}(국면)</div>'
                f'<div style="font-size:10px;color:#9CA3AF;margin-bottom:8px;">'
                f'모멘텀 상세: {mom_detail}</div>'
                f'{lv2_rows}'
                f'{eg_html}'
                f'</div>',
                unsafe_allow_html=True
            )

        # ── Lv.3: 심화 ───────────────────────────────────────────────
        with lv_tab3:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:12px;">'
                f'<span class="lv3">Lv.3</span>'
                f'<span style="font-size:12px;font-weight:600;color:#1A1D23;">확률 심화 분석</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            with st.spinner("Lv.3 계산 중..."):
                var_95  = calc_var(target, confidence=0.95)
                mc_data = calc_monte_carlo(target, simulations=1000)

            # VaR
            if var_95 is not None:
                var_clr = "#DC2626" if var_95 < -3 else "#D97706" if var_95 < -1.5 else "#059669"
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;'
                    f'padding:14px 16px;margin-bottom:10px;">'
                    f'<div style="font-size:11px;color:#9CA3AF;margin-bottom:4px;">📉 VaR (95% · 1일)</div>'
                    f'<div style="font-size:22px;font-weight:700;color:{var_clr};">{var_95:.2f}%</div>'
                    f'<div style="font-size:11px;color:#6B7280;margin-top:4px;">'
                    f'95% 확률로 하루 최대 <b>{var_95:.2f}%</b> 이상 손실 안 남</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # 몬테카를로 — 기간별 표
            if mc_data and mc_data.get("periods"):
                periods = mc_data["periods"]

                # 기간별 행 먼저 조립
                period_rows = (
                    f'<table style="width:100%;border-collapse:collapse;font-size:11px;">'
                    f'<thead>'
                    f'<tr><td colspan="5" style="padding:0 0 8px;font-size:10px;color:#6B7280;line-height:1.6;">'
                    f'📌 <b>읽는 법</b> — 1,000번 무작위 시뮬레이션 결과:<br>'
                    f'· <b style="color:#DC2626;">최악구간</b>: 하위 5% 시나리오를 제외한 가장 나쁜 결과 (95%는 이보다 낫다)<br>'
                    f'· <b style="color:#D97706;">중간값</b>: 딱 중간에 해당하는 결과 (절반은 이보다 낫고 절반은 나쁘다)<br>'
                    f'· <b style="color:#059669;">최고구간</b>: 상위 5% 시나리오를 제외한 가장 좋은 결과 (95%는 이보다 못하다)<br>'
                    f'· <b>상승확률</b>: 1,000번 중 현재가보다 <b>높게 끝난 횟수 비율</b> (최대손실·수익과 무관)</td></tr>'
                    f'<tr>'
                    f'<th style="padding:6px 8px;text-align:left;color:#9CA3AF;font-weight:600;'
                    f'border-bottom:1px solid #E8EAED;">기간</th>'
                    f'<th style="padding:6px 8px;text-align:center;color:#DC2626;font-weight:600;'
                    f'border-bottom:1px solid #E8EAED;">최악구간</th>'
                    f'<th style="padding:6px 8px;text-align:center;color:#D97706;font-weight:600;'
                    f'border-bottom:1px solid #E8EAED;">중간값</th>'
                    f'<th style="padding:6px 8px;text-align:center;color:#059669;font-weight:600;'
                    f'border-bottom:1px solid #E8EAED;">최고구간</th>'
                    f'<th style="padding:6px 8px;text-align:center;color:#6B7280;font-weight:600;'
                    f'border-bottom:1px solid #E8EAED;">상승확률</th>'
                    f'</tr></thead><tbody>'
                )
                for lbl in ["1달", "6개월", "1년", "5년"]:
                    p    = periods[lbl]
                    up_c = "#059669" if p["prob_up"] >= 50 else "#DC2626"
                    period_rows += (
                        f'<tr style="border-bottom:1px solid #F3F4F6;">'
                        f'<td style="padding:8px;font-weight:600;color:#1A1D23;">{lbl}</td>'
                        f'<td style="padding:8px;text-align:center;color:#DC2626;font-weight:700;">'
                        f'{p["loss_p95"]:+.1f}%</td>'
                        f'<td style="padding:8px;text-align:center;color:#D97706;font-weight:700;">'
                        f'{p["ret_p50"]:+.1f}%</td>'
                        f'<td style="padding:8px;text-align:center;color:#059669;font-weight:700;">'
                        f'{p["gain_p95"]:+.1f}%</td>'
                        f'<td style="padding:8px;text-align:center;color:{up_c};font-weight:700;">'
                        f'{p["prob_up"]:.0f}%</td>'
                        f'</tr>'
                    )
                period_rows += '</tbody></table>'

                # 한 번에 렌더링
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;'
                    f'padding:14px 16px;margin-bottom:10px;">'
                    f'<div style="font-size:11px;color:#9CA3AF;margin-bottom:10px;">'
                    f'🎲 몬테카를로 시뮬레이션 (1,000회 · 현재가 ${mc_data["current"]:.2f})</div>'
                    f'{period_rows}'
                    f'<div style="font-size:10px;color:#B0B7C3;margin-top:8px;">'
                    f'최대손실·최대수익은 95% 신뢰구간 기준 · 과거 변동성 기반 참고치<br>'
                    f'⚠ 과거 1년 변동성 기준 계산 → 장기 역사적 상승 추세는 미반영. 실제보다 보수적으로 나올 수 있음</div>'
                    f'</div>',
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
            f' → 승률 기여 <b style="color:{zcolor(weighted_z)};">{macro_contrib}%p</b>'
            f'<span style="color:#9CA3AF;"> · Z값은 최근 가격이 평균 대비 얼마나 벗어났는지를 나타냄 (0=평균, ±1=보통, ±2=극단)</span>'
            f'</div></div>',
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

            # 직관적 상태 표현
            if eff_z > 1.5:   state = "📈 강하게 밀어올리는 중"
            elif eff_z > 0.3: state = "↗ 약하게 유리한 방향"
            elif eff_z > -0.3:state = "→ 거의 중립"
            elif eff_z > -1.5:state = "↘ 약하게 불리한 방향"
            else:             state = "📉 강하게 눌리는 중"
            state_clr = "#059669" if eff_z > 0.3 else "#DC2626" if eff_z < -0.3 else "#6B7280"

            st.markdown(f"""
<div class="ind-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
        <div>
            <span style="font-size:13px;font-weight:600;color:#1A1D23;">{ind['name']}</span>
            <span style="font-size:10px;color:#9CA3AF;margin-left:5px;">({ind['ticker']})</span>
            <span class="sensitivity-{sens}" style="margin-left:6px;">{SENSITIVITY_LABEL.get(sens,'')}</span>
            <div style="font-size:11px;color:#9CA3AF;margin-top:2px;">{ind['desc']}</div>
        </div>
        <div style="text-align:right;min-width:90px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:15px;
                        font-weight:700;color:{zcolor(ind['z'])};">{ind['z']:+.2f}σ</div>
            <div style="font-size:10px;color:{zcolor(ind['z'])};">{zdesc(ind['z'])}</div>
            <div style="font-size:10px;color:{state_clr};margin-top:2px;font-weight:600;">{state}</div>
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
            f'<div style="font-size:11px;color:#6B7280;margin-top:6px;line-height:1.7;">'
            f'📌 <b>상관 분석이란?</b> 이 종목의 주가가 각 거시 지표와 얼마나 같이 움직이는지를 수치로 나타냅니다.<br>'
            f'예를 들어 나스닥(QQQ)과 상관계수 +0.8이면, 나스닥이 오를 때 이 종목도 같이 오를 가능성이 높다는 뜻입니다.<br>'
            f'<b>범위: -1(완전 역방향) ~ 0(관계없음) ~ +1(완전 동조)</b> · 최근 60거래일(약 3개월) 기준<br>'
            f'<span style="color:#059669;">● 초록</span>: 이론과 일치 — 예상대로 움직이는 중. 크게 신경 안 써도 됩니다.<br>'
            f'<span style="color:#DC2626;">● 빨강</span>: 이론과 반대 — 예상과 다르게 움직이는 중. <b>이때가 주의 신호</b>입니다.<br>'
            f'<span style="color:#9CA3AF;">예: 금리가 오르면 기술주에 악재인데, 실제로는 같이 오르고 있다면 빨강 표시.</span>'
            f'</div></div>',
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

    # ── TAB 4: 뉴스 ──────────────────────────────────────────────────
    with tab4:
        # nb, news_items는 상단 calc_win_rate 호출 시 이미 수집됨 → 재사용
        ko_bonus, ko_news = nb, news_items

        if ko_news:
            pos_c  = sum(1 for n in ko_news if n["sentiment"] == "Positive")
            neg_c  = sum(1 for n in ko_news if n["sentiment"] == "Negative")
            neu_c  = sum(1 for n in ko_news if n["sentiment"] == "Neutral")
            per_c  = sum(1 for n in ko_news if n.get("news_type","short") != "short")
            nb_clr = "#059669" if ko_bonus > 0 else "#DC2626" if ko_bonus < 0 else "#9CA3AF"

            # 감성 요약 바
            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;'
                f'padding:10px 14px;margin-bottom:14px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;">'
                f'<span style="font-size:11px;color:#6B7280;">{len(ko_news)}건</span>'
                f'<span style="color:#059669;font-size:12px;font-weight:600;">▲ {pos_c}</span>'
                f'<span style="color:#DC2626;font-size:12px;font-weight:600;">▼ {neg_c}</span>'
                f'<span style="color:#9CA3AF;font-size:12px;">● {neu_c}</span>'
                f'<span style="background:#EFF6FF;color:#2563EB;border:1px solid #BFDBFE;'
                f'border-radius:4px;padding:1px 6px;font-size:10px;font-weight:600;">'
                f'📌 지속 {per_c}</span>'
                f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
                f'color:{nb_clr};font-weight:700;margin-left:auto;">'
                f'보정 {ko_bonus:+.1f}%</span></div>',
                unsafe_allow_html=True
            )

            # ── 지속성 뉴스 (시간 무관 60% 반영) ────────────────────
            persistent = [n for n in ko_news if n.get("news_type","short") != "short"]
            if persistent:
                st.markdown(
                    '<div style="font-size:12px;font-weight:700;color:#2563EB;'
                    'margin-bottom:8px;padding-bottom:4px;border-bottom:2px solid #2563EB;">'
                    '📌 지속성 뉴스 <span style="font-size:10px;font-weight:400;color:#6B7280;">'
                    '— 시간 경과해도 주가에 계속 영향</span></div>',
                    unsafe_allow_html=True
                )
                for n in persistent:
                    nt   = n.get("news_type","short")
                    css  = "news-pos" if n["sentiment"]=="Positive" else "news-neg" if n["sentiment"]=="Negative" else "news-neu"
                    icon = "▲" if n["sentiment"]=="Positive" else "▼" if n["sentiment"]=="Negative" else "●"
                    tc   = "#059669" if n["sentiment"]=="Positive" else "#DC2626" if n["sentiment"]=="Negative" else "#9CA3AF"
                    pub  = f'<span style="color:#9CA3AF;font-size:10px;">{n.get("pub_date","")}</span>' if n.get("pub_date") else ""
                    # 지속성 타입 배지
                    badge = (
                        '<span style="background:#EFF6FF;color:#2563EB;border:1px solid #BFDBFE;'
                        'border-radius:3px;padding:1px 5px;font-size:9px;font-weight:600;margin-left:4px;">지속반영 60%</span>'
                    )
                    st.markdown(
                        f'<div class="{css}" style="margin-bottom:8px;border-left-width:3px;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
                        f'<span style="font-size:10px;color:{tc};font-weight:700;">{icon} {n["sentiment"].upper()}{badge}</span>'
                        f'{pub}</div>'
                        f'<a href="{n["link"]}" target="_blank" '
                        f'style="font-size:13px;color:#1A1D23;text-decoration:none;font-weight:500;line-height:1.5;">'
                        f'{n["title"]}</a></div>',
                        unsafe_allow_html=True
                    )

            # ── 주요 뉴스 (긍/부정, 단기) ────────────────────────────
            major = [n for n in ko_news
                     if n["sentiment"] in ("Negative","Positive")
                     and n.get("news_type","short") == "short"][:4]
            if major:
                st.markdown(
                    '<div style="font-size:12px;font-weight:700;color:#1A1D23;'
                    'margin:14px 0 8px;padding-bottom:4px;border-bottom:2px solid #1A1D23;">'
                    '⚡ 주요 뉴스</div>', unsafe_allow_html=True
                )
                for n in major:
                    css  = "news-pos" if n["sentiment"]=="Positive" else "news-neg"
                    icon = "▲" if n["sentiment"]=="Positive" else "▼"
                    tc   = "#059669" if n["sentiment"]=="Positive" else "#DC2626"
                    pub  = f'<span style="color:#9CA3AF;font-size:10px;">{n.get("pub_date","")}</span>' if n.get("pub_date") else ""
                    st.markdown(
                        f'<div class="{css}" style="margin-bottom:8px;">'
                        f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                        f'<span style="font-size:10px;color:{tc};font-weight:700;">{icon} {n["sentiment"].upper()}</span>'
                        f'{pub}</div>'
                        f'<a href="{n["link"]}" target="_blank" '
                        f'style="font-size:13px;color:#1A1D23;text-decoration:none;font-weight:500;line-height:1.5;">'
                        f'{n["title"]}</a></div>',
                        unsafe_allow_html=True
                    )

            # ── 최근 뉴스 (전체) ─────────────────────────────────────
            st.markdown(
                '<div style="font-size:12px;font-weight:700;color:#1A1D23;'
                'margin:14px 0 8px;padding-bottom:4px;border-bottom:2px solid #E8EAED;">'
                '🕐 최근 뉴스</div>', unsafe_allow_html=True
            )
            for n in ko_news:
                css  = "news-pos" if n["sentiment"]=="Positive" else "news-neg" if n["sentiment"]=="Negative" else "news-neu"
                icon = "▲" if n["sentiment"]=="Positive" else "▼" if n["sentiment"]=="Negative" else "●"
                tc   = "#059669" if n["sentiment"]=="Positive" else "#DC2626" if n["sentiment"]=="Negative" else "#9CA3AF"
                pub  = f'<span style="color:#9CA3AF;font-size:10px;">{n.get("pub_date","")}</span>' if n.get("pub_date") else ""
                pin  = ('📌 ' if n.get("news_type","short") != "short" else "")
                st.markdown(
                    f'<div class="{css}" style="margin-bottom:7px;">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                    f'<span style="font-size:10px;color:{tc};font-weight:600;">{icon} {n["sentiment"].upper()}</span>'
                    f'{pub}</div>'
                    f'<a href="{n["link"]}" target="_blank" '
                    f'style="font-size:13px;color:#1A1D23;text-decoration:none;font-weight:500;line-height:1.5;">'
                    f'{pin}{n["title"]}</a></div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;'
                'padding:24px;text-align:center;">'
                '<div style="font-size:24px;margin-bottom:8px;">📰</div>'
                '<div style="font-size:13px;color:#D97706;font-weight:600;">뉴스를 불러올 수 없습니다</div>'
                '<div style="font-size:12px;color:#9CA3AF;margin-top:4px;">잠시 후 다시 시도해주세요</div></div>',
                unsafe_allow_html=True
            )

    # ── TAB 5: 백테스트 ───────────────────────────────────────────────
    with tab5:
        st.markdown(
            '<div style="background:#F8FAFF;border:1px solid #DBEAFE;border-radius:8px;'
            'padding:14px 16px;margin-bottom:14px;font-size:12px;color:#374151;line-height:1.8;">'
            '<b style="font-size:13px;color:#1A1D23;">🧪 백테스트란?</b><br>'
            '이 앱의 승률 신호가 과거에 실제로 얼마나 맞았는지 검증하는 기능입니다.<br>'
            '과거 2년치 데이터를 20 거래일(약 1개월) 간격으로 나눠, 각 시점에서 신호를 계산하고 '
            '그로부터 <b>20 거래일 후의 실제 수익률</b>을 확인합니다.<br>'
            '<span style="color:#059669;">● 매수 신호</span>: 승률 60% 이상일 때 &nbsp;'
            '<span style="color:#DC2626;">● 리스크 신호</span>: 승률 45% 미만일 때<br>'
            '<b>적중률</b>: 매수 신호 후 실제로 올랐던 비율 / 리스크 신호 후 실제로 내렸던 비율<br>'
            '<b>샤프지수</b>: 수익률 대비 변동성 — 0.5 이상이면 신호 품질이 검증된 수준<br>'
            '<span style="color:#9CA3AF;font-size:11px;">⚠ 과거 결과가 미래를 보장하지 않습니다. 참고 지표로만 활용하세요.</span>'
            '</div>',
            unsafe_allow_html=True
        )

        with st.spinner("백테스트 계산 중... (첫 실행 시 30초 내외)"):
            bt = run_backtest(target, cfg["indicators"])

        if bt is None:
            st.info("데이터가 부족하여 백테스트를 실행할 수 없습니다.")
        else:
            # ── 기간별 탭: 1개월 / 3개월 ─────────────────────────────
            shp_clr = "#059669" if bt["sharpe"] >= 0.5 else "#D97706" if bt["sharpe"] >= 0 else "#DC2626"

            st.markdown(
                f'<div style="font-size:11px;color:#9CA3AF;text-align:center;margin:0 0 12px;">' +
                f'과거 2년 · 총 {bt["total"]}번 신호 발생 ' +
                f'(매수 {bt["buy_count"]}회 · 리스크 {bt["risk_count"]}회)</div>',
                unsafe_allow_html=True
            )

            _bt_tab1, _bt_tab2 = st.tabs(["📅 1개월 후 검증", "📆 3개월 후 검증"])

            def _draw_bt_kpis(buy_acc, risk_acc, avg_buy, avg_risk, period_lbl, sharpe_val=None):
                bc = "#059669" if buy_acc  >= 55 else "#D97706" if buy_acc  >= 45 else "#DC2626"
                rc = "#059669" if risk_acc >= 55 else "#D97706" if risk_acc >= 45 else "#DC2626"
                ac = "#059669" if avg_buy  >= 0 else "#DC2626"
                items = [
                    ("매수 신호 적중률",   f"신호 후 {period_lbl} 실제 상승", f"{buy_acc}%",       bc),
                    ("리스크 신호 적중률", f"신호 후 {period_lbl} 실제 하락", f"{risk_acc}%",      rc),
                    ("매수 평균 수익",     f"{period_lbl} 평균 수익률",       f"{avg_buy:+.1f}%",  ac),
                ]
                if sharpe_val is not None:
                    items.append(("샤프지수(근사)", "0.5↑ 우수 · 0↑ 보통", f"{sharpe_val}", shp_clr))
                _kc = st.columns(len(items))
                for _col, (_lbl, _sub, _val, _clr) in zip(_kc, items):
                    _col.markdown(
                        f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;'
                        f'padding:10px;text-align:center;">'
                        f'<div style="font-size:9px;color:#9CA3AF;margin-bottom:2px;">{_lbl}</div>'
                        f'<div style="font-size:9px;color:#B0B7C3;margin-bottom:4px;">{_sub}</div>'
                        f'<div style="font-family:JetBrains Mono,monospace;font-size:17px;'
                        f'font-weight:700;color:{_clr};">{_val}</div></div>',
                        unsafe_allow_html=True
                    )

            with _bt_tab1:
                _draw_bt_kpis(
                    bt["buy_acc"], bt["risk_acc"],
                    bt["avg_ret_buy"], bt["avg_ret_risk"],
                    "1개월", bt["sharpe"]
                )

            with _bt_tab2:
                _acc_3m_buy  = bt.get("buy_acc_3m",  0.0)
                _acc_3m_risk = bt.get("risk_acc_3m", 0.0)
                _avg_3m_buy  = bt.get("avg_buy_3m",  0.0)
                _avg_3m_risk = bt.get("avg_risk_3m", 0.0)
                _draw_bt_kpis(
                    _acc_3m_buy, _acc_3m_risk,
                    _avg_3m_buy, _avg_3m_risk,
                    "3개월"
                )
                st.markdown(
                    '<div style="font-size:10px;color:#9CA3AF;margin-top:6px;">' +
                    '1개월 신호 기준 3개월 후 수익률 — 신호가 중기에도 유효한지 확인</div>',
                    unsafe_allow_html=True
                )


            # ── 신호별 수익률 바 차트 ─────────────────────────────────
            if bt["buy_count"] > 0 or bt["risk_count"] > 0:
                bar_labels = []
                bar_vals   = []
                bar_colors = []
                if bt["buy_count"] > 0:
                    bar_labels.append(f"매수 신호\n(n={bt['buy_count']})")
                    bar_vals.append(bt["avg_ret_buy"])
                    bar_colors.append("#059669" if bt["avg_ret_buy"] >= 0 else "#DC2626")
                if bt["risk_count"] > 0:
                    bar_labels.append(f"리스크 신호\n(n={bt['risk_count']})")
                    bar_vals.append(bt["avg_ret_risk"])
                    bar_colors.append("#059669" if bt["avg_ret_risk"] >= 0 else "#DC2626")

                fig_bt = go.Figure(go.Bar(
                    x=bar_labels, y=bar_vals,
                    marker_color=bar_colors, opacity=0.85,
                    text=[f"{v:+.2f}%" for v in bar_vals],
                    textposition="outside",
                    textfont=dict(family="JetBrains Mono", size=12),
                ))
                fig_bt.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#374151")),
                    yaxis=dict(showgrid=True, gridcolor="#F3F4F6",
                               ticksuffix="%", tickfont=dict(size=10)),
                    margin=dict(t=30, b=10, l=0, r=0), height=180,
                    showlegend=False,
                )
                st.plotly_chart(fig_bt, use_container_width=True)

            # ── 최근 5개 샘플 (간소) ──────────────────────────────────
            if bt["samples"]:
                st.markdown(
                    '<div style="font-size:11px;font-weight:600;color:#6B7280;'
                    'letter-spacing:0.5px;text-transform:uppercase;margin-bottom:8px;">'
                    '최근 신호 샘플</div>',
                    unsafe_allow_html=True
                )
                for s in bt["samples"]:
                    s_clr  = "#059669" if s["signal"] == "매수" else "#DC2626"
                    r_clr  = "#059669" if s["ret"] >= 0 else "#DC2626"
                    r_icon = "▲" if s["ret"] >= 0 else "▼"
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'padding:8px 12px;background:#FFFFFF;border:1px solid #E8EAED;'
                        f'border-radius:7px;margin-bottom:5px;">'
                        f'<span style="font-size:11px;color:#9CA3AF;">{s["date"]}</span>'
                        f'<span style="font-size:11px;font-weight:700;color:{s_clr};">'
                        f'{s["signal"]} {s["score"]:.0f}%</span>'
                        f'<span style="font-size:11px;color:#9CA3AF;">{s["pct"]:.0f}%ile</span>'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:12px;'
                        f'font-weight:700;color:{r_clr};">{r_icon}{abs(s["ret"]):.1f}%</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # ── 해석 안내 ─────────────────────────────────────────────
            st.markdown(
                '<div style="background:#F9FAFB;border:1px solid #E8EAED;border-radius:8px;'
                'padding:12px 14px;margin-top:10px;font-size:11px;color:#374151;line-height:1.8;">'
                '<b>❓ 승률 vs 적중률 — 뭐가 다른가요?</b><br>'
                '· <b>현재 승률</b> = 지금 이 순간의 환경 점수. 예보와 같음.<br>'
                '· <b>매수 신호 적중률</b> = 과거에 승률이 60% 이상 나왔을 때, '
                '실제로 1개월 뒤 주가가 오른 비율. 이 앱의 성적표.<br>'
                '예: 현재 승률 35% → 지금은 불리한 환경. '
                '적중률 40% → 과거 매수 신호의 신뢰도는 40%였다는 뜻.<br>'
                '<span style="color:#9CA3AF;">⚠ 과거 적중률이 미래 수익을 보장하지 않습니다. 참고 지표로만 활용하세요.</span>'
                '</div>',
                unsafe_allow_html=True
            )

            # ── 캘리브레이션 검증 ────────────────────────────────────
            st.markdown(
                '<div style="font-size:12px;font-weight:700;color:#1A1D23;'
                'margin:16px 0 8px;padding-bottom:4px;border-bottom:2px solid #E8EAED;">'
                '📐 승률 신뢰도 검증</div>',
                unsafe_allow_html=True
            )
            # 백테스트 결과로 구간별 캘리브레이션
            if bt:
                calib_rows = ""
                for sig_label, acc, avg_ret, count in [
                    ("매수 신호 (60%↑)", bt["buy_acc"],  bt["avg_ret_buy"],  bt["buy_count"]),
                    ("리스크 신호 (45%↓)", bt["risk_acc"], bt["avg_ret_risk"], bt["risk_count"]),
                ]:
                    if count == 0:
                        continue
                    acc_clr  = "#059669" if acc >= 60 else "#D97706" if acc >= 45 else "#DC2626"
                    ret_clr  = "#059669" if avg_ret >= 0 else "#DC2626"
                    # 신뢰도 판정
                    if acc >= 60:   trust = "✅ 신뢰 가능"
                    elif acc >= 50: trust = "🟡 보통"
                    else:           trust = "❌ 신뢰도 낮음"

                    calib_rows += (
                        f'<div style="background:#FFFFFF;border:1px solid #E8EAED;'
                        f'border-radius:8px;padding:10px 14px;margin-bottom:8px;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                        f'<div>'
                        f'<div style="font-size:12px;font-weight:600;color:#1A1D23;">{sig_label}</div>'
                        f'<div style="font-size:11px;color:#6B7280;margin-top:2px;">'
                        f'총 {count}회 신호 · 평균수익 '
                        f'<span style="color:{ret_clr};font-weight:600;">{avg_ret:+.1f}%</span></div>'
                        f'</div>'
                        f'<div style="text-align:right;">'
                        f'<div style="font-size:18px;font-weight:700;color:{acc_clr};">{acc:.0f}%</div>'
                        f'<div style="font-size:10px;color:{acc_clr};">{trust}</div>'
                        f'</div></div>'
                        f'</div>'
                    )
                if calib_rows:
                    st.markdown(calib_rows, unsafe_allow_html=True)
                st.markdown(
                    '<div style="font-size:10px;color:#B0B7C3;margin-top:4px;">'
                    '적중률이 60% 이상이면 이 종목에서 신호가 통계적으로 유효합니다.</div>',
                    unsafe_allow_html=True
                )

        # ── 수치 검증 리포트 ─────────────────────────────────────────
        st.markdown(
            '<div style="font-size:12px;font-weight:700;color:#1A1D23;'
            'margin:20px 0 8px;padding-bottom:4px;border-bottom:2px solid #1A1D23;">'
            '🔬 승률 수치 검증 리포트</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="font-size:11px;color:#6B7280;margin-bottom:10px;">'
            '현재 승률이 어떤 항목에서 얼마나 나왔는지 실시간으로 검증합니다.</div>',
            unsafe_allow_html=True
        )

        # 항목별 기여도 분해 — 실제 calc_win_rate adj값 사용
        adj_pos   = breakdown.get("adj_position",    0)   # position_score * 0.7
        mac_s     = breakdown.get("macro_score",     0)
        news_s    = breakdown.get("news_bonus",      0)
        mom_s     = breakdown.get("adj_momentum",    0)   # momentum_score * 1.3
        regime_s  = breakdown.get("regime_adj",      0)
        mom_off   = breakdown.get("momentum_offset", 0)
        pct_v     = breakdown.get("percentile",      50)
        mac_z     = breakdown.get("macro_z",         0)
        total_raw = breakdown.get("total_raw",       50)

        # 각 항목 신뢰도 판단
        def score_badge(score, item):
            if item == "position":
                if abs(score) > 10: return "강한 신호", "#059669" if score > 0 else "#DC2626"
                elif abs(score) > 5: return "보통 신호", "#D97706"
                else: return "약한 신호", "#9CA3AF"
            elif item == "macro":
                if abs(score) > 12: return "강한 신호", "#059669" if score > 0 else "#DC2626"
                elif abs(score) > 6: return "보통 신호", "#D97706"
                else: return "약한 신호", "#9CA3AF"
            else:
                if abs(score) > 5: return "강한 신호", "#059669" if score > 0 else "#DC2626"
                elif abs(score) > 2: return "보통 신호", "#D97706"
                else: return "약한 신호", "#9CA3AF"

        p_badge,  p_clr  = score_badge(adj_pos, "position")
        m_badge,  m_clr  = score_badge(mac_s,   "macro")
        n_badge,  n_clr  = score_badge(news_s,  "news")
        mo_badge, mo_clr = score_badge(mom_s,   "news")

        verify_rows = ""
        for lbl, score, badge, clr, desc in [
            ("📍 가격위치", adj_pos,  p_badge,  p_clr,
             f"1년 중 {pct_v:.0f}%ile — {'저점권 (유리)' if pct_v < 30 else '고점권 (불리)' if pct_v > 70 else '중간권'} (×0.7 조정)"),
            ("📡 거시환경", mac_s,    m_badge,  m_clr,
             f"가중Z {mac_z:+.3f}σ → {'호재 우세' if mac_z > 0.2 else '악재 우세' if mac_z < -0.2 else '중립'}"),
            ("📰 뉴스보정", news_s,   n_badge,  n_clr,
             f"감쇠 적용 후 {news_s:+.1f}점 — {'긍정 우세' if news_s > 0 else '부정 우세' if news_s < 0 else '중립'}"),
            ("🚀 모멘텀",  mom_s,    mo_badge, mo_clr,
             f"추세+거래량+신고가 (×1.3 조정){f' · 오프셋 {mom_off:+.1f}' if mom_off != 0 else ''}"),
            ("🌐 시장국면", regime_s, "참고",   "#6B7280",
             "시장 레짐 보정 (Quiet/Trending/Volatile)"),
        ]:
            bar_w = min(100, abs(score) / 20 * 100)
            bar_clr = "#059669" if score >= 0 else "#DC2626"
            verify_rows += (
                f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;'
                f'padding:10px 14px;margin-bottom:8px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
                f'<span style="font-size:12px;font-weight:600;color:#1A1D23;">{lbl}</span>'
                f'<div style="display:flex;align-items:center;gap:8px;">'
                f'<span style="font-size:10px;color:{clr};font-weight:600;">{badge}</span>'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:14px;font-weight:700;color:{bar_clr};">'
                f'{score:+.1f}점</span></div></div>'
                f'<div style="height:4px;background:#F3F4F6;border-radius:2px;margin-bottom:5px;">'
                f'<div style="height:100%;width:{bar_w}%;background:{bar_clr};border-radius:2px;"></div></div>'
                f'<div style="font-size:11px;color:#6B7280;">{desc}</div>'
                f'</div>'
            )

        # 최종 합산 검증
        clamp_yn  = "⚠ clamp 적용됨" if total_raw != fw else "✓ 정상 범위"
        clamp_clr = "#D97706" if total_raw != fw else "#059669"
        _off_txt  = f" {mom_off:+.1f}(오프셋)" if mom_off != 0 else ""

        st.markdown(
            verify_rows +
            f'<div style="background:#F9FAFB;border:1px solid #E8EAED;border-radius:8px;'
            f'padding:10px 14px;">'
            f'<div style="font-size:11px;color:#6B7280;margin-bottom:4px;">합산 검증</div>'
            f'<div style="font-size:12px;color:#374151;">'
            f'50(기본) {adj_pos:+.1f}(가격) {mac_s:+.1f}(거시) {news_s:+.1f}(뉴스)'
            f' {mom_s:+.1f}(모멘텀){_off_txt} {regime_s:+.1f}(국면)'
            f' = <b style="color:#1A1D23;">{total_raw:.1f}점</b> → '
            f'<b style="color:{sv_};">{fw:.1f}%</b> '
            f'<span style="font-size:10px;color:{clamp_clr};">{clamp_yn}</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

