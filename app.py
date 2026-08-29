import sys
import os

# Ensure project root is in sys.path for Streamlit Cloud deployments
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.graph_objects as go
import time
import json
from datetime import datetime
from stock_bot.data_fetcher import fetch_stock_data
from stock_bot.technical_analysis import analyze_technicals
from stock_bot.sentiment_analysis import analyze_sentiment
from stock_bot.qualitative_analysis import analyze_qualitative_factors
from stock_bot.scoring_engine import compute_overall_signal
from stock_bot.config import format_currency
from stock_bot.trending import get_trending_tickers
from stock_bot.comparator import build_multi_pillar_chart, render_multi_comparison_table, PALETTE

PRECOMPUTED_FILE = os.path.join(os.path.dirname(__file__), "stock_bot", "precomputed_trending.json")

def clean_html(html_str: str) -> str:
    """Strips leading whitespace from lines to prevent Markdown from converting HTML into code blocks."""
    lines = [line.strip() for line in html_str.strip().splitlines()]
    return "".join(lines)

@st.cache_data(ttl=1800)
def fetch_cached_trending():
    """Caches trending tickers for 30 minutes."""
    return get_trending_tickers(limit=6)

@st.cache_data(ttl=3600)
def load_precomputed_reports():
    """Loads pre-analyzed trending stock reports if available."""
    if os.path.exists(PRECOMPUTED_FILE):
        try:
            with open(PRECOMPUTED_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

# ─── Astigmatism-Friendly & High Legibility CSS ───
M3_DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@500;700&family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');

:root {
    --bg-main: #181825;
    --card-bg: #242438;
    --card-border: #383854;
    --text-primary: #E2E8F0;
    --text-secondary: #A6ADC8;
    --text-muted: #888EA8;
    --accent-purple: #CBA6F7;
    --btn-bg: #4A3780;
    --btn-hover: #5B449C;
    --btn-text: #F5F3FF;
}

.stApp {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    font-size: 1.25rem !important;
    line-height: 1.75 !important;
}

/* Ensure sidebar header container & collapse control remain visible and easily clickable */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    z-index: 99999 !important;
}

[data-testid="stSidebarCollapsedControl"] {
    background-color: #242438 !important;
    border: 1px solid #383854 !important;
    border-radius: 12px !important;
    margin: 12px !important;
    padding: 6px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] svg {
    color: #CBA6F7 !important;
    fill: #CBA6F7 !important;
}

[data-testid="stSidebar"] {
    background-color: var(--card-bg) !important;
    border-right: 1px solid var(--card-border) !important;
}

