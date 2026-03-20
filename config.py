# config.py
SECTOR_CONFIG = {
    "Energy": {
        "icon":"🛢️","color":"#D97706","label":"에너지",
        "cycle_note":"유가 사이클 — OPEC 결정·지정학 리스크·달러 강세에 연동",
        "indicators":[
            {"name":"WTI 유가",       "ticker":"CL=F",     "weight":+14,"desc":"매출·마진 직결. 유가 1% 상승 ≈ EPS 2~3% 개선"},
            {"name":"천연가스",       "ticker":"NG=F",      "weight":+6, "desc":"LNG·가스 사업 비중 종목에 직접 영향"},
            {"name":"에너지ETF(XLE)", "ticker":"XLE",       "weight":+8, "desc":"섹터 전반 기관 자금 흐름 반영"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-5, "desc":"달러 강세 = 원자재 가격 하락 압력"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-4, "desc":"고배당 에너지주 vs 채권 경쟁"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-5, "desc":"경기침체 공포 = 원자재 수요 감소"},
        ]
    },
    "Technology": {
        "icon":"💻","color":"#2563EB","label":"기술주",
        "cycle_note":"금리 사이클 — DCF 할인율 직결. 금리 1%p 상승 시 고PER 기술주 밸류에이션 ~15% 하락",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-14,"desc":"가장 중요. 미래 현금흐름 할인율 직접 영향"},
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+10,"desc":"기술주 섹터 모멘텀 — 기관 수급 반영"},
            {"name":"반도체(SOXX)",   "ticker":"SOXX",      "weight":+7, "desc":"빅테크 AI 인프라 투자 선행지표"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-7, "desc":"공포 구간 = 고PER 종목 먼저 청산"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-4, "desc":"해외 매출 비중 높은 빅테크 역풍"},
            {"name":"2년물 금리",     "ticker":"^IRX",      "weight":-5, "desc":"단기 유동성 비용 — 성장주 자금조달"},
        ]
    },
    "Semiconductor": {
        "icon":"🔬","color":"#0891B2","label":"반도체",
        "cycle_note":"재고 사이클 (18~36개월) — 공급과잉/부족 사이클. SOX 지수·PC/서버 수요가 핵심",
        "indicators":[
            {"name":"반도체(SOXX)",   "ticker":"SOXX",      "weight":+14,"desc":"섹터 사이클 직접 반영. 재고 조정 신호"},
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+8, "desc":"AI·클라우드 수요 — 반도체 end-demand"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-10,"desc":"CAPEX 비용 — 파운드리 설비 확장에 영향"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-6, "desc":"TSMC 등 아시아 공급망 원가·환율"},
            {"name":"구리 선물",      "ticker":"HG=F",      "weight":+5, "desc":"전자부품 원자재 + 경기 선행지표"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-5, "desc":"리스크오프 = 사이클주 집중 매도"},
        ]
    },
    "Consumer Cyclical": {
        "icon":"🛍️","color":"#DC2626","label":"경기소비재/EV",
        "cycle_note":"경기+금리 복합 사이클 — 소비자 구매력(금리·고용)과 EV는 배터리 원가 사이클에 추가 연동",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-11,"desc":"자동차 할부금리 직결 — 금리 1%p = 월납부 증가"},
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+8, "desc":"소비·기술 복합 종목(TSLA 등) 동조화"},
            {"name":"리튬ETF(LIT)",   "ticker":"LIT",       "weight":+7, "desc":"배터리 핵심 원자재 — EV 마진 직접 영향"},
            {"name":"임의소비(XLY)",  "ticker":"XLY",       "weight":+6, "desc":"소비심리 선행지표 — 기관 섹터 수급"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-7, "desc":"불안 = 고가 내구재 소비 위축"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-3, "desc":"글로벌 판매 환율 효과"},
        ]
    },
    "Consumer Defensive": {
        "icon":"🛒","color":"#059669","label":"필수소비재",
        "cycle_note":"경기 방어 섹터 — VIX 상승(공포장)에서 역발상 수혜. 인플레이션 구매력 훼손이 핵심 리스크",
        "indicators":[
            {"name":"CPI 인플레",     "ticker":"RINF",      "weight":-9, "desc":"인플레 심화 = 실질 구매력 하락"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-6, "desc":"고금리 = 고배당 방어주 상대 매력 감소"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":+6, "desc":"공포 시 안전자산 수요 → 방어주 유입"},
            {"name":"필수소비(XLP)",  "ticker":"XLP",       "weight":+7, "desc":"섹터 기관 자금 흐름"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-3, "desc":"수입 원자재·식품 원가 영향"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+4, "desc":"전체 장 상승 시 동반 상승"},
        ]
    },
    "Financial Services": {
        "icon":"🏦","color":"#7C3AED","label":"금융주",
        "cycle_note":"금리 사이클 — 장단기 스프레드(예대마진)가 핵심. 금리 인상기 수혜, 역전 시 압박",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":+13,"desc":"대출 금리 기준 — 예대마진 확대 직접 호재"},
            {"name":"2년물 금리",     "ticker":"^IRX",      "weight":+6, "desc":"단기 조달 비용 — 금리 스프레드 핵심"},
            {"name":"금융ETF(XLF)",   "ticker":"XLF",       "weight":+7, "desc":"섹터 기관 수급 반영"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-9, "desc":"금융위기 공포 = 모든 금융주 동시 하락"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":+3, "desc":"글로벌 금융사 달러 자산 가치 상승"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+4, "desc":"경제 성장 = 대출 수요 증가"},
        ]
    },
    "Healthcare": {
        "icon":"💊","color":"#0891B2","label":"헬스케어",
        "cycle_note":"방어+성장 복합 — FDA 규제·바이오 사이클이 개별 종목 변동성 높임",
        "indicators":[
            {"name":"바이오(XBI)",    "ticker":"XBI",       "weight":+8, "desc":"신약 파이프라인 투자심리 선행지표"},
            {"name":"헬스케어(XLV)",  "ticker":"XLV",       "weight":+6, "desc":"섹터 기관 자금 흐름"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":+5, "desc":"불안장 = 방어적 헬스케어 선호 증가"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-6, "desc":"신약 R&D 자금조달 비용 상승"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-4, "desc":"해외 판매 환율 — 글로벌 제약사"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+5, "desc":"전체 강세장 수혜"},
        ]
    },
    "Industrials": {
        "icon":"🏭","color":"#374151","label":"산업재",
        "cycle_note":"경기 사이클 — ISM 제조업 지수와 높은 상관. 인프라 지출·무역정책·달러에 민감",
        "indicators":[
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+9, "desc":"경기 확장 = 설비투자·인프라 수요 직결"},
            {"name":"구리 선물",      "ticker":"HG=F",      "weight":+8, "desc":"닥터 코퍼 — 산업 수요 경기 선행지표"},
            {"name":"산업재(XLI)",    "ticker":"XLI",       "weight":+6, "desc":"섹터 자금 흐름"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-6, "desc":"자본재 투자 비용 상승"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-7, "desc":"수출 제조업 경쟁력 하락"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"경기 불안 = 설비 발주 취소"},
        ]
    },
    "Real Estate": {
        "icon":"🏢","color":"#065F46","label":"부동산(REIT)",
        "cycle_note":"금리 사이클 — 모기지 금리와 직결. 금리 상승 시 가장 큰 타격 받는 섹터",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-15,"desc":"모기지 금리 기준 — REIT 밸류에이션 직격"},
            {"name":"2년물 금리",     "ticker":"^IRX",      "weight":-8, "desc":"단기 자금조달 비용 상승"},
            {"name":"부동산(XLRE)",   "ticker":"XLRE",      "weight":+7, "desc":"섹터 전반 기관 수급"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"경기침체 = 공실률 상승 우려"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-3, "desc":"해외 부동산 보유 REIT 환율"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+4, "desc":"경제 성장 = 임대 수요 증가"},
        ]
    },
    "Utilities": {
        "icon":"⚡","color":"#0369A1","label":"유틸리티",
        "cycle_note":"금리·배당 사이클 — 채권 대체 자산. AI 전력 수요가 신규 성장 변수로 부상",
        "indicators":[
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-12,"desc":"채권 대비 배당 매력 — 금리 상승 = 경쟁"},
            {"name":"유틸리티(XLU)",  "ticker":"XLU",       "weight":+8, "desc":"섹터 자금 흐름"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":+5, "desc":"불안장 = 방어적 유틸리티 자금 유입"},
            {"name":"천연가스",       "ticker":"NG=F",       "weight":-5, "desc":"발전 원가 — 가스 발전 비중 유틸리티"},
            {"name":"2년물 금리",     "ticker":"^IRX",      "weight":-6, "desc":"단기 부채 비용 — 자본 집약적 사업"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+3, "desc":"전체 장 약세 시 방어적 수요"},
        ]
    },
    "Basic Materials": {
        "icon":"⛏️","color":"#92400E","label":"소재/원자재",
        "cycle_note":"달러·원자재 사이클 — 달러 약세 + 중국 경기 회복 + 인프라 수요가 삼각 동력",
        "indicators":[
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-10,"desc":"달러 약세 = 원자재 가격 상승 (역상관)"},
            {"name":"구리 선물",      "ticker":"HG=F",      "weight":+10,"desc":"글로벌 제조·건설 수요 척도"},
            {"name":"소재ETF(XLB)",   "ticker":"XLB",       "weight":+6, "desc":"섹터 기관 수급"},
            {"name":"금 선물",        "ticker":"GC=F",      "weight":+5, "desc":"인플레·불확실성 헷지 수요"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"경기침체 = 원자재 수요 감소"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-4, "desc":"달러 강세 압력 간접 경로"},
        ]
    },
    "Communication Services": {
        "icon":"📡","color":"#1D4ED8","label":"통신/미디어",
        "cycle_note":"기술+경기 복합 — 광고 수익(경기 민감) + 구독 수익(방어적) 혼재",
        "indicators":[
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+10,"desc":"빅테크 동조 — 광고·플랫폼 연계"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-9, "desc":"성장주 밸류에이션 할인율 영향"},
            {"name":"통신ETF(XLC)",   "ticker":"XLC",       "weight":+5, "desc":"섹터 자금 흐름"},
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+6, "desc":"광고 수익 = 경기와 직결"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"불안 = 디지털 광고 지출 감소"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-4, "desc":"해외 매출 환율 — 글로벌 플랫폼"},
        ]
    },
    "Unknown": {
        "icon":"📊","color":"#6B7280","label":"기타",
        "cycle_note":"섹터를 특정할 수 없어 범용 지표를 적용합니다.",
        "indicators":[
            {"name":"S&P500(SPY)",    "ticker":"SPY",       "weight":+8, "desc":"전체 시장 흐름"},
            {"name":"나스닥(QQQ)",    "ticker":"QQQ",       "weight":+5, "desc":"성장주 흐름"},
            {"name":"10년물 금리",    "ticker":"^TNX",      "weight":-5, "desc":"거시 금리 환경"},
            {"name":"VIX 공포",       "ticker":"^VIX",      "weight":-6, "desc":"시장 공포 수준"},
            {"name":"달러 인덱스",    "ticker":"DX-Y.NYB",  "weight":-3, "desc":"달러 강세/약세"},
        ]
    },
}

