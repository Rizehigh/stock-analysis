"""
Data Fetcher module for Stock Analysis Bot.
Extracts financial metrics, earnings, valuation ratios, analyst ratings, and dividend/calendar data.
"""

import yfinance as yf
from typing import Dict, Any
from stock_bot.config import get_exchange_info, format_currency

def safe_get(dictionary: dict, keys: list, default=None):
    """Attempt to retrieve value from a dictionary using a list of alternative key names."""
    if not isinstance(dictionary, dict):
        return default
    for k in keys:
        if k in dictionary and dictionary[k] is not None:
            return dictionary[k]
    return default

def fetch_stock_data(symbol: str) -> Dict[str, Any]:
    """
    Fetches comprehensive ticker data using yfinance.
    Handles US and international tickers cleanly.
    """
    symbol = symbol.strip().upper()
    ticker = yf.Ticker(symbol)
    
    info = ticker.info or {}
    exchange_meta = get_exchange_info(symbol)
    
    currency = safe_get(info, ["currency", "financialCurrency"], "USD")
    company_name = safe_get(info, ["longName", "shortName"], symbol)
    sector = safe_get(info, ["sector"], "N/A")
    industry = safe_get(info, ["industry"], "N/A")
    summary = safe_get(info, ["longBusinessSummary", "summary"], "No business summary available.")
    
    # 1. Price & Volume Metrics
    current_price = safe_get(info, ["currentPrice", "regularMarketPrice", "navPrice", "previousClose"], 0.0)
    previous_close = safe_get(info, ["previousClose", "regularMarketPreviousClose"], current_price)
    fifty_two_week_high = safe_get(info, ["fiftyTwoWeekHigh"], current_price)
    fifty_two_week_low = safe_get(info, ["fiftyTwoWeekLow"], current_price)
    volume = safe_get(info, ["volume", "regularMarketVolume"], 0)
    avg_volume = safe_get(info, ["averageVolume", "averageDailyVolume10Day", "averageVolume10days"], volume)
    
    # 2. Valuation Ratios
    pe_ratio = safe_get(info, ["trailingPE"])
    forward_pe = safe_get(info, ["forwardPE"])
    peg_ratio = safe_get(info, ["pegRatio"])
    price_to_sales = safe_get(info, ["priceToSalesTrailing12Months", "priceToSales"])
    price_to_book = safe_get(info, ["priceToBook"])
    ev_to_ebitda = safe_get(info, ["enterpriseToEbitda"])
    market_cap = safe_get(info, ["marketCap"])
    enterprise_value = safe_get(info, ["enterpriseValue"])
    
    # 3. Earnings & Performance Metrics
    eps_trailing = safe_get(info, ["trailingEps"])
    eps_forward = safe_get(info, ["forwardEps"])
    earnings_growth = safe_get(info, ["earningsGrowth", "earningsQuarterlyGrowth"])
    revenue_growth = safe_get(info, ["revenueGrowth"])
    total_revenue = safe_get(info, ["totalRevenue"])
    net_income = safe_get(info, ["netIncomeToCommon"])
    profit_margins = safe_get(info, ["profitMargins"])
    operating_margins = safe_get(info, ["operatingMargins"])
    return_on_equity = safe_get(info, ["returnOnEquity"])
    return_on_assets = safe_get(info, ["returnOnAssets"])
    
    # 4. Financial Health & Solvency
    total_debt = safe_get(info, ["totalDebt"])
    total_cash = safe_get(info, ["totalCash", "totalCashAndCashEquivalents"])
    debt_to_equity = safe_get(info, ["debtToEquity"])
    current_ratio = safe_get(info, ["currentRatio"])
    quick_ratio = safe_get(info, ["quickRatio"])
    free_cash_flow = safe_get(info, ["freeCashflow", "operatingCashflow"])
    dividend_yield = safe_get(info, ["dividendYield", "trailingAnnualDividendYield"])
    payout_ratio = safe_get(info, ["payoutRatio"])
    
    # Format yield to percentage if given as decimal
    if dividend_yield is not None and dividend_yield < 1.0:
        dividend_yield_pct = dividend_yield * 100
    else:
        dividend_yield_pct = dividend_yield
        
    # 5. Analyst Recommendations & Price Targets
    target_low = safe_get(info, ["targetLowPrice"])
    target_mean = safe_get(info, ["targetMeanPrice"])
    target_high = safe_get(info, ["targetHighPrice"])
    target_median = safe_get(info, ["targetMedianPrice"])
    recommendation_key = safe_get(info, ["recommendationKey"], "N/A")
    recommendation_mean = safe_get(info, ["recommendationMean"])
    number_of_analysts = safe_get(info, ["numberOfAnalystOpinions"], 0)
    
    implied_upside = None
    if current_price > 0 and target_mean is not None:
        implied_upside = ((target_mean - current_price) / current_price) * 100
        
    # Analyst count breakdown from recommendations_summary if available
    rec_breakdown = {"strongBuy": 0, "buy": 0, "hold": 0, "sell": 0, "strongSell": 0}
    try:
        rec_df = getattr(ticker, "recommendations_summary", None)
        if rec_df is not None and not rec_df.empty:
            latest_row = rec_df.iloc[0]
            for col in ["strongBuy", "buy", "hold", "sell", "strongSell"]:
                if col in latest_row:
                    rec_breakdown[col] = int(latest_row[col])
    except Exception:
        pass

    # 6. Calendar & Upcoming News
    calendar = {}
    try:
        cal_raw = getattr(ticker, "calendar", None)
        if isinstance(cal_raw, dict):
            calendar = cal_raw
        elif hasattr(cal_raw, "to_dict"):
            calendar = cal_raw.to_dict()
    except Exception:
        pass
        
    next_earnings_date = "Unknown"
    earnings_dates = calendar.get("Earnings Date", [])
    if isinstance(earnings_dates, list) and len(earnings_dates) > 0:
        next_earnings_date = str(earnings_dates[0])
    elif earnings_dates:
        next_earnings_date = str(earnings_dates)

    earnings_high_est = calendar.get("Earnings High")
    earnings_low_est = calendar.get("Earnings Low")
    earnings_avg_est = calendar.get("Earnings Average")
    
    return {
        "symbol": symbol,
        "company_name": company_name,
        "exchange_info": exchange_meta,
        "currency": currency,
        "sector": sector,
        "industry": industry,
        "summary": summary,
        
        # Price & Volume
        "current_price": current_price,
        "previous_close": previous_close,
        "fifty_two_week_high": fifty_two_week_high,
        "fifty_two_week_low": fifty_two_week_low,
        "volume": volume,
        "avg_volume": avg_volume,
        
        # Valuation
        "pe_ratio": pe_ratio,
        "forward_pe": forward_pe,
        "peg_ratio": peg_ratio,
        "price_to_sales": price_to_sales,
        "price_to_book": price_to_book,
        "ev_to_ebitda": ev_to_ebitda,
        "market_cap": market_cap,
        "enterprise_value": enterprise_value,
        
        # Earnings & Margins
        "eps_trailing": eps_trailing,
        "eps_forward": eps_forward,
        "earnings_growth": earnings_growth,
        "revenue_growth": revenue_growth,
        "total_revenue": total_revenue,
        "net_income": net_income,
        "profit_margins": profit_margins,
        "operating_margins": operating_margins,
        "return_on_equity": return_on_equity,
        "return_on_assets": return_on_assets,
        
        # Financial Health
        "total_debt": total_debt,
        "total_cash": total_cash,
        "debt_to_equity": debt_to_equity,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "free_cash_flow": free_cash_flow,
        "dividend_yield_pct": dividend_yield_pct,
        "payout_ratio": payout_ratio,
        
        # Analyst Targets
        "target_low": target_low,
        "target_mean": target_mean,
        "target_high": target_high,
        "target_median": target_median,
        "recommendation_key": recommendation_key,
        "recommendation_mean": recommendation_mean,
        "number_of_analysts": number_of_analysts,
        "implied_upside_pct": implied_upside,
        "rec_breakdown": rec_breakdown,
        
        # Upcoming Events
        "next_earnings_date": next_earnings_date,
        "earnings_high_est": earnings_high_est,
        "earnings_low_est": earnings_low_est,
        "earnings_avg_est": earnings_avg_est,
        
        # Original ticker object for historical price extraction
        "_ticker_obj": ticker
    }
