
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
@st.cache_data(ttl=600)
def get_z_and_price(ticker):
    try:
        raw  = yf.download(ticker, period="1y", interval="1d", progress=False, timeout=10)
        if raw is None or raw.empty: return 0.0, 0.0
        data = _extract_close(raw).dropna()
        if len(data) < 21:
            return 0.0, float(data.iloc[-1]) if len(data) > 0 else 0.0
        cur  = float(data.iloc[-1])
        mean = float(data.tail(20).mean())
        std  = float(data.tail(20).std())
        z    = round((cur - mean) / std, 2) if std > 0 else 0.0
        return z, round(cur, 2)
    except Exception:
        return 0.0, 0.0


@st.cache_data(ttl=600)
def get_percentile(ticker):
    """현재가가 1년 데이터 중 몇 번째 백분위인지 (0~100)"""
    try:
        raw  = yf.download(ticker, period="1y", interval="1d", progress=False, timeout=10)
        if raw is None or raw.empty: return 50.0
        data = _extract_close(raw).dropna()
        if len(data) < 30: return 50.0
        cur = float(data.iloc[-1])
        return round(float((data < cur).sum() / len(data) * 100), 1)
    except Exception:
        return 50.0


# ── 차트 데이터 ───────────────────────────────────────────────────────────────
PERIOD_MAP = {
    "1개월": ("1mo",  "1d"),   # 1개월치 일봉
    "3개월": ("3mo",  "1d"),   # 3개월치 일봉
    "1년":   ("1y",   "1wk"),  # 1년치 주봉
    "5년":   ("5y",   "1mo"),  # 5년치 월봉
}
PERIOD_LABELS = ["1개월", "3개월", "1년", "5년"]

@st.cache_data(ttl=120)
def get_chart_data(ticker, period_key="1개월"):
    period, interval = PERIOD_MAP.get(period_key, ("1mo","1d"))
    try:
        raw = yf.download(ticker, period=period, interval=interval, progress=False, timeout=10)
        if raw is None or raw.empty: return pd.DataFrame()
        return _extract_ohlcv(raw)
    except Exception:
        return pd.DataFrame()

def get_price_stats(df):
    empty = {"max_gain":0,"max_loss":0,"period_ret":0,"volatility":0,"high":0,"low":0}
    if df.empty or "Close" not in df.columns: return empty
    closes    = df["Close"].dropna()
    if len(closes) < 2: return empty
    daily_ret = closes.pct_change().dropna()
    vol_factor= 252 if len(daily_ret) > 20 else 52
    return {
        "max_gain":   round(float(daily_ret.max() * 100), 2),
        "max_loss":   round(float(daily_ret.min() * 100), 2),
        "period_ret": round(float((closes.iloc[-1] / closes.iloc[0] - 1) * 100), 2),
        "volatility": round(float(daily_ret.std() * np.sqrt(vol_factor) * 100), 2),
        "high": round(float(df["High"].max()) if "High" in df.columns else float(closes.max()), 2),
        "low":  round(float(df["Low"].min())  if "Low"  in df.columns else float(closes.min()), 2),
    }


# ── 가격 히스토리 ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_price_history(ticker, period="60d"):
    try:
        raw  = yf.download(ticker, period=period, interval="1d", progress=False, timeout=10)
        if raw is None or raw.empty: return pd.DataFrame()
        data = _extract_close(raw).dropna()
        df   = data.reset_index()
        df.columns = ["Date","Close"]
        return df
    except Exception:
        return pd.DataFrame()


# ── 섹터 분석 ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_sector_analysis(ticker):
    try:
        sk  = detect_sector(ticker)
        cfg = SECTOR_CONFIG[sk]
        results = []
        for ind in cfg["indicators"]:
            z, price = get_z_and_price(ind["ticker"])
            results.append({**ind, "z": z, "price": price})
        return sk, cfg, results
    except Exception:
        cfg = SECTOR_CONFIG["Unknown"]
        return "Unknown", cfg, [{**ind, "z": 0.0, "price": 0.0} for ind in cfg["indicators"]]


# ── 상관계수 계산 ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_macro_correlation(stock_ticker, indicators):
    try:
        sh = get_price_history(stock_ticker)
        if sh.empty: return []
        sr = sh.set_index("Date")["Close"].pct_change().dropna()
    except:
        return []
    results = []
    for ind in indicators:
        try:
            ih     = get_price_history(ind["ticker"])
            if ih.empty: results.append({**ind, "corr": 0.0}); continue
            ir     = ih.set_index("Date")["Close"].pct_change().dropna()
            common = sr.index.intersection(ir.index)
            if len(common) < 10: results.append({**ind, "corr": 0.0}); continue
            corr   = float(np.corrcoef(sr.loc[common].values, ir.loc[common].values)[0,1])
            results.append({**ind, "corr": round(corr, 3)})
        except:
            results.append({**ind, "corr": 0.0})
    return results


# ── 동적 가중치 (개선 ②) ──────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def _get_dynamic_weights(stock_ticker, indicators):
    """
    60일 실제 상관계수로 고정 가중치를 보정.
    - 이론 방향 일치 + 강한 상관 → 최대 1.5배
    - 무상관(|r|<0.1)                → 0.5배
    - 이론 역방향                    → 최소 0.2배
    """
    corr_data = get_macro_correlation(stock_ticker, indicators)
    corr_map  = {d["ticker"]: d["corr"] for d in corr_data}
    weights   = {}
    for ind in indicators:
        corr    = corr_map.get(ind["ticker"], 0.0)
        aligned = (corr > 0 and ind["direction"] == +1) or \
                  (corr < 0 and ind["direction"] == -1)
        abs_c   = abs(corr)
        if abs_c < 0.1:
            mult = 0.5
        elif aligned:
            mult = 1.0 + 0.5 * min(abs_c, 1.0)
        else:
            mult = max(0.2, 1.0 - abs_c)
        weights[ind["ticker"]] = ind["driver_weight"] * mult
    total = sum(weights.values())
    if total > 0:
        weights = {k: v / total for k, v in weights.items()}
    return weights


def get_weighted_z(indicators, dynamic_weights=None):
    if dynamic_weights:
        total_w = sum(dynamic_weights.get(ind["ticker"], ind["driver_weight"]) for ind in indicators)
        if total_w == 0: return 0.0
        return round(sum(
            ind["z"] * ind["direction"] * dynamic_weights.get(ind["ticker"], ind["driver_weight"])
            for ind in indicators
        ) / total_w, 3)
    else:
        total_w = sum(ind["driver_weight"] for ind in indicators)
        if total_w == 0: return 0.0
        return round(sum(
            ind["z"] * ind["direction"] * ind["driver_weight"] for ind in indicators
        ) / total_w, 3)


# ── 종목별 지속성 뉴스 키워드 ────────────────────────────────────────────────
# 시간이 지나도 주가에 계속 영향을 주는 구조적 이슈 키워드
# 긍정 지속성
PERSISTENT_POS_KW = [
    # 기업 구조
    "상장","IPO","스핀오프","분사","합병","인수","지분 취득","전략적 제휴","파트너십",
    # 경영·리더십
    "CEO","대표이사","최고경영자","이사회","창업자 복귀",
    # 사업 확장
    "신사업","신시장","독점","특허","라이선스","정부 계약","수주 확정","장기 계약",
    "공장 증설","설비 투자","생산 확대","글로벌 확장",
    # 기술·제품
    "신제품 출시","플랫폼 출시","FDA 승인","규제 승인","임상 성공",
    # 영문
    "ipo","spinoff","merger","acquisition","partnership","exclusive","patent",
    "government contract","factory","expansion","approved","approval","launch",
]
# 부정 지속성
PERSISTENT_NEG_KW = [
    # 법률·규제
    "소송","집단소송","반독점","규제 조사","SEC 조사","청문회","제재","벌금","과징금",
    "리콜","결함","안전 문제","특허 침해",
    # 경영 위기
    "파산","구조조정","대량 해고","감원","CEO 사임","경영진 교체","내부 고발",
    # 사업 철수
    "사업 철수","시장 철수","공장 폐쇄","사업 중단","계약 해지","파트너 이탈",
    # 지정학
    "수출 규제","수입 금지","관세 부과","무역 제재","블랙리스트",
    # 영문
    "lawsuit","antitrust","sec investigation","recall","defect","bankruptcy",
    "layoff","restructuring","resignation","sanctions","export ban","tariff","blacklist",
]

