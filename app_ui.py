import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    .stApp{background:#F7F8FA; font-family:'Inter',sans-serif;}
    .macro-card{background:#FFFFFF; border:1px solid #E8EAED; border-radius:10px; padding:14px;}
    .stock-card{background:#FFFFFF; border:1px solid #E8EAED; border-radius:10px; padding:16px;}
    .badge-green{background:#ECFDF5;color:#059669;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;}
    .badge-yellow{background:#FFFBEB;color:#D97706;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;}
    .badge-red{background:#FEF2F2;color:#DC2626;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;}
    .section-hdr{font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;margin-bottom:12px;border-bottom:1px solid #E8EAED;}
    </style>
    """, unsafe_allow_html=True)

def get_signal_ui(wr):
    if wr >= 60:   return "매수 우위","badge-green","#059669"
    elif wr >= 45: return "중립 관망","badge-yellow","#D97706"
    else:          return "리스크 경고","badge-red","#DC2626"

def zcolor(z):
    if z > 1.5: return "#DC2626"
    elif z < -1.5: return "#059669"
    else: return "#6B7280"

