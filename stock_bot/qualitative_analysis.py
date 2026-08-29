"""
Qualitative Analysis module for Stock Analysis Bot.
Evaluates priced-in market expectations, industry trends, macro environment, regulatory policies, and competitive moat.
"""

from typing import Dict, Any, List
from stock_bot.config import format_currency

def evaluate_priced_in_expectations(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates what expectations are currently priced into the stock valuation.
    """
    pe = data.get("pe_ratio")
    fwd_pe = data.get("forward_pe")
    peg = data.get("peg_ratio")
    rev_growth = data.get("revenue_growth")
    earnings_growth = data.get("earnings_growth")
    
    priced_in_summary = []
    valuation_tier = "Moderate"
    
    if pe is not None:
        if pe > 40:
            valuation_tier = "High Growth Premium"
            priced_in_summary.append("High P/E ratio indicates market has priced in strong future earnings acceleration.")
        elif pe < 15:
            valuation_tier = "Value / Low Expectation"
            priced_in_summary.append("Low P/E ratio suggests market is pricing in modest growth or cyclical headwinds.")
        else:
            valuation_tier = "Fair Value Range"
            priced_in_summary.append("P/E ratio reflects balanced market expectations for mid-range growth.")

    if fwd_pe is not None and pe is not None:
        if fwd_pe < pe:
            pct_drop = ((pe - fwd_pe) / pe) * 100
            priced_in_summary.append(f"Forward P/E is {pct_drop:.1f}% lower than trailing P/E, pricing in robust earnings recovery/growth.")
        elif fwd_pe > pe:
            priced_in_summary.append("Forward P/E is higher than trailing P/E, pricing in potential earnings contraction.")

    if peg is not None:
        if peg < 1.0:
            priced_in_summary.append(f"PEG ratio of {peg:.2f} suggests stock may be undervalued relative to expected growth.")
        elif peg > 2.5:
            priced_in_summary.append(f"PEG ratio of {peg:.2f} signals premium valuation relative to growth rate.")

    return {
        "valuation_tier": valuation_tier,
        "priced_in_points": priced_in_summary if priced_in_summary else ["Market pricing reflects baseline sector performance."]
    }

def evaluate_macro_and_policy(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates macroeconomic environment, central bank stance, and regulatory policies based on stock location and sector.
    """
    exchange_info = data.get("exchange_info", {})
    country = exchange_info.get("country", "United States")
    central_bank = exchange_info.get("central_bank", "Federal Reserve (Fed)")
    sector = data.get("sector", "N/A")
    industry = data.get("industry", "N/A")
    
    macro_factors = []
    policy_risks = []
    
    # Macro environment notes
    macro_factors.append(f"Operating in {country} under {central_bank} interest rate policy environment.")
    
    if sector in ["Financial Services", "Banks"]:
        macro_factors.append("Interest rate yield curve directly impacts net interest margin (NIM) and loan volume demand.")
        policy_risks.append("Subject to banking regulatory capital requirements (e.g. APRA for Australia, Fed/OCC for US, Basel III).")
    elif sector in ["Technology", "Consumer Cyclical"]:
        macro_factors.append("Consumer sentiment and discretionary spending impact demand during inflation/rate shifts.")
        policy_risks.append("Antitrust oversight, data privacy laws, and international tariff trade policies affect cross-border supply chains.")
    elif sector in ["Healthcare", "Pharmaceuticals"]:
        macro_factors.append("Defensive sector with stable demand relatively inelastic to interest rate cycles.")
        policy_risks.append("Government drug pricing regulations, Medicare negotiations, and approval timelines.")
    elif sector in ["Energy", "Basic Materials"]:
        macro_factors.append("Highly commodity price sensitive (oil, copper, iron ore) and global economic expansion cycles.")
        policy_risks.append("Environmental emissions regulations, ESG mandates, and resource taxation policies.")
    else:
        macro_factors.append(f"Performance closely aligned with overall {country} economic trajectory.")
        policy_risks.append("Standard corporate governance and trade policy conditions apply.")
        
    return {
        "macro_factors": macro_factors,
        "policy_risks": policy_risks
    }

def evaluate_competitive_moat(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assesses economic moat and competitive positioning based on profit margins and return metrics.
    """
    roe = data.get("return_on_equity")
    net_margin = data.get("profit_margins")
    mcap = data.get("market_cap", 0) or 0
    currency = data.get("currency", "USD")
    
    moat_score = 50.0  # Base neutral
    moat_tier = "Moderate Moat"
    reasons = []

    if roe is not None and roe > 0.20:
        moat_score += 20
        reasons.append(f"Strong Return on Equity (ROE: {roe*100:.1f}%), indicating high capital efficiency and competitive advantage.")
    elif roe is not None and roe < 0.05:
        moat_score -= 15
        reasons.append(f"Low Return on Equity (ROE: {roe*100:.1f}%), indicating margin pressure or weak capital efficiency.")

    if net_margin is not None and net_margin > 0.15:
        moat_score += 15
        reasons.append(f"High net profit margin ({net_margin*100:.1f}%), demonstrating pricing power.")
    elif net_margin is not None and net_margin < 0.03:
        moat_score -= 15
        reasons.append(f"Thin net profit margin ({net_margin*100:.1f}%), making company vulnerable to cost inflation.")

    if mcap > 100e9:  # > 100 Billion
        moat_score += 15
        reasons.append(f"Mega-cap scale ({format_currency(mcap, currency)}) provides massive distribution and cost advantages.")
        
    if moat_score >= 75:
        moat_tier = "Wide Moat"
    elif moat_score >= 50:
        moat_tier = "Narrow Moat"
    else:
        moat_tier = "Weak / No Moat"

    return {
        "moat_tier": moat_tier,
        "moat_score": round(max(0.0, min(100.0, moat_score)), 1),
        "reasons": reasons if reasons else ["Standard market positioning within industry."]
    }

def analyze_qualitative_factors(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes qualitative assessment (priced-in, macro, policy, competitive moat).
    """
    priced_in = evaluate_priced_in_expectations(data)
    macro_policy = evaluate_macro_and_policy(data)
    moat = evaluate_competitive_moat(data)
    
    # Combined qualitative score (0 to 100)
    qual_score = (moat["moat_score"] * 0.6) + (50.0 * 0.4)
    
    return {
        "priced_in": priced_in,
        "macro_policy": macro_policy,
        "moat": moat,
        "qualitative_score": round(qual_score, 1)
    }