# 단기 이벤트성 키워드 (시간 감쇠 강하게)
SHORT_TERM_KW = [
    "급등","급락","상승","하락","실적 발표","어닝","분기","전망","목표가",
    "오늘","금일","이번주","반등","조정","surges","plunges","earnings","quarterly",
]


def _classify_news(title):
    """
    뉴스를 세 가지로 분류:
    - 'persistent_pos': 긍정 지속성 (감쇠 없이 장기 반영)
    - 'persistent_neg': 부정 지속성
    - 'short':          단기 이벤트 (기존 시간 감쇠)
    """
    t = title.lower()
    if any(kw.lower() in t for kw in PERSISTENT_POS_KW):
        return "persistent_pos"
    if any(kw.lower() in t for kw in PERSISTENT_NEG_KW):
        return "persistent_neg"
    return "short"


# ── 뉴스 시간 감쇠 (지속성 뉴스 구분 적용) ───────────────────────────────────
def _news_decay(raw_score, pub_date_str, title=""):
    """
    지속성 뉴스: 시간 경과해도 60% 고정 반영 (이중반영 방지용 40% 할인만)
    단기 뉴스:
      0~24h  → 100%
      24~48h → 50%
      48h+   → 10%
    """
    news_type = _classify_news(title)

    if news_type in ("persistent_pos", "persistent_neg"):
        # 지속성 뉴스는 시간 무관 60% 고정
        return raw_score * 0.6

    # 단기 뉴스 — 시간 감쇠
    if not pub_date_str:
        return raw_score * 0.5
    try:
        from email.utils import parsedate_to_datetime
        pub_dt  = parsedate_to_datetime(pub_date_str)
        now_utc = datetime.now(pub_dt.tzinfo) if pub_dt.tzinfo else datetime.utcnow()
        hours   = (now_utc - pub_dt).total_seconds() / 3600
        if hours <= 24:   return raw_score * 1.0
        elif hours <= 48: return raw_score * 0.5
        else:             return raw_score * 0.1
    except:
        return raw_score * 0.5


def _percentile_score(ticker):
    """Percentile → 승률 보정 (-15 ~ +15점)"""
    pct   = get_percentile(ticker)
    score = round((50 - pct) / 50 * 15, 1)
    return score, pct


@st.cache_data(ttl=600)
def _get_market_regime():
    """
    시장 국면 분류 (겉으로 표시 안 함 — 승률 보정에만 사용)
    SPY 20일 모멘텀 + VIX 수준으로 3가지 국면 판단.
    하락장 패널티(-5)를 상승장 보너스(+3)보다 크게 설정 → FN(위험 과소평가) 방지.
    """
    try:
        raw_spy = yf.download("SPY", period="2mo", interval="1d", progress=False, timeout=10)
        spy = _extract_close(raw_spy).dropna()
        if len(spy) < 21: return 0, 0.0
        mom_20 = float((spy.iloc[-1] / spy.iloc[-21] - 1) * 100)

        raw_vix = yf.download("^VIX", period="5d", interval="1d", progress=False, timeout=10)
        vix_ser = _extract_close(raw_vix).dropna()
        vix = float(vix_ser.iloc[-1]) if not vix_ser.empty else 20.0

        if mom_20 > 3 and vix < 20:   return +1, +3.0   # 상승장
        elif mom_20 < -3 or vix > 28: return -1, -5.0   # 하락장 (FN 방지)
        else:                          return  0,  0.0   # 중립
    except Exception:
        return 0, 0.0




# ── 모멘텀 팩터 (추세 지속성 보정) ───────────────────────────────────────────
@st.cache_data(ttl=600)
def _get_momentum_score(ticker):
    """
    모멘텀 팩터: 3단계 구조
      ① 기본 모멘텀 점수 — 20일/60일 수익률 기반 (-12 ~ +12점)
      ② 거래량 신뢰도 배율 — 거래량 폭발 동반 시 강화, 없으면 약화
      ③ 신고가 근접 여부 — 52주 신고가 돌파 + 거래량이면 추세 지속 가능성 보너스

    NVDA 2024처럼 가격+거래량+신고가 3박자 갖춘 종목 → 최대 +15점
    거래량 없이 가격만 오른 종목 → 절반 이하로 감쇠
    과열 후 거래량 급감 구간 → 오히려 패널티
    """
    try:
        raw = yf.download(ticker, period="1y", interval="1d", progress=False, timeout=10)
        if raw is None or raw.empty:
            return 0.0, {}

        closes = _extract_close(raw).dropna()
        if len(closes) < 60:
            return 0.0, {}

        # ── ① 기본 모멘텀: 20일·60일 수익률 ─────────────────────────────
        mom_20 = float((closes.iloc[-1] / closes.iloc[-21] - 1) * 100)  if len(closes) >= 21 else 0.0
        mom_60 = float((closes.iloc[-1] / closes.iloc[-61] - 1) * 100)  if len(closes) >= 61 else 0.0

        # 20일 모멘텀: -10% 이하 → -8점, +10% 이상 → +8점 (선형 보간)
        m20_score = round(max(-8.0, min(8.0, mom_20 * 0.6)), 1)
        # 60일 모멘텀: -20% 이하 → -6점, +20% 이상 → +6점
        m60_score = round(max(-6.0, min(6.0, mom_60 * 0.25)), 1)
        base_score = m20_score + m60_score   # -14 ~ +14

        # ── ② 거래량 신뢰도 배율 ─────────────────────────────────────────
        vol_multiplier = 1.0  # 기본 배율
        vol_label      = "보통"

        if "Volume" in raw.columns or (hasattr(raw.columns, "get_level_values") and
                                        "Volume" in raw.columns.get_level_values(0)):
            try:
                if isinstance(raw.columns, pd.MultiIndex):
                    vol_series = raw["Volume"].iloc[:, 0].dropna()
                else:
                    vol_series = raw["Volume"].dropna()

                if len(vol_series) >= 21:
                    vol_ma20  = float(vol_series.tail(21).mean())    # 20일 평균 거래량
                    vol_recent = float(vol_series.tail(5).mean())    # 최근 5일 평균
                    vol_ratio  = vol_recent / vol_ma20 if vol_ma20 > 0 else 1.0

                    if vol_ratio >= 2.0:
                        vol_multiplier = 1.5   # 거래량 2배 이상 폭발 → 신뢰도 강화
                        vol_label      = "폭발 🔥"
                    elif vol_ratio >= 1.3:
                        vol_multiplier = 1.2   # 거래량 증가 → 소폭 강화
                        vol_label      = "증가 ↑"
                    elif vol_ratio < 0.5:
                        vol_multiplier = 0.4   # 거래량 급감 → 신뢰도 약화
                        vol_label      = "급감 ↓"
                    elif vol_ratio < 0.7:
                        vol_multiplier = 0.7   # 거래량 감소
                        vol_label      = "감소"
            except Exception:
                pass

        # ── ③ 52주 신고가 근접 보너스 ────────────────────────────────────
        high_bonus = 0.0
        high_label = ""

        high_52w = float(closes.max())
        cur_price = float(closes.iloc[-1])
        pct_from_high = (cur_price - high_52w) / high_52w * 100  # 신고가 대비 %

        if pct_from_high >= -3.0:          # 52주 신고가 97% 이상 (신고가 근처 or 돌파)
            if vol_multiplier >= 1.2:      # 거래량 동반 시에만 보너스
                high_bonus = 3.0
                high_label = "신고가 돌파+거래량 📈"
            else:
                high_bonus = 1.0           # 거래량 없으면 소폭만
                high_label = "신고가 근처"
        elif pct_from_high >= -10.0:       # 신고가 대비 -10% 이내
            high_bonus = 1.0
            high_label = "신고가 근처"
        elif pct_from_high <= -40.0:       # 신고가 대비 -40% 이하 (깊은 하락)
            high_bonus = -1.0
            high_label = "52주 저점권"

        # ── 최종 합산: 거래량 배율 × 기본 모멘텀 + 신고가 보너스 ─────────
        raw_score  = base_score * vol_multiplier + high_bonus
        # 클램프: -15 ~ +15
        final_score = round(max(-15.0, min(15.0, raw_score)), 1)

        meta = {
            "mom_20":          round(mom_20, 1),
            "mom_60":          round(mom_60, 1),
            "m20_score":       m20_score,
            "m60_score":       m60_score,
            "vol_multiplier":  round(vol_multiplier, 2),
            "vol_label":       vol_label,
            "high_bonus":      high_bonus,
            "high_label":      high_label,
            "pct_from_high":   round(pct_from_high, 1),
            "final":           final_score,
        }
        return final_score, meta

    except Exception:
        return 0.0, {}

