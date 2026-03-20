# engine.py
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from config import SECTOR_CONFIG, SECTOR_MAP, ETF_MAP

@st.cache_data(ttl=3600)
def detect_sector(ticker):
    t = ticker.upper().strip()
    if t in ETF_MAP:
        return ETF_MAP[t]
    try:
        info = yf.Ticker(ticker).info
        return SECTOR_MAP.get(info.get("sector","Unknown"), "Unknown")
    except:
        return "Unknown"

@st.cache_data(ttl=300)
def get_z_and_price(ticker):
    try:
        raw = yf.download(ticker, period="60d", interval="1d", progress=False)
        if raw.empty: return 0.0, 0.0
        if isinstance(raw.columns, pd.MultiIndex):
            data = raw['Close'].iloc[:,0] if 'Close' in raw.columns.get_level_values(0) else raw.iloc[:,0]
        else:
            data = raw['Close'] if 'Close' in raw.columns else raw.iloc[:,0]
        data = data.dropna()
        if len(data) < 21: return 0.0, float(data.iloc[-1]) if len(data) > 0 else 0.0
        cur = float(data.iloc[-1])
        mean = float(data.tail(20).mean())
        std = float(data.tail(20).std())
        if std == 0: return 0.0, round(cur,2)
        return round((cur-mean)/std,2), round(cur,2)
    except:
        return 0.0, 0.0

@st.cache_data(ttl=300)
def get_sector_analysis(ticker):
    sk = detect_sector(ticker)
    cfg = SECTOR_CONFIG[sk]
    results = []
    for ind in cfg["indicators"]:
        z, price = get_z_and_price(ind["ticker"])
        results.append({**ind, "z":z, "price":price})
    return sk, cfg, results

@st.cache_data(ttl=300)
def get_price_history(ticker):
    try:
        raw = yf.download(ticker, period="60d", interval="1d", progress=False)
        if raw.empty: return pd.DataFrame()
        if isinstance(raw.columns, pd.MultiIndex):
            data = raw['Close'].iloc[:,0] if 'Close' in raw.columns.get_level_values(0) else raw.iloc[:,0]
        else:
            data = raw['Close'] if 'Close' in raw.columns else raw.iloc[:,0]
        df = data.dropna().reset_index()
        df.columns = ['Date','Close']
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_news(ticker):
    try:
        news_list = yf.Ticker(ticker).news[:5]
        pos_kw = ['buy','growth','up','positive','surge','profit','beat','record','strong','upgrade','bullish','soars','rises','rally']
        neg_kw = ['sell','fall','down','negative','drop','loss','risk','crisis','miss','weak','downgrade','bearish','cut','slump','plunge']
        score, analyzed = 0, []
        for n in news_list:
            title = n.get('title','').lower()
            if any(w in title for w in pos_kw):
                score += 1; sentiment = "Positive"
            elif any(w in title for w in neg_kw):
                score -= 1; sentiment = "Negative"
            else:
                sentiment = "Neutral"
            analyzed.append({"title":n.get('title',''),"link":n.get('link','#'),"sentiment":sentiment})
        return score*2.5, analyzed
    except:
        return 0.0, []

def calc_win_rate(z_stock, indicators, news_bonus):
    """직관적인 승률 계산 공식 (100점 만점)"""
    base = 50.0  # 1. 기본 점수 (중립)
    z_penalty = round(-(z_stock * 3.0), 1) 
    macro_score = round(sum([ind["z"] * (ind["weight"] / 5.0) for ind in indicators]), 1)
    total = base + z_penalty + macro_score + news_bonus
    final_win = round(max(5.0, min(95.0, total)), 1)
    explain = f"기본(50) {'+' if z_penalty>=0 else ''}{z_penalty}(가격위치) {'+' if macro_score>=0 else ''}{macro_score}(거시지표) {'+' if news_bonus>=0 else ''}{news_bonus}(뉴스) = {final_win}%"
    return final_win, explain

def get_signal(wr):
    if wr >= 60:   return "매수 우위","badge-green","#059669"
    elif wr >= 45: return "중립 관망","badge-yellow","#D97706"
    else:          return "리스크 경고","badge-red","#DC2626"

def zcolor(z):
    if z > 1.5:    return "#DC2626"
    elif z > 0.5:  return "#D97706"
    elif z < -1.5: return "#059669"
    elif z < -0.5: return "#2563EB"
    else:          return "#6B7280"

def zdesc(z):
    if z > 2.0:    return "극단 과열"
    elif z > 1.0:  return "과매수"
    elif z > 0.3:  return "평균 이상"
    elif z > -0.3: return "중립"
    elif z > -1.0: return "평균 이하"
    elif z > -2.0: return "과매도"
    else:          return "극단 과매도"
