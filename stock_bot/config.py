"""
Configuration settings, scoring weights, and market metadata for Stock Analysis Bot.
"""

# Scoring Weights for the Multi-Factor Signal Model (Total: 1.0)
#
# QUANTITATIVE METHODOLOGY NOTE:
# These weights are derived from a heuristic multi-factor fundamental tilting framework
# (anchored in classic Quality & Value factor investing principles, e.g., MSCI / Fama-French):
#
# 1. Fundamental & Valuation Core (45% total):
#    - Fundamentals (25%): Capital efficiency (ROE), profit margins, revenue growth, cash flow & balance sheet solvency.
#    - Valuation (20%): Trailing/Forward P/E, PEG ratio, Price-to-Sales (margin of safety).
#    * Reason: Anchors the composite model against speculative hype by prioritizing intrinsic economic health.
#
# 2. Market Timing & Sentiment Layer (45% total):
#    - Technicals (15%): Trend momentum (RSI, 50/200 SMA, MACD).
#    - Sentiment (15%): News sentiment, NLP polarity, and social volume velocity.
#    - Analyst Consensus (15%): Wall Street price targets, recommendation revisions, and upside potential.
#    * Reason: Prevents buying sound companies prematurely during downward momentum or downgrade cycles.
#
# 3. Macro & Moat Context (10% total):
#    - Macro/Industry (10%): Central bank interest rate sensitivity, economic moat, and pricing power.
#    * Reason: High-level regime filter.
#
# NOTE ON BACKTESTING & OUT-OF-SAMPLE (OOS) HIT RATE:
# These are expert-defined heuristic weights to avoid lookahead/overfitting bias from machine-learning
# hyperparameter optimization (which often fails across regime shifts, e.g., 2022 rate hike shifts).
# An empirical out-of-sample (OOS) backtest suite (e.g., historical Walk-Forward Optimization against CRSP/Compustat)
# is not included in this live execution engine.
WEIGHTS = {
    "fundamentals": 0.25,
    "valuation": 0.20,
    "technicals": 0.15,
    "sentiment": 0.15,
    "analyst": 0.15,
    "macro_industry": 0.10
}

# Recommendation Signal Thresholds (Composite Score out of 100)
SIGNAL_THRESHOLDS = {
    "STRONG BUY": (82, 100),
    "BUY": (65, 81),
    "HOLD": (45, 64),
    "SELL": (30, 44),
    "STRONG SELL": (0, 29)
}

# Major Exchange Suffix Map for International Context
EXCHANGE_MAP = {
    "AX": {"country": "Australia", "exchange": "ASX", "central_bank": "Reserve Bank of Australia (RBA)", "currency_symbol": "A$"},
    "L":  {"country": "United Kingdom", "exchange": "LSE", "central_bank": "Bank of England (BOE)", "currency_symbol": "£"},
    "TO": {"country": "Canada", "exchange": "TSX", "central_bank": "Bank of Canada (BOC)", "currency_symbol": "C$"},
    "DE": {"country": "Germany", "exchange": "XETRA", "central_bank": "European Central Bank (ECB)", "currency_symbol": "€"},
    "PA": {"country": "France", "exchange": "Euronext Paris", "central_bank": "European Central Bank (ECB)", "currency_symbol": "€"},
    "HK": {"country": "Hong Kong", "exchange": "HKEX", "central_bank": "Hong Kong Monetary Authority (HKMA)", "currency_symbol": "HK$"},
    "TYO": {"country": "Japan", "exchange": "TSE", "central_bank": "Bank of Japan (BOJ)", "currency_symbol": "¥"},
    "T":  {"country": "Japan", "exchange": "TSE", "central_bank": "Bank of Japan (BOJ)", "currency_symbol": "¥"},
    "SS": {"country": "China", "exchange": "Shanghai", "central_bank": "People's Bank of China (PBOC)", "currency_symbol": "¥"},
    "SZ": {"country": "China", "exchange": "Shenzhen", "central_bank": "People's Bank of China (PBOC)", "currency_symbol": "¥"},
    "NS": {"country": "India", "exchange": "NSE", "central_bank": "Reserve Bank of India (RBI)", "currency_symbol": "₹"},
    "BO": {"country": "India", "exchange": "BSE", "central_bank": "Reserve Bank of India (RBI)", "currency_symbol": "₹"},
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

def get_exchange_info(symbol: str) -> dict:
    """Detect exchange, country, and central bank from ticker symbol suffix."""
    if "." in symbol:
        suffix = symbol.split(".")[-1].upper()
        if suffix in EXCHANGE_MAP:
            return EXCHANGE_MAP[suffix]
        
    # Default to US market if no known suffix
    return {
        "country": "United States",
        "exchange": "NYSE/NASDAQ",
        "central_bank": "Federal Reserve (FED)",
        "currency_symbol": "$"
    }

def format_currency(val: float, currency_code: str = "USD") -> str:
    """Format large currency values nicely (K, M, B, T) with locale-appropriate currency prefix."""
    if val is None:
        return "N/A"
    
    prefix = "$"
    if currency_code == "AUD":
        prefix = "A$"
    elif currency_code == "EUR":
        prefix = "€"
    elif currency_code == "GBP" or currency_code == "GBp":
        prefix = "£"
        if currency_code == "GBp":  # Pence
            val = val / 100.0
    elif currency_code == "CAD":
        prefix = "C$"
    elif currency_code == "JPY":
        prefix = "¥"
    elif currency_code == "INR":
        prefix = "₹"
    elif currency_code == "HKD":
        prefix = "HK$"
    elif currency_code == "CNY":
        prefix = "¥"

    sign = "-" if val < 0 else ""
    abs_val = abs(val)

    if abs_val >= 1e12:
        return f"{sign}{prefix}{abs_val / 1e12:.2f}T"
    elif abs_val >= 1e9:
        return f"{sign}{prefix}{abs_val / 1e9:.2f}B"
    elif abs_val >= 1e6:
        return f"{sign}{prefix}{abs_val / 1e6:.2f}M"
    elif abs_val >= 1e3:
        return f"{sign}{prefix}{abs_val / 1e3:.2f}K"
    else:
        return f"{sign}{prefix}{abs_val:.2f}"
