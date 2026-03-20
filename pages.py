# pages.py
import streamlit as st
import plotly.graph_objects as go
from config import *
from engine import *

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
    .news-pos{background:#ECFDF5;border-left:3px solid #059669;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
    .news-neg{background:#FEF2F2;border-left:3px solid #DC2626;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
    .news-neu{background:#F9FAFB;border-left:3px solid #D1D5DB;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
    </style>
    """, unsafe_allow_html=True)

def render_main_page():
    st.markdown('<div style="margin-bottom:20px;"><h2 style="font-size:22px;font-weight:700;color:#1A1D23;margin:0;">📊 포트폴리오 현황</h2></div>', unsafe_allow_html=True)

    # 주요 거시 지표
    st.markdown('<div class="section-hdr">📡 주요 거시 지표</div>', unsafe_allow_html=True)
    macro_list = [("S&P 500","^GSPC","시장 전체"),("나스닥 100","^NDX","기술·성장주"),
                  ("10년물 금리","^TNX","금리 환경"),("VIX 공포","^VIX","시장 불안"),("WTI 유가","CL=F","에너지·인플레")]
    mc = st.columns(5)
    for col,(label,sym,desc) in zip(mc, macro_list):
        z,price = get_z_and_price(sym)
        arrow = "▲" if z>0.2 else "▼" if z<-0.2 else "—"
        ac = "#059669" if z>0.2 else "#DC2626" if z<-0.2 else "#6B7280"
        col.markdown(f'<div class="macro-card"><div style="font-size:10px;font-weight:600;color:#6B7280;margin-bottom:4px;">{label}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:19px;font-weight:700;color:{zcolor(z)};">{price:,.2f} <span style="font-size:13px;color:{ac};">{arrow}</span></div><div style="font-size:10px;color:#9CA3AF;margin-top:2px;">Z {z:+.2f}σ · {desc}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.portfolio:
        st.markdown('<div style="background:#FFFFFF;border:2px dashed #D1D5DB;border-radius:12px;padding:48px;text-align:center;"><div style="font-size:36px;margin-bottom:10px;">📭</div><div style="font-size:16px;font-weight:600;color:#374151;margin-bottom:6px;">아직 종목이 없습니다</div><div style="font-size:13px;color:#9CA3AF;">왼쪽 사이드바에서 <b>➕ 종목 추가</b>를 눌러주세요.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="section-hdr">📈 보유 종목 분석 <span class="lv1" style="margin-left:6px;">Lv.1</span></div>', unsafe_allow_html=True)
        chunk = 4
        for rs in range(0, len(st.session_state.portfolio), chunk):
            row = st.session_state.portfolio[rs:rs+chunk]
            cols = st.columns(len(row))
            for col, stock in zip(cols, row):
                with col:
                    with st.spinner(""):
                        zs, price = get_z_and_price(stock['ticker'])
                        _, cfg, inds = get_sector_analysis(stock['ticker'])
                        nb, _ = get_news(stock['ticker'])
                        win, explain_text = calc_win_rate(zs, inds, nb)
                    st_,sc_,sv_ = get_signal(win)
                    
                    if stock.get('avg_price', 0) > 0:
                        pnl = ((price-stock['avg_price'])/stock['avg_price']*100)
                        pnl_text = f"{'+'if pnl>=0 else ''}{pnl:.1f}%"
                        pc = "#059669" if pnl>=0 else "#DC2626"
                    else:
                        pnl_text = "미입력"; pc = "#9CA3AF"
                        
                    ti = max(inds, key=lambda x: abs(x["z"]*x["weight"]))
                    tc2 = ti["z"]*ti["weight"]*0.5
                    tclr = "#059669" if tc2>0 else "#DC2626"
                    
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
        <span style="font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:700;color:{sv_};line-height:1;">{win}%</span>
        <span style="font-size:10px;color:#9CA3AF;">승률 <span title="{explain_text}" style="cursor:help;font-size:12px;background:#F3F4F6;padding:2px 4px;border-radius:10px;">❔</span></span>
    </div>
    <div style="font-size:10px;color:{tclr};margin-bottom:8px;">{'▲' if tc2>0 else '▼'} {ti['name']} Z{ti['z']:+.1f}</div>
    <div style="display:flex;justify-content:space-between;font-size:11px;padding-top:8px;border-top:1px solid #F3F4F6;">
        <span style="color:#6B7280;">${price:.1f}</span>
        <span style="color:{pc};font-weight:500;">{pnl_text}</span>
        <span style="color:#9CA3AF;">{stock['weight']}%</span>
    </div>
</div>""", unsafe_allow_html=True)
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                    if st.button("상세 분석 →", key=f"go_{stock['ticker']}_{rs}"):
                        st.session_state.selected = stock['ticker']
                        st.session_state.page = 'detail'; st.rerun()

        # 배분 차트
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">📊 포트폴리오 구성</div>', unsafe_allow_html=True)
        cc, bc = st.columns([1,2])
        with cc:
            labels  = [s['ticker'] for s in st.session_state.portfolio]
            weights = [s['weight'] for s in st.session_state.portfolio]
            colors  = [SECTOR_CONFIG[detect_sector(s['ticker'])]["color"] for s in st.session_state.portfolio]
            fig = go.Figure(go.Pie(values=weights,labels=labels,hole=0.6, marker=dict(colors=colors,line=dict(color="#FFFFFF",width=2))))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",showlegend=False, margin=dict(t=10,b=10,l=10,r=10),height=200, annotations=[dict(text=f"<b>{sum(weights)}%</b>",x=0.5,y=0.5,showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)
        with bc:
            for s in st.session_state.portfolio:
                sc = SECTOR_CONFIG[detect_sector(s['ticker'])]
                st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="font-size:13px;font-weight:600;color:#1A1D23;">{s["ticker"]} <span style="font-size:11px;color:{sc["color"]};">{sc["icon"]} {sc["label"]}</span></span><span style="font-size:13px;font-weight:600;color:#2563EB;">{s["weight"]}%</span></div><div style="height:4px;background:#F3F4F6;border-radius:2px;"><div style="height:100%;width:{min(s["weight"],100)}%;background:{sc["color"]};border-radius:2px;opacity:0.8;"></div></div></div>', unsafe_allow_html=True)

def render_detail_page():
    target = st.session_state.selected or ''
    if not target: st.session_state.page = 'main'; st.rerun()
    if st.sidebar.button("← 대시보드로", use_container_width=True): st.session_state.page = 'main'; st.rerun()

    si = next((s for s in st.session_state.portfolio if s['ticker']==target), {"name":target,"weight":"—","avg_price":0,"shares":0})

    with st.spinner(f"{target} 분석 중..."):
        zs, price = get_z_and_price(target)
        sk, cfg, inds = get_sector_analysis(target)
        nb, nd = get_news(target)
        fw, explain_text = calc_win_rate(zs, inds, nb)
        history = get_price_history(target)

    st_, sc_, sv_ = get_signal(fw)
    pnl = ((price-si['avg_price'])/si['avg_price']*100) if price and si['avg_price'] > 0 else 0
    pc = "#059669" if pnl>=0 else "#DC2626"

    # 헤더
    hl,hr = st.columns([3,1])
    with hl:
        st.markdown(f'<div style="margin-bottom:16px;"><div style="font-size:11px;color:#6B7280;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{cfg["icon"]} {cfg["label"]} 섹터</div><div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;"><h1 style="font-size:26px;font-weight:700;color:#1A1D23;margin:0;">{target}</h1><div class="{sc_}">{st_}</div></div><div style="font-size:12px;color:#6B7280;">{si["name"]} · 비중 {si["weight"]}% · 평균 ${si["avg_price"]:.2f}</div></div>', unsafe_allow_html=True)
    with hr:
        st.markdown(f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:10px;padding:18px;text-align:center;border-top:3px solid {sv_};"><div style="font-size:10px;color:#9CA3AF;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">오늘의 승률</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:42px;font-weight:700;color:{sv_};line-height:1;">{fw}%</div><div style="font-size:11px;color:#9CA3AF;margin-top:4px;" title="{explain_text}">계산 근거 확인 ❔</div></div>', unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["🌡️ 종합 기상도", f"{cfg['icon']} 섹터 지표", "📰 뉴스 분석"])
    
    with tab1:
        gl,gr = st.columns([1,2])
        with gl:
            gauge = go.Figure(go.Indicator(mode="gauge+number",value=fw, number={"suffix":"%","font":{"family":"JetBrains Mono","size":28,"color":sv_}}, gauge={"axis":{"range":[0,100]}, "bar":{"color":sv_}, "steps":[{"range":[0,45],"color":"rgba(220,38,38,0.05)"},{"range":[45,60],"color":"rgba(217,119,6,0.05)"},{"range":[60,100],"color":"rgba(5,150,105,0.05)"}]}))
            gauge.update_layout(height=200, margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(gauge, use_container_width=True)
        with gr:
            if not history.empty:
                fh = go.Figure(go.Scatter(x=history['Date'],y=history['Close'],mode='lines', line=dict(color=sv_,width=2),fill='tozeroy'))
                fh.update_layout(height=240, margin=dict(t=10,b=10,l=0,r=0))
                st.plotly_chart(fh, use_container_width=True)

    with tab2:
        for ind in inds:
            contrib = ind["z"]*(ind["weight"]/5.0)
            st.markdown(f'<div style="background:#FFFFFF;border:1px solid #E8EAED;border-radius:8px;padding:14px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;"><b>{ind["name"]}</b> <span>{ind["z"]:+.2f}σ</span></div><div style="font-size:11px;color:#9CA3AF;">{ind["desc"]}</div><div style="font-size:11px;color:{"#059669" if contrib>0 else "#DC2626"};margin-top:4px;">승률 기여 {contrib:+.1f}%p</div></div>', unsafe_allow_html=True)

    with tab3:
        if nd:
            for n in nd:
                css="news-pos" if n['sentiment']=="Positive" else "news-neg" if n['sentiment']=="Negative" else "news-neu"
                st.markdown(f'<div class="{css}"><a href="{n["link"]}" target="_blank" style="font-size:12px;color:#374151;text-decoration:none;">{n["title"]}</a></div>', unsafe_allow_html=True)
        else: st.info("데이터가 없습니다.")