# ── 핵심 승률 계산 ────────────────────────────────────────────────────────────
def calc_win_rate(z_stock, indicators, news_bonus, stock_ticker=None, news_items=None, invest_mode="단기"):
    # 1. 주가 위치 (Percentile)
    if stock_ticker:
        position_score, percentile = _percentile_score(stock_ticker)
    else:
        position_score = round(-z_stock * 3.0, 1)
        percentile     = 50.0

    # 2. 거시 환경 (동적 가중치)
    if stock_ticker:
        try:
            dyn_w   = _get_dynamic_weights(stock_ticker, indicators)
            macro_z = get_weighted_z(indicators, dyn_w)
        except Exception:
            dyn_w   = None
            macro_z = get_weighted_z(indicators)
    else:
        dyn_w   = None
        macro_z = get_weighted_z(indicators)
    macro_score = round(max(-20.0, min(20.0, macro_z * 15)), 1)

    # 3. 뉴스 (시간 감쇠)
    if news_items:
        news_adj = round(sum(
            _news_decay(
                5.0 if n["sentiment"]=="Positive" else -5.0 if n["sentiment"]=="Negative" else 0.0,
                n.get("pub_date_raw",""),
                n.get("title","")
            ) for n in news_items
        ), 1)
    else:
        news_adj = round(news_bonus * 0.5, 1)

    # 4. 시장 국면 보정
    _, regime_adj = _get_market_regime()
    regime_adj = round(regime_adj, 1)

    # 5. 모멘텀 팩터 (추세 지속성)
    #    거래량·신고가로 신뢰도 보정된 모멘텀 점수 (-15 ~ +15)
    if stock_ticker:
        try:
            momentum_score, momentum_meta = _get_momentum_score(stock_ticker)
        except Exception:
            momentum_score = 0.0
            momentum_meta  = {}
    else:
        momentum_score = 0.0
        momentum_meta  = {}

    # 6. 모드별 가중치 설정
    if invest_mode == "장기":
        # 장기 보유 모드:
        # - 가격 위치 패널티 50% 축소 (장기엔 단기 고점이 의미 없음)
        # - 하락장 패널티 제거 (장기엔 하락이 오히려 기회)
        # - 모멘텀·상대강도 강화 (주도주 판별이 핵심)
        pos_w       = 0.5    # 가격위치 가중치 50%로 축소
        regime_use  = 0.0    # 하락장 패널티 무시
        momentum_w  = 1.5    # 모멘텀 1.5배 강화
        macro_w     = 0.8    # 거시환경 소폭 축소
    elif invest_mode == "스윙":
        # 스윙 모드 (수주~수개월):
        pos_w       = 0.75
        regime_use  = regime_adj * 0.5
        momentum_w  = 1.2
        macro_w     = 1.0
    else:  # 단기 (기본)
        pos_w       = 1.0
        regime_use  = regime_adj
        momentum_w  = 1.0
        macro_w     = 1.0

    adj_position = round(position_score * pos_w, 1)
    adj_momentum = round(momentum_score * momentum_w, 1)
    adj_macro    = round(macro_score * macro_w, 1)

    # 모멘텀 오프셋 (고점 패널티 상쇄)
    momentum_offset = 0.0
    if adj_momentum > 5.0 and adj_position < 0:
        momentum_offset = round(min(abs(adj_position) * 0.5, adj_momentum * 0.3), 1)
    elif adj_momentum < -5.0 and adj_position > 0:
        momentum_offset = round(max(-abs(adj_position) * 0.5, adj_momentum * 0.3), 1)

    total = (50.0 + adj_position + momentum_offset
             + adj_macro + news_adj + regime_use + adj_momentum)
    final = round(max(5.0, min(95.0, total)), 1)

    # 신뢰구간: 구성 요소 수(5개)와 각 점수의 표준편차로 근사
    # 각 구성요소 불확실성의 합으로 ±범위 추정
    _uncertainty = round(
        (abs(position_score) * 0.3    # 가격위치 불확실성
         + abs(macro_score) * 0.25    # 거시 불확실성
         + abs(news_adj) * 0.4        # 뉴스 불확실성 (가장 높음)
         + abs(momentum_score) * 0.2  # 모멘텀 불확실성
         + 5.0                        # 기본 모델 오차
        ), 1
    )
    confidence_range = round(min(_uncertainty, 20.0), 1)  # 최대 ±20점

    return final, {
        "base":            50.0,
        "position_score":  position_score,
        "percentile":      percentile,
        "macro_score":     macro_score,
        "macro_z":         macro_z,
        "news_bonus":      news_adj,
        "news_raw":        news_bonus,
        "regime_adj":      regime_adj,
        "momentum_score":  momentum_score,
        "momentum_meta":   momentum_meta,
        "momentum_offset": momentum_offset,
        "confidence_range": confidence_range,
        "total_raw":       round(total, 1),
        "final":           final,
        "dynamic_weights": dyn_w,
        "z_penalty":       position_score,
        "invest_mode":     invest_mode,
        "adj_position":    adj_position,
        "adj_momentum":    adj_momentum,
        "explain": (
            f"[{invest_mode}] 기본(50) {'+' if adj_position>=0 else ''}{adj_position}"
            f"(가격{percentile:.0f}%ile) "
            f"{'+' if adj_macro>=0 else ''}{adj_macro}(거시Z) "
            f"{'+' if news_adj>=0 else ''}{news_adj}(뉴스) "
            f"{'+' if adj_momentum>=0 else ''}{adj_momentum}(모멘텀) = {final}%"
        ),
    }


