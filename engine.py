# engine.py — 정교화된 분석 엔진
#
# 업그레이드 포인트:
#   1. calc_win_rate() → 단순 합산 → 가중 평균 Z-Score 기반으로 교체
#   2. get_weighted_z()  — 섹터 드라이버 가중 평균 Z-Score 반환
#   3. get_macro_correlation() — 종목과 거시 지표 간 60일 상관계수 계산
#   4. breakdown 딕셔너리 — 각 구성 요소의 기여를 투명하게 노출

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from config import SECTOR_CONFIG, SECTOR_MAP, ETF_MAP


# ── 섹터 감지 ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def detect_sector(ticker: str) -> str:
    t = ticker.upper().strip()
    if t in ETF_MAP:
        return ETF_MAP[t]
    try:
        info = yf.Ticker(ticker).info
        return SECTOR_MAP.get(info.get("sector", "Unknown"), "Unknown")
    except Exception:
        return "Unknown"


# ── yfinance 데이터 추출 헬퍼 ─────────────────────────────────────────────────
def _extract_close(raw: pd.DataFrame) -> pd.Series:
    """yfinance MultiIndex / 단순 컬럼 모두 대응"""
    if raw.empty:
        return pd.Series(dtype=float)
    if isinstance(raw.columns, pd.MultiIndex):
        return (raw["Close"].iloc[:, 0]
                if "Close" in raw.columns.get_level_values(0)
                else raw.iloc[:, 0])
    return raw["Close"] if "Close" in raw.columns else raw.iloc[:, 0]


# ── Z-Score & 현재가 ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_z_and_price(ticker: str) -> tuple[float, float]:
    """Z-Score = (현재가 - 20일 평균) / 20일 표준편차"""
    try:
        raw  = yf.download(ticker, period="60d", interval="1d", progress=False)
        data = _extract_close(raw).dropna()
        if len(data) < 21:
            return 0.0, float(data.iloc[-1]) if len(data) > 0 else 0.0
        cur  = float(data.iloc[-1])
        mean = float(data.tail(20).mean())
        std  = float(data.tail(20).std())
        if std == 0:
            return 0.0, round(cur, 2)
        return round((cur - mean) / std, 2), round(cur, 2)
    except Exception:
        return 0.0, 0.0


# ── 가격 이력 ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_price_history(ticker: str, period: str = "60d") -> pd.DataFrame:
    """Date / Close 컬럼 고정 반환"""
    try:
        raw  = yf.download(ticker, period=period, interval="1d", progress=False)
        data = _extract_close(raw).dropna()
        df   = data.reset_index()
        df.columns = ["Date", "Close"]
        return df
    except Exception:
        return pd.DataFrame()


# ── 섹터 지표 분석 ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_sector_analysis(ticker: str) -> tuple[str, dict, list]:
    """섹터 감지 → 각 지표의 Z-Score·가격 계산"""
    sk  = detect_sector(ticker)
    cfg = SECTOR_CONFIG[sk]
    results = []
    for ind in cfg["indicators"]:
        z, price = get_z_and_price(ind["ticker"])
        results.append({**ind, "z": z, "price": price})
    return sk, cfg, results


# ── ★ 핵심 업그레이드: 가중 평균 Z-Score 계산 ─────────────────────────────────
def get_weighted_z(indicators: list) -> float:
    """
    단순 합산이 아닌 가중 평균 Z-Score.

    공식:
      weighted_z = Σ(z_i × direction_i × driver_weight_i)
                 / Σ(driver_weight_i)   ← 정규화

    - direction: +1(호재) / -1(악재) → 방향 반영
    - driver_weight: 섹터 내 해당 지표의 상대적 중요도 (합계=1.0)
    - 결과: -3 ~ +3 범위의 "섹터 거시 환경 종합 Z-Score"
    """
    total_w = sum(ind["driver_weight"] for ind in indicators)
    if total_w == 0:
        return 0.0
    weighted_sum = sum(
        ind["z"] * ind["direction"] * ind["driver_weight"]
        for ind in indicators
    )
    return round(weighted_sum / total_w, 3)


