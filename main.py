# main.py — 통합 검색 + 연관검색어 (빠른추가 제거)
import streamlit as st
from config import SECTOR_CONFIG, ETF_MAP
from engine import detect_sector, get_z_and_price, search_tickers, TICKER_NAME_MAP
from pages import apply_custom_style, render_main_page, render_detail_page

st.set_page_config(page_title="Risk Guide", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
apply_custom_style()

def init_session():
    defaults={"portfolio":[],"page":"main","selected":None,"editing":None,"show_add":False}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
init_session()

with st.sidebar:
    st.markdown("### 📂 내 포트폴리오")
    total_w=sum(s["weight"] for s in st.session_state.portfolio)
    bar_pct=min(total_w,100); bar_clr="#059669" if total_w<=100 else "#DC2626"
    st.markdown(f'<div style="margin-bottom:12px;"><div style="display:flex;justify-content:space-between;font-size:12px;color:{bar_clr};margin-bottom:4px;"><span>총 비중 {total_w}% {"✓" if total_w<=100 else "⚠ 초과"}</span><span>{len(st.session_state.portfolio)}개 종목</span></div><div style="height:5px;background:#E8EAED;border-radius:3px;"><div style="height:100%;width:{bar_pct}%;background:{bar_clr};border-radius:3px;"></div></div></div>', unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.portfolio:
        st.markdown('<div style="text-align:center;padding:14px 8px;color:#9CA3AF;font-size:12px;background:#F9FAFB;border-radius:8px;margin-bottom:10px;">📭 아직 종목이 없어요<br><span style="font-size:11px;">아래에서 추가해보세요</span></div>', unsafe_allow_html=True)

    for i, stock in enumerate(st.session_state.portfolio):
        sec=detect_sector(stock["ticker"]); cfg=SECTOR_CONFIG[sec]
        if st.session_state.editing==i:
            st.markdown(f"**✏️ {stock['ticker']} 수정**")
            nn=st.text_input("종목명",value=stock["name"],key=f"en_{i}")
            nw=st.number_input("비중(%)",value=int(stock["weight"]),min_value=1,max_value=100,key=f"ew_{i}")
            ns=st.number_input("수량(주)",value=int(stock.get("shares",1)),min_value=1,max_value=1000000,key=f"es_{i}")
            na=st.number_input("평균단가($)",value=float(stock["avg_price"]),min_value=0.0,max_value=999999.0,format="%.2f",key=f"ea_{i}")
            c1,c2=st.columns(2)
            with c1:
                if st.button("✅ 저장",key=f"save_{i}",use_container_width=True):
                    st.session_state.portfolio[i].update({"name":nn,"weight":nw,"shares":ns,"avg_price":na})
                    st.session_state.editing=None; st.rerun()
            with c2:
                if st.button("✕ 취소",key=f"cancel_{i}",use_container_width=True):
                    st.session_state.editing=None; st.rerun()
        else:
            _,cur_price=get_z_and_price(stock["ticker"])
            pnl=((cur_price-stock["avg_price"])/stock["avg_price"]*100) if cur_price and stock["avg_price"]>0 else None
            pnl_str=f"{'+'if pnl>=0 else ''}{pnl:.1f}%" if pnl is not None else "—"
            pnl_clr="#059669" if (pnl or 0)>=0 else "#DC2626"
            value_str=f"${cur_price*stock.get('shares',0):,.0f}" if cur_price and stock.get("shares") else "—"
            st.markdown(f'<div style="padding:8px 0;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="font-weight:700;font-size:14px;color:#1A1D23;">{stock["ticker"]}</span> <span style="font-size:11px;color:{cfg["color"]};">{cfg["icon"]}</span><div style="font-size:10px;color:#9CA3AF;">{stock["name"]}</div></div><div style="text-align:right;"><div style="font-weight:700;font-size:14px;color:#2563EB;">{stock["weight"]}%</div><div style="font-size:10px;color:{pnl_clr};">{pnl_str}</div></div></div><div style="display:flex;justify-content:space-between;font-size:10px;color:#9CA3AF;margin-top:2px;"><span>${cur_price:.1f} · {stock.get("shares",0)}주</span><span>평가 {value_str}</span></div></div>', unsafe_allow_html=True)
            cb1,cb2=st.columns([1,1])
            with cb1:
                if st.button("✏️ 수정",key=f"edit_{i}",use_container_width=True):
                    st.session_state.editing=i; st.rerun()
            with cb2:
                if st.button("🗑 삭제",key=f"del_{i}",use_container_width=True):
                    st.session_state.portfolio.pop(i)
                    if st.session_state.editing==i: st.session_state.editing=None
                    st.rerun()
        st.markdown("<hr style='margin:6px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)

    # ── 통합 종목 검색 & 추가 ──────────────────────────────────────────
    if st.button("➕  종목 추가", use_container_width=True, key="toggle_add"):
        st.session_state.show_add=not st.session_state.show_add

    if st.session_state.show_add:
        st.markdown('<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px;">🔍 종목 검색</div>', unsafe_allow_html=True)

        # 통합 검색창 (티커 + 종목명 동시 검색)
        query=st.text_input(
            "티커 또는 종목명",
            placeholder="예: AAPL, Apple, 반도체, 나스닥…",
            key="search_q",
            label_visibility="collapsed"
        ).strip()

        # 연관 검색 결과
        selected_ticker=""
        selected_name=""
        selected_price=0.0

        if query:
            suggestions=search_tickers(query)
            if suggestions:
                st.markdown('<div style="font-size:10px;color:#9CA3AF;margin-bottom:4px;">연관 종목</div>', unsafe_allow_html=True)
                for sg in suggestions:
                    col_btn, col_info=st.columns([1,3])
                    with col_btn:
                        if st.button(sg["ticker"], key=f"sg_{sg['ticker']}", use_container_width=True):
                            st.session_state["_sel_ticker"]=sg["ticker"]
                            st.session_state["_sel_name"]=sg["name"]
                            st.rerun()
                    with col_info:
                        st.markdown(f'<div style="padding:4px 0;font-size:11px;color:#1A1D23;"><b>{sg["name"]}</b> <span style="color:{SECTOR_CONFIG.get(sg["sector"],SECTOR_CONFIG["Unknown"])["color"]};">{sg["sector_icon"]} {sg["sector_label"]}</span></div>', unsafe_allow_html=True)
            else:
                # 쿼리 자체를 티커로 시도
                st.markdown(f'<div style="font-size:11px;color:#D97706;padding:4px 0;">"{query}" — 직접 티커로 추가 시도</div>', unsafe_allow_html=True)

        # 선택된 종목 or 직접 입력
        pre_ticker=st.session_state.get("_sel_ticker","")
        pre_name  =st.session_state.get("_sel_name","")

        if pre_ticker:
            # 선택된 종목 미리보기
            _,pre_price=get_z_and_price(pre_ticker)
            sec=detect_sector(pre_ticker); cfg2=SECTOR_CONFIG.get(sec,SECTOR_CONFIG["Unknown"])
            st.markdown(f"""
            <div style="background:#F0FDF4;border:1px solid #A7F3D0;border-radius:8px;
                        padding:10px 12px;margin:6px 0;font-size:12px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-weight:700;color:#1A1D23;">{pre_ticker} — {pre_name}</span>
                    <span style="color:#059669;font-size:10px;">선택됨 ✓</span>
                </div>
                <div style="color:#6B7280;">{cfg2["icon"]} {cfg2["label"]} · 현재가 <b>${pre_price:.2f}</b></div>
            </div>
            """, unsafe_allow_html=True)
            nt=pre_ticker; auto_name=pre_name; auto_price=pre_price
        else:
            # 검색 결과 없거나 아직 미선택 → 직접 입력
            nt=(query or "").upper().strip()
            if nt and len(nt)>=1:
                _,auto_price=get_z_and_price(nt)
                auto_name=TICKER_NAME_MAP.get(nt,nt)
            else:
                auto_name=""; auto_price=0.0

        st.markdown("---")
        nn=st.text_input("종목명",value=auto_name,placeholder="자동 입력",key="add_n")
        nw=st.number_input("비중(%)",min_value=1,max_value=100,value=10,key="add_w")
        ns=st.number_input("수량(주)",min_value=1,max_value=1000000,value=1,key="add_s")
        na=st.number_input("평균단가($)",min_value=0.0,max_value=999999.0,
                           value=round(float(auto_price),2) if auto_price else 0.0,
                           format="%.2f",key="add_a",help="0 입력 시 수익률 계산 생략")

        c1,c2=st.columns(2)
        with c1:
            if st.button("✅ 추가",key="do_add",use_container_width=True):
                final_ticker=nt or pre_ticker
                if final_ticker:
                    st.session_state.portfolio.append({"ticker":final_ticker,"name":nn or final_ticker,"weight":nw,"shares":ns,"avg_price":na})
                    st.session_state.show_add=False
                    st.session_state.pop("_sel_ticker",None); st.session_state.pop("_sel_name",None)
                    st.rerun()
        with c2:
            if st.button("✕ 닫기",key="close_add",use_container_width=True):
                st.session_state.show_add=False
                st.session_state.pop("_sel_ticker",None); st.session_state.pop("_sel_name",None)
                st.rerun()

    st.markdown("---")
    with st.expander("⚙️ 설정"):
        if st.button("🔄 전체 초기화",use_container_width=True):
            st.session_state.portfolio=[]; st.session_state.editing=None; st.rerun()

if st.session_state.page=="main": render_main_page()
elif st.session_state.page=="detail": render_detail_page()