# ── 간이 백테스트 (개선 ④) ───────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def run_backtest(ticker, indicators_config):
    """
    과거 신호 → 20 거래일 후 실제 수익률 검증
    - 2년치 데이터, 20일 간격 슬라이딩
    - 매수/리스크 신호별 적중률·평균수익률·샤프 계산
    - 최근 5개 샘플 반환
    """
    try:
        raw   = yf.download(ticker, period="2y", interval="1d", progress=False)
        close = _extract_close(raw).dropna()
        if len(close) < 60: return None

        # 지표 데이터 미리 로드
        ind_data = {}
        for ind in indicators_config:
            try:
                r = yf.download(ind["ticker"], period="2y", interval="1d", progress=False)
                s = _extract_close(r).dropna()
                if not s.empty: ind_data[ind["ticker"]] = s
            except:
                pass

        results = []
        step    = 20
        for i in range(60, len(close) - step, step):
            signal_date = close.index[i]
            window      = close.iloc[max(0, i-252):i]
            if len(window) < 30: continue

            cur = float(close.iloc[i])
            pct = float((window < cur).sum() / len(window) * 100)
            p_s = round((50 - pct) / 50 * 12, 1)

            # 거시 Z (고정 가중치, 백테스트 단순화)
            mz_sum = 0.0; tw = 0.0
            for ind in indicators_config:
                if ind["ticker"] not in ind_data: continue
                past = ind_data[ind["ticker"]][ind_data[ind["ticker"]].index <= signal_date].tail(21)
                if len(past) < 5: continue
                ic = float(past.iloc[-1])
                im = float(past.tail(20).mean())
                ist= float(past.tail(20).std())
                iz = (ic - im) / ist if ist > 0 else 0.0
                mz_sum += iz * ind["direction"] * ind["driver_weight"]
                tw     += ind["driver_weight"]

            macro_z = mz_sum / tw if tw > 0 else 0.0
            score   = max(5, min(95, 50 + p_s + macro_z * 15))
            signal  = "매수" if score >= 60 else "리스크" if score < 45 else "중립"

            future_price = float(close.iloc[i + step])
            ret          = round((future_price - cur) / cur * 100, 2)
            results.append({
                "date":   str(signal_date)[:10],
                "score":  round(score, 1),
                "signal": signal,
                "ret":    ret,
                "pct":    round(pct, 1),
            })

        if not results: return None
        df_r = pd.DataFrame(results)

        buy_df  = df_r[df_r["signal"] == "매수"]
        risk_df = df_r[df_r["signal"] == "리스크"]

        buy_acc  = round(float((buy_df["ret"]  > 0).mean() * 100), 1) if len(buy_df)  > 0 else 0.0
        risk_acc = round(float((risk_df["ret"] < 0).mean() * 100), 1) if len(risk_df) > 0 else 0.0
        avg_buy  = round(float(buy_df["ret"].mean()),  2) if len(buy_df)  > 0 else 0.0
        avg_risk = round(float(risk_df["ret"].mean()), 2) if len(risk_df) > 0 else 0.0

        sharpe = round(
            float(buy_df["ret"].mean() / buy_df["ret"].std() * np.sqrt(12)), 2
        ) if len(buy_df) > 1 and buy_df["ret"].std() > 0 else 0.0

        # 최근 5개 샘플 (매수/리스크만, 최신순)
        samples = df_r[df_r["signal"] != "중립"].tail(6).iloc[::-1].head(5).to_dict("records")

        return {
            "total":        len(df_r),
            "buy_count":    len(buy_df),
            "risk_count":   len(risk_df),
            "buy_acc":      buy_acc,
            "risk_acc":     risk_acc,
            "avg_ret_buy":  avg_buy,
            "avg_ret_risk": avg_risk,
            "sharpe":       sharpe,
            "samples":      samples,
        }
    except:
        return None


# ── 뉴스 수집 ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_korean_news(ticker, stock_name=""):
    pos_kw = ["상승","급등","호재","매수","추천","목표가 상향","실적 개선","흑자","성장",
              "수혜","돌파","신고가","강세","긍정","반등","최고","증가","확대","수주","계약","출시","승인"]
    neg_kw = ["하락","급락","악재","매도","목표가 하향","실적 부진","적자","우려","리스크",
              "위기","하회","약세","부정","손실","감소","축소","취소","리콜","소송","조사"]
    queries  = []
    if stock_name and stock_name != ticker: queries.append(stock_name)
    queries.append(f"{ticker} 주가")
    all_news = []; seen = set()

    for query in queries:
        if len(all_news) >= 8: break
        try:
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            for item in root.findall(".//item")[:6]:
                te    = item.find("title"); le = item.find("link")
                pe    = item.find("pubDate"); se = item.find("source")
                title = te.text.strip() if te is not None else ""
                link  = le.text.strip() if le is not None else "#"
                pub   = pe.text.strip() if pe is not None else ""
                src   = se.text.strip() if se is not None else "Google News"
                if not title or title in seen: continue
                seen.add(title)
                if any(kw in title for kw in pos_kw):   sentiment = "Positive"
                elif any(kw in title for kw in neg_kw): sentiment = "Negative"
                else:                                   sentiment = "Neutral"
                news_type = _classify_news(title)   # 지속성 분류
                all_news.append({
                    "title": title, "link": link, "source": src,
                    "pub_date": pub[:16] if pub else "",
                    "pub_date_raw": pub,
                    "sentiment": sentiment,
                    "news_type": news_type,          # 'persistent_pos/neg' or 'short'
                })
        except:
            continue

    subset = all_news[:8]
    decayed = sum(
        _news_decay(
            2.5 if n["sentiment"]=="Positive" else -2.5 if n["sentiment"]=="Negative" else 0.0,
            n.get("pub_date_raw",""),
            n.get("title","")   # ← 지속성 분류
        ) for n in subset
    )
    return round(decayed, 1), subset


@st.cache_data(ttl=600)
def get_news(ticker):
    # 구문 기반 긍정 표현 (단순 단어 대신 실제 뉴스 표현)
    pos_kw = [
        "beat estimates", "beats expectations", "record revenue", "record profit",
        "raises guidance", "raised guidance", "strong earnings", "profit surge",
        "upgrade", "buy rating", "outperform", "bullish", "breakthrough",
        "fda approval", "clinical success", "major contract", "partnership deal",
    ]
    # 구문 기반 부정 표현
    neg_kw = [
        "misses estimates", "misses expectations", "profit warning", "lowers guidance",
        "lowered guidance", "revenue decline", "earnings miss", "downgrade",
        "sell rating", "underperform", "bearish", "bankruptcy", "recall",
        "sec investigation", "class action", "fraud", "layoffs", "job cuts",
        "revenue fell", "loss widens", "guidance cut",
    ]
    neg_prefix = ["not ", "no ", "miss", "fail", "below", "weak", "poor", "disappoint"]
    try:
        news_list = yf.Ticker(ticker).news[:8]
        score = 0; analyzed = []
        for n in news_list:
            raw_title = n.get("title", "")
            title_lo  = raw_title.lower()
            sentiment = "Neutral"
            if any(kw in title_lo for kw in pos_kw):
                if any(title_lo.startswith(p) or f" {p}" in title_lo for p in neg_prefix):
                    sentiment = "Negative"; score -= 1
                else:
                    sentiment = "Positive"; score += 1
            elif any(kw in title_lo for kw in neg_kw):
                sentiment = "Negative"; score -= 1
            news_type = _classify_news(raw_title)
            analyzed.append({
                "title":        raw_title,
                "link":         n.get("link", "#"),
                "sentiment":    sentiment,
                "pub_date_raw": "",
                "news_type":    news_type,
            })
        return score * 2.0, analyzed
    except Exception:
        return 0.0, []


