#!/usr/bin/env python3
"""
Stock Analysis Bot CLI Launcher (analyse.py)
Supports both US (e.g. AAPL, NVDA) and International stocks (e.g. CBA.AX, BHP.AX, SHEL.L).
"""

import sys
import os

# Automatic environment self-re-execution fix to ensure virtual environment Python is used
# (Skipped in GitHub Actions CI where dependencies are installed globally)
venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python")
if os.path.exists(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
    os.execv(venv_python, [venv_python] + sys.argv)

import argparse
from stock_bot.data_fetcher import fetch_stock_data
from stock_bot.technical_analysis import analyze_technicals
from stock_bot.sentiment_analysis import analyze_sentiment
from stock_bot.qualitative_analysis import analyze_qualitative_factors
from stock_bot.scoring_engine import compute_overall_signal
from stock_bot.report_generator import print_cli_report, generate_markdown_report, generate_html_report

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Stock Analysis Bot")
    parser.add_argument("symbol", nargs="?", default="AAPL", help="Stock ticker symbol (e.g. AAPL, NVDA, CBA.AX)")
    args = parser.parse_args()
    
    ticker = args.symbol.upper().strip()
    print(f"Fetching market & financial data for {ticker}...")
    
    try:
        data = fetch_stock_data(ticker)
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        sys.exit(1)
        
    print("Running technical analysis...")
    tech = analyze_technicals(data)
    
    print("Analyzing news & social sentiment...")
    sent = analyze_sentiment(ticker, data.get("company_name", ticker))
    
    print("Performing qualitative, macro & moat modeling...")
    qual = analyze_qualitative_factors(data)
    
    print("Computing 6-Pillar composite score & recommendation signal...")
    sig = compute_overall_signal(data, tech, sent, qual)
    
    # 1. Print formatted CLI output
    print_cli_report(data, tech, sent, qual, sig)
    
    # 2. Export reports
    md_path = generate_markdown_report(data, tech, sent, qual, sig)
    html_path = generate_html_report(data, tech, sent, qual, sig)
    
    print(f"✅ Markdown Report saved to: {md_path}")
    print(f"✅ HTML Report saved to:     {html_path}")
    print("Analysis complete!\n")

if __name__ == "__main__":
    main()
