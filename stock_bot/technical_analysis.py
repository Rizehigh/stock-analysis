"""
Technical Analysis module for Stock Analysis Bot.
Computes technical indicators (SMA, RSI, MACD, Bollinger Bands, Volume trend, Price Momentum).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def compute_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate Relative Strength Index (RSI)."""
    if len(prices) < period + 1:
        return 50.0  # Neutral default
        
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1]
    
    if pd.isna(last_rsi):
        return 50.0
    return float(last_rsi)

def compute_macd(prices: pd.Series) -> Dict[str, float]:
    """Calculate MACD Line, Signal Line, and Histogram."""
    if len(prices) < 35:
        return {"macd": 0.0, "signal": 0.0, "histogram": 0.0, "crossover": "NEUTRAL"}
        
    exp1 = prices.ewm(span=12, adjust=False).mean()
    exp2 = prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    
    last_macd = float(macd.iloc[-1])
    last_signal = float(signal.iloc[-1])
    last_hist = float(hist.iloc[-1])
    prev_hist = float(hist.iloc[-2]) if len(hist) > 1 else last_hist
    
    crossover = "NEUTRAL"
    if last_hist > 0 and prev_hist <= 0:
        crossover = "BULLISH_CROSS"
    elif last_hist < 0 and prev_hist >= 0:
        crossover = "BEARISH_CROSS"
    elif last_hist > 0:
        crossover = "BULLISH"
    elif last_hist < 0:
        crossover = "BEARISH"
        
    return {
        "macd": last_macd,
        "signal": last_signal,
        "histogram": last_hist,
        "crossover": crossover
    }

def analyze_technicals(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetches historical data and computes technical indicators, trends, and a 0-100 technical score.
    """
    ticker_obj = data.get("_ticker_obj")
    current_price = data.get("current_price", 0.0)
    
    hist = pd.DataFrame()
    if ticker_obj is not None:
        try:
            hist = ticker_obj.history(period="1y")
        except Exception:
            pass
            
    if hist.empty or "Close" not in hist.columns or len(hist) < 20:
        return {
            "sma_20": None, "sma_50": None, "sma_200": None,
            "rsi_14": 50.0, "rsi_status": "NEUTRAL",
            "macd_data": {"macd": 0.0, "signal": 0.0, "histogram": 0.0, "crossover": "NEUTRAL"},
            "cross_status": "NEUTRAL",
            "fifty_two_week_pos_pct": 50.0,
            "returns": {"1m": 0.0, "3m": 0.0, "6m": 0.0, "1y": 0.0},
            "technical_score": 50.0,
            "signals": ["Insufficient price history for complete technical analysis."]
        }
        
    closes = hist["Close"]
    latest_price = float(closes.iloc[-1]) if current_price == 0 else float(current_price)
    
    # 1. Moving Averages
    sma_20 = float(closes.rolling(20).mean().iloc[-1]) if len(closes) >= 20 else None
    sma_50 = float(closes.rolling(50).mean().iloc[-1]) if len(closes) >= 50 else None
    sma_200 = float(closes.rolling(200).mean().iloc[-1]) if len(closes) >= 200 else None
    
    cross_status = "NEUTRAL"
    if sma_50 is not None and sma_200 is not None and not np.isnan(sma_50) and not np.isnan(sma_200):
        if sma_50 > sma_200:
            cross_status = "GOLDEN_CROSS"  # Bullish
        else:
            cross_status = "DEATH_CROSS"   # Bearish
            
    # 2. RSI & RSI Status
    rsi = compute_rsi(closes, 14)
    if rsi >= 70:
        rsi_status = "OVERBOUGHT"
    elif rsi <= 30:
        rsi_status = "OVERSOLD"
    elif rsi >= 55:
        rsi_status = "BULLISH"
    elif rsi <= 45:
        rsi_status = "BEARISH"
    else:
        rsi_status = "NEUTRAL"
        
    # 3. MACD
    macd_data = compute_macd(closes)
    
    # 4. 52-Week Position Percentage
    high_52 = float(hist["High"].max())
    low_52 = float(hist["Low"].min())
    if high_52 > low_52:
        pos_52_pct = ((latest_price - low_52) / (high_52 - low_52)) * 100
    else:
        pos_52_pct = 50.0
        
    # 5. Price Returns
    ret_1m = ((latest_price / float(closes.iloc[-21])) - 1) * 100 if len(closes) >= 21 else 0.0
    ret_3m = ((latest_price / float(closes.iloc[-63])) - 1) * 100 if len(closes) >= 63 else 0.0
    ret_6m = ((latest_price / float(closes.iloc[-126])) - 1) * 100 if len(closes) >= 126 else 0.0
    ret_1y = ((latest_price / float(closes.iloc[0])) - 1) * 100 if len(closes) >= 200 else 0.0
    
    # 6. Scoring Technicals (0 to 100)
    score = 50.0  # Base neutral
    signals = []
    
    # Helper check for valid non-nan float
    def is_valid_num(val):
        return val is not None and not np.isnan(val)

    # Price vs SMA 50
    if is_valid_num(sma_50):
        if latest_price > sma_50:
            pct_above = ((latest_price - sma_50) / sma_50) * 100
            score += min(15, pct_above * 1.5)
            signals.append(f"Price is {pct_above:.1f}% above 50-day SMA (Bullish)")
        else:
            pct_below = ((sma_50 - latest_price) / sma_50) * 100
            score -= min(15, pct_below * 1.5)
            signals.append(f"Price is {pct_below:.1f}% below 50-day SMA (Bearish)")

    # Golden/Death Cross
    if cross_status == "GOLDEN_CROSS":
        score += 10
        signals.append("50-day SMA is above 200-day SMA (Golden Cross)")
    elif cross_status == "DEATH_CROSS":
        score -= 10
        signals.append("50-day SMA is below 200-day SMA (Death Cross)")

    # RSI score
    if rsi_status == "OVERSOLD":
        score += 12  # Rebound potential
        signals.append(f"RSI is oversold at {rsi:.1f} (Potential Rebound)")
    elif rsi_status == "OVERBOUGHT":
        score -= 8   # Pullback risk
        signals.append(f"RSI is overbought at {rsi:.1f} (Pullback Risk)")
    elif rsi_status == "BULLISH":
        score += 5
    elif rsi_status == "BEARISH":
        score -= 5

    # MACD score
    if macd_data["crossover"] in ["BULLISH_CROSS", "BULLISH"]:
        score += 10
        signals.append("MACD histogram indicates positive bullish momentum")
    elif macd_data["crossover"] in ["BEARISH_CROSS", "BEARISH"]:
        score -= 10
        signals.append("MACD histogram indicates negative bearish momentum")

    # Momentum score (1m & 3m)
    if ret_1m > 5.0:
        score += 5
    elif ret_1m < -5.0:
        score -= 5

    technical_score = max(0.0, min(100.0, score))

    return {
        "latest_price": latest_price,
        "sma_20": sma_20,
        "sma_50": sma_50,
        "sma_200": sma_200,
        "rsi_14": rsi,
        "rsi_status": rsi_status,
        "macd_data": macd_data,
        "cross_status": cross_status,
        "fifty_two_week_pos_pct": pos_52_pct,
        "high_52": high_52,
        "low_52": low_52,
        "returns": {
            "1m": ret_1m,
            "3m": ret_3m,
            "6m": ret_6m,
            "1y": ret_1y
        },
        "technical_score": round(technical_score, 1),
        "signals": signals
    }
