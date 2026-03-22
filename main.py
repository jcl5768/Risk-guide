# main.py
import streamlit as st
from config import SECTOR_CONFIG, ETF_MAP
from engine import detect_sector, get_z_and_price, search_tickers, TICKER_NAME_MAP
from pages import apply_custom_style, render_main_page, render_detail_page

st.set_page_config(page_title="Risk Guide", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")
apply_custom_style()

def init_session():
    if "portfolio"    not in st.session_state: st.session_state.portfolio    = []
    if "page"         not in st.session_state: st.session_state.page         = "main"
    if "selected"     not in st.session_state: st.session_state.selected     = None
    if "editing"      not in st.session_state: st.session_state.editing      = None
    if "show_add"     not in st.session_state: st.session_state.show_add     = False
    if "chart_period" not in st.session_state: st.session_state.chart_period = "1달"
init_session()

# ── 사이드바: 종목 목록 + 수정/삭제만 ───────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 포트폴리오")
    total_w=sum(s["weight"] for s in st.session_state.portfolio)
    bar_pct=min(total_w,100); bar_clr="#059669" if total_w<=100 else "#DC2626"
    st.markdown(f'''<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;font-size:12px;color:{bar_clr};margin-bottom:4px;"><span>총 비중 {total_w:.1f}% {"✓" if total_w<=100 else "⚠"}</span><span>{len(st.session_state.portfolio)}종목</span></div><div style="height:4px;background:#E8EAED;border-radius:2px;"><div style="height:100%;width:{bar_pct}%;background:{bar_clr};border-radius:2px;"></div></div></div>''', unsafe_allow_html=True)
    st.markdown("---")
    if not st.session_state.portfolio:
        st.markdown('<p style="color:#9CA3AF;font-size:12px;text-align:center;padding:12px;">아직 종목이 없습니다</p>', unsafe_allow_html=True)
    for i,stock in enumerate(st.session_state.portfolio):
        sec=detect_sector(stock["ticker"]); cfg=SECTOR_CONFIG[sec]
        if st.session_state.editing==i:
            st.markdown(f"**✏️ {stock['ticker']} 수정**")
            nn=st.text_input("종목명",value=stock["name"],key=f"en_{i}")
            nw=st.number_input("비중(%)",value=float(stock["weight"]),min_value=0.1,max_value=100.0,step=0.1,format="%.1f",key=f"ew_{i}")
            ns=st.number_input("수량",value=float(stock.get("shares",1)),min_value=0.01,max_value=1000000.0,step=0.01,format="%.2f",key=f"es_{i}")
            na=st.number_input("평단가($)",value=float(stock["avg_price"]),min_value=1.0,max_value=999999.0,format="%.2f",key=f"ea_{i}")
            c1,c2=st.columns(2)
            with c1:
                if st.button("✅",key=f"save_{i}",use_container_width=True):
                    st.session_state.portfolio[i].update({"name":nn,"weight":round(nw,1),"shares":round(ns,2),"avg_price":na})
                    st.session_state.editing=None; st.rerun()
            with c2:
                if st.button("✕",key=f"cancel_{i}",use_container_width=True):
                    st.session_state.editing=None; st.rerun()
        else:
            _,cur=get_z_and_price(stock["ticker"])
            pnl=((cur-stock["avg_price"])/stock["avg_price"]*100) if cur and stock["avg_price"]>0 else None
            pnl_s=f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "—"
            pnl_c="#059669" if (pnl or 0)>=0 else "#DC2626"
            st.markdown(f'''<div style="padding:6px 0;"><div style="display:flex;justify-content:space-between;"><div><b style="font-size:13px;">{stock["ticker"]}</b> <span style="color:{cfg["color"]};font-size:11px;">{cfg["icon"]}</span><div style="font-size:10px;color:#9CA3AF;">{stock["name"]}</div></div><div style="text-align:right;"><b style="color:#2563EB;">{stock["weight"]:.1f}%</b><div style="font-size:10px;color:{pnl_c};">{pnl_s}</div></div></div></div>''', unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("✏️",key=f"edit_{i}",use_container_width=True):
                    st.session_state.editing=i; st.rerun()
            with c2:
                if st.button("🗑",key=f"del_{i}",use_container_width=True):
                    st.session_state.portfolio.pop(i)
                    if st.session_state.editing==i: st.session_state.editing=None
                    st.rerun()
        st.markdown("<hr style='margin:4px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("⚙️ 설정"):
        if st.button("🔄 전체 초기화",use_container_width=True):
            st.session_state.portfolio=[]; st.session_state.editing=None; st.rerun()

# ── 종목 추가 페이지 ─────────────────────────────────────────────────────────
def render_add_page():
    if st.button("← 돌아가기", key="back_from_add"):
        st.session_state.show_add=False
        for k in ("_aticker","_aname","_aprice"): st.session_state.pop(k,None)
        st.rerun()
    st.markdown("## 🔍 종목 추가")
    st.markdown("---")

    # 검색창 하나만 — 종목명 입력칸 없음
    query=st.text_input("","placeholder",placeholder="티커 또는 종목명 입력  예: AAPL · Apple · 반도체 · 나스닥",key="asearch",label_visibility="collapsed").strip()

    sel_t=st.session_state.get("_aticker","")
    sel_n=st.session_state.get("_aname","")
    sel_p=st.session_state.get("_aprice",0.0)

    if query:
        suggestions=search_tickers(query)
        if suggestions:
            st.markdown('<p style="font-size:11px;color:#9CA3AF;margin:8px 0 4px;">연관 종목</p>', unsafe_allow_html=True)
            for sg in suggestions:
                c_cfg=SECTOR_CONFIG.get(sg["sector"],SECTOR_CONFIG["Unknown"])
                ca,cb=st.columns([1,3])
                with ca:
                    if st.button(sg["ticker"],key=f"pick_{sg['ticker']}",use_container_width=True):
                        _,px=get_z_and_price(sg["ticker"])
                        st.session_state["_aticker"]=sg["ticker"]
                        st.session_state["_aname"]=sg["name"]
                        st.session_state["_aprice"]=px
                        st.rerun()
                with cb:
                    st.markdown(f'<div style="padding:4px 0;font-size:12px;"><b>{sg["name"]}</b> <span style="color:{c_cfg["color"]};">{c_cfg["icon"]} {sg["sector_label"]}</span></div>', unsafe_allow_html=True)
        else:
            sel_t=query.upper(); _,sel_p=get_z_and_price(sel_t); sel_n=TICKER_NAME_MAP.get(sel_t,sel_t)

    if sel_t:
        sec=detect_sector(sel_t); cfg=SECTOR_CONFIG.get(sec,SECTOR_CONFIG["Unknown"])
        st.markdown(f'''<div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:12px;padding:16px 20px;margin:14px 0;display:flex;justify-content:space-between;align-items:center;"><div><div style="font-size:20px;font-weight:700;color:#1A1D23;">{sel_t}</div><div style="font-size:13px;color:#6B7280;margin-top:2px;">{sel_n}</div><div style="font-size:12px;color:{cfg["color"]};margin-top:2px;">{cfg["icon"]} {cfg["label"]}</div></div><div style="text-align:right;"><div style="font-size:24px;font-weight:700;color:#1A1D23;">${sel_p:.2f}</div><div style="font-size:11px;color:#059669;margin-top:2px;">현재가 ✓</div></div></div>''', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            nw=st.number_input("비중(%)",min_value=0.1,max_value=100.0,value=10.0,step=0.1,format="%.1f",key="anw")
        with c2:
            ns=st.number_input("수량",min_value=0.01,max_value=1000000.0,value=1.0,step=0.01,format="%.2f",key="ans")
        na=st.number_input("평균단가($)",min_value=1.0,max_value=999999.0,value=max(1.0,round(float(sel_p),2)),format="%.2f",key="ana")
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("✅  포트폴리오에 추가하기",use_container_width=True,type="primary",key="confirm_add"):
            st.session_state.portfolio.append({"ticker":sel_t,"name":sel_n or sel_t,"weight":round(nw,1),"shares":round(ns,2),"avg_price":na})
            for k in ("_aticker","_aname","_aprice","asearch"): st.session_state.pop(k,None)
            st.session_state.show_add=False; st.rerun()
    else:
        st.markdown('<p style="color:#9CA3AF;font-size:13px;text-align:center;padding:32px;">위 검색창에 종목을 검색해주세요</p>', unsafe_allow_html=True)

# ── 라우팅 ───────────────────────────────────────────────────────────────────
if st.session_state.show_add:
    render_add_page()
elif st.session_state.page=="main":
    render_main_page()
elif st.session_state.page=="detail":
    render_detail_page()