# ── 유틸 ─────────────────────────────────────────────────────────────────────
TICKER_NAME_MAP = {
    "AAPL":"Apple","MSFT":"Microsoft","GOOGL":"Alphabet","GOOG":"Alphabet",
    "META":"Meta","AMZN":"Amazon","NVDA":"NVIDIA","TSLA":"Tesla",
    "AMD":"AMD","INTC":"Intel","QCOM":"Qualcomm","AVGO":"Broadcom",
    "MU":"Micron","SOXX":"반도체 ETF","SMH":"반도체 ETF",
    "AMAT":"Applied Materials","LRCX":"Lam Research","ASML":"ASML",
    "TSM":"TSMC","ARM":"ARM Holdings","KLAC":"KLA Corp","MRVL":"Marvell","TXN":"Texas Instruments",
    "JPM":"JPMorgan","BAC":"Bank of America","GS":"Goldman Sachs",
    "MS":"Morgan Stanley","WFC":"Wells Fargo","V":"Visa","MA":"Mastercard",
    "BLK":"BlackRock","C":"Citigroup","SCHW":"Charles Schwab",
    "AXP":"American Express","COF":"Capital One","PYPL":"PayPal","SQ":"Block","COIN":"Coinbase",
    "XOM":"Exxon Mobil","CVX":"Chevron","COP":"ConocoPhillips","SLB":"Schlumberger","EOG":"EOG Resources",
    "JNJ":"J&J","UNH":"UnitedHealth","PFE":"Pfizer","MRK":"Merck",
    "ABBV":"AbbVie","LLY":"Eli Lilly","TMO":"Thermo Fisher",
    "AMGN":"Amgen","GILD":"Gilead","MRNA":"Moderna","REGN":"Regeneron","VRTX":"Vertex",
    "XLK":"기술주 ETF","XLE":"에너지 ETF","XLF":"금융 ETF","XLV":"헬스케어 ETF",
    "XLP":"필수소비재 ETF","XLY":"임의소비재 ETF","XLI":"산업재 ETF","XLB":"소재 ETF",
    "XLU":"유틸리티 ETF","XLRE":"부동산 ETF","XLC":"통신 ETF",
    "QQQ":"나스닥 ETF","SPY":"S&P500 ETF","IWM":"러셀2000 ETF","GLD":"금 ETF",
    "RIVN":"Rivian","LCID":"Lucid","NIO":"NIO","F":"Ford","GM":"GM",
    "HD":"Home Depot","NKE":"Nike","ABNB":"Airbnb",
    "PG":"P&G","KO":"Coca-Cola","WMT":"Walmart","COST":"Costco",
    "PEP":"PepsiCo","MCD":"McDonald's","PM":"Philip Morris","MO":"Altria",
    "NEE":"NextEra Energy","DUK":"Duke Energy","SO":"Southern Company",
    "FCX":"Freeport-McMoRan","NEM":"Newmont","LIN":"Linde",
    "CAT":"Caterpillar","DE":"John Deere","BA":"Boeing","GE":"GE","UPS":"UPS",
    "RTX":"Raytheon","HON":"Honeywell","LMT":"Lockheed Martin","FDX":"FedEx",
    "AMT":"American Tower","PLD":"Prologis","EQIX":"Equinix",
    "NFLX":"Netflix","DIS":"Disney","VZ":"Verizon","T":"AT&T",
    "CMCSA":"Comcast","SNAP":"Snap","SPOT":"Spotify","LIT":"리튬 ETF","ARKK":"ARK ETF",

    # ── 양자컴퓨팅
    "IONQ":"IonQ","RGTI":"Rigetti Computing","QUBT":"Quantum Computing Inc",
    "QBTS":"D-Wave Quantum","QTUM":"Defiance Quantum ETF",

    # ── AI 인프라 / 데이터센터
    "VRT":"Vertiv Holdings","SMCI":"Super Micro Computer",
    "DELL":"Dell Technologies","HPE":"HP Enterprise",
    "CDNS":"Cadence Design","SNPS":"Synopsys","KEYS":"Keysight",
    "AEHR":"Aehr Test Systems","ONTO":"Onto Innovation",

    # ── 우주·방산
    "RKLB":"Rocket Lab","SPCE":"Virgin Galactic","ASTS":"AST SpaceMobile",
    "LUNR":"Intuitive Machines","RDW":"Redwire","KTOS":"Kratos Defense",
    "JOBY":"Joby Aviation","ACHR":"Archer Aviation",

    # ── 바이오테크 (소형)
    "NVAX":"Novavax","BNTX":"BioNTech","CRSP":"CRISPR Therapeutics",
    "BEAM":"Beam Therapeutics","EDIT":"Editas Medicine","NTLA":"Intellia Therapeutics",
    "HIMS":"Hims & Hers",

    # ── 핀테크·크립토
    "HOOD":"Robinhood","MSTR":"MicroStrategy","MARA":"Marathon Digital",
    "RIOT":"Riot Platforms","CLSK":"CleanSpark","HUT":"Hut 8",
    "SOFI":"SoFi Technologies","AFRM":"Affirm","UPST":"Upstart",

    # ── 청정에너지·원자력
    "OKLO":"Oklo","SMR":"NuScale Power","BWXT":"BWX Technologies",
    "CCJ":"Cameco","UEC":"Uranium Energy","UUUU":"Energy Fuels",
    "PLUG":"Plug Power","FCEL":"FuelCell Energy","BE":"Bloom Energy",

    # ── 자율주행·로보틱스
    "LAZR":"Luminar Technologies","MBLY":"Mobileye",

    # ── 소형 성장주
    "CELH":"Celsius Holdings","DKNG":"DraftKings","OPEN":"Opendoor",
    "Z":"Zillow","AI":"C3.ai","PATH":"UiPath","S":"SentinelOne",
    "CRWD":"CrowdStrike","ZS":"Zscaler","DDOG":"Datadog","NET":"Cloudflare",
    "MDB":"MongoDB","GTLB":"GitLab","U":"Unity Software","RBLX":"Roblox",

    # ── 금융 SaaS / 기업용 소프트웨어
    "INTU":"Intuit","NOW":"ServiceNow","WDAY":"Workday","HUBS":"HubSpot",
    "VEEV":"Veeva Systems","TEAM":"Atlassian","ZM":"Zoom","DOCU":"DocuSign",
    "BOX":"Box","OKTA":"Okta",

    # ── 전통 대형주
    "BRK-B":"Berkshire Hathaway","UNP":"Union Pacific","CSX":"CSX",
    "WM":"Waste Management","ECL":"Ecolab","APH":"Amphenol",
    "ITW":"Illinois Tool Works","PH":"Parker-Hannifin",
    "GWW":"W.W. Grainger","ODFL":"Old Dominion Freight",

    # ── 헬스케어
    "ISRG":"Intuitive Surgical","SYK":"Stryker","BSX":"Boston Scientific",
    "EW":"Edwards Lifesciences","RMD":"ResMed","DXCM":"DexCom",
    "PODD":"Insulet","HOLX":"Hologic","IDXX":"IDEXX Laboratories",

    # ── 소비재
    "LULU":"Lululemon","RH":"RH","BURL":"Burlington","ROST":"Ross Stores",
    "DG":"Dollar General","DLTR":"Dollar Tree","SFM":"Sprouts Farmers",
    "ELF":"e.l.f. Beauty",

    # ── 에너지
    "DVN":"Devon Energy","FANG":"Diamondback Energy","OXY":"Occidental",
    "MRO":"Marathon Oil","BKR":"Baker Hughes","NOV":"NOV Inc",

    # ── 리츠
    "WELL":"Welltower","DLR":"Digital Realty","PSA":"Public Storage",
    "EXR":"Extra Space Storage","AVB":"AvalonBay",
}

