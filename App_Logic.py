import yfinance as yf
import pandas as pd
import numpy as np

# 섹터 및 ETF 설정 (기존 코드에서 설정 부분만 가져옴)
SECTOR_CONFIG = {
    "Energy": {"icon":"🛢️","color":"#D97706","label":"에너지","indicators":[{"name":"WTI 유가","ticker":"CL=F","weight":+14,"desc":"매출·마진 직결"},{"name":"달러 인덱스","ticker":"DX-Y.NYB","weight":-5,"desc":"달러 강세=원자재 하락"}]},
    "Technology": {"icon":"💻","color":"#2563EB","label":"기술주","indicators":[{"name":"10년물 금리","ticker":"^TNX","weight":-14,"desc":"할인율 영향"},{"name":"나스닥(QQQ)","ticker":"QQQ", "weight":+10,"desc":"섹터 모멘텀"}]},
    "Semiconductor": {"icon":"🔬","color":"#0891B2","label":"반도체","indicators":[{"name":"반도체(SOXX)","ticker":"SOXX","weight":14,"desc":"재고 조정 신호"},{"name":"10년물 금리","ticker":"^TNX","weight":-10,"desc":"설비투자 비용"}]},
    "Consumer Cyclical": {"icon":"🛍️","color":"#DC2626","label":"경기소비재/EV","indicators":[{"name":"10년물 금리","ticker":"^TNX","weight":-11,"desc":"할부금리 직결"},{"name":"리튬ETF(LIT)","ticker":"LIT","weight":7,"desc":"배터리 원가"}]},
    "Consumer Defensive": {"icon":"🛒","color":"#059669","label":"필수소비재","indicators":[{"name":"CPI 인플레","ticker":"RINF","weight":-9,"desc":"구매력 하락"},{"name":"VIX 공포","ticker":"^VIX","weight":+6,"desc":"안전자산 수요"}]},
    "Financial Services": {"icon":"🏦","color":"#7C3AED","label":"금융주","indicators":[{"name":"10년물 금리","ticker":"^TNX","weight":+13,"desc":"예대마진 확대"},{"name":"VIX 공포","ticker":"^VIX","weight":-9,"desc":"금융위기 공포"}]},
    "Healthcare": {"icon":"💊","color":"#0891B2","label":"헬스케어","indicators":[{"name":"바이오(XBI)","ticker":"XBI","weight":8,"desc":"투자심리 지표"},{"name":"VIX 공포","ticker":"^VIX","weight":5,"desc":"방어적 수요"}]},
    "Industrials": {"icon":"🏭","color":"#374151","label":"산업재","indicators":[{"name":"S&P500(SPY)","ticker":"SPY","weight":9,"desc":"경기 확장 수요"},{"name":"구리 선물","ticker":"HG=F","weight":8,"desc":"산업 수요 선행"}]},
    "Real Estate": {"icon":"🏢","color":"#065F46","label":"부동산(REIT)","indicators":[{"name":"10년물 금리","ticker":"^TNX","weight":-15,"desc":"모기지 금리 직격"},{"name":"부동산(XLRE)","ticker":"XLRE","weight":7,"desc":"섹터 수급"}]},
    "Utilities": {"icon":"⚡","color":"#0369A1","label":"유틸리티","indicators":[{"name":"10년물 금리","ticker":"^TNX","weight":-12,"desc":"채권 대비 매력"},{"name":"VIX 공포","ticker":"^VIX","weight":5,"desc":"방어적 자금"}]},
    "Basic Materials": {"icon":"⛏️","color":"#92400E","label":"소재/원자재","indicators":[{"name":"달러 인덱스","ticker":"DX-Y.NYB","weight":-10,"desc":"원자재 가격 상승"},{"name":"구리 선물","ticker":"HG=F","weight":10,"desc":"제조 수요"}]},
    "Communication Services": {"icon":"📡","color":"#1D4ED8","label":"통신/미디어","indicators":[{"name":"나스닥(QQQ)","ticker":"QQQ","weight":10,"desc":"광고·플랫폼 연계"},{"name":"S&P500(SPY)","ticker":"SPY","weight":6,"desc":"경기 수익 직결"}]},
    "Unknown": {"icon":"📊","color":"#6B7280","label":"기타","indicators":[{"name":"S&P500(SPY)","ticker":"SPY","weight":8,"desc":"전체 시장"},{"name":"VIX 공포","ticker":"^VIX","weight":-6,"desc":"공포 수준"}]},
}

