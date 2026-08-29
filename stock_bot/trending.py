"""
Trending Equities Fetcher - ApeWisdom, StockTwits & Yahoo Finance Integrator
Fetches live trending equities across Reddit/WallStreetBets, StockTwits, and Yahoo.
"""
import requests
import json
import os
from bs4 import BeautifulSoup

CACHE_FILE = os.path.join(os.path.dirname(__file__), "trending_cache.json")
DEFAULT_TRENDING = ["NVDA", "TSLA", "GME", "AAPL", "AMD", "PLTR"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_apewisdom_trending():
    """Scrapes top trending stock tickers from ApeWisdom (Reddit / WSB sentiment)."""
    tickers = []
    try:
        url = "https://apewisdom.io/all/"
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all("a")
            for l in links:
                href = l.get("href", "")
                if "/stocks/" in href:
                    sym = href.split("/stocks/")[1].strip("/").upper()
                    # Filter out indices, crypto, and long symbols
                    if sym and len(sym) <= 5 and sym not in ["SPY", "QQQ", "IWM", "BTC", "ETH", "USD"] and sym not in tickers:
                        tickers.append(sym)
                    if len(tickers) >= 8:
                        break
    except Exception:
        pass
    return tickers

def fetch_stocktwits_trending():
    """Fetches trending tickers from StockTwits sentiment API."""
    tickers = []
    try:
        url = "https://api.stocktwits.com/api/2/trending/symbols.json"
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            data = r.json()
            symbols = data.get("symbols", [])
            for s in symbols:
                sym = s.get("symbol", "").upper()
                if sym and len(sym) <= 5 and "." not in sym and sym not in ["BTC.X", "ETH.X", "SOL.X", "SPY", "QQQ"]:
                    if sym not in tickers:
                        tickers.append(sym)
                    if len(tickers) >= 8:
                        break
    except Exception:
        pass
    return tickers

def fetch_yahoo_trending():
    """Fetches trending stocks from Yahoo Finance API."""
    tickers = []
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            data = r.json()
            quotes = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
            for q in quotes:
                sym = q.get("symbol", "").upper()
                if sym and len(sym) <= 5 and "^" not in sym and "-USD" not in sym and sym not in ["SPY", "QQQ"]:
                    if sym not in tickers:
                        tickers.append(sym)
                    if len(tickers) >= 8:
                        break
    except Exception:
        pass
    return tickers

def get_trending_tickers(limit: int = 6):
    """
    Returns a unified, deduplicated list of top trending stock tickers.
    Merges ApeWisdom (Reddit WSB), StockTwits, and Yahoo Finance trending streams.
    """
    combined = []
    
    # 1. Try ApeWisdom
    ape = fetch_apewisdom_trending()
    combined.extend(ape)
    
    # 2. Try StockTwits if needed
    if len(combined) < limit:
        st_list = fetch_stocktwits_trending()
        for t in st_list:
            if t not in combined:
                combined.append(t)
                
    # 3. Try Yahoo if needed
    if len(combined) < limit:
        yh_list = fetch_yahoo_trending()
        for t in yh_list:
            if t not in combined:
                combined.append(t)

    # 4. Save to local cache file if we got fresh results
    if combined:
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump({"trending": combined, "updated_at": str(os.getenv("GITHUB_RUN_ID", "local"))}, f)
        except Exception:
            pass

    # 5. Fallback to cache file if empty
    if not combined and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cached_data = json.load(f)
                combined = cached_data.get("trending", [])
        except Exception:
            pass

    # 6. Fallback to default popular stocks
    if not combined:
        combined = DEFAULT_TRENDING

    return combined[:limit]

if __name__ == "__main__":
    print("Live Trending Tickers:", get_trending_tickers())
