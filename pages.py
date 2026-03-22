import streamlit as st
import plotly.graph_objects as go
from engine import get_z_and_price, get_chart_data, get_sector_analysis, calc_win_rate, get_news, get_signal

def apply_custom_style():
    st.markdown("""
    <style>
    /* 지표 카드를 아주 작게 강제 조정 */
    .macro-card {
        background: white !important;
        padding: 5px 10px !important;
        border: 1px solid #EEE !important;
        border-radius: 5px !important;
        margin-bottom: 5px !important;
    }
    .macro-card h5 { font-size: 14px !important; margin: 0 !important; }
    .macro-card p { font-size: 10px !important; margin: 0 !important; color: #666 !important; }
    
    /* 버튼 크기 축소 */
    div[data-testid="stButton"] button {
        padding: 2px 5px !important;
        font-size: 11px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_main_page():
    st.title("메인 대시보드")
    # 상단 지표 4개 작게 표시
    cols = st.columns(4)
    items = [("S&P500", "^GSPC"), ("나스닥", "^IXIC"), ("금리", "^TNX"), ("VIX", "^VIX")]
    for col, (lab, tic) in zip(cols, items):
        z, p = get_z_and_price(tic)
        col.markdown(f"""
            <div class="macro-card">
                <p>{lab}</p>
                <h5>{p:,.1f} ({z:+.1f}σ)</h5>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    # (나머지 대시보드 내용...)

def render_detail_page():
    target = st.session_state.selected
    if st.button("← 뒤로가기"):
        st.session_state.page = "main"
        st.rerun()
    
    st.header(f"{target} 상세 분석")
    
    # 1. 차트 먼저 표시
    df = get_chart_data(target, st.session_state.chart_period)
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#2563EB'))])
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. 차트 바로 아래에 기간 버튼 배치 (작게)
    p_cols = st.columns([1,1,1,1,5])
    for i, label in enumerate(["1일", "1주", "1달", "1년"]):
        with p_cols[i]:
            if st.button(label, key=f"btn_{label}"):
                st.session_state.chart_period = label
                st.rerun()
