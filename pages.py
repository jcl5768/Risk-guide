import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from engine import (
    get_z_and_price, get_historical_data, detect_sector, 
    SECTOR_CONFIG, ETF_MAP, TICKER_NAME_MAP
)

def apply_custom_style():
    """앱 전체에 적용할 커스텀 CSS"""
    st.markdown("""
        <style>
        /* 기본 폰트 및 배경 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* 메인 배경색 */
        .stApp {
            background-color: #FFFFFF;
        }

        /* 카드 스타일 */
        .metric-card {
            background-color: #F8FAFC;
            border: 1px solid #F1F5F9;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s ease;
        }
        .metric-card:hover {
            border-color: #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* 버튼 스타일 커스텀 */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
        
        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: transparent !important;
            border: none !important;
            font-weight: 600;
            color: #64748B;
        }
        .stTabs [aria-selected="true"] {
            color: #2563EB !important;
            border-bottom: 2px solid #2563EB !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_main_page():
    """포트폴리오 대시보드 메인 페이지"""
    st.title("📈 리스크 가이드")
    st.markdown("현재 내 자산의 위치와 위험도를 한눈에 확인하세요.")
    
    if not st.session_state.portfolio:
        render_empty_state()
        return

    # 데이터 전처리
    df = pd.DataFrame(st.session_state.portfolio)
    
    # 상단 요약 지표 (Metrics)
    render_summary_metrics(df)

    st.markdown("---")

    # 메인 레이아웃 (좌: 차트, 우: 상세 리스트)
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("섹터별 비중")
        render_sector_pie_chart(df)
        
    with col2:
        st.subheader("종목별 상세 현황")
        render_stock_table(df)

    st.markdown("---")
    
    # 하단: 과매수/과매도 리스크 분석
    st.subheader("🔍 실시간 리스크 분석 (Z-Score)")
    render_risk_analysis(df)

def render_empty_state():
    """종목이 없을 때 표시되는 화면"""
    st.info("왼쪽 사이드바에서 종목을 추가하여 분석을 시작해 보세요!")
    
    # 샘플 가이드 이미지나 설명을 넣을 수 있음
    st.image("https://images.unsplash.com/photo-1611974714024-4607a50d6c2a?q=80&w=2070&auto=format&fit=crop", 
             caption="데이터를 통해 스마트한 투자 결정을 내리세요.")

def render_summary_metrics(df):
    """상단 요약 수치 카드"""
    cols = st.columns(4)
    
    total_value = 0
    total_pnl = 0
    weights_sum = df['weight'].sum()
    
    for _, row in df.iterrows():
        _, price = get_z_and_price(row['ticker'])
        val = price * row.get('shares', 0)
        cost = row['avg_price'] * row.get('shares', 0)
        total_value += val
        total_pnl += (val - cost)

    pnl_pct = (total_pnl / (total_value - total_pnl) * 100) if (total_value - total_pnl) > 0 else 0

    with cols[0]:
        st.metric("총 평가금액", f"${total_value:,.0f}")
    with cols[1]:
        st.metric("총 수익금", f"${total_pnl:,.0f}", f"{pnl_pct:.1f}%")
    with cols[2]:
        st.metric("설정 비중 합계", f"{weights_sum:.1f}%", delta=None, delta_color="normal")
    with cols[3]:
        st.metric("보유 종목 수", f"{len(df)}개")

def render_sector_pie_chart(df):
    """섹터 비중 파이 차트"""
    # 각 티커별 섹터 감지 및 비중 합산
    df['sector'] = df['ticker'].apply(detect_sector)
    sector_grouped = df.groupby('sector')['weight'].sum().reset_index()
    
    # 색상 매핑
    colors = [SECTOR_CONFIG[s]['color'] for s in sector_grouped['sector']]
    labels = [f"{SECTOR_CONFIG[s]['icon']} {SECTOR_CONFIG[s]['label']}" for s in sector_grouped['sector']]

    fig = px.pie(
        sector_grouped, 
        values='weight', 
        names=labels,
        hole=0.4,
        color_discrete_sequence=colors
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

def render_stock_table(df):
    """종목별 현황 테이블"""
    display_data = []
    for _, row in df.iterrows():
        _, price = get_z_and_price(row['ticker'])
        display_data.append({
            "티커": row['ticker'],
            "비중": f"{row['weight']}%",
            "현재가": f"${price:,.2f}",
            "수익률": f"{((price - row['avg_price'])/row['avg_price']*100):.1f}%" if row['avg_price'] > 0 else "0%"
        })
    
    st.dataframe(
        pd.DataFrame(display_data),
        hide_index=True,
        use_container_width=True
    )

def render_risk_analysis(df):
    """Z-Score 기반 리스크 분석 시각화"""
    risk_data = []
    for _, row in df.iterrows():
        z, price = get_z_and_price(row['ticker'])
        risk_data.append({
            "ticker": row['ticker'],
            "z_score": z,
            "price": price
        })
    
    rdf = pd.DataFrame(risk_data)
    
    # Z-Score 바 차트
    fig = px.bar(
        rdf, x='ticker', y='z_score',
        color='z_score',
        color_continuous_scale='RdYlGn_r', # 과매수(빨강) -> 과매도(초록)
        range_color
