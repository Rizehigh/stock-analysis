"""
Report Generator module for Stock Analysis Bot.
Renders colorful terminal output and generates markdown & HTML reports saved to reports/.
"""

import os
from datetime import datetime
from typing import Dict, Any
from stock_bot.config import format_currency

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

def get_signal_color(signal: str) -> str:
    if "BUY" in signal:
        return Colors.GREEN + Colors.BOLD
    elif "SELL" in signal:
        return Colors.RED + Colors.BOLD
    else:
        return Colors.YELLOW + Colors.BOLD

def print_cli_report(
    data: Dict[str, Any],
    tech: Dict[str, Any],
    sent: Dict[str, Any],
    qual: Dict[str, Any],
    sig: Dict[str, Any]
):
    """Renders formatted terminal output."""
    curr = data.get("currency", "USD")
    price_str = format_currency(data.get("current_price"), curr)
    mcap_str = format_currency(data.get("market_cap"), curr)
    
    print("\n" + Colors.BOLD + Colors.CYAN + "=" * 78 + Colors.RESET)
    print(Colors.BOLD + Colors.HEADER + f" COMPREHENSIVE STOCK ANALYSIS BOT REPORT: {data['symbol']} ({data['company_name']})" + Colors.RESET)
    print(f" Exchange: {data['exchange_info']['exchange']} ({data['exchange_info']['country']}) | Currency: {curr}")
    print(f" Current Price: {Colors.BOLD}{price_str}{Colors.RESET} | Market Cap: {mcap_str} | Sector: {data['sector']}")
    print(Colors.BOLD + Colors.CYAN + "=" * 78 + Colors.RESET + "\n")

    # 1. ULTIMATE RECOMMENDATION BOX
    sig_color = get_signal_color(sig["signal"])
    print("  " + Colors.BOLD + "+--------------------------------------------------------------+" + Colors.RESET)
    print(f"  | {Colors.BOLD}RECOMMENDATION SIGNAL:{Colors.RESET} {sig_color}{sig['signal']:<12}{Colors.RESET} | {Colors.BOLD}CONFIDENCE:{Colors.RESET} {Colors.CYAN}{sig['confidence_pct']}%{Colors.RESET}   |")
    print(f"  | {Colors.BOLD}COMPOSITE SCORE:{Colors.RESET}       {Colors.BOLD}{sig['composite_score']:.1f} / 100{Colors.RESET}                                 |")
    print("  " + Colors.BOLD + "+--------------------------------------------------------------+" + Colors.RESET + "\n")

    # 2. PILLAR SCORES BREAKDOWN
    print(Colors.BOLD + Colors.UNDERLINE + "1. PILLAR SCORES BREAKDOWN (0 - 100)" + Colors.RESET)
    pillars = sig["pillar_scores"]
    for p_name, p_val in pillars.items():
        bar_len = int(p_val // 5)
        bar = "#" * bar_len + "-" * (20 - bar_len)
        print(f"  - {p_name.capitalize():<15}: [{bar}] {p_val:>5.1f}")
    print()

    # 3. FINANCIAL HEALTH & VALUATION METRICS
    print(Colors.BOLD + Colors.UNDERLINE + "2. KEY FINANCIAL METRICS & VALUATION" + Colors.RESET)
    pe_val = f"{data['pe_ratio']:.1f}" if data.get('pe_ratio') is not None else "N/A"
    fwd_pe_val = f"{data['forward_pe']:.1f}" if data.get('forward_pe') is not None else "N/A"
    peg_val = f"{data['peg_ratio']:.2f}" if data.get('peg_ratio') is not None else "N/A"
    ps_val = f"{data['price_to_sales']:.2f}" if data.get('price_to_sales') is not None else "N/A"
    roe_val = f"{data['return_on_equity']*100:.1f}%" if data.get('return_on_equity') is not None else "N/A"
    margin_val = f"{data['profit_margins']*100:.1f}%" if data.get('profit_margins') is not None else "N/A"
    rev_growth_val = f"{data['revenue_growth']*100:.1f}%" if data.get('revenue_growth') is not None else "N/A"
    div_val = f"{data['dividend_yield_pct']:.2f}%" if data.get('dividend_yield_pct') is not None else "N/A"
    
    print(f"  P/E (TTM): {pe_val:<8} | Forward P/E: {fwd_pe_val:<8} | PEG Ratio: {peg_val}")
    print(f"  P/S Ratio: {ps_val:<8} | Profit Margin: {margin_val:<8} | ROE: {roe_val}")
    print(f"  Rev Growth: {rev_growth_val:<7} | Dividend Yield: {div_val:<6} | Next Earnings: {data.get('next_earnings_date')}")
    print()

    # 4. TECHNICAL INDICATORS & TRENDS
    print(Colors.BOLD + Colors.UNDERLINE + "3. TECHNICAL INDICATORS & PRICE TRENDS" + Colors.RESET)
    print(f"  RSI (14-day): {tech['rsi_14']:.1f} ({tech['rsi_status']}) | Cross Status: {tech['cross_status']}")
    print(f"  MACD Crossover: {tech['macd_data']['crossover']} | 52-wk Range Position: {tech['fifty_two_week_pos_pct']:.1f}%")
    if tech.get("signals"):
        for s in tech["signals"][:3]:
            print(f"   * {s}")
    print()

    # 5. SENTIMENT ANALYSIS (NEWS & REDDIT)
    print(Colors.BOLD + Colors.UNDERLINE + "4. REDDIT & NEWS SENTIMENT ANALYSIS" + Colors.RESET)
    print(f"  Sentiment Label: {Colors.BOLD}{sent['label']}{Colors.RESET} | Sentiment Score: {sent['sentiment_score']:.1f}/100")
    print(f"  Headlines Analyzed: {sent['headline_count']} | Combined Polarity Index: {sent['combined_polarity']}")
    if sent.get("positive_highlights"):
        print("  Positive News Highlights:")
        for h in sent["positive_highlights"][:2]:
            print(f"   + {h}")
    if sent.get("negative_highlights"):
        print("  Negative News Highlights:")
        for h in sent["negative_highlights"][:2]:
            print(f"   - {h}")
    print()

    # 6. ANALYST CONSENSUS & PRICE TARGETS
    print(Colors.BOLD + Colors.UNDERLINE + "5. WALL STREET ANALYST CONSENSUS" + Colors.RESET)
    target_mean_str = format_currency(data.get("target_mean"), curr)
    target_high_str = format_currency(data.get("target_high"), curr)
    target_low_str = format_currency(data.get("target_low"), curr)
    upside_val = f"+{data['implied_upside_pct']:.1f}%" if data.get('implied_upside_pct') and data['implied_upside_pct'] > 0 else f"{data['implied_upside_pct']:.1f}%" if data.get('implied_upside_pct') is not None else "N/A"
    
    print(f"  Target Price (Mean): {target_mean_str} (Range: {target_low_str} - {target_high_str})")
    print(f"  Implied Price Target Upside: {Colors.BOLD}{upside_val}{Colors.RESET} | Analyst Consensus: {str(data.get('recommendation_key')).upper()}")
    rec_b = data.get("rec_breakdown", {})
    print(f"  Ratings: Strong Buy: {rec_b.get('strongBuy', 0)} | Buy: {rec_b.get('buy', 0)} | Hold: {rec_b.get('hold', 0)} | Sell: {rec_b.get('sell', 0)}")
    print()

    # 7. QUALITATIVE, PRICED-IN & MACRO FACTORS
    print(Colors.BOLD + Colors.UNDERLINE + "6. QUALITATIVE, PRICED-IN & MACRO FACTORS" + Colors.RESET)
    print(f"  Economic Moat: {Colors.BOLD}{qual['moat']['moat_tier']}{Colors.RESET}")
    print(f"  Market Pricing Tier: {qual['priced_in']['valuation_tier']}")
    for p in qual.get("priced_in", {}).get("priced_in_points", [])[:2]:
        print(f"   * {p}")
    for m in qual.get("macro_policy", {}).get("macro_factors", [])[:2]:
        print(f"   * {m}")
    for r in qual.get("macro_policy", {}).get("policy_risks", [])[:2]:
        print(f"   ! Regulatory Risk: {r}")
    print()

    print(Colors.BOLD + Colors.CYAN + "=" * 78 + Colors.RESET + "\n")

def generate_markdown_report(
    data: Dict[str, Any],
    tech: Dict[str, Any],
    sent: Dict[str, Any],
    qual: Dict[str, Any],
    sig: Dict[str, Any]
) -> str:
    """Generates markdown analysis report and saves to reports/ directory."""
    os.makedirs("reports", exist_ok=True)
    symbol = data["symbol"]
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"reports/{symbol}_analysis_{date_str}.md"
    
    curr = data.get("currency", "USD")
    price_str = format_currency(data.get("current_price"), curr)
    mcap_str = format_currency(data.get("market_cap"), curr)
    target_mean_str = format_currency(data.get("target_mean"), curr)
    target_high_str = format_currency(data.get("target_high"), curr)
    target_low_str = format_currency(data.get("target_low"), curr)
    upside_str = f"{data['implied_upside_pct']:.1f}%" if data.get('implied_upside_pct') is not None else "N/A"

    pe_formatted = f"{data['pe_ratio']:.1f}" if data.get('pe_ratio') else "N/A"
    fwd_pe_formatted = f"{data['forward_pe']:.1f}" if data.get('forward_pe') else "N/A"
    peg_formatted = f"{data['peg_ratio']:.2f}" if data.get('peg_ratio') else "N/A"
    ps_formatted = f"{data['price_to_sales']:.2f}" if data.get('price_to_sales') else "N/A"
    margin_formatted = f"{data['profit_margins']*100:.1f}%" if data.get('profit_margins') else "N/A"
    roe_formatted = f"{data['return_on_equity']*100:.1f}%" if data.get('return_on_equity') else "N/A"
    rev_formatted = f"{data['revenue_growth']*100:.1f}%" if data.get('revenue_growth') else "N/A"
    div_formatted = f"{data['dividend_yield_pct']:.2f}%" if data.get('dividend_yield_pct') else "N/A"
    debt_formatted = f"{data['debt_to_equity']:.1f}" if data.get('debt_to_equity') else "N/A"
    current_formatted = f"{data['current_ratio']:.2f}" if data.get('current_ratio') else "N/A"

    md_lines = [
        f"# Stock Analysis Report: {symbol} - {data['company_name']}",
        "",
        f"**Generated Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Exchange:** {data['exchange_info']['exchange']} ({data['exchange_info']['country']})",
        f"**Current Price:** {price_str} ({curr}) | **Market Cap:** {mcap_str}",
        f"**Sector:** {data['sector']} | **Industry:** {data['industry']}",
        "",
        "---",
        "",
        "## Executive Summary & Signal",
        "",
        "| Parameter | Value |",
        "| :--- | :--- |",
        f"| **Recommendation Signal** | **`{sig['signal']}`** |",
        f"| **Confidence Level** | **`{sig['confidence_pct']}%`** |",
        f"| **Composite Score** | **`{sig['composite_score']} / 100`** |",
        "",
        "### Top Catalysts & Bull Case"
    ]
    for pos in sig.get("key_positives", []):
        md_lines.append(f"- ✅ {pos}")

    md_lines.append("")
    md_lines.append("### Key Risks & Bear Case")
    for risk in sig.get("key_risks", []):
        md_lines.append(f"- ⚠️ {risk}")

    md_lines.extend([
        "",
        "---",
        "",
        "## Pillar Score Breakdown",
        "",
        "| Pillar | Score (0-100) | Weight | Contribution |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Financial Fundamentals** | {sig['pillar_scores']['fundamentals']} | 25% | {sig['pillar_scores']['fundamentals']*0.25:.1f} |",
        f"| **Valuation & Multiples** | {sig['pillar_scores']['valuation']} | 20% | {sig['pillar_scores']['valuation']*0.20:.1f} |",
        f"| **Technical Momentum** | {sig['pillar_scores']['technicals']} | 15% | {sig['pillar_scores']['technicals']*0.15:.1f} |",
        f"| **Reddit & News Sentiment** | {sig['pillar_scores']['sentiment']} | 15% | {sig['pillar_scores']['sentiment']*0.15:.1f} |",
        f"| **Analyst Targets** | {sig['pillar_scores']['analyst']} | 15% | {sig['pillar_scores']['analyst']*0.15:.1f} |",
        f"| **Macro, Industry & Moat** | {sig['pillar_scores']['macro_moat']} | 10% | {sig['pillar_scores']['macro_moat']*0.10:.1f} |",
        f"| **Total Composite Score** | **{sig['composite_score']}** | **100%** | **{sig['composite_score']}** |",
        "",
        "---",
        "",
        "## Financial Health & Valuation",
        "",
        "| Financial Metric | Value | Valuation Ratio | Value |",
        "| :--- | :--- | :--- | :--- |",
        f"| **P/E Ratio (TTM)** | {pe_formatted} | **Forward P/E** | {fwd_pe_formatted} |",
        f"| **PEG Ratio** | {peg_formatted} | **P/S Ratio** | {ps_formatted} |",
        f"| **Profit Margin** | {margin_formatted} | **ROE** | {roe_formatted} |",
        f"| **Revenue Growth YoY** | {rev_formatted} | **Dividend Yield** | {div_formatted} |",
        f"| **Debt to Equity** | {debt_formatted} | **Current Ratio** | {current_formatted} |",
        "",
        "---",
        "",
        "## Technical Indicators & Price Trends",
        "",
        f"- **RSI (14-day):** `{tech['rsi_14']:.1f}` ({tech['rsi_status']})",
        f"- **50-day SMA:** `{tech.get('sma_50') if tech.get('sma_50') else 'N/A'}` | **200-day SMA:** `{tech.get('sma_200') if tech.get('sma_200') else 'N/A'}`",
        f"- **SMA Cross Status:** `{tech['cross_status']}`",
        f"- **MACD Crossover:** `{tech['macd_data']['crossover']}`",
        f"- **52-Week Range Position:** `{tech['fifty_two_week_pos_pct']:.1f}%`",
        "",
        "---",
        "",
        "## Reddit & News Sentiment Analysis",
        "",
        f"- **Sentiment Classification:** `{sent['label']}` (Score: `{sent['sentiment_score']}/100`)",
        f"- **Combined Polarity Index:** `{sent['combined_polarity']}`",
        f"- **Headlines Analyzed:** `{sent['headline_count']}`",
        "",
        "### Recent Headline Sample & Sentiment"
    ])
    for h in sent.get("recent_headlines", [])[:4]:
        md_lines.append(f"- {h}")

    md_lines.extend([
        "",
        "---",
        "",
        "## Wall Street Analyst Ratings & Target Prices",
        "",
        f"- **Average Price Target:** `{target_mean_str}` (Range: `{target_low_str}` to `{target_high_str}`)",
        f"- **Implied Upside/Downside:** `{upside_str}`",
        f"- **Analyst Consensus:** `{str(data.get('recommendation_key')).upper()}`",
        "",
        "---",
        "",
        "## Qualitative, Priced-In Expectations & Macro Factors",
        "",
        f"- **Competitive Moat:** `{qual['moat']['moat_tier']}`",
        f"- **Valuation Expectation Tier:** `{qual['priced_in']['valuation_tier']}`",
        "",
        "### Market Expectations (What is Priced In):"
    ])
    for point in qual.get("priced_in", {}).get("priced_in_points", []):
        md_lines.append(f"- {point}")

    md_lines.append("")
    md_lines.append("### Macro Environment & Regulatory Policies:")
    for m in qual.get("macro_policy", {}).get("macro_factors", []):
        md_lines.append(f"- {m}")
    for r in qual.get("macro_policy", {}).get("policy_risks", []):
        md_lines.append(f"- ⚠️ {r}")

    md_lines.append("")
    md_lines.append("---")
    md_lines.append("*Report generated automatically by DeepSeek Stock Analysis Bot.*")

    content = "\n".join(md_lines)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
        
    return filename

def generate_html_report(
    data: Dict[str, Any],
    tech: Dict[str, Any],
    sent: Dict[str, Any],
    qual: Dict[str, Any],
    sig: Dict[str, Any]
) -> str:
    """Generates a styled HTML analysis report and saves to reports/ directory."""
    os.makedirs("reports", exist_ok=True)
    symbol = data["symbol"]
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"reports/{symbol}_analysis_{date_str}.html"
    
    curr = data.get("currency", "USD")
    price_str = format_currency(data.get("current_price"), curr)
    mcap_str = format_currency(data.get("market_cap"), curr)
    target_mean_str = format_currency(data.get("target_mean"), curr)
    target_high_str = format_currency(data.get("target_high"), curr)
    target_low_str = format_currency(data.get("target_low"), curr)
    upside_str = f"{data['implied_upside_pct']:.1f}%" if data.get('implied_upside_pct') is not None else "N/A"

    sig_str = sig["signal"]
    if "BUY" in sig_str:
        badge_bg = "#10b981"
    elif "SELL" in sig_str:
        badge_bg = "#ef4444"
    else:
        badge_bg = "#f59e0b"

    pe_formatted = f"{data['pe_ratio']:.1f}" if data.get('pe_ratio') else "N/A"
    fwd_pe_formatted = f"{data['forward_pe']:.1f}" if data.get('forward_pe') else "N/A"
    peg_formatted = f"{data['peg_ratio']:.2f}" if data.get('peg_ratio') else "N/A"
    ps_formatted = f"{data['price_to_sales']:.2f}" if data.get('price_to_sales') else "N/A"
    margin_formatted = f"{data['profit_margins']*100:.1f}%" if data.get('profit_margins') else "N/A"
    roe_formatted = f"{data['return_on_equity']*100:.1f}%" if data.get('return_on_equity') else "N/A"
    rev_formatted = f"{data['revenue_growth']*100:.1f}%" if data.get('revenue_growth') else "N/A"
    div_formatted = f"{data['dividend_yield_pct']:.2f}%" if data.get('dividend_yield_pct') else "N/A"
    debt_formatted = f"{data['debt_to_equity']:.1f}" if data.get('debt_to_equity') else "N/A"
    current_formatted = f"{data['current_ratio']:.2f}" if data.get('current_ratio') else "N/A"

    pillars_rows = ""
    for p_name, p_val in sig["pillar_scores"].items():
        pillars_rows += f"""
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; font-weight: 600; margin-bottom: 4px;">
                <span>{p_name.capitalize()}</span>
                <span>{p_val:.1f} / 100</span>
            </div>
            <div style="background: #e2e8f0; border-radius: 6px; height: 10px; overflow: hidden;">
                <div style="background: #3b82f6; width: {p_val}%; height: 100%; border-radius: 6px;"></div>
            </div>
        </div>
        """

    pos_items = "".join([f"<li style='margin-bottom: 6px;'>✅ {p}</li>" for p in sig.get("key_positives", [])])
    neg_items = "".join([f"<li style='margin-bottom: 6px;'>⚠️ {r}</li>" for r in sig.get("key_risks", [])])
    headlines_items = "".join([f"<li style='margin-bottom: 6px;'>📰 {h}</li>" for h in sent.get("recent_headlines", [])[:5]])
    priced_in_items = "".join([f"<li style='margin-bottom: 6px;'>🔹 {p}</li>" for p in qual.get("priced_in", {}).get("priced_in_points", [])])
    macro_items = "".join([f"<li style='margin-bottom: 6px;'>🌍 {m}</li>" for m in qual.get("macro_policy", {}).get("macro_factors", [])])
    policy_items = "".join([f"<li style='margin-bottom: 6px;'>⚖️ {r}</li>" for r in qual.get("macro_policy", {}).get("policy_risks", [])])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Report - {symbol}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 24px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .card {{ background: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); padding: 24px; margin-bottom: 24px; border: 1px solid #e2e8f0; }}
        .header-box {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #ffffff; border-radius: 12px; padding: 28px; margin-bottom: 24px; }}
        .signal-badge {{ background-color: {badge_bg}; color: #ffffff; font-weight: 700; font-size: 1.5rem; padding: 8px 20px; border-radius: 8px; display: inline-block; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background-color: #f1f5f9; font-weight: 600; }}
        ul {{ padding-left: 20px; margin: 8px 0; }}
        h2 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 0; }}
        .footer {{ text-align: center; font-size: 0.85rem; color: #64748b; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-box">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <h1 style="margin: 0; font-size: 2.2rem;">{symbol} - {data['company_name']}</h1>
                    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 1rem;">Exchange: {data['exchange_info']['exchange']} ({data['exchange_info']['country']}) | Sector: {data['sector']} | Industry: {data['industry']}</p>
                </div>
                <div><span class="signal-badge">{sig_str}</span></div>
            </div>
            <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div><strong>Current Price:</strong> <span style="font-size: 1.2rem; color: #38bdf8;">{price_str}</span> ({curr})</div>
                <div><strong>Market Cap:</strong> {mcap_str}</div>
                <div><strong>Composite Score:</strong> {sig['composite_score']} / 100</div>
                <div><strong>Confidence:</strong> {sig['confidence_pct']}%</div>
            </div>
        </div>
        <div class="grid-2">
            <div class="card"><h2>Analytical Pillar Scores</h2>{pillars_rows}</div>
            <div class="card"><h2>Catalysts & Risk Factors</h2><h3 style="color: #059669; font-size: 1.05rem;">Top Bull Catalysts</h3><ul>{pos_items}</ul><h3 style="color: #dc2626; font-size: 1.05rem;">Key Bear Risks</h3><ul>{neg_items}</ul></div>
        </div>
        <div class="card">
            <h2>Financial Fundamentals & Valuation Multiples</h2>
            <table>
                <thead><tr><th>Metric</th><th>Value</th><th>Metric</th><th>Value</th></tr></thead>
                <tbody>
                    <tr><td><strong>P/E Ratio (TTM)</strong></td><td>{pe_formatted}</td><td><strong>Forward P/E</strong></td><td>{fwd_pe_formatted}</td></tr>
                    <tr><td><strong>PEG Ratio</strong></td><td>{peg_formatted}</td><td><strong>P/S Ratio</strong></td><td>{ps_formatted}</td></tr>
                    <tr><td><strong>Profit Margin</strong></td><td>{margin_formatted}</td><td><strong>Return on Equity (ROE)</strong></td><td>{roe_formatted}</td></tr>
                    <tr><td><strong>Revenue Growth YoY</strong></td><td>{rev_formatted}</td><td><strong>Dividend Yield</strong></td><td>{div_formatted}</td></tr>
                    <tr><td><strong>Debt to Equity</strong></td><td>{debt_formatted}</td><td><strong>Current Ratio</strong></td><td>{current_formatted}</td></tr>
                </tbody>
            </table>
        </div>
        <div class="grid-2">
            <div class="card">
                <h2>Technical Analysis & Momentum</h2>
                <ul>
                    <li><strong>RSI (14-day):</strong> {tech['rsi_14']:.1f} ({tech['rsi_status']})</li>
                    <li><strong>50-day SMA:</strong> {tech.get('sma_50') if tech.get('sma_50') else 'N/A'}</li>
                    <li><strong>200-day SMA:</strong> {tech.get('sma_200') if tech.get('sma_200') else 'N/A'}</li>
                    <li><strong>SMA Cross Status:</strong> {tech['cross_status']}</li>
                    <li><strong>MACD Crossover:</strong> {tech['macd_data']['crossover']}</li>
                    <li><strong>52-Week Range Position:</strong> {tech['fifty_two_week_pos_pct']:.1f}%</li>
                </ul>
            </div>
            <div class="card">
                <h2>Wall Street Analyst Consensus</h2>
                <ul>
                    <li><strong>Average Target Price:</strong> {target_mean_str} (Range: {target_low_str} - {target_high_str})</li>
                    <li><strong>Implied Target Upside:</strong> {upside_str}</li>
                    <li><strong>Consensus Recommendation:</strong> {str(data.get('recommendation_key')).upper()}</li>
                    <li><strong>Strong Buy / Buy Count:</strong> {data.get('rec_breakdown', {}).get('strongBuy', 0) + data.get('rec_breakdown', {}).get('buy', 0)}</li>
                    <li><strong>Hold / Sell Count:</strong> {data.get('rec_breakdown', {}).get('hold', 0) + data.get('rec_breakdown', {}).get('sell', 0)}</li>
                </ul>
            </div>
        </div>
        <div class="card">
            <h2>Reddit & News Sentiment</h2>
            <p><strong>Sentiment Classification:</strong> {sent['label']} (Score: {sent['sentiment_score']}/100) | <strong>Polarity Index:</strong> {sent['combined_polarity']}</p>
            <ul>{headlines_items}</ul>
        </div>
        <div class="card">
            <h2>Qualitative, Priced-In Expectations & Macro Policy</h2>
            <p><strong>Economic Moat:</strong> {qual['moat']['moat_tier']} | <strong>Valuation Pricing Tier:</strong> {qual['priced_in']['valuation_tier']}</p>
            <h3 style="font-size: 1rem;">Market Pricing Expectations:</h3>
            <ul>{priced_in_items}</ul>
            <h3 style="font-size: 1rem;">Macro Environment & Regulatory Policy:</h3>
            <ul>{macro_items}{policy_items}</ul>
        </div>
        <div class="footer">Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by DeepSeek Stock Analysis Bot.</div>
    </div>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return filename