# engine.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from config import SECTOR_CONFIG, SECTOR_MAP, ETF_MAP

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

@st.cache_data(ttl=3600)
def detect_sector(ticker):
    t = ticker.upper().strip()
    if t in ETF_MAP: return ETF_MAP[t]
    try:
        info = yf.Ticker(ticker).info
        return SECTOR_MAP.get(info.get("sector","Unknown"), "Unknown")
    except: return "Unknown"

@st.cache_data(ttl=300)
def get_z_and_price(ticker):
    try:
        raw = yf.download(ticker, period="60d", interval="1d", progress=False)
        data = _extract_close(raw).dropna()
        if len(data) < 21: return 0.0, float(data.iloc[-1]) if len(data)>0 else 0.0
        cur=float(data.iloc[-1]); mean=float(data.tail(20).mean()); std=float(data.tail(20).std())
        if std==0: return 0.0, round(cur,2)
        return round((cur-mean)/std,2), round(cur,2)
    except: return 0.0, 0.0

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
        raw = yf.download(ticker, period=period, interval=interval, progress=False)
        return _extract_ohlcv(raw)
    except: return pd.DataFrame()

def get_price_stats(df):
    empty = {"max_gain":0,"max_loss":0,"period_ret":0,"volatility":0,"high":0,"low":0}
    if df.empty or "Close" not in df.columns: return empty
    closes = df["Close"].dropna()
    if len(closes) < 2: return empty
    daily_ret = closes.pct_change().dropna()
    max_gain  = float(daily_ret.max()*100)
    max_loss  = float(daily_ret.min()*100)
    period_ret= float((closes.iloc[-1]/closes.iloc[0]-1)*100)
    vol_factor= 252 if len(daily_ret)>20 else 52
    volatility= float(daily_ret.std()*np.sqrt(vol_factor)*100)
    high = float(df["High"].max()) if "High" in df.columns else float(closes.max())
    low  = float(df["Low"].min())  if "Low"  in df.columns else float(closes.min())
    return {"max_gain":round(max_gain,2),"max_loss":round(max_loss,2),
            "period_ret":round(period_ret,2),"volatility":round(volatility,2),
            "high":round(high,2),"low":round(low,2)}

@st.cache_data(ttl=300)
def get_price_history(ticker, period="60d"):
    try:
        raw = yf.download(ticker, period=period, interval="1d", progress=False)
        data = _extract_close(raw).dropna()
        df = data.reset_index(); df.columns=["Date","Close"]
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=300)
def get_sector_analysis(ticker):
    sk=detect_sector(ticker); cfg=SECTOR_CONFIG[sk]
    results=[]
    for ind in cfg["indicators"]:
        z,price=get_z_and_price(ind["ticker"])
        results.append({**ind,"z":z,"price":price})
    return sk, cfg, results

def get_weighted_z(indicators):
    total_w=sum(ind["driver_weight"] for ind in indicators)
    if total_w==0: return 0.0
    return round(sum(ind["z"]*ind["direction"]*ind["driver_weight"] for ind in indicators)/total_w,3)

def calc_win_rate(z_stock, indicators, news_bonus):
    macro_z=get_weighted_z(indicators); macro_score=round(macro_z*15,1)
    z_penalty=round(-z_stock*3.0,1); total=50.0+z_penalty+macro_score+news_bonus
    final=round(max(5.0,min(95.0,total)),1)
    return final, {"base":50.0,"z_penalty":z_penalty,"macro_score":macro_score,
        "macro_z":macro_z,"news_bonus":news_bonus,"total_raw":round(total,1),"final":final,
        "explain":f"기본(50) {'+' if z_penalty>=0 else ''}{z_penalty}(가격위치) {'+' if macro_score>=0 else ''}{macro_score}(거시Z) {'+' if news_bonus>=0 else ''}{news_bonus}(뉴스) = {final}%"}

@st.cache_data(ttl=600)
def get_macro_correlation(stock_ticker, indicators):
    try:
        sh=get_price_history(stock_ticker)
        if sh.empty: return []
        sr=sh.set_index("Date")["Close"].pct_change().dropna()
    except: return []
    results=[]
    for ind in indicators:
        try:
            ih=get_price_history(ind["ticker"])
            if ih.empty: results.append({**ind,"corr":0.0}); continue
            ir=ih.set_index("Date")["Close"].pct_change().dropna()
            common=sr.index.intersection(ir.index)
            if len(common)<10: results.append({**ind,"corr":0.0}); continue
            corr=float(np.corrcoef(sr.loc[common].values,ir.loc[common].values)[0,1])
            results.append({**ind,"corr":round(corr,3)})
        except: results.append({**ind,"corr":0.0})
    return results