def search_tickers(query):
    if not query or len(query) < 1: return []
    q = query.upper().strip()
    results = []; seen = set()

    def _add(ticker, name, priority):
        if ticker in seen: return
        seen.add(ticker)
        sec = ETF_MAP.get(ticker, "Unknown")
        cfg = SECTOR_CONFIG.get(sec, SECTOR_CONFIG["Unknown"])
        results.append({
            "ticker": ticker, "name": name or TICKER_NAME_MAP.get(ticker, ticker),
            "sector": sec, "sector_label": cfg["label"],
            "sector_icon": cfg["icon"], "priority": priority,
        })

    # 1순위: ETF_MAP 직접 일치
    if q in ETF_MAP: _add(q, TICKER_NAME_MAP.get(q, q), 0)
    # 2순위: 티커 앞글자 일치
    for t in ETF_MAP:
        if t.startswith(q) and t != q: _add(t, TICKER_NAME_MAP.get(t, t), 1)
    # 3순위: 티커 부분 일치
    for t in ETF_MAP:
        if q in t and not t.startswith(q): _add(t, TICKER_NAME_MAP.get(t, t), 2)
    # 4순위: 종목명 검색 (한글/영문)
    q_lower = query.lower()
    for t, name in TICKER_NAME_MAP.items():
        if q_lower in name.lower() and t not in seen: _add(t, name, 3)

    results.sort(key=lambda x: (x["priority"], x["ticker"]))
    local_hits = results[:8]

    # 5순위: yfinance 실시간 검색 (로컬에 없을 때)
    if len(local_hits) == 0 and len(q) >= 1:
        try:
            import yfinance as yf
            # 티커로 직접 시도
            ticker_candidate = q.upper()
            info = yf.Ticker(ticker_candidate).info
            long_name = info.get("longName") or info.get("shortName") or ticker_candidate
            if long_name and long_name != ticker_candidate:
                sec = SECTOR_MAP.get(info.get("sector", "Unknown"), "Unknown")
                cfg = SECTOR_CONFIG.get(sec, SECTOR_CONFIG["Unknown"])
                local_hits = [{
                    "ticker": ticker_candidate,
                    "name": long_name,
                    "sector": sec,
                    "sector_label": cfg["label"],
                    "sector_icon": cfg["icon"],
                    "priority": 4,
                }]
        except Exception:
            pass

    return local_hits[:8]

def get_signal(wr):
    if wr >= 60:   return "매수 우위",  "badge-green",  "#059669"
    elif wr >= 45: return "중립 관망",  "badge-yellow", "#D97706"
    else:          return "리스크 경고","badge-red",    "#DC2626"

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

def corr_color(corr, direction):
    aligned = (corr > 0 and direction == 1) or (corr < 0 and direction == -1)
    if abs(corr) < 0.15: return "#9CA3AF"
    return "#059669" if aligned else "#DC2626"


# ══════════════════════════════════════════════════════════════════════════════
# ── LEVEL 1: 직관 지표 ────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_fear_greed():
    """
    Lv.1 — 복합 공포·탐욕 지수 (0~100)
    VIX 50% + 나스닥 모멘텀 30% + 달러 강세 20% 가중 합산.
    """
    try:
        # 1. VIX (공포 지수) — 낮을수록 탐욕
        _, vix = get_z_and_price("^VIX")
        vix_score = max(5, min(95, 100 - (vix / 40 * 100))) if vix > 0 else 50

        # 2. 나스닥 모멘텀 — 20일 수익률 기반
        #    양수(상승 추세) = 탐욕, 음수(하락 추세) = 공포
        try:
            raw_qqq = yf.download("QQQ", period="2mo", interval="1d",
                                  progress=False, timeout=10)
            closes_qqq = _extract_close(raw_qqq).dropna()
            if len(closes_qqq) >= 21:
                mom = float((closes_qqq.iloc[-1] / closes_qqq.iloc[-21] - 1) * 100)
                # +10% 이상 → 탐욕(90), -10% 이하 → 공포(10)
                qqq_score = max(5, min(95, 50 + mom * 4))
            else:
                qqq_score = 50
        except Exception:
            qqq_score = 50

        # 3. 달러 강세 — 달러 강세 = 위험자산 회피 = 공포
        #    달러 약세 = 위험자산 선호 = 탐욕
        try:
            dxy_z, _ = get_z_and_price("DX-Y.NYB")
            # Z > 0 (달러 강세) → 공포 방향, Z < 0 (달러 약세) → 탐욕 방향
            dxy_score = max(5, min(95, 50 - dxy_z * 15))
        except Exception:
            dxy_score = 50

        # 가중 합산
        score = round(vix_score * 0.5 + qqq_score * 0.3 + dxy_score * 0.2, 0)
        score = int(max(5, min(95, score)))

        if score >= 75:   label, clr = "탐욕",    "#059669"
        elif score >= 55: label, clr = "낙관",    "#10B981"
        elif score >= 45: label, clr = "중립",    "#D97706"
        elif score >= 25: label, clr = "공포",    "#EF4444"
        else:             label, clr = "극도공포", "#DC2626"

        return score, label, clr
    except Exception:
        return 50, "중립", "#D97706"


def get_portfolio_lv1(portfolio, batch_data=None, invest_mode="단기"):
    """
    Lv.1 — 포트폴리오 전체 가중 평균 승률 + 날씨 신호등
    batch_data: get_batch_portfolio_data() 결과를 넘기면 중복 API 호출 없이 재사용.
    반환: (weighted_win, weather_icon, weather_label, weather_clr, summary_text)
    """
    if not portfolio:
        return 50.0, "⛅", "데이터 없음", "#D97706", "종목을 추가해주세요."

    total_w = 0.0
    weighted_win = 0.0
    worst_ticker = None
    worst_win = 100.0

    for stock in portfolio:
        try:
            # 배치 데이터가 있으면 재사용, 없으면 개별 호출
            if batch_data and stock["ticker"] in batch_data:
                d   = batch_data[stock["ticker"]]
                win = d.get("win", 50.0)
            else:
                zs, _  = get_z_and_price(stock["ticker"])
                _, _, inds = get_sector_analysis(stock["ticker"])
                nb, items  = get_korean_news(stock["ticker"])
                win, _ = calc_win_rate(zs, inds, nb,
                                       stock_ticker=stock["ticker"],
                                       news_items=items)
            w = stock.get("weight", 10)
            weighted_win += win * w
            total_w      += w
            if win < worst_win:
                worst_win    = win
                worst_ticker = stock["ticker"]
        except Exception:
            continue

    if total_w == 0:
        return 50.0, "⛅", "계산 불가", "#D97706", "데이터를 불러올 수 없습니다."

    avg_win = round(weighted_win / total_w, 1)

    if avg_win >= 65:
        icon, label, clr = "☀️", "맑음",   "#059669"
        summary = "포트폴리오 전반이 우호적입니다. 비중을 유지하세요."
    elif avg_win >= 50:
        icon, label, clr = "⛅", "구름",   "#D97706"
        summary = "전반적으로 중립입니다."
        if worst_ticker:
            summary += f" {worst_ticker}를 주시하세요."
    else:
        icon, label, clr = "🌧️", "비",    "#DC2626"
        summary = "리스크 경고 구간입니다."
        if worst_ticker:
            summary += f" {worst_ticker}({worst_win:.0f}%)가 가장 취약합니다."

    return avg_win, icon, label, clr, summary


# ══════════════════════════════════════════════════════════════════════════════
# ── LEVEL 3: 심화 확률 모델 ───────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def calc_var(ticker, confidence=0.95, horizon_days=1):
    """
    Lv.3 — VaR (Value at Risk) 개별 종목
    """
    try:
        raw    = yf.download(ticker, period="1y", interval="1d", progress=False, timeout=10)
        closes = _extract_close(raw).dropna()
        if len(closes) < 30: return None
        returns = closes.pct_change().dropna()
        var     = float(np.percentile(returns, (1 - confidence) * 100)) * np.sqrt(horizon_days) * 100
        return round(var, 2)
    except Exception:
        return None


