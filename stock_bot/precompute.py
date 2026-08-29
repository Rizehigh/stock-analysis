import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from stock_bot.data_fetcher import fetch_stock_data
from stock_bot.technical_analysis import analyze_technicals
from stock_bot.sentiment_analysis import analyze_sentiment
from stock_bot.qualitative_analysis import analyze_qualitative_factors
from stock_bot.scoring_engine import compute_overall_signal
from stock_bot.trending import get_trending_tickers

PRECOMPUTED_FILE = os.path.join(os.path.dirname(__file__), "precomputed_trending.json")

def sanitize_for_json(obj):
    """Recursively converts non-serializable objects (Ticker, Timestamp, numpy types) to primitive types."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items() if k != "raw_ticker"}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif hasattr(obj, "item"): # numpy scalar
        return obj.item()
    elif type(obj).__name__ in ["Ticker", "Timestamp"]:
        return str(obj)
    return obj

def precompute_trending_reports():
    tickers = get_trending_tickers(limit=6)
    print("Pre-computing reports for trending tickers:", tickers)
    reports = {}
    for t in tickers:
        try:
            print(f"Analyzing {t}...")
            data = fetch_stock_data(t)
            tech = analyze_technicals(data)
            sent = analyze_sentiment(t, data.get("company_name", t))
            qual = analyze_qualitative_factors(data)
            sig = compute_overall_signal(data, tech, sent, qual)
            
            clean_report = sanitize_for_json({
                "data": data,
                "tech": tech,
                "sent": sent,
                "qual": qual,
                "sig": sig,
            })
            reports[t] = clean_report
        except Exception as e:
            print(f"Failed to precompute {t}: {e}")
            
    with open(PRECOMPUTED_FILE, "w") as f:
        json.dump(reports, f, indent=2)
    print(f"Pre-computed {len(reports)} reports to {PRECOMPUTED_FILE}")

if __name__ == "__main__":
    precompute_trending_reports()
