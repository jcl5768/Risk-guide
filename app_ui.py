import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { background: #F7F8FA; font-family: 'Inter', sans-serif; }
    .macro-card { background: white; border-radius: 12px; padding: 20px; border: 1px solid #E8EAED; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .stock-card { background: white; border-radius: 12px; padding: 20px; border: 1px solid #E8EAED; transition: 0.3s; }
    .stock-card:hover { transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .badge-green { background:#ECFDF5; color:#059669; border:1px solid #A7F3D0; border-radius:20px; padding:4px 12px; font-size:12px; font-weight:600; }
    .badge-red { background:#FEF2F2; color:#DC2626; border:1px solid #FECACA; border-radius:20px; padding:4px 12px; font-size:12px; font-weight:600; }
    .badge-yellow { background:#FFFBEB; color:#D97706; border:1px solid #FDE68A; border-radius:20px; padding:4px 12px; font-size:12px; font-weight:600; }
    </style>
    """, unsafe_allow_html=True)

def get_signal_ui(wr):
    if wr >= 65: return "강력 매수", "badge-green", "#059669"
    elif wr >= 45: return "중립", "badge-yellow", "#D97706"
    else: return "위험 관리", "badge-red", "#DC2626"
