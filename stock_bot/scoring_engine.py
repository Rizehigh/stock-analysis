"""
Scoring Engine module for Stock Analysis Bot.
Synthesizes all 6 pillars (Fundamentals, Valuation, Technicals, Sentiment, Analyst Consensus, Macro/Moat)
into a 0-100 composite score, Buy/Sell/Hold signal, and confidence rating.
"""

import numpy as np
from typing import Dict, Any, Tuple, List
from stock_bot.config import WEIGHTS, SIGNAL_THRESHOLDS

def calculate_fundamentals_score(data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
    """Calculates Fundamental Health Score (0-100) and lists of bull/bear points."""
    score = 50.0
    pos_highlights = []
    neg_highlights = []
    
    roe = data.get("return_on_equity")
    margin = data.get("profit_margins")
    growth = data.get("revenue_growth")
    debt = data.get("debt_to_equity")
    current = data.get("current_ratio")
    fcf = data.get("free_cash_flow")

    # ROE
    if roe is not None:
        if roe > 0.20:
            score += 15
            pos_highlights.append(f"Exceptional Return on Equity ({roe*100:.1f}%)")
        elif roe > 0.12:
            score += 8
            pos_highlights.append(f"Solid Return on Equity ({roe*100:.1f}%)")
        elif roe < 0.05:
            score -= 10
            neg_highlights.append(f"Subpar Return on Equity ({roe*100:.1f}%)")

    # Margins
    if margin is not None:
        if margin > 0.20:
            score += 15
            pos_highlights.append(f"High profit margin ({margin*100:.1f}%)")
        elif margin > 0.10:
            score += 8
        elif margin < 0.03:
            score -= 12
            neg_highlights.append(f"Thin profit margin ({margin*100:.1f}%)")

    # Growth
    if growth is not None:
        if growth > 0.15:
            score += 12
            pos_highlights.append(f"Strong YoY revenue growth ({growth*100:.1f}%)")
        elif growth > 0.05:
            score += 5
        elif growth < 0.0:
            score -= 12
            neg_highlights.append(f"Declining YoY revenue ({growth*100:.1f}%)")

    # Balance Sheet Solvency
    if debt is not None:
        if debt < 50:
            score += 8
            pos_highlights.append(f"Low debt-to-equity ratio ({debt:.1f})")
        elif debt > 150:
            score -= 10
            neg_highlights.append(f"Elevated debt-to-equity ratio ({debt:.1f})")

    if current is not None:
        if current > 1.5:
            score += 5
        elif current < 1.0:
            score -= 8
            neg_highlights.append(f"Current ratio below 1.0 ({current:.2f})")

    # Free Cash Flow
    if fcf is not None and fcf > 0:
        score += 10
        pos_highlights.append("Positive free cash flow generation")
    elif fcf is not None and fcf < 0:
        score -= 10
        neg_highlights.append("Negative free cash flow generation")

    final_score = max(0.0, min(100.0, score))
    return round(final_score, 1), pos_highlights, neg_highlights

def calculate_valuation_score(data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
    """Calculates Valuation Score (0-100) and lists of bull/bear points."""
    score = 50.0
    pos_highlights = []
    neg_highlights = []
    
    pe = data.get("pe_ratio")
    fwd_pe = data.get("forward_pe")
    peg = data.get("peg_ratio")
    ps = data.get("price_to_sales")

    if pe is not None:
        if pe < 15:
            score += 15
            pos_highlights.append(f"Low P/E ratio ({pe:.1f}x)")
        elif pe < 25:
            score += 5
        elif pe > 45:
            score -= 15
            neg_highlights.append(f"High P/E ratio ({pe:.1f}x)")

    if fwd_pe is not None:
        if fwd_pe < 15:
            score += 15
            pos_highlights.append(f"Attractive Forward P/E ({fwd_pe:.1f}x)")
        elif fwd_pe < 25:
            score += 5
        elif fwd_pe > 40:
            score -= 12
            neg_highlights.append(f"Elevated Forward P/E ({fwd_pe:.1f}x)")

    if peg is not None:
        if peg < 1.0:
            score += 15
            pos_highlights.append(f"Favorable PEG ratio ({peg:.2f}x < 1.0)")
        elif peg > 2.5:
            score -= 12
            neg_highlights.append(f"High PEG ratio ({peg:.2f}x)")

    if ps is not None and ps < 2.0:
        score += 5
        pos_highlights.append(f"Low P/S ratio ({ps:.2f}x)")

    final_score = max(0.0, min(100.0, score))
    return round(final_score, 1), pos_highlights, neg_highlights

def calculate_analyst_score(data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
    """Calculates Analyst Consensus Score (0-100) and lists of bull/bear points."""
    score = 50.0
    pos_highlights = []
    neg_highlights = []
    
    upside = data.get("implied_upside_pct")
    rec_mean = data.get("recommendation_mean")
    rec_breakdown = data.get("rec_breakdown", {})
    
    # Implied Upside
    if upside is not None:
        if upside > 20:
            score += 25
            pos_highlights.append(f"Significant price target upside (+{upside:.1f}%)")
        elif upside > 10:
            score += 15
            pos_highlights.append(f"Moderate price target upside (+{upside:.1f}%)")
        elif upside > 0:
            score += 5
        else:
            score -= 15
            neg_highlights.append(f"Price exceeds average analyst target ({upside:.1f}%)")

    # Recommendation Mean (1 = Strong Buy, 5 = Strong Sell)
    if rec_mean is not None:
        if rec_mean <= 1.8:
            score += 20
            pos_highlights.append("Strong Wall Street analyst consensus (Strong Buy)")
        elif rec_mean <= 2.4:
            score += 12
            pos_highlights.append("Bullish analyst consensus (Buy)")
        elif rec_mean >= 3.5:
            score -= 20
            neg_highlights.append("Bearish analyst consensus (Sell/Underperform)")

    # Breakdown ratio
    strong_buy = rec_breakdown.get("strongBuy", 0) + rec_breakdown.get("buy", 0)
    sell = rec_breakdown.get("sell", 0) + rec_breakdown.get("strongSell", 0)
    if strong_buy + sell > 0:
        buy_ratio = strong_buy / (strong_buy + sell)
        if buy_ratio > 0.8:
            score += 10
            pos_highlights.append(f"{buy_ratio*100:.0f}% of analyst ratings are Buy/Strong Buy")
        elif buy_ratio < 0.3:
            score -= 10
            neg_highlights.append("Majority of analyst ratings are Hold/Sell")
            
    final_score = max(0.0, min(100.0, score))
    return round(final_score, 1), pos_highlights, neg_highlights

def compute_overall_signal(
    data: Dict[str, Any],
    tech_results: Dict[str, Any],
    sentiment_results: Dict[str, Any],
    qual_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesizes all 6 pillars into a composite score, signal, and confidence level.
    """
    # 1. Compute Individual Pillar Scores
    fund_score, fund_pos, fund_neg = calculate_fundamentals_score(data)
    val_score, val_pos, val_neg = calculate_valuation_score(data)
    tech_score = tech_results.get("technical_score", 50.0)
    sent_score = sentiment_results.get("sentiment_score", 50.0)
    analyst_score, analyst_pos, analyst_neg = calculate_analyst_score(data)
    macro_score = qual_results.get("qualitative_score", 50.0)

    # 2. Weighted Composite Score
    composite_score = (
        (fund_score * WEIGHTS["fundamentals"]) +
        (val_score * WEIGHTS["valuation"]) +
        (tech_score * WEIGHTS["technicals"]) +
        (sent_score * WEIGHTS["sentiment"]) +
        (analyst_score * WEIGHTS["analyst"]) +
        (macro_score * WEIGHTS["macro_industry"])
    )
    composite_score = round(composite_score, 1)

    # 3. Determine Signal
    signal = "HOLD"
    for s_name, (low, high) in SIGNAL_THRESHOLDS.items():
        if low <= composite_score <= high:
            signal = s_name
            break

    # 4. Determine Confidence Percentage
    pillar_scores = [fund_score, val_score, tech_score, sent_score, analyst_score, macro_score]
    std_dev = float(np.std(pillar_scores))
    
    confidence = 88.0 - (std_dev * 1.2)
    non_null_count = sum(1 for v in [data.get("pe_ratio"), data.get("forward_pe"), data.get("return_on_equity"), data.get("target_mean")] if v is not None)
    confidence += (non_null_count * 2.0)
    
    confidence_pct = round(max(45.0, min(96.0, confidence)), 1)

    # 5. Top Pros & Cons (Bull & Bear Case Summary)
    tech_signals = tech_results.get("signals", [])
    tech_pos = [s for s in tech_signals if "Bullish" in s or "Golden Cross" in s or "oversold" in s]
    tech_neg = [s for s in tech_signals if "Bearish" in s or "Death Cross" in s or "overbought" in s]

    all_positives = fund_pos + val_pos + analyst_pos + tech_pos
    all_negatives = fund_neg + val_neg + analyst_neg + tech_neg

    return {
        "composite_score": composite_score,
        "signal": signal,
        "confidence_pct": confidence_pct,
        "pillar_scores": {
            "fundamentals": fund_score,
            "valuation": val_score,
            "technicals": tech_score,
            "sentiment": sent_score,
            "analyst": analyst_score,
            "macro_moat": macro_score
        },
        "key_positives": all_positives[:4] if all_positives else ["Stable underlying corporate metrics."],
        "key_risks": all_negatives[:4] if all_negatives else ["Standard market risk and volatility."]
    }