# ── 승률 계산 (가중 평균 Z-Score 기반) ───────────────────────────────────────
def calc_win_rate(z_stock: float, indicators: list, news_bonus: float) -> tuple[float, dict]:
    """
    Lv.1/2 승률 계산 — 가중 평균 Z-Score 사용.

    공식:
      macro_z    = get_weighted_z(indicators)       ← 거시환경 가중 Z
      macro_score = macro_z × 15                    ← 최대 ±45pt 기여
      z_penalty  = -z_stock × 3                     ← 주가 과열 패널티
      total      = 50 + z_penalty + macro_score + news_bonus
      final      = clamp(total, 5, 95)

    반환:
      (final_win_rate, breakdown_dict)
        breakdown: 각 구성요소 기여를 투명하게 제공 → UI 호버 툴팁에 활용
    """
    macro_z     = get_weighted_z(indicators)
    macro_score = round(macro_z * 15, 1)          # 스케일: Z 1.0 = +15pt
    z_penalty   = round(-z_stock * 3.0, 1)

    total = 50.0 + z_penalty + macro_score + news_bonus
    final = round(max(5.0, min(95.0, total)), 1)

    breakdown = {
        "base":        50.0,
        "z_penalty":   z_penalty,
        "macro_score": macro_score,
        "macro_z":     macro_z,
        "news_bonus":  news_bonus,
        "total_raw":   round(total, 1),
        "final":       final,
        "explain": (
            f"기본(50) "
            f"{'+' if z_penalty >= 0 else ''}{z_penalty}(가격위치) "
            f"{'+' if macro_score >= 0 else ''}{macro_score}(거시가중Z={macro_z:+.2f}) "
            f"{'+' if news_bonus >= 0 else ''}{news_bonus}(뉴스) "
            f"= {final}%"
        ),
    }
    return final, breakdown


# ── ★ 신규: 거시 지표 ↔ 종목 60일 상관계수 ────────────────────────────────────
@st.cache_data(ttl=600)
def get_macro_correlation(stock_ticker: str, indicators: list) -> list:
    """
    종목과 각 거시 지표 간 60일 일간 수익률 상관계수를 계산.
    반환: [{"name", "ticker", "corr", "direction", "sensitivity"}, ...]

    - corr: -1 ~ +1 (피어슨 상관계수)
    - direction이 +1인데 corr이 음수 → 예상과 반대로 움직이는 중 (이상 신호)
    """
    try:
        stock_hist = get_price_history(stock_ticker)
        if stock_hist.empty:
            return []
        stock_ret = stock_hist.set_index("Date")["Close"].pct_change().dropna()
    except Exception:
        return []

    results = []
    for ind in indicators:
        try:
            ind_hist = get_price_history(ind["ticker"])
            if ind_hist.empty:
                results.append({**ind, "corr": 0.0})
                continue
            ind_ret = ind_hist.set_index("Date")["Close"].pct_change().dropna()

            # 공통 날짜만 사용
            common = stock_ret.index.intersection(ind_ret.index)
            if len(common) < 10:
                results.append({**ind, "corr": 0.0})
                continue

            corr = float(np.corrcoef(
                stock_ret.loc[common].values,
                ind_ret.loc[common].values
            )[0, 1])
            results.append({**ind, "corr": round(corr, 3)})
        except Exception:
            results.append({**ind, "corr": 0.0})

    return results


# ── 뉴스 감성 분석 ────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_news(ticker: str) -> tuple[float, list]:
    pos_kw = ["buy","growth","up","positive","surge","profit","beat","record",
              "strong","upgrade","bullish","soars","rises","rally","outperform"]
    neg_kw = ["sell","fall","down","negative","drop","loss","risk","crisis",
              "miss","weak","downgrade","bearish","cut","slump","plunge","recall","fraud"]
    try:
        news_list = yf.Ticker(ticker).news[:5]
        score, analyzed = 0, []
        for n in news_list:
            title = n.get("title", "").lower()
            if any(w in title for w in pos_kw):
                score += 1; sentiment = "Positive"
            elif any(w in title for w in neg_kw):
                score -= 1; sentiment = "Negative"
            else:
                sentiment = "Neutral"
            analyzed.append({
                "title":     n.get("title", ""),
                "link":      n.get("link", "#"),
                "sentiment": sentiment,
            })
        return score * 2.5, analyzed
    except Exception:
        return 0.0, []


# ── 신호등 & 색상 유틸 ────────────────────────────────────────────────────────
def get_signal(wr: float) -> tuple[str, str, str]:
    if wr >= 60:   return "매수 우위", "badge-green",  "#059669"
    elif wr >= 45: return "중립 관망", "badge-yellow", "#D97706"
    else:          return "리스크 경고", "badge-red",  "#DC2626"

def zcolor(z: float) -> str:
    if z > 1.5:    return "#DC2626"
    elif z > 0.5:  return "#D97706"
    elif z < -1.5: return "#059669"
    elif z < -0.5: return "#2563EB"
    else:          return "#6B7280"

def zdesc(z: float) -> str:
    if z > 2.0:    return "극단 과열"
    elif z > 1.0:  return "과매수"
    elif z > 0.3:  return "평균 이상"
    elif z > -0.3: return "중립"
    elif z > -1.0: return "평균 이하"
    elif z > -2.0: return "과매도"
    else:          return "극단 과매도"

def corr_color(corr: float, direction: int) -> str:
    """상관계수 색상: 기대 방향과 일치하면 초록, 반대면 빨강"""
    aligned = (corr > 0 and direction == 1) or (corr < 0 and direction == -1)
    if abs(corr) < 0.15:
        return "#9CA3AF"   # 무상관 — 회색
    return "#059669" if aligned else "#DC2626"