SECTOR_MAP = {
    "Energy":"Energy","Technology":"Technology","Consumer Cyclical":"Consumer Cyclical",
    "Consumer Defensive":"Consumer Defensive","Financial Services":"Financial Services",
    "Healthcare":"Healthcare","Industrials":"Industrials","Basic Materials":"Basic Materials",
    "Real Estate":"Real Estate","Utilities":"Utilities",
    "Communication Services":"Communication Services",
}

ETF_MAP = {
    "XLE":"Energy","XOM":"Energy","CVX":"Energy","COP":"Energy","SLB":"Energy",
    "XLK":"Technology","AAPL":"Technology","MSFT":"Technology","CRM":"Technology","ADBE":"Technology","ORCL":"Technology",
    "NVDA":"Semiconductor","AMD":"Semiconductor","INTC":"Semiconductor","QCOM":"Semiconductor",
    "MU":"Semiconductor","SOXX":"Semiconductor","SMH":"Semiconductor","AMAT":"Semiconductor",
    "LRCX":"Semiconductor","ASML":"Semiconductor","TSM":"Semiconductor","AVGO":"Semiconductor","ARM":"Semiconductor",
    "TSLA":"Consumer Cyclical","F":"Consumer Cyclical","GM":"Consumer Cyclical","RIVN":"Consumer Cyclical",
    "AMZN":"Consumer Cyclical","HD":"Consumer Cyclical","NKE":"Consumer Cyclical","XLY":"Consumer Cyclical","LIT":"Consumer Cyclical",
    "XLP":"Consumer Defensive","PG":"Consumer Defensive","KO":"Consumer Defensive",
    "WMT":"Consumer Defensive","COST":"Consumer Defensive","PEP":"Consumer Defensive","MCD":"Consumer Defensive",
    "XLF":"Financial Services","JPM":"Financial Services","BAC":"Financial Services",
    "GS":"Financial Services","MS":"Financial Services","WFC":"Financial Services","V":"Financial Services","MA":"Financial Services",
    "XLV":"Healthcare","JNJ":"Healthcare","UNH":"Healthcare","PFE":"Healthcare",
    "MRK":"Healthcare","ABBV":"Healthcare","LLY":"Healthcare","TMO":"Healthcare",
    "XLI":"Industrials","CAT":"Industrials","DE":"Industrials","BA":"Industrials","GE":"Industrials","UPS":"Industrials",
    "XLRE":"Real Estate","AMT":"Real Estate","PLD":"Real Estate","EQIX":"Real Estate",
    "XLU":"Utilities","NEE":"Utilities","DUK":"Utilities","SO":"Utilities",
    "XLB":"Basic Materials","FCX":"Basic Materials","NEM":"Basic Materials","GLD":"Basic Materials",
    "XLC":"Communication Services","META":"Communication Services","GOOGL":"Communication Services",
    "NFLX":"Communication Services","DIS":"Communication Services","VZ":"Communication Services","T":"Communication Services",
    "QQQ":"Technology","SPY":"Unknown","IWM":"Unknown","DIA":"Unknown","ARKK":"Technology",
}