ETF_MAP = {"XLE":"Energy","XOM":"Energy","CVX":"Energy","XLK":"Technology","AAPL":"Technology","MSFT":"Technology","NVDA":"Semiconductor","AMD":"Semiconductor","TSLA":"Consumer Cyclical","AMZN":"Consumer Cyclical","XLP":"Consumer Defensive","PG":"Consumer Defensive","XLF":"Financial Services","JPM":"Financial Services","XLV":"Healthcare","JNJ":"Healthcare","XLI":"Industrials","CAT":"Industrials","XLRE":"Real Estate","XLU":"Utilities","XLB":"Basic Materials","XLC":"Communication Services","META":"Communication Services","GOOGL":"Communication Services","SPY":"Unknown","QQQ":"Technology"}
SECTOR_MAP = {"Energy":"Energy","Technology":"Technology","Consumer Cyclical":"Consumer Cyclical","Consumer Defensive":"Consumer Defensive","Financial Services":"Financial Services","Healthcare":"Healthcare","Industrials":"Industrials","Basic Materials":"Basic Materials","Real Estate":"Real Estate","Utilities":"Utilities","Communication Services":"Communication Services"}

def detect_sector(ticker):
    t = ticker.upper().strip()
    if t in ETF_MAP: return ETF_MAP[t]
    try:
        info = yf.Ticker(ticker).info
        return SECTOR_MAP.get(info.get("sector","Unknown"), "Unknown")
    except: return "Unknown"

def get_z_and_price(ticker):
    try:
        raw = yf.download(ticker, period="60d", interval="1d", progress=False)
        if raw.empty: return 0.0, 0.0
        data = raw['Close'].iloc[:,0] if isinstance(raw.columns, pd.MultiIndex) else raw['Close']
        data = data.dropna()
        if len(data) < 21: return 0.0, float(data.iloc[-1])
        cur, mean, std = float(data.iloc[-1]), float(data.tail(20).mean()), float(data.tail(20).std())
        return round((cur-mean)/std, 2) if std != 0 else 0.0, round(cur, 2)
    except: return 0.0, 0.0

def get_sector_analysis(ticker):
    sk = detect_sector(ticker)
    cfg = SECTOR_CONFIG[sk]
    results = []
    for ind in cfg["indicators"]:
        z, price = get_z_and_price(ind["ticker"])
        results.append({**ind, "z":z, "price":price})
    return sk, cfg, results

def get_news(ticker):
    try:
        news_list = yf.Ticker(ticker).news[:5]
        score, analyzed = 0, []
        pos_kw = ['buy','growth','up','positive','surge','profit','beat']
        neg_kw = ['sell','fall','down','negative','drop','loss','risk']
        for n in news_list:
            title = n.get('title','').lower()
            sentiment = "Neutral"
            if any(w in title for w in pos_kw): score += 1; sentiment = "Positive"
            elif any(w in title for w in neg_kw): score -= 1; sentiment = "Negative"
            analyzed.append({"title":n.get('title',''),"link":n.get('link','#'),"sentiment":sentiment})
        return score*2.5, analyzed
    except: return 0.0, []

def calc_win_rate(z_stock, indicators, news_bonus):
    base = 50.0
    z_penalty = round(-(z_stock * 3.0), 1) 
    macro_score = round(sum([ind["z"] * (ind["weight"] / 5.0) for ind in indicators]), 1)
    total = base + z_penalty + macro_score + news_bonus
    final_win = round(max(5.0, min(95.0, total)), 1)
    explain = f"기본(50) {z_penalty:+.1f}(가격) {macro_score:+.1f}(거시) {news_bonus:+.1f}(뉴스) = {final_win}%"
    return final_win, explain

