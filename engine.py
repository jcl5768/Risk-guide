# =============================================================================
# engine.py — 분석 엔진 (데이터 수집 + 계산 로직)
#
# ✅ 이 파일을 수정하는 경우:
#   - 승률 계산 공식 변경   → calc_win_rate()
#   - Z-Score 기간 조정     → get_z_and_price() 의 period/tail 값
#   - 뉴스 키워드 추가      → get_news() 의 pos_kw / neg_kw
#   - Lv.3 알고리즘 추가    → 새 함수 작성 후 pages.py에서 호출
#
# UI 코드(HTML/st.markdown)는 pages.py에 있습니다.
# 섹터·지표 설정은 config.py에 있습니다.
# =============================================================================

import streamlit as st
import pandas as pd
import yfinance as yf

from config import SECTOR_CONFIG, SECTOR_MAP, ETF_MAP


# ── 섹터 감지 ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)   # 섹터 정보는 1시간 캐시 (거의 안 바뀜)
def detect_sector(ticker: str) -> str:
    """
    티커 → 섹터 키(SECTOR_CONFIG 키) 반환.
    1순위: ETF_MAP 직접 매핑 (API 호출 없이 즉시)
    2순위: yfinance .info 에서 sector 필드 읽기
    3순위: 감지 실패 시 "Unknown"
    """
    t = ticker.upper().strip()
    if t in ETF_MAP:
        return ETF_MAP[t]
    try:
        info = yf.Ticker(ticker).info
        return SECTOR_MAP.get(info.get("sector", "Unknown"), "Unknown")
    except Exception:
        return "Unknown"


# ── 가격 & Z-Score ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)    # 5분 캐시
def get_z_and_price(ticker: str) -> tuple[float, float]:
    """
    Z-Score = (현재가 - 20일 평균) / 20일 표준편차
    반환: (z_score, current_price)

    ★ 버그 수정: yfinance 최신 버전의 MultiIndex 컬럼 구조 대응
    """
    try:
        raw = yf.download(ticker, period="60d", interval="1d", progress=False)
        if raw.empty:
            return 0.0, 0.0

        # MultiIndex(최신 yfinance) vs 단순 컬럼(구버전) 모두 대응
        if isinstance(raw.columns, pd.MultiIndex):
            data = (raw["Close"].iloc[:, 0]
                    if "Close" in raw.columns.get_level_values(0)
                    else raw.iloc[:, 0])
        else:
            data = raw["Close"] if "Close" in raw.columns else raw.iloc[:, 0]

        data = data.dropna()
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


# ── 섹터 지표 분석 ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_sector_analysis(ticker: str) -> tuple[str, dict, list]:
    """
    해당 종목의 섹터를 감지하고, 섹터에 맞는 모든 지표의 Z-Score를 계산.
    반환: (sector_key, sector_config_dict, indicators_with_z_list)
    """
    sector_key = detect_sector(ticker)
    cfg = SECTOR_CONFIG[sector_key]
    results = []
    for ind in cfg["indicators"]:
        z, price = get_z_and_price(ind["ticker"])
        results.append({**ind, "z": z, "price": price})
    return sector_key, cfg, results


# ── 가격 이력 (차트용) ────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_price_history(ticker: str) -> pd.DataFrame:
    """
    60일 일봉 데이터를 DataFrame으로 반환.
    컬럼: ['Date', 'Close']  ← 항상 이 이름으로 통일

    ★ 버그 수정: KeyError: 'Date' 방지 — reset_index 후 컬럼명 강제 지정
    """
    try:
        raw = yf.download(ticker, period="60d", interval="1d", progress=False)
        if raw.empty:
            return pd.DataFrame()

        if isinstance(raw.columns, pd.MultiIndex):
            data = (raw["Close"].iloc[:, 0]
                    if "Close" in raw.columns.get_level_values(0)
                    else raw.iloc[:, 0])
        else:
            data = raw["Close"] if "Close" in raw.columns else raw.iloc[:, 0]

        df = data.dropna().reset_index()
        df.columns = ["Date", "Close"]   # 버전 무관하게 컬럼명 고정
        return df

    except Exception:
        return pd.DataFrame()


# ── 뉴스 감성 분석 ────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)    # 10분 캐시 (뉴스는 덜 빈번하게 갱신)
def get_news(ticker: str) -> tuple[float, list]:
    """
    yfinance 뉴스 최신 5개 → 키워드 기반 감성 분류.
    반환: (news_bonus_pct, analyzed_news_list)
      news_bonus_pct : 승률에 더해지는 보정값 (뉴스당 +/-2.5%)
      analyzed_news  : [{"title", "link", "sentiment"}, ...]
    """
    pos_kw = [
        "buy", "growth", "up", "positive", "surge", "profit", "beat",
        "record", "strong", "upgrade", "bullish", "soars", "rises", "rally",
        "outperform", "expand", "win", "boost",
    ]
    neg_kw = [
        "sell", "fall", "down", "negative", "drop", "loss", "risk",
        "crisis", "miss", "weak", "downgrade", "bearish", "cut", "slump",
        "plunge", "recall", "lawsuit", "fine", "fraud",
    ]
    try:
        news_list = yf.Ticker(ticker).news[:5]
        score, analyzed = 0, []
        for n in news_list:
            title = n.get("title", "").lower()
            if any(w in title for w in pos_kw):
                score += 1
                sentiment = "Positive"
            elif any(w in title for w in neg_kw):
                score -= 1
                sentiment = "Negative"
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


# ── 승률 계산 ────────────────────────────────────────────────────────────────
def calc_win_rate(z_stock: float, indicators: list, news_bonus: float) -> float:
    """
    Lv.1 승률 계산 공식:
      base = 50 - z_stock * 5          (주가 자체 과열/저평가 반영)
      base += Σ(z_i × weight_i × 0.5) (섹터 맞춤 지표 가중 합산)
      final = clamp(base + news_bonus, 5, 95)

    Lv.3에서는 이 함수를 대체하거나 보정하는 방식으로 확장 예정.
    """
    base = 50.0 - z_stock * 5
    for ind in indicators:
        base += ind["z"] * ind["weight"] * 0.5
    return round(max(5.0, min(95.0, base + news_bonus)), 1)


# ── 신호등 ───────────────────────────────────────────────────────────────────
def get_signal(win_rate: float) -> tuple[str, str, str]:
    """
    반환: (표시 텍스트, CSS 클래스명, 색상 hex)
    """
    if win_rate >= 60:
        return "매수 우위", "badge-green",  "#059669"
    elif win_rate >= 45:
        return "중립 관망", "badge-yellow", "#D97706"
    else:
        return "리스크 경고", "badge-red",  "#DC2626"


# ── Z-Score 색상 & 설명 ──────────────────────────────────────────────────────
def zcolor(z: float) -> str:
    """Z-Score 값에 따른 색상 반환"""
    if z > 1.5:    return "#DC2626"   # 과열 — 빨강
    elif z > 0.5:  return "#D97706"   # 주의 — 주황
    elif z < -1.5: return "#059669"   # 과매도 — 초록
    elif z < -0.5: return "#2563EB"   # 저평가 — 파랑
    else:          return "#6B7280"   # 중립 — 회색


def zdesc(z: float) -> str:
    """Z-Score 값에 따른 한국어 설명 반환"""
    if z > 2.0:    return "극단 과열"
    elif z > 1.0:  return "과매수"
    elif z > 0.3:  return "평균 이상"
    elif z > -0.3: return "중립"
    elif z > -1.0: return "평균 이하"
    elif z > -2.0: return "과매도"
    else:          return "극단 과매도"