@st.cache_data(ttl=600)
def get_korean_news(ticker, stock_name=""):
    pos_kw=["상승","급등","호재","매수","추천","목표가 상향","실적 개선","흑자","성장","수혜","돌파","신고가","강세","긍정","반등","최고","증가","확대","수주","계약","출시","승인"]
    neg_kw=["하락","급락","악재","매도","목표가 하향","실적 부진","적자","우려","리스크","위기","하회","약세","부정","손실","감소","축소","취소","리콜","소송","조사"]
    queries=[]
    if stock_name and stock_name!=ticker: queries.append(stock_name)
    queries.append(f"{ticker} 주가")
    all_news=[]; seen=set()
    for query in queries:
        if len(all_news)>=8: break
        try:
            url=f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=5) as resp: xml_data=resp.read()
            root=ET.fromstring(xml_data)
            for item in root.findall(".//item")[:6]:
                te=item.find("title"); le=item.find("link")
                pe=item.find("pubDate"); se=item.find("source")
                title=te.text.strip() if te is not None else ""
                link=le.text.strip() if le is not None else "#"
                pub=pe.text.strip()[:16] if pe is not None else ""
                src=se.text.strip() if se is not None else "Google News"
                if not title or title in seen: continue
                seen.add(title)
                if any(kw in title for kw in pos_kw): sentiment="Positive"
                elif any(kw in title for kw in neg_kw): sentiment="Negative"
                else: sentiment="Neutral"
                all_news.append({"title":title,"link":link,"source":src,"pub_date":pub,"sentiment":sentiment})
        except: continue
    subset=all_news[:8]
    score=sum(1 if n["sentiment"]=="Positive" else -1 if n["sentiment"]=="Negative" else 0 for n in subset)
    return round(score*2.5,1), subset

@st.cache_data(ttl=600)
def get_news(ticker):
    pos_kw=["buy","growth","up","positive","surge","profit","beat","record","strong","upgrade","bullish","soars","rises","rally","outperform"]
    neg_kw=["sell","fall","down","negative","drop","loss","risk","crisis","miss","weak","downgrade","bearish","cut","slump","plunge","recall","fraud"]
    try:
        news_list=yf.Ticker(ticker).news[:5]; score,analyzed=0,[]
        for n in news_list:
            title=n.get("title","").lower()
            if any(w in title for w in pos_kw): score+=1; sentiment="Positive"
            elif any(w in title for w in neg_kw): score-=1; sentiment="Negative"
            else: sentiment="Neutral"
            analyzed.append({"title":n.get("title",""),"link":n.get("link","#"),"sentiment":sentiment})
        return score*2.5, analyzed
    except: return 0.0, []

TICKER_NAME_MAP={
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
    if not query or len(query)<1: return []
    q=query.upper().strip()
    results=[]; seen=set()
    def _add(ticker,priority):
        if ticker in seen: return
        seen.add(ticker)
        sec=ETF_MAP.get(ticker,"Unknown"); cfg=SECTOR_CONFIG.get(sec,SECTOR_CONFIG["Unknown"])
        results.append({"ticker":ticker,"name":TICKER_NAME_MAP.get(ticker,ticker),
            "sector":sec,"sector_label":cfg["label"],"sector_icon":cfg["icon"],"priority":priority})
    if q in ETF_MAP: _add(q,0)
    for t in ETF_MAP:
        if t.startswith(q) and t!=q: _add(t,1)
    for t in ETF_MAP:
        if q in t and not t.startswith(q): _add(t,2)
    for t,name in TICKER_NAME_MAP.items():
        if q in name.upper() and t not in seen: _add(t,3)
    results.sort(key=lambda x:(x["priority"],x["ticker"]))
    return results[:8]

def get_signal(wr):
    if wr>=60: return "매수 우위","badge-green","#059669"
    elif wr>=45: return "중립 관망","badge-yellow","#D97706"
    else: return "리스크 경고","badge-red","#DC2626"

def zcolor(z):
    if z>1.5: return "#DC2626"
    elif z>0.5: return "#D97706"
    elif z<-1.5: return "#059669"
    elif z<-0.5: return "#2563EB"
    else: return "#6B7280"

def zdesc(z):
    if z>2.0: return "극단 과열"
    elif z>1.0: return "과매수"
    elif z>0.3: return "평균 이상"
    elif z>-0.3: return "중립"
    elif z>-1.0: return "평균 이하"
    elif z>-2.0: return "과매도"
    else: return "극단 과매도"

def corr_color(corr,direction):
    aligned=(corr>0 and direction==1) or (corr<0 and direction==-1)
    if abs(corr)<0.15: return "#9CA3AF"
    return "#059669" if aligned else "#DC2626"
