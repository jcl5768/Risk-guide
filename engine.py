# engine.py — 개선된 로직
# 변경 포인트:
#   1. Percentile 기반 주가 위치 (Z-Score 정규분포 가정 탈피)
#   2. 동적 가중치 (60일 상관계수로 고정 가중치 보정)
#   3. 뉴스 감쇠 (48시간 이내만 full 반영, 이후 급격히 감쇠)
#   4. 간이 백테스트 (과거 신호 → 실제 수익률 검증)

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from config import SECTOR_CONFIG, SECTOR_MAP, ETF_MAP


# ── 내부 유틸 ─────────────────────────────────────────────────────────────────
def _extract_close(raw):
    if raw.empty: return pd.Series(dtype=float)
    if isinstance(raw.columns, pd.MultiIndex):
        return raw["Close"].iloc[:,0] if "Close" in raw.columns.get_level_values(0) else raw.iloc[:,0]
    return raw["Close"] if "Close" in raw.columns else raw.iloc[:,0]

def _extract_ohlcv(raw):
    if raw.empty: return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        cols = {pt: raw[pt].iloc[:,0] for pt in ["Open","High","Low","Close","Volume"] if pt in raw.columns.get_level_values(0)}
    else:
        cols = {pt: raw[pt] for pt in ["Open","High","Low","Close","Volume"] if pt in raw.columns}
    if not cols: return pd.DataFrame()
    df = pd.DataFrame(cols).dropna(subset=["Close"]).reset_index()
    df = df.rename(columns={df.columns[0]: "Date"})
    return df


# ── 섹터 감지 ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def detect_sector(ticker):
    t = ticker.upper().strip()
    if t in ETF_MAP: return ETF_MAP[t]
    try:
        info = yf.Ticker(ticker).info
        return SECTOR_MAP.get(info.get("sector","Unknown"), "Unknown")
    except Exception:
        return "Unknown"


# ── 주가 Z-Score + Percentile ─────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_z_and_price(ticker):
    try:
        raw  = yf.download(ticker, period="1y", interval="1d", progress=False, timeout=10)
        if raw is None or raw.empty: return 0.0, 0.0
        data = _extract_close(raw).dropna()
        if len(data) < 21:
            return 0.0, float(data.iloc[-1]) if len(data)