def calc_portfolio_var(portfolio, confidence=0.95):
    """
    Lv.3 — 포트폴리오 전체 VaR
    각 종목의 비중을 반영한 가중 합산 수익률로 VaR 계산.
    반환: {
        "var_1d":  1일 VaR (%),
        "var_5d":  5일 VaR (%),
        "amount_1d": 1일 예상 최대 손실액 (총 평가금액 기준),
        "total_value": 총 평가금액 ($),
    }
    """
    try:
        if not portfolio:
            return None

        # 각 종목 수익률 시계열 수집
        returns_list = []
        weights_list = []
        total_value  = 0.0

        for stock in portfolio:
            try:
                raw    = yf.download(stock["ticker"], period="1y", interval="1d",
                                     progress=False, timeout=10)
                closes = _extract_close(raw).dropna()
                if len(closes) < 30:
                    continue
                ret = closes.pct_change().dropna()
                returns_list.append(ret)

                # 평가금액 = 현재가 × 수량, 수량 없으면 비중으로 대체
                cur_price = float(closes.iloc[-1])
                shares    = stock.get("shares", 0)
                if shares > 0:
                    value = cur_price * shares
                    total_value += value
                else:
                    value = float(stock.get("weight", 10))  # 비중 자체를 가중치로
                weights_list.append(value)
            except Exception:
                continue

        if not returns_list or len(weights_list) == 0:
            return None

        # 공통 날짜 맞추기
        import pandas as pd
        df = pd.concat(returns_list, axis=1).dropna()
        if len(df) < 30:
            return None

        # 비중 계산
        w = np.array(weights_list[:df.shape[1]])
        w = w / w.sum()

        # 포트폴리오 일별 수익률
        port_ret = df.values @ w

        # VaR 계산
        var_1d  = round(float(np.percentile(port_ret, (1 - confidence) * 100)) * 100, 2)
        var_7d  = round(var_1d * np.sqrt(7),   2)
        var_1mo = round(var_1d * np.sqrt(21),  2)
        var_1y  = round(var_1d * np.sqrt(252), 2)
        amount_7d = round(total_value * abs(var_7d) / 100, 0)

        return {
            "var_1d":       var_1d,
            "var_7d":       var_7d,
            "var_1mo":      var_1mo,
            "var_1y":       var_1y,
            "amount_7d":    amount_7d,
            "total_value":  round(total_value, 0),
            "confidence":   int(confidence * 100),
        }
    except Exception:
        return None


@st.cache_data(ttl=600)
def calc_monte_carlo(ticker, days=30, simulations=1000):
    """
    Lv.3 — 몬테카를로 시뮬레이션
    과거 변동성 기반으로 simulations개의 가상 가격 경로 생성.
    반환: {
        "current": 현재가,
        "p10": 하위 10% 가격 (비관),
        "p50": 중앙값 (중립),
        "p90": 상위 90% 가격 (낙관),
        "prob_up": 상승 확률(%),
        "max_gain": 시뮬레이션 중 최대 수익률(%),
        "max_loss": 시뮬레이션 중 최대 손실률(%),
        "days": 기간(일),
        "periods": 기간별 결과 딕셔너리 (1달/6개월/1년/5년),
    }
    """
    try:
        raw    = yf.download(ticker, period="1y", interval="1d", progress=False, timeout=10)
        closes = _extract_close(raw).dropna()
        if len(closes) < 30: return None

        current = float(closes.iloc[-1])
        returns = closes.pct_change().dropna()
        mu      = float(returns.mean())
        sigma   = float(returns.std())

        np.random.seed(42)

        # 기간별 설정 (거래일 기준)
        period_map = {
            "1달":   21,
            "6개월": 126,
            "1년":   252,
            "5년":   1260,
        }

        periods_result = {}
        for label, d in period_map.items():
            rand_ret     = np.random.normal(mu, sigma, (simulations, d))
            price_paths  = current * np.cumprod(1 + rand_ret, axis=1)
            final_prices = price_paths[:, -1]

            # 최종 가격 기준
            p10     = round(float(np.percentile(final_prices, 10)), 2)
            p50     = round(float(np.percentile(final_prices, 50)), 2)
            p90     = round(float(np.percentile(final_prices, 90)), 2)
            prob_up = round(float((final_prices > current).mean() * 100), 1)

            # 경로 중 최대 수익·최대 손실 (경로 내 최고점·최저점 기준)
            path_highs = price_paths.max(axis=1)   # 각 경로의 최고가
            path_lows  = price_paths.min(axis=1)   # 각 경로의 최저가
            max_gain   = round(float((path_highs.max() - current) / current * 100), 1)
            max_loss   = round(float((path_lows.min()  - current) / current * 100), 1)

            # 95% 신뢰구간 기준 현실적 최대수익·최대손실
            gain_p95 = round(float((np.percentile(path_highs, 95) - current) / current * 100), 1)
            loss_p95 = round(float((np.percentile(path_lows,   5) - current) / current * 100), 1)

            periods_result[label] = {
                "days":      d,
                "p10":       p10,
                "p50":       p50,
                "p90":       p90,
                "prob_up":   prob_up,
                "max_gain":  max_gain,    # 시뮬레이션 전체 최대 수익
                "max_loss":  max_loss,    # 시뮬레이션 전체 최대 손실
                "gain_p95":  gain_p95,    # 95% 신뢰구간 최대 수익 (더 현실적)
                "loss_p95":  loss_p95,    # 95% 신뢰구간 최대 손실
                "ret_p10":   round((p10 - current) / current * 100, 1),
                "ret_p50":   round((p50 - current) / current * 100, 1),
                "ret_p90":   round((p90 - current) / current * 100, 1),
            }

        # 기본값 (1달 기준, 하위호환)
        base = periods_result["1달"]
        return {
            "current":  current,
            "p10":      base["p10"],
            "p50":      base["p50"],
            "p90":      base["p90"],
            "prob_up":  base["prob_up"],
            "max_gain": base["max_gain"],
            "max_loss": base["max_loss"],
            "days":     days,
            "periods":  periods_result,
        }
    except Exception:
        return None


@st.cache_data(ttl=600)
def calc_bayesian_update(prior_win, indicators, new_event_direction):
    """
    Lv.3 — 간이 베이지안 업데이트
    새로운 매크로 이벤트(긍정/부정)가 발생했을 때 사후 승률 추정.
    new_event_direction: +1(호재) or -1(악재)
    """
    try:
        # 단순화: 이벤트 강도에 따라 사전 승률을 베이즈적으로 조정
        # P(up|event) = P(event|up)*P(up) / P(event)
        # 여기서는 근사적으로 likelihood ratio 방식 사용
        prior    = prior_win / 100.0
        # 호재 이벤트: 상승 가능성 likelihood 1.4배, 하락 가능성 0.7배
        if new_event_direction == +1:
            likelihood_up   = 1.4
            likelihood_down = 0.7
        else:
            likelihood_up   = 0.7
            likelihood_down = 1.4

        posterior_num = likelihood_up * prior
        posterior_den = likelihood_up * prior + likelihood_down * (1 - prior)
        posterior     = posterior_num / posterior_den if posterior_den > 0 else prior

        return round(posterior * 100, 1)
    except Exception:
        return prior_win


# ══════════════════════════════════════════════════════════════════════════════
# ── 추가 기능 1: 포트폴리오 종목 간 상관계수 행렬 ────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def get_portfolio_correlation_matrix(tickers_tuple):
    tickers = list(tickers_tuple)
    if len(tickers) < 2:
        return None, []
    try:
        returns_map = {}
        for t in tickers:
            try:
                raw = yf.download(t, period="3mo", interval="1d", progress=False, timeout=10)
                cl  = _extract_close(raw).dropna()
                if len(cl) >= 20:
                    returns_map[t] = cl.pct_change().dropna()
            except Exception:
                pass
        if len(returns_map) < 2:
            return None, []
        df = pd.concat(returns_map, axis=1).dropna()
        if len(df) < 15:
            return None, []
        corr_matrix = df.corr().round(3)
        warnings = []
        cols = corr_matrix.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                r = corr_matrix.iloc[i, j]
                if abs(r) >= 0.75:
                    warnings.append({"t1": cols[i], "t2": cols[j], "r": round(r, 3),
                                     "type": "동조" if r > 0 else "역방향"})
        warnings.sort(key=lambda x: -abs(x["r"]))
        return corr_matrix, warnings
    except Exception:
        return None, []


