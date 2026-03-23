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
            return 0.0, float(data.iloc[-1]) if len(data) > 0 else 0.0
        cur  = float(data.iloc[-1])
        mean = float(data.tail(20).mean())
        std  = float(data.tail(20).std())
        z    = round((cur - mean) / std, 2) if std > 0 else 0.0
        return z, round(cur, 2)
    except Exception:
        return 0.0, 0.0


@st.cache_data(ttl=300)
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
    "1일": ("5d",  "5m"),
    "1주": ("5d",  "1h"),
    "1달": ("1mo", "1d"),
    "1년": ("1y",  "1d"),
}

@st.cache_data(ttl=120)
def get_chart_data(ticker, period_key="1달"):
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
@st.cache_data(ttl=300)
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
    """Percentile → 승률 보정 (-12 ~ +12점)"""
    pct   = get_percentile(ticker)
    score = round((50 - pct) / 50 * 12, 1)
    return score, pct


# ── 핵심 승률 계산 (전면 개선) ────────────────────────────────────────────────
def calc_win_rate(z_stock, indicators, news_bonus, stock_ticker=None, news_items=None):
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
        except:
            dyn_w   = None
            macro_z = get_weighted_z(indicators)
    else:
        dyn_w   = None
        macro_z = get_weighted_z(indicators)
    macro_score = round(macro_z * 15, 1)

    # 3. 뉴스 (시간 감쇠)
    if news_items:
        news_adj = round(sum(
            _news_decay(
                2.5 if n["sentiment"]=="Positive" else -2.5 if n["sentiment"]=="Negative" else 0.0,
                n.get("pub_date_raw",""),
                n.get("title","")        # ← 지속성 분류에 사용
            ) for n in news_items
        ), 1)
    else:
        news_adj = round(news_bonus * 0.5, 1)

    # 4. 합산
    total = 50.0 + position_score + macro_score + news_adj
    final = round(max(5.0, min(95.0, total)), 1)

    return final, {
        "base":            50.0,
        "position_score":  position_score,
        "percentile":      percentile,
        "macro_score":     macro_score,
        "macro_z":         macro_z,
        "news_bonus":      news_adj,
        "news_raw":        news_bonus,
        "total_raw":       round(total, 1),
        "final":           final,
        "dynamic_weights": dyn_w,
        "z_penalty":       position_score,   # 기존 호환
        "explain": (
            f"기본(50) {'+' if position_score>=0 else ''}{position_score}"
            f"(가격{percentile:.0f}%ile) "
            f"{'+' if macro_score>=0 else ''}{macro_score}(거시Z동적) "
            f"{'+' if news_adj>=0 else ''}{news_adj}(뉴스감쇠) = {final}%"
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
    pos_kw = ["buy","growth","up","positive","surge","profit","beat","record","strong",
              "upgrade","bullish","soars","rises","rally","outperform"]
    neg_kw = ["sell","fall","down","negative","drop","loss","risk","crisis","miss","weak",
              "downgrade","bearish","cut","slump","plunge","recall","fraud"]
    try:
        news_list = yf.Ticker(ticker).news[:5]
        score = 0; analyzed = []
        for n in news_list:
            raw_title = n.get("title","")
            title     = raw_title.lower()
            if any(w in title for w in pos_kw):   score += 1; sentiment = "Positive"
            elif any(w in title for w in neg_kw): score -= 1; sentiment = "Negative"
            else:                                 sentiment = "Neutral"
            news_type = _classify_news(raw_title)
            analyzed.append({
                "title":         raw_title,
                "link":          n.get("link","#"),
                "sentiment":     sentiment,
                "pub_date_raw":  "",
                "news_type":     news_type,
            })
        return score * 2.5, analyzed
    except:
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
}

def search_tickers(query):
    if not query or len(query) < 1: return []
    q = query.upper().strip()
    results = []; seen = set()
    def _add(ticker, priority):
        if ticker in seen: return
        seen.add(ticker)
        sec = ETF_MAP.get(ticker, "Unknown")
        cfg = SECTOR_CONFIG.get(sec, SECTOR_CONFIG["Unknown"])
        results.append({
            "ticker": ticker, "name": TICKER_NAME_MAP.get(ticker, ticker),
            "sector": sec, "sector_label": cfg["label"],
            "sector_icon": cfg["icon"], "priority": priority,
        })
    if q in ETF_MAP: _add(q, 0)
    for t in ETF_MAP:
        if t.startswith(q) and t != q: _add(t, 1)
    for t in ETF_MAP:
        if q in t and not t.startswith(q): _add(t, 2)
    for t, name in TICKER_NAME_MAP.items():
        if q in name.upper() and t not in seen: _add(t, 3)
    results.sort(key=lambda x: (x["priority"], x["ticker"]))
    return results[:8]

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
