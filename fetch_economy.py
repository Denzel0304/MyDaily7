import yfinance as yf
import json
import os
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
today = datetime.now(KST).strftime("%Y-%m-%d")

def get_pct(ticker, period="2d"):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if len(hist) >= 2:
            prev = hist["Close"].iloc[-2]
            curr = hist["Close"].iloc[-1]
            return round((curr - prev) / prev * 100, 2)
        return None
    except:
        return None

def get_price(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1d")
        if not hist.empty:
            return round(hist["Close"].iloc[-1], 2)
        return None
    except:
        return None

def get_market_cap(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return info.get("marketCap", None)
    except:
        return None

# VIX
vix = get_price("^VIX")
vix_pct = get_pct("^VIX")

# 나스닥 등락률
nasdaq_pct = get_pct("^IXIC")
nasdaq_price = get_price("^IXIC")

# 코스피
kospi_price = get_price("^KS11")
kospi_pct = get_pct("^KS11")

# 달러환율
usdkrw = get_price("USDKRW=X")
usdkrw_pct = get_pct("USDKRW=X")

# 미국 시총 1위/2위
candidates = {
    "NVDA": "엔비디아",
    "AAPL": "애플",
    "MSFT": "마이크로소프트",
    "AMZN": "아마존",
    "GOOGL": "구글",
}
caps = {}
for ticker, name in candidates.items():
    cap = get_market_cap(ticker)
    if cap:
        caps[name] = cap

sorted_caps = sorted(caps.items(), key=lambda x: x[1], reverse=True)
top1_name, top1_cap = sorted_caps[0] if len(sorted_caps) > 0 else ("N/A", 0)
top2_name, top2_cap = sorted_caps[1] if len(sorted_caps) > 1 else ("N/A", 0)
cap_diff_pct = round((top1_cap - top2_cap) / top2_cap * 100, 1) if top2_cap else None

data = {
    "date": today,
    "vix": {"value": vix, "pct": vix_pct},
    "nasdaq": {"value": nasdaq_price, "pct": nasdaq_pct},
    "kospi": {"value": kospi_price, "pct": kospi_pct},
    "usdkrw": {"value": usdkrw, "pct": usdkrw_pct},
    "top_stock": {
        "rank1": top1_name,
        "rank2": top2_name,
        "cap_diff_pct": cap_diff_pct,
    }
}

# data/ 폴더 없으면 생성
os.makedirs("data", exist_ok=True)

# 오늘 데이터를 latest.json에 저장
with open("data/economy_latest.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# history.json에 누적 (최대 35일)
history_path = "data/economy_history.json"
if os.path.exists(history_path):
    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []

# 오늘 날짜 중복 제거 후 추가
history = [h for h in history if h["date"] != today]
history.append(data)
# 최신순 정렬, 최대 35개
history = sorted(history, key=lambda x: x["date"], reverse=True)[:35]

with open("data/economy_history.json", "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)

print(f"✅ {today} 데이터 저장 완료")
print(json.dumps(data, ensure_ascii=False, indent=2))