[data-testid="stSidebar"] label {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

div[data-baseweb="input"] {
    background-color: #1E1E2E !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
}

div[data-baseweb="input"] input {
    color: var(--text-primary) !important;
    font-size: 1.2rem !important;
    padding: 12px 16px !important;
}

.stButton > button, div.stButton > button[kind="primary"], form button {
    background-color: var(--btn-bg) !important;
    color: var(--btn-text) !important;
    font-family: 'Google Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.25rem !important;
    padding: 14px 28px !important;
    border-radius: 14px !important;
    border: 1px solid #6B46C1 !important;
    box-shadow: none !important;
    transition: background-color 0.2s ease !important;
    cursor: pointer !important;
}

.stButton > button:hover, div.stButton > button[kind="primary"]:hover, form button:hover {
    background-color: var(--btn-hover) !important;
    color: #FFFFFF !important;
    border-color: #8B5CF6 !important;
}

.m3-card {
    background: var(--card-bg);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 28px;
    border: 1px solid var(--card-border);
}

.m3-header {
    background: linear-gradient(135deg, #2D2545 0%, #1E1A2F 100%);
    color: #FFFFFF;
    border-radius: 24px;
    padding: 40px;
    margin-bottom: 32px;
    border: 1px solid #5B449C;
}

.m3-header h1 {
    font-family: 'Google Sans', sans-serif !important;
    font-weight: 700;
    font-size: 3.5rem !important;
    letter-spacing: -0.5px;
    margin: 0;
    color: #FFFFFF;
}

.m3-signal-badge {
    font-size: 2.2rem !important;
    font-weight: 700;
    padding: 16px 36px;
    border-radius: 20px;
    display: inline-block;
    letter-spacing: 1px;
}

.m3-signal-buy { background: #1B432C; color: #86EFAC; border: 2px solid #22C55E; }
.m3-signal-sell { background: #4C1D24; color: #FCA5A5; border: 2px solid #EF4444; }
.m3-signal-hold { background: #4D3817; color: #FDE047; border: 2px solid #EAB308; }

.m3-chip {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 22px;
    border-radius: 14px;
    font-size: 1.15rem !important;
    font-weight: 600;
}

.m3-chip-buy { background: #1B432C; color: #86EFAC; border: 1px solid #22C55E; }
.m3-chip-sell { background: #4C1D24; color: #FCA5A5; border: 1px solid #EF4444; }
.m3-chip-hold { background: #4D3817; color: #FDE047; border: 1px solid #EAB308; }

.m3-pillar-container { margin-bottom: 22px; }
.m3-pillar-label {
    font-size: 1.2rem !important;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.m3-pillar-bar-bg {
    background: #1E1E2E;
    height: 16px;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
    border: 1px solid var(--card-border);
}

.m3-pillar-bar-fill {
    background: linear-gradient(90deg, #9F7AEA 0%, #CBA6F7 100%);
    height: 100%;
    border-radius: 8px;
}

.m3-bull-item {
    padding: 18px 24px;
    background: #1B3325;
    border-radius: 16px;
    margin-bottom: 14px;
    font-size: 1.2rem !important;
    color: #C6F6D5;
    border-left: 6px solid #22C55E;
    line-height: 1.7;
}

.m3-bear-item {
    padding: 18px 24px;
    background: #3E1F24;
    border-radius: 16px;
    margin-bottom: 14px;
    font-size: 1.2rem !important;
    color: #FED7D7;
    border-left: 6px solid #EF4444;
    line-height: 1.7;
}

.m3-headline-item {
    padding: 18px 24px;
    background: #1E1E2E;
    border-radius: 16px;
    margin-bottom: 14px;
    font-size: 1.2rem !important;
    color: var(--text-primary);
    border-left: 6px solid var(--accent-purple);
    line-height: 1.7;
}

.m3-table-container { overflow-x: auto; margin-bottom: 32px; }
.m3-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid var(--card-border);
    background: var(--card-bg);
}

.m3-table th {
    background: #2D2D45;
    color: var(--accent-purple);
    font-weight: 700;
    font-size: 1.15rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 20px 24px;
    text-align: left;
    border-bottom: 2px solid var(--card-border);
}

.m3-table td {
    padding: 20px 24px;
    border-bottom: 1px solid var(--card-border);
    font-size: 1.25rem !important;
    color: var(--text-primary);
    font-weight: 500;
}

.m3-table tr:last-child td { border-bottom: none; }

.m3-section-title {
    font-family: 'Google Sans', sans-serif !important;
    font-weight: 700;
    font-size: 1.9rem !important;
    color: var(--accent-purple);
    margin: 32px 0 20px 0;
    display: flex;
    align-items: center;
    gap: 14px;
}

.m3-footer {
    text-align: center;
    font-size: 1.05rem !important;
    color: var(--text-secondary);
    margin-top: 64px;
    padding: 32px;
    border-top: 1px solid var(--card-border);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

def fmt_val(val, fmt_str=".1f", suffix="", prefix="", fallback="N/A"):
    if val is None: return fallback
    try: return f"{prefix}{val:{fmt_str}}{suffix}"
    except (ValueError, TypeError): return fallback

def get_signal_badge(signal):
    if "BUY" in signal: return f'<span class="m3-signal-badge m3-signal-buy">{signal}</span>'
    elif "SELL" in signal: return f'<span class="m3-signal-badge m3-signal-sell">{signal}</span>'
    return f'<span class="m3-signal-badge m3-signal-hold">{signal}</span>'

def get_chip(signal):
    if "BUY" in signal: return f'<span class="m3-chip m3-chip-buy">{signal}</span>'
    elif "SELL" in signal: return f'<span class="m3-chip m3-chip-sell">{signal}</span>'
    return f'<span class="m3-chip m3-chip-hold">{signal}</span>'

def build_pillar_bar(name: str, score: float, weight: str) -> str:
    score_val = max(0.0, min(100.0, float(score)))
    return f"""
    <div class="m3-pillar-container">
        <div class="m3-pillar-label"><span>{name} ({weight})</span><span><strong>{score_val:.1f}</strong> / 100</span></div>
        <div class="m3-pillar-bar-bg"><div class="m3-pillar-bar-fill" style="width: {score_val:.1f}%;"></div></div>
    </div>
    """

def build_gauge_chart(score: float, title: str = "Composite Score"):
    if score >= 70: bar_color = "#86EFAC"
    elif score >= 40: bar_color = "#FDE047"
    else: bar_color = "#FCA5A5"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"size": 24, "family": "Inter, sans-serif", "color": "#A6ADC8"}},
        number={"font": {"size": 56, "family": "Google Sans, sans-serif", "color": "#E2E8F0"}, "suffix": "/100"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 2, "tickcolor": "#888EA8", "dtick": 20, "tickfont": {"color": "#A6ADC8", "size": 16}},
            "bar": {"color": bar_color, "thickness": 0.35},
            "bgcolor": "#1E1E2E",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "#4C1D24"},
                {"range": [30, 55], "color": "#4D3817"},
                {"range": [55, 75], "color": "#2D2D45"},
                {"range": [75, 100], "color": "#1B432C"},
            ],
            "threshold": {"line": {"color": "#CBA6F7", "width": 4}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(
        height=290,
        margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif"},
    )
    return fig

def run_analysis(ticker: str):
    """Executes full 6-pillar analysis pipeline with instant precomputed cache lookup."""
    ticker = ticker.upper().strip()
    precomputed = load_precomputed_reports()
    
    if ticker in precomputed:
        p = precomputed[ticker]
        return p["data"], p["tech"], p["sent"], p["qual"], p["sig"]

    prog = st.progress(0, text=f"Fetching financial data for {ticker}...")
    data = fetch_stock_data(ticker)
    prog.progress(20, text="Calculating RSI, MACD & Moving Averages...")
    tech = analyze_technicals(data)
    prog.progress(45, text="Parsing News & Social Sentiment...")
    sent = analyze_sentiment(ticker, data.get("company_name", ticker))
    prog.progress(65, text="Evaluating Macro & Competitive Moat...")
    qual = analyze_qualitative_factors(data)
    prog.progress(85, text="Computing 6-Pillar Composite Score...")
    sig = compute_overall_signal(data, tech, sent, qual)
    prog.progress(100, text="Analysis Complete!")
    time.sleep(0.2)
    prog.empty()
    return data, tech, sent, qual, sig

def render_report(data, tech, sent, qual, sig):
    """Renders complete Material Design 3 Dark report with header compare form."""
    curr = data.get("currency", "USD")
    symbol = data["symbol"]
    price_str = format_currency(data.get("current_price"), curr)
    mcap_str = format_currency(data.get("market_cap"), curr)

    # ── Top Bar Header + Dynamic Compare Search Bar ──
    hdr_col1, hdr_col2 = st.columns([2.6, 1.4])
    with hdr_col2:
        is_comparing = st.session_state.get(f"show_inline_comp_{symbol}", False)
        if is_comparing:
            with st.form(f"inline_compare_form_{symbol}", clear_on_submit=False):
                compare_target = st.text_input(
                    f"Compare {symbol} with:",
                    placeholder="e.g. AMD, MSFT (Press Enter)",
                    key=f"compare_input_{symbol}"
                )
                comp_submitted = st.form_submit_button("⚔️  Run Comparison", type="primary", use_container_width=True)
                if comp_submitted and compare_target.strip():
                    new_targets = [t.strip().upper() for t in compare_target.strip().split(",") if t.strip()]
                    full_list = [symbol] + [t for t in new_targets if t != symbol]
                    
                    st.session_state["active_view"] = "Compare Equities"
                    st.session_state["compare_tickers_list"] = full_list[:6]
                    st.session_state["compare_query_text"] = ", ".join(full_list[:6])
                    st.rerun()
        else:
            if st.button("➕  Compare Stock", key=f"btn_show_inline_{symbol}", use_container_width=True):
                st.session_state[f"show_inline_comp_{symbol}"] = True
                st.rerun()

    header_html = f"""
    <div class="m3-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 24px;">
            <div>
                <h1>{symbol}</h1>
                <p style="margin: 10px 0 0 0; color: #E2E8F0; font-size: 1.6rem; font-weight: 600;">{data.get('company_name', symbol)}</p>
                <p style="margin: 8px 0 0 0; color: #A6ADC8; font-size: 1.2rem;">{data['exchange_info']['exchange']} ({data['exchange_info']['country']}) &bull; {data.get('sector', 'N/A')} &bull; {data.get('industry', 'N/A')}</p>
            </div>
            <div style="text-align: right;">
                {get_signal_badge(sig['signal'])}
                <p style="margin: 14px 0 0 0; color: #E2E8F0; font-size: 1.25rem;">Confidence: <strong>{sig['confidence_pct']}%</strong></p>
            </div>
        </div>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.18); margin: 28px 0 24px 0;">
        <div style="display: flex; gap: 56px; flex-wrap: wrap;">
            <div><span style="color: #A6ADC8; font-size: 1.05rem; text-transform: uppercase; letter-spacing: 1px;">Current Price</span><br><span style="font-size: 2rem; font-weight: 700; color: #FFFFFF;">{price_str}</span></div>
            <div><span style="color: #A6ADC8; font-size: 1.05rem; text-transform: uppercase; letter-spacing: 1px;">Market Cap</span><br><span style="font-size: 2rem; font-weight: 700; color: #FFFFFF;">{mcap_str}</span></div>
            <div><span style="color: #A6ADC8; font-size: 1.05rem; text-transform: uppercase; letter-spacing: 1px;">Composite Score</span><br><span style="font-size: 2rem; font-weight: 700; color: #CBA6F7;">{sig['composite_score']} / 100</span></div>
        </div>
    </div>
    """
    st.markdown(clean_html(header_html), unsafe_allow_html=True)

    col_gauge, col_pillars = st.columns([1, 1.4])
    with col_gauge:
        st.plotly_chart(build_gauge_chart(sig["composite_score"]), use_container_width=True, key=f"gauge-{symbol}")

    with col_pillars:
        pillar_names = {
            "fundamentals": ("Financial Fundamentals", "25%"),
            "valuation": ("Valuation & Multiples", "20%"),
            "technicals": ("Technical Momentum", "15%"),
            "sentiment": ("News & Social Sentiment", "15%"),
            "analyst": ("Analyst Consensus", "15%"),
            "macro_moat": ("Macro, Moat & Industry", "10%"),
        }
        pillar_html = '<div class="m3-card">'
        pillar_html += '<div class="m3-section-title"><span class="material-symbols-outlined">analytics</span> Pillar Score Breakdown</div>'
        for key, (label, weight) in pillar_names.items():
            pillar_html += build_pillar_bar(label, sig["pillar_scores"][key], weight)
        pillar_html += '</div>'
        st.markdown(clean_html(pillar_html), unsafe_allow_html=True)

    col_bull, col_bear = st.columns(2)
    with col_bull:
        bull_html = '<div class="m3-card"><div class="m3-section-title" style="color: #86EFAC;"><span class="material-symbols-outlined">trending_up</span> Bull Catalysts</div>'
        for p in sig.get("key_positives", []): bull_html += f'<div class="m3-bull-item">✅ {p}</div>'
        bull_html += '</div>'
        st.markdown(clean_html(bull_html), unsafe_allow_html=True)
    with col_bear:
        bear_html = '<div class="m3-card"><div class="m3-section-title" style="color: #FCA5A5;"><span class="material-symbols-outlined">trending_down</span> Bear Risks</div>'
        for r in sig.get("key_risks", []): bear_html += f'<div class="m3-bear-item">⚠️ {r}</div>'
        bear_html += '</div>'
        st.markdown(clean_html(bear_html), unsafe_allow_html=True)

    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">account_balance</span> Financial Fundamentals & Valuation</div>'), unsafe_allow_html=True)

    tbl = '<div class="m3-table-container"><table class="m3-table"><thead><tr><th>Metric</th><th>Value</th><th>Metric</th><th>Value</th></tr></thead><tbody>'
    rows = [
        ("P/E Ratio (TTM)", fmt_val(data.get('pe_ratio')), "Forward P/E", fmt_val(data.get('forward_pe'))),
        ("PEG Ratio", fmt_val(data.get('peg_ratio'), ".2f"), "P/S Ratio", fmt_val(data.get('price_to_sales'), ".2f")),
        ("Profit Margin", fmt_val(data.get('profit_margins'), ".1f", "%", "", "N/A") if data.get('profit_margins') is None else f"{data['profit_margins']*100:.1f}%",
         "Return on Equity", fmt_val(data.get('return_on_equity'), ".1f", "%", "", "N/A") if data.get('return_on_equity') is None else f"{data['return_on_equity']*100:.1f}%"),
        ("Revenue Growth", fmt_val(data.get('revenue_growth'), ".1f", "%", "", "N/A") if data.get('revenue_growth') is None else f"{data['revenue_growth']*100:.1f}%",
         "Dividend Yield", fmt_val(data.get('dividend_yield_pct'), ".2f", "%")),
        ("Debt to Equity", fmt_val(data.get('debt_to_equity')), "Current Ratio", fmt_val(data.get('current_ratio'), ".2f")),
    ]
    for r in rows:
        tbl += f'<tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td><strong>{r[2]}</strong></td><td>{r[3]}</td></tr>'
    tbl += '</tbody></table></div>'
    st.markdown(clean_html(tbl), unsafe_allow_html=True)

    col_tech, col_analyst = st.columns(2)
    with col_tech:
        tech_html = '<div class="m3-card"><div class="m3-section-title"><span class="material-symbols-outlined">candlestick_chart</span> Technical Indicators</div>'
        tech_items = [
            f"<strong>RSI (14-day):</strong> {tech['rsi_14']:.1f} ({tech['rsi_status']})",
            f"<strong>50-day SMA:</strong> {tech.get('sma_50') if tech.get('sma_50') else 'N/A'}",
            f"<strong>200-day SMA:</strong> {tech.get('sma_200') if tech.get('sma_200') else 'N/A'}",
            f"<strong>SMA Cross:</strong> {tech['cross_status']}",
            f"<strong>MACD:</strong> {tech['macd_data']['crossover']}",
            f"<strong>52-Week Range Pos:</strong> {tech['fifty_two_week_pos_pct']:.1f}%",
        ]
        for item in tech_items: tech_html += f'<p style="margin: 14px 0; font-size: 1.2rem;">{item}</p>'
        if tech.get("signals"):
            for s in tech["signals"][:3]: tech_html += f'<div class="m3-headline-item">{s}</div>'
        tech_html += '</div>'
        st.markdown(clean_html(tech_html), unsafe_allow_html=True)

    with col_analyst:
        target_mean = format_currency(data.get("target_mean"), curr)
        target_high = format_currency(data.get("target_high"), curr)
        target_low = format_currency(data.get("target_low"), curr)
        upside = fmt_val(data.get('implied_upside_pct'), "+.1f", "%") if data.get('implied_upside_pct') and data['implied_upside_pct'] > 0 else fmt_val(data.get('implied_upside_pct'), ".1f", "%")
        rec_key = str(data.get('recommendation_key', 'N/A')).upper()
        rec_b = data.get("rec_breakdown", {})

        analyst_html = f'<div class="m3-card"><div class="m3-section-title"><span class="material-symbols-outlined">groups</span> Analyst Consensus</div>'
        analyst_html += f'<p style="margin: 14px 0; font-size: 1.2rem;"><strong>Target Price:</strong> {target_mean} ({target_low} &ndash; {target_high})</p>'
        analyst_html += f'<p style="margin: 14px 0; font-size: 1.2rem;"><strong>Implied Upside:</strong> {upside}</p>'
        analyst_html += f'<p style="margin: 14px 0; font-size: 1.2rem;"><strong>Wall St Rating:</strong> {get_chip(rec_key)}</p>'
        analyst_html += f'<p style="margin: 16px 0 0 0; font-size: 1.15rem; color: #A6ADC8;">Buy: {rec_b.get("buy", 0) + rec_b.get("strongBuy", 0)} &bull; Hold: {rec_b.get("hold", 0)} &bull; Sell: {rec_b.get("sell", 0) + rec_b.get("underperform", 0)}</p>'
        analyst_html += '</div>'
        st.markdown(clean_html(analyst_html), unsafe_allow_html=True)

    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">newspaper</span> News & Social Sentiment</div>'), unsafe_allow_html=True)
    sent_html = f'<div class="m3-card">'
    sent_html += f'<p style="font-size: 1.25rem; margin-bottom: 20px;"><strong>Sentiment Rating:</strong> {get_chip(sent["label"])} &nbsp; <strong>Score:</strong> {sent["sentiment_score"]:.1f}/100 &nbsp; <strong>Polarity Index:</strong> {sent["combined_polarity"]}</p>'
    if sent.get("positive_highlights"):
        for h in sent["positive_highlights"][:3]: sent_html += f'<div class="m3-bull-item">📰 {h}</div>'
    if sent.get("negative_highlights"):
        for h in sent["negative_highlights"][:3]: sent_html += f'<div class="m3-bear-item">📰 {h}</div>'
    sent_html += '</div>'
    st.markdown(clean_html(sent_html), unsafe_allow_html=True)

    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">shield</span> Qualitative, Macro & Competitive Moat</div>'), unsafe_allow_html=True)
    qual_html = '<div class="m3-card">'
    qual_html += f'<p style="font-size: 1.25rem; margin-bottom: 20px;"><strong>Economic Moat:</strong> {get_chip(qual["moat"]["moat_tier"])} &nbsp; <strong>Valuation Pricing:</strong> {get_chip(qual["priced_in"]["valuation_tier"])}</p>'
    for pt in qual.get("priced_in", {}).get("priced_in_points", []): qual_html += f'<div class="m3-headline-item">🔹 {pt}</div>'
    for m in qual.get("macro_policy", {}).get("macro_factors", []): qual_html += f'<div class="m3-headline-item">🌍 {m}</div>'
    for r in qual.get("macro_policy", {}).get("policy_risks", []): qual_html += f'<div class="m3-bear-item">⚖️ {r}</div>'
    qual_html += '</div>'
    st.markdown(clean_html(qual_html), unsafe_allow_html=True)

    st.markdown(clean_html(f'<div class="m3-footer">Aegis Equity Terminal &bull; Analysis generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>For educational purposes only. Not financial advice.</div>'), unsafe_allow_html=True)


def render_multi_comparison(tickers: list):
    """Renders multi-equity comparison for up to 6 stocks with Final Verdict cards and top-right '+ Add Stock to Compare' button."""
    tickers = list(dict.fromkeys([t.upper().strip() for t in tickers if t.strip()]))[:6]
    if not tickers:
        st.warning("Please enter at least 1 ticker to compare.")
        return

    # Top Header Row with "+ Add Stock to Compare" button (Disappears when 6 stocks reach capacity)
    comp_title_col, comp_btn_col = st.columns([2.6, 1.4])
    with comp_title_col:
        st.markdown(clean_html(f'<div class="m3-section-title"><span class="material-symbols-outlined">compare_arrows</span> Multi-Stock Comparison ({len(tickers)}/6): {" vs ".join(tickers)}</div>'), unsafe_allow_html=True)

    with comp_btn_col:
        if len(tickers) < 6:
            is_adding = st.session_state.get("show_inline_multi_comp", False)
            if is_adding:
                with st.form("inline_add_multi_comp_form", clear_on_submit=False):
                    add_target = st.text_input(
                        "Add stock to compare:",
                        placeholder="e.g. MSFT, TSLA (Press Enter)",
                        key="input_add_multi_comp"
                    )
                    sub_add = st.form_submit_button("⚔️  Add & Compare", type="primary", use_container_width=True)
                    if sub_add and add_target.strip():
                        new_t_list = [t.strip().upper() for t in add_target.strip().split(",") if t.strip()]
                        updated_list = list(dict.fromkeys(tickers + new_t_list))[:6]
                        st.session_state["compare_tickers_list"] = updated_list
                        st.session_state["compare_query_text"] = ", ".join(updated_list)
                        st.session_state["show_inline_multi_comp"] = False
                        st.rerun()
            else:
                if st.button("➕  Add Stock to Compare", key="btn_show_multi_add", use_container_width=True):
                    st.session_state["show_inline_multi_comp"] = True
                    st.rerun()
    
    data_map = {}
    sig_map = {}

    with st.spinner(f"Analyzing {len(tickers)} equities ({', '.join(tickers)})..."):
        for t in tickers:
            data, tech, sent, qual, sig = run_analysis(t)
            data_map[t] = data
            sig_map[t] = sig

    # 1. Final Verdict & Signal Summary Cards (One card per stock)
    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">gavel</span> Final Verdict & Signal Summary</div>'), unsafe_allow_html=True)
    
    verdict_cols = st.columns(min(len(tickers), 3))
    for idx, sym in enumerate(tickers):
        with verdict_cols[idx % min(len(tickers), 3)]:
            color = PALETTE[idx % len(PALETTE)]
            c_name = data_map[sym].get("company_name", sym)
            curr = data_map[sym].get("currency", "USD")
            price_s = format_currency(data_map[sym].get("current_price"), curr)
            mcap_s = format_currency(data_map[sym].get("market_cap"), curr)
            score = sig_map[sym]["composite_score"]
            conf = sig_map[sym]["confidence_pct"]
            sig_badge = get_signal_badge(sig_map[sym]["signal"])

            v_html = f"""
            <div class="m3-card" style="border-color: {color}; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: {color}; font-size: 1.7rem; margin: 0;">{sym}</h3>
                    {sig_badge}
                </div>
                <p style="color: #E2E8F0; font-size: 1.1rem; font-weight: 600; margin: 6px 0 12px 0;">{c_name[:24]}</p>
                <hr style="border: 0; border-top: 1px solid var(--card-border); margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #A6ADC8; font-size: 1.1rem;">Composite Score:</span>
                    <span style="font-size: 1.6rem; font-weight: 700; color: #CBA6F7;">{score} / 100</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                    <span style="color: #A6ADC8; font-size: 1.1rem;">Signal Confidence:</span>
                    <span style="font-size: 1.2rem; font-weight: 600; color: #E2E8F0;">{conf}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                    <span style="color: #A6ADC8; font-size: 1.05rem;">Price: {price_s}</span>
                    <span style="color: #A6ADC8; font-size: 1.05rem;">MCap: {mcap_s}</span>
                </div>
            </div>
            """
            st.markdown(clean_html(v_html), unsafe_allow_html=True)

    # 2. Multi-Bar 6-Pillar Chart
    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">bar_chart</span> 6-Pillar Score Breakdown</div>'), unsafe_allow_html=True)
    st.plotly_chart(build_multi_pillar_chart(sig_map), use_container_width=True, key=f"multi-comp-chart-{''.join(tickers)}")

    # 3. Detailed Matrix Table
    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">table_view</span> Financial & Valuation Metrics Matrix</div>'), unsafe_allow_html=True)
    st.markdown(clean_html(render_multi_comparison_table(data_map, sig_map)), unsafe_allow_html=True)

    # 4. Catalysts & Risks Grid
    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">shield</span> Top Catalysts & Risks</div>'), unsafe_allow_html=True)
    
    grid_cols = st.columns(min(len(tickers), 3))
    for idx, sym in enumerate(tickers):
        with grid_cols[idx % min(len(tickers), 3)]:
            color = PALETTE[idx % len(PALETTE)]
            card_html = f'<div class="m3-card"><h3 style="color: {color}; margin: 0 0 16px 0; font-size: 1.4rem;">{sym} Insights</h3>'
            card_html += '<p style="color: #86EFAC; font-weight: 700; margin: 8px 0 4px 0;">Top Catalysts:</p>'
            for p in sig_map[sym].get("key_positives", [])[:2]: card_html += f'<div class="m3-bull-item" style="font-size: 1.05rem !important;">✅ {p}</div>'
            card_html += '<p style="color: #FCA5A5; font-weight: 700; margin: 16px 0 4px 0;">Key Risks:</p>'
            for r in sig_map[sym].get("key_risks", [])[:2]: card_html += f'<div class="m3-bear-item" style="font-size: 1.05rem !important;">⚠️ {r}</div>'
            card_html += '</div>'
            st.markdown(clean_html(card_html), unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MAIN STREAMLIT APPLICATION ENTRY POINT
# ═══════════════════════════════════════════

st.set_page_config(
    page_title="Aegis Equity Terminal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(M3_DARK_CSS, unsafe_allow_html=True)

# ── Session State Persistence Setup ──
if "active_view" not in st.session_state:
    st.session_state["active_view"] = "Single Stock Analysis"

if "active_single_ticker" not in st.session_state:
    st.session_state["active_single_ticker"] = None

if "compare_tickers_list" not in st.session_state:
    st.session_state["compare_tickers_list"] = []

if "compare_query_text" not in st.session_state:
    st.session_state["compare_query_text"] = "NVDA, AMD"

selected_by_quick_chip = None

with st.sidebar:
    st.markdown(clean_html("""
    <div style="padding: 16px 0 8px 0;">
        <h2 style="font-family: 'Google Sans', sans-serif; color: #CBA6F7; font-size: 2.1rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 12px;">
            <span class="material-symbols-outlined" style="font-size: 2.6rem;">shield</span> Aegis Equity
        </h2>
        <p style="color: #A6ADC8; font-size: 1.05rem; margin: 6px 0 0 0;">Multi-Factor Stock Intelligence</p>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("---")

    # Radio widget synchronized with st.session_state["active_view"]
    radio_index = 0 if st.session_state["active_view"] == "Single Stock Analysis" else 1
    chosen_mode = st.radio(
        "Analysis Mode",
        options=["Single Stock Analysis", "Compare Equities"],
        index=radio_index
    )
    if chosen_mode != st.session_state["active_view"]:
        st.session_state["active_view"] = chosen_mode
        st.rerun()

    st.markdown("---")

    if st.session_state["active_view"] == "Single Stock Analysis":
        st.markdown("<h3 style='font-size: 1.35rem; color: #E2E8F0; margin-bottom: 8px;'>Stock Search</h3>", unsafe_allow_html=True)
        with st.form("single_search_form", clear_on_submit=False):
            single_input = st.text_input(
                "Ticker Symbol (Press Enter)",
                placeholder="e.g. NVDA, GME, CBA.AX",
                help="Type any symbol and press Enter to run live analysis"
            )
            single_submit_btn = st.form_submit_button("🔍  Run Analysis", type="primary", use_container_width=True)
            if single_submit_btn and single_input.strip():
                st.session_state["active_single_ticker"] = single_input.strip().upper()
                st.rerun()

        st.markdown("---")
        st.markdown("<h4 style='font-size: 1.2rem; color: #CBA6F7; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;'><span class='material-symbols-outlined'>local_fire_department</span> Trending Stocks Today</h4>", unsafe_allow_html=True)
        trending_list = fetch_cached_trending()
        t_cols = st.columns(2)
        for idx, t_sym in enumerate(trending_list):
            with t_cols[idx % 2]:
                if st.button(f"🔥 {t_sym}", key=f"btn_trend_{t_sym}", use_container_width=True):
                    st.session_state["active_single_ticker"] = t_sym
                    st.rerun()

    else:
        st.markdown("<h3 style='font-size: 1.35rem; color: #E2E8F0; margin-bottom: 8px;'>Compare Equities</h3>", unsafe_allow_html=True)
        with st.form("compare_search_form", clear_on_submit=False):
            comp_input = st.text_input(
                "Stock Tickers (Press Enter)",
                value=st.session_state.get("compare_query_text", "NVDA, AMD"),
                placeholder="e.g. NVDA, AMD, MSFT (up to 6)",
                help="Type up to 6 comma-separated stock tickers and press Enter"
            )
            comp_submit_btn = st.form_submit_button("⚔️  Run Comparison", type="primary", use_container_width=True)
            if comp_submit_btn and comp_input.strip():
                parsed = [t.strip().upper() for t in comp_input.strip().split(",") if t.strip()]
                st.session_state["compare_tickers_list"] = parsed[:6]
                st.session_state["compare_query_text"] = comp_input.strip()
                st.rerun()

    st.markdown("---")
    st.markdown(clean_html("""
    <div style="font-size: 1.05rem; color: #A6ADC8; line-height: 1.8;">
        <strong style="color: #E2E8F0;">6 Analytical Pillars:</strong><br>
        1. Financial Fundamentals (25%)<br>
        2. Valuation Multiples (20%)<br>
        3. Technical Momentum (15%)<br>
        4. News & Sentiment (15%)<br>
        5. Analyst Consensus (15%)<br>
        6. Macro & Moat (10%)
    </div>
    """), unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Aegis Equity Engine v2.0 &bull; Stock Comparator")


# ── Main Content Execution ──
if st.session_state["active_view"] == "Single Stock Analysis":
    target_ticker = st.session_state.get("active_single_ticker")

    if target_ticker:
        try:
            data, tech, sent, qual, sig = run_analysis(target_ticker)
            render_report(data, tech, sent, qual, sig)
        except Exception as e:
            st.error(f"Error executing analysis for '{target_ticker}': {e}")
    else:
        landing_html = """
        <div style="text-align: center; padding: 80px 20px;">
            <div style="display: inline-block; background: #242438; border: 1px solid #383854; border-radius: 40px; padding: 32px; margin-bottom: 32px;">
                <span class="material-symbols-outlined" style="font-size: 5rem; color: #CBA6F7;">shield_with_house</span>
            </div>
            <h1 style="font-family: 'Google Sans', sans-serif; color: #E2E8F0; font-weight: 700; font-size: 3.6rem; margin-bottom: 20px;">Aegis Equity Terminal</h1>
            <p style="color: #A6ADC8; font-size: 1.45rem; max-width: 780px; margin: 0 auto 40px auto; line-height: 1.7;">Enter any stock ticker to view a 6-pillar deep dive report, click <strong>Trending Stocks</strong> for instant loading, or click <strong>➕ Compare Stock</strong> to compare up to 6 equities side-by-side.</p>
            <div style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
                <span class="m3-chip m3-chip-buy" style="font-size: 1.15rem;">📊 6-Pillar Composite Quant Model</span>
                <span class="m3-chip m3-chip-buy" style="font-size: 1.15rem;">🌐 US, ASX, LSE & EU Market Data</span>
                <span class="m3-chip m3-chip-buy" style="font-size: 1.15rem;">📈 Technical Indicators (RSI, MACD, SMA)</span>
                <span class="m3-chip m3-chip-buy" style="font-size: 1.15rem;">📰 WSB & Social Sentiment Tracker</span>
            </div>
        </div>
        """
        st.markdown(clean_html(landing_html), unsafe_allow_html=True)

else:
    # Compare Mode Execution
    run_tickers = st.session_state.get("compare_tickers_list", [])
    if not run_tickers and st.session_state.get("compare_query_text"):
        run_tickers = [t.strip().upper() for t in st.session_state["compare_query_text"].split(",") if t.strip()]

    if run_tickers:
        try:
            render_multi_comparison(run_tickers)
        except Exception as e:
            st.error(f"Error executing comparison for {run_tickers}: {e}")
    else:
        landing_comp_html = """
        <div style="text-align: center; padding: 80px 20px;">
            <div style="display: inline-block; background: #242438; border: 1px solid #383854; border-radius: 40px; padding: 32px; margin-bottom: 32px;">
                <span class="material-symbols-outlined" style="font-size: 5rem; color: #86EFAC;">compare_arrows</span>
            </div>
            <h1 style="font-family: 'Google Sans', sans-serif; color: #E2E8F0; font-weight: 700; font-size: 3.6rem; margin-bottom: 20px;">Multi-Equity Stock Comparison</h1>
            <p style="color: #A6ADC8; font-size: 1.45rem; max-width: 780px; margin: 0 auto 40px auto; line-height: 1.7;">Type up to 6 stock tickers separated by commas (e.g. <strong>NVDA, AMD, MSFT, AAPL, TSLA, GOOGL</strong>) and press Enter to compare side-by-side.</p>
        </div>
        """
        st.markdown(clean_html(landing_comp_html), unsafe_allow_html=True)