# ══════════════════════════════════════════════════════════════════════════════
# ── 추가 기능 2: 포트폴리오 전체 수익률 시뮬레이션 ────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=900)
def simulate_portfolio_history(portfolio_snapshot):
    try:
        portfolio = list(portfolio_snapshot)
        if not portfolio:
            return None
        total_w = sum(w for _, w in portfolio)
        if total_w == 0:
            return None
        stock_series = {}
        for ticker, _ in portfolio:
            try:
                raw = yf.download(ticker, period="6mo", interval="1d", progress=False, timeout=10)
                cl  = _extract_close(raw).dropna()
                if len(cl) >= 20:
                    stock_series[ticker] = cl
            except Exception:
                pass
        if not stock_series:
            return None
        df_all = pd.concat(stock_series, axis=1).dropna()
        if len(df_all) < 20:
            return None
        valid_tickers = df_all.columns.tolist()
        weight_map = {}
        for ticker, weight in portfolio:
            if ticker in valid_tickers:
                weight_map[ticker] = weight
        total_valid_w = sum(weight_map.values())
        if total_valid_w == 0:
            return None
        for t in weight_map:
            weight_map[t] /= total_valid_w
        daily_rets = df_all.pct_change().dropna()
        port_ret = pd.Series(0.0, index=daily_rets.index)
        for t, w in weight_map.items():
            port_ret += daily_rets[t] * w
        cum_ret = (1 + port_ret).cumprod() - 1
        try:
            spy_raw = yf.download("SPY", period="6mo", interval="1d", progress=False, timeout=10)
            spy_cl  = _extract_close(spy_raw).dropna()
            spy_common = spy_cl.reindex(cum_ret.index).dropna()
            spy_ret = (spy_common / spy_common.iloc[0] - 1) * 100
        except Exception:
            spy_ret = pd.Series(0.0, index=cum_ret.index)
        port_pct = (cum_ret * 100).round(2)
        cumulative = (1 + port_ret).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = round(float(drawdown.min() * 100), 2)
        stock_rets = {}
        for t in valid_tickers:
            first = float(df_all[t].iloc[0])
            last  = float(df_all[t].iloc[-1])
            if first > 0:
                stock_rets[t] = round((last / first - 1) * 100, 2)
        best_stock  = max(stock_rets.items(), key=lambda x: x[1]) if stock_rets else ("—", 0)
        worst_stock = min(stock_rets.items(), key=lambda x: x[1]) if stock_rets else ("—", 0)
        dates = [str(d)[:10] for d in port_pct.index.tolist()]
        spy_aligned = spy_ret.reindex(port_pct.index).ffill().fillna(0).round(2).tolist()
        return {
            "dates": dates,
            "portfolio_returns": port_pct.tolist(),
            "spy_returns": spy_aligned,
            "final_ret": round(float(port_pct.iloc[-1]), 2),
            "spy_final_ret": round(float(spy_ret.iloc[-1]) if len(spy_ret) > 0 else 0, 2),
            "max_drawdown": max_drawdown,
            "best_stock": best_stock,
            "worst_stock": worst_stock,
            "stock_rets": stock_rets,
        }
    except Exception:
        return None




# ── 섹터 대비 상대 모멘텀 ────────────────────────────────────────────────────
_SECTOR_ETF_MAP = {
    "Technology": "XLK", "Semiconductor": "SOXX",
    "Consumer Cyclical": "XLY", "Consumer Defensive": "XLP",
    "Financial Services": "XLF", "Healthcare": "XLV",
    "Industrials": "XLI", "Real Estate": "XLRE",
    "Utilities": "XLU", "Basic Materials": "XLB",
    "Communication Services": "XLC", "Energy": "XLE",
    "Unknown": "SPY",
}

@st.cache_data(ttl=600)
def get_relative_momentum(ticker, sector="Unknown"):
    """
    섹터 ETF 대비 상대 모멘텀.
    종목이 섹터보다 강하게 오르면 양수, 약하면 음수.
    반환: {
        "rel_20": 20일 상대 수익률(%),
        "rel_60": 60일 상대 수익률(%),
        "sector_etf": 비교 ETF,
        "label": "섹터 아웃퍼폼" / "섹터 언더퍼폼" / "비슷",
        "score": -10 ~ +10점 (승률 보조 참고용)
    }
    """
    try:
        etf = _SECTOR_ETF_MAP.get(sector, "SPY")

        # 종목 수익률
        raw_stock = yf.download(ticker, period="3mo", interval="1d",
                                progress=False, timeout=10)
        stock_cl = _extract_close(raw_stock).dropna()
        if len(stock_cl) < 21:
            return {"rel_20": 0.0, "rel_60": 0.0, "sector_etf": etf,
                    "label": "데이터 부족", "score": 0.0}

        # ETF 수익률
        raw_etf = yf.download(etf, period="3mo", interval="1d",
                              progress=False, timeout=10)
        etf_cl = _extract_close(raw_etf).dropna()
        if len(etf_cl) < 21:
            return {"rel_20": 0.0, "rel_60": 0.0, "sector_etf": etf,
                    "label": "데이터 부족", "score": 0.0}

        stock_20 = float((stock_cl.iloc[-1] / stock_cl.iloc[-21] - 1) * 100)
        etf_20   = float((etf_cl.iloc[-1]   / etf_cl.iloc[-21]   - 1) * 100)
        rel_20   = round(stock_20 - etf_20, 1)

        stock_60 = float((stock_cl.iloc[-1] / stock_cl.iloc[0] - 1) * 100) if len(stock_cl) >= 60 else stock_20
        etf_60   = float((etf_cl.iloc[-1]   / etf_cl.iloc[0]   - 1) * 100) if len(etf_cl)   >= 60 else etf_20
        rel_60   = round(stock_60 - etf_60, 1)

        # 라벨 결정 (20일 기준)
        if rel_20 > 5:    label = f"섹터({etf}) 대비 강세 💪"
        elif rel_20 > 1:  label = f"섹터({etf}) 소폭 아웃퍼폼"
        elif rel_20 < -5: label = f"섹터({etf}) 대비 약세 ⚠"
        elif rel_20 < -1: label = f"섹터({etf}) 소폭 언더퍼폼"
        else:             label = f"섹터({etf})와 비슷"

        # 점수: -10 ~ +10 (참고용, 승률에 직접 반영하지 않음)
        score = round(max(-10.0, min(10.0, rel_20 * 0.5 + rel_60 * 0.2)), 1)

        return {
            "rel_20":     rel_20,
            "rel_60":     rel_60,
            "sector_etf": etf,
            "label":      label,
            "score":      score,
        }
    except Exception:
        return {"rel_20": 0.0, "rel_60": 0.0,
                "sector_etf": "SPY", "label": "계산 불가", "score": 0.0}

# ══════════════════════════════════════════════════════════════════════════════
# ── 배치 로더: 메인 대시보드용 종목 일괄 계산 ─────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def get_batch_portfolio_data(tickers_tuple, invest_mode="단기"):
    """
    메인 대시보드용 배치 로더.
    종목 리스트를 받아 z·가격·섹터분석·승률을 한 번에 캐시 조회.
    tickers_tuple: tuple of ticker strings (캐시 호환)
    반환: {ticker: {"z", "price", "sk", "cfg", "inds", "win", "breakdown"}}
    """
    result = {}
    for ticker in tickers_tuple:
        try:
            zs, price      = get_z_and_price(ticker)
            sk, cfg, inds  = get_sector_analysis(ticker)
            # 한국어 뉴스로 단일화 (감쇠 적용 가능, 더 정확)
            nb, items      = get_korean_news(ticker)
            win, breakdown = calc_win_rate(
                zs, inds, nb, stock_ticker=ticker, news_items=items,
                invest_mode=invest_mode
            )
            result[ticker] = {
                "z": zs, "price": price,
                "sk": sk, "cfg": cfg, "inds": inds,
                "win": win, "breakdown": breakdown,
            }
        except Exception:
            result[ticker] = {
                "z": 0.0, "price": 0.0,
                "sk": "Unknown",
                "cfg": SECTOR_CONFIG["Unknown"],
                "inds": [],
                "win": 50.0,
                "breakdown": {},
            }
    return result
