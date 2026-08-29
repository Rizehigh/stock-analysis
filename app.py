"""
Aegis Equity Terminal - Streamlit Web Application
Material Design 3 Dark themed multi-factor stock analysis workstation.
"""
import streamlit as st
import plotly.graph_objects as go
import time
import re
from datetime import datetime
from stock_bot.data_fetcher import fetch_stock_data
from stock_bot.technical_analysis import analyze_technicals
from stock_bot.sentiment_analysis import analyze_sentiment
from stock_bot.qualitative_analysis import analyze_qualitative_factors
from stock_bot.scoring_engine import compute_overall_signal
from stock_bot.config import format_currency

def clean_html(html_str: str) -> str:
    """Strips leading whitespace from lines to prevent Markdown from converting HTML into code blocks."""
    lines = [line.strip() for line in html_str.strip().splitlines()]
    return "".join(lines)

# ─── Material Design 3 Dark: Custom CSS Injection ───
M3_DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');

:root {
    --md-sys-color-primary: #D0BCFF;
    --md-sys-color-on-primary: #381E72;
    --md-sys-color-primary-container: #4F378B;
    --md-sys-color-on-primary-container: #EADDFF;
    --md-sys-color-secondary: #CCC2DC;
    --md-sys-color-secondary-container: #332D41;
    --md-sys-color-on-secondary-container: #E8DEF8;
    --md-sys-color-tertiary: #EFB8C8;
    --md-sys-color-tertiary-container: #633B48;
    --md-sys-color-surface: #121318;
    --md-sys-color-surface-container: #1E1F25;
    --md-sys-color-surface-container-high: #2B2930;
    --md-sys-color-on-surface: #E6E1E5;
    --md-sys-color-on-surface-variant: #CAC4D0;
    --md-sys-color-outline: #938F99;
    --md-sys-color-outline-variant: #49454F;
    --md-sys-color-error: #F2B8B5;
    --md-sys-color-error-container: #8C1D18;
    --md-sys-color-on-error: #601410;
    --md-sys-color-success: #6DD58C;
    --md-sys-color-success-container: #0D3B1A;
    --md-sys-color-warning: #FFB74D;
    --md-sys-color-warning-container: #4A3800;
    --md-ref-typeface-brand: 'Google Sans', sans-serif;
    --md-ref-typeface-plain: 'Roboto', sans-serif;
}

.stApp {
    background-color: var(--md-sys-color-surface) !important;
    color: var(--md-sys-color-on-surface) !important;
    font-family: var(--md-ref-typeface-plain) !important;
    font-size: 1.05rem !important;
}

[data-testid="stSidebar"] {
    background-color: var(--md-sys-color-surface-container) !important;
    border-right: 1px solid var(--md-sys-color-outline-variant) !important;
}

.m3-card {
    background: var(--md-sys-color-surface-container);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 20px;
    border: 1px solid var(--md-sys-color-outline-variant);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.m3-header {
    background: linear-gradient(135deg, #4F378B 0%, #1E1F25 100%);
    color: #FFFFFF;
    border-radius: 28px;
    padding: 36px;
    margin-bottom: 28px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    border: 1px solid #6750A4;
}

.m3-header h1 {
    font-family: var(--md-ref-typeface-brand) !important;
    font-weight: 700;
    font-size: 2.8rem !important;
    letter-spacing: -0.5px;
    margin: 0;
    color: #EADDFF;
}

.m3-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    border-radius: 12px;
    font-size: 1rem !important;
    font-weight: 500;
    border: 1px solid var(--md-sys-color-outline);
}

.m3-chip-buy {
    background: #0D3B1A;
    color: #6DD58C;
    border-color: #1B6B2E;
}

.m3-chip-sell {
    background: #601410;
    color: #F2B8B5;
    border-color: #B3261E;
}

.m3-chip-hold {
    background: #4A3800;
    color: #FFDDB3;
    border-color: #7C5800;
}

.m3-signal-badge {
    font-size: 2rem !important;
    font-weight: 700;
    padding: 14px 32px;
    border-radius: 20px;
    display: inline-block;
    letter-spacing: 1.5px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.4);
}

.m3-signal-buy { background: #1B6B2E; color: #E8F5E9; border: 2px solid #6DD58C; }
.m3-signal-sell { background: #8C1D18; color: #FFEBEE; border: 2px solid #F2B8B5; }
.m3-signal-hold { background: #7C5800; color: #FFF8E1; border: 2px solid #FFDDB3; }

.m3-pillar-container {
    margin-bottom: 18px;
}

.m3-pillar-label {
    font-size: 1.05rem !important;
    font-weight: 500;
    color: var(--md-sys-color-on-surface);
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}

.m3-pillar-bar-bg {
    background: var(--md-sys-color-surface-container-high);
    height: 12px;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 16px;
    border: 1px solid var(--md-sys-color-outline-variant);
}

.m3-pillar-bar-fill {
    background: linear-gradient(90deg, #9A82DB 0%, #D0BCFF 100%);
    height: 100%;
    border-radius: 6px;
}

.m3-bull-item {
    padding: 12px 18px;
    background: #0D3B1A;
    border-radius: 14px;
    margin-bottom: 10px;
    font-size: 1.02rem !important;
    color: #E8F5E9;
    border-left: 4px solid #6DD58C;
    line-height: 1.5;
}

.m3-bear-item {
    padding: 12px 18px;
    background: #4A120E;
    border-radius: 14px;
    margin-bottom: 10px;
    font-size: 1.02rem !important;
    color: #FFEBEE;
    border-left: 4px solid #F2B8B5;
    line-height: 1.5;
}

.m3-headline-item {
    padding: 12px 18px;
    background: var(--md-sys-color-surface-container-high);
    border-radius: 14px;
    margin-bottom: 10px;
    font-size: 1.02rem !important;
    color: var(--md-sys-color-on-surface);
    border-left: 4px solid var(--md-sys-color-primary);
    line-height: 1.5;
}

.m3-table-container {
    overflow-x: auto;
    margin-bottom: 24px;
}

.m3-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--md-sys-color-outline-variant);
    background: var(--md-sys-color-surface-container);
}

.m3-table th {
    background: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
    font-weight: 700;
    font-size: 1rem !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 16px 20px;
    text-align: left;
    border-bottom: 2px solid var(--md-sys-color-outline);
}

.m3-table td {
    padding: 16px 20px;
    border-bottom: 1px solid var(--md-sys-color-outline-variant);
    font-size: 1.08rem !important;
    color: var(--md-sys-color-on-surface);
}

.m3-table tr:last-child td {
    border-bottom: none;
}

.m3-section-title {
    font-family: var(--md-ref-typeface-brand) !important;
    font-weight: 700;
    font-size: 1.5rem !important;
    color: var(--md-sys-color-primary);
    margin: 24px 0 16px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.m3-footer {
    text-align: center;
    font-size: 0.9rem !important;
    color: var(--md-sys-color-on-surface-variant);
    margin-top: 50px;
    padding: 24px;
    border-top: 1px solid var(--md-sys-color-outline-variant);
}

div[data-baseweb="input"] {
    background-color: var(--md-sys-color-surface-container-high) !important;
    border-radius: 12px !important;
}

.stButton > button {
    border-radius: 14px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
}

#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

def fmt_val(val, fmt_str=".1f", suffix="", prefix="", fallback="N/A"):
    """Safe format helper for nullable numeric values."""
    if val is None:
        return fallback
    try:
        return f"{prefix}{val:{fmt_str}}{suffix}"
    except (ValueError, TypeError):
        return fallback

def get_signal_badge(signal):
    if "BUY" in signal:
        return f'<span class="m3-signal-badge m3-signal-buy">{signal}</span>'
    elif "SELL" in signal:
        return f'<span class="m3-signal-badge m3-signal-sell">{signal}</span>'
    return f'<span class="m3-signal-badge m3-signal-hold">{signal}</span>'

def get_chip(signal):
    if "BUY" in signal:
        return f'<span class="m3-chip m3-chip-buy">{signal}</span>'
    elif "SELL" in signal:
        return f'<span class="m3-chip m3-chip-sell">{signal}</span>'
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
    """Creates a Plotly gauge chart with M3 dark colors."""
    if score >= 70:
        bar_color = "#6DD58C"
    elif score >= 40:
        bar_color = "#FFDDB3"
    else:
        bar_color = "#F2B8B5"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"size": 20, "family": "Google Sans, sans-serif", "color": "#CAC4D0"}},
        number={"font": {"size": 48, "family": "Google Sans, sans-serif", "color": "#E6E1E5"}, "suffix": "/100"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 2, "tickcolor": "#938F99", "dtick": 20, "tickfont": {"color": "#CAC4D0", "size": 14}},
            "bar": {"color": bar_color, "thickness": 0.35},
            "bgcolor": "#2B2930",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "#4A120E"},
                {"range": [30, 55], "color": "#4A3800"},
                {"range": [55, 75], "color": "#332D41"},
                {"range": [75, 100], "color": "#0D3B1A"},
            ],
            "threshold": {
                "line": {"color": "#D0BCFF", "width": 4},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Google Sans, Roboto, sans-serif"},
    )
    return fig

def run_analysis(ticker: str):
    """Executes full 6-pillar analysis pipeline."""
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
    time.sleep(0.3)
    prog.empty()
    return data, tech, sent, qual, sig

def render_report(data, tech, sent, qual, sig):
    """Renders complete Material Design 3 Dark report."""
    curr = data.get("currency", "USD")
    symbol = data["symbol"]
    price_str = format_currency(data.get("current_price"), curr)
    mcap_str = format_currency(data.get("market_cap"), curr)

    # ── Header Card ──
    header_html = f"""
    <div class="m3-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px;">
            <div>
                <h1>{symbol}</h1>
                <p style="margin: 8px 0 0 0; color: #EADDFF; font-size: 1.4rem; font-weight: 500;">{data.get('company_name', symbol)}</p>
                <p style="margin: 6px 0 0 0; color: #CAC4D0; font-size: 1.05rem;">{data['exchange_info']['exchange']} ({data['exchange_info']['country']}) &bull; {data.get('sector', 'N/A')} &bull; {data.get('industry', 'N/A')}</p>
            </div>
            <div style="text-align: right;">
                {get_signal_badge(sig['signal'])}
                <p style="margin: 10px 0 0 0; color: #EADDFF; font-size: 1.1rem;">Confidence: <strong>{sig['confidence_pct']}%</strong></p>
            </div>
        </div>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.2); margin: 24px 0 18px 0;">
        <div style="display: flex; gap: 40px; flex-wrap: wrap;">
            <div><span style="color: #CAC4D0; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 1px;">Current Price</span><br><span style="font-size: 1.6rem; font-weight: 700; color: #FFFFFF;">{price_str}</span></div>
            <div><span style="color: #CAC4D0; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 1px;">Market Cap</span><br><span style="font-size: 1.6rem; font-weight: 700; color: #FFFFFF;">{mcap_str}</span></div>
            <div><span style="color: #CAC4D0; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 1px;">Composite Score</span><br><span style="font-size: 1.6rem; font-weight: 700; color: #D0BCFF;">{sig['composite_score']} / 100</span></div>
        </div>
    </div>
    """
    st.markdown(clean_html(header_html), unsafe_allow_html=True)

    # ── Score Gauge + Pillar Bars ──
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

    # ── Bull / Bear Cases ──
    col_bull, col_bear = st.columns(2)
    with col_bull:
        bull_html = '<div class="m3-card"><div class="m3-section-title" style="color: #6DD58C;"><span class="material-symbols-outlined">trending_up</span> Bull Catalysts</div>'
        for p in sig.get("key_positives", []):
            bull_html += f'<div class="m3-bull-item">✅ {p}</div>'
        bull_html += '</div>'
        st.markdown(clean_html(bull_html), unsafe_allow_html=True)
    with col_bear:
        bear_html = '<div class="m3-card"><div class="m3-section-title" style="color: #F2B8B5;"><span class="material-symbols-outlined">trending_down</span> Bear Risks</div>'
        for r in sig.get("key_risks", []):
            bear_html += f'<div class="m3-bear-item">⚠️ {r}</div>'
        bear_html += '</div>'
        st.markdown(clean_html(bear_html), unsafe_allow_html=True)

    # ── Financial Metrics Table ──
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

    # ── Technical Analysis + Analyst Consensus ──
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
        for item in tech_items:
            tech_html += f'<p style="margin: 10px 0; font-size: 1.05rem;">{item}</p>'
        if tech.get("signals"):
            for s in tech["signals"][:3]:
                tech_html += f'<div class="m3-headline-item">{s}</div>'
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
        analyst_html += f'<p style="margin: 10px 0; font-size: 1.05rem;"><strong>Target Price:</strong> {target_mean} ({target_low} &ndash; {target_high})</p>'
        analyst_html += f'<p style="margin: 10px 0; font-size: 1.05rem;"><strong>Implied Upside:</strong> {upside}</p>'
        analyst_html += f'<p style="margin: 10px 0; font-size: 1.05rem;"><strong>Wall St Rating:</strong> {get_chip(rec_key)}</p>'
        analyst_html += f'<p style="margin: 12px 0 0 0; font-size: 1.02rem; color: #CAC4D0;">Buy: {rec_b.get("buy", 0) + rec_b.get("strongBuy", 0)} &bull; Hold: {rec_b.get("hold", 0)} &bull; Sell: {rec_b.get("sell", 0) + rec_b.get("underperform", 0)}</p>'
        analyst_html += '</div>'
        st.markdown(clean_html(analyst_html), unsafe_allow_html=True)

    # ── Sentiment Analysis ──
    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">newspaper</span> News & Social Sentiment</div>'), unsafe_allow_html=True)
    sent_html = f'<div class="m3-card">'
    sent_html += f'<p style="font-size: 1.08rem; margin-bottom: 16px;"><strong>Sentiment Rating:</strong> {get_chip(sent["label"])} &nbsp; <strong>Score:</strong> {sent["sentiment_score"]:.1f}/100 &nbsp; <strong>Polarity Index:</strong> {sent["combined_polarity"]}</p>'
    if sent.get("positive_highlights"):
        for h in sent["positive_highlights"][:3]:
            sent_html += f'<div class="m3-bull-item">📰 {h}</div>'
    if sent.get("negative_highlights"):
        for h in sent["negative_highlights"][:3]:
            sent_html += f'<div class="m3-bear-item">📰 {h}</div>'
    sent_html += '</div>'
    st.markdown(clean_html(sent_html), unsafe_allow_html=True)

    # ── Qualitative / Macro / Moat ──
    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">shield</span> Qualitative, Macro & Competitive Moat</div>'), unsafe_allow_html=True)
    qual_html = '<div class="m3-card">'
    qual_html += f'<p style="font-size: 1.08rem; margin-bottom: 16px;"><strong>Economic Moat:</strong> {get_chip(qual["moat"]["moat_tier"])} &nbsp; <strong>Valuation Pricing:</strong> {get_chip(qual["priced_in"]["valuation_tier"])}</p>'
    for pt in qual.get("priced_in", {}).get("priced_in_points", []):
        qual_html += f'<div class="m3-headline-item">🔹 {pt}</div>'
    for m in qual.get("macro_policy", {}).get("macro_factors", []):
        qual_html += f'<div class="m3-headline-item">🌍 {m}</div>'
    for r in qual.get("macro_policy", {}).get("policy_risks", []):
        qual_html += f'<div class="m3-bear-item">⚖️ {r}</div>'
    qual_html += '</div>'
    st.markdown(clean_html(qual_html), unsafe_allow_html=True)

    # ── Footer ──
    st.markdown(clean_html(f'<div class="m3-footer">Aegis Equity Terminal &bull; Analysis generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>For educational purposes only. Not financial advice.</div>'), unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MAIN STREAMLIT APPLICATION ENTRY POINT
# ═══════════════════════════════════════════

st.set_page_config(
    page_title="Aegis Equity Terminal",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(M3_DARK_CSS, unsafe_allow_html=True)

# ── Sidebar Setup ──
with st.sidebar:
    st.markdown(clean_html("""
    <div style="padding: 12px 0;">
        <h2 style="font-family: 'Google Sans', sans-serif; color: #D0BCFF; font-size: 1.8rem; margin: 0; display: flex; align-items: center; gap: 10px;">
            <span class="material-symbols-outlined" style="font-size: 2.2rem;">shield</span> Aegis Equity
        </h2>
        <p style="color: #CAC4D0; font-size: 0.95rem; margin: 4px 0 0 0;">Multi-Factor Stock Intelligence</p>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("---")

    # Selectbox or free-text input pattern without session state collision
    st.markdown("### Stock Selection")
    
    preset = st.selectbox(
        "Select Ticker Preset or Custom",
        options=["Custom Ticker Input", "AAPL — Apple Inc.", "NVDA — NVIDIA Corp", "MSFT — Microsoft", "TSLA — Tesla", "CBA.AX — Commonwealth Bank", "SHEL.L — Shell plc"],
        index=0
    )

    default_val = ""
    if preset != "Custom Ticker Input":
        default_val = preset.split(" ")[0]

    ticker_text = st.text_input(
        "Ticker Symbol",
        value=default_val,
        placeholder="e.g. AAPL, NVDA, CBA.AX, SHEL.L",
        help="Supports US (AAPL) and international tickers (CBA.AX, SHEL.L, SAP.DE)"
    )

    submit_btn = st.button("🔍  Run Analysis", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown(clean_html("""
    <div style="font-size: 0.88rem; color: #CAC4D0; line-height: 1.6;">
        <strong>6 Analytical Pillars:</strong><br>
        • Financial Fundamentals (25%)<br>
        • Valuation Multiples (20%)<br>
        • Technical Momentum (15%)<br>
        • News & Sentiment (15%)<br>
        • Analyst Consensus (15%)<br>
        • Macro & Moat (10%)
    </div>
    """), unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Aegis Equity Engine v2.0")

# ── Main Content Area ──
target_ticker = ticker_text.strip().upper() if ticker_text else None

if submit_btn and target_ticker:
    try:
        data, tech, sent, qual, sig = run_analysis(target_ticker)
        render_report(data, tech, sent, qual, sig)
    except Exception as e:
        st.error(f"Error executing analysis for '{target_ticker}': {e}")
elif target_ticker and preset != "Custom Ticker Input":
    # Auto-run when a preset is selected
    try:
        data, tech, sent, qual, sig = run_analysis(target_ticker)
        render_report(data, tech, sent, qual, sig)
    except Exception as e:
        st.error(f"Error executing analysis for '{target_ticker}': {e}")
else:
    # Welcome Landing Page
    landing_html = """
    <div style="text-align: center; padding: 70px 20px;">
        <div style="display: inline-block; background: #4F378B; border-radius: 32px; padding: 24px; margin-bottom: 24px;">
            <span class="material-symbols-outlined" style="font-size: 4rem; color: #D0BCFF;">shield_with_house</span>
        </div>
        <h1 style="font-family: 'Google Sans', sans-serif; color: #EADDFF; font-weight: 700; font-size: 3rem; margin-bottom: 16px;">Aegis Equity Terminal</h1>
        <p style="color: #CAC4D0; font-size: 1.25rem; max-width: 700px; margin: 0 auto 32px auto; line-height: 1.6;">Enter any equity ticker symbol in the sidebar to execute a complete 6-pillar analysis across financial health, valuation multiples, technical momentum, news sentiment, analyst targets, and macroeconomic positioning.</p>
        <div style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
            <span class="m3-chip" style="font-size: 1.05rem;">🇺🇸 US Equities (AAPL, NVDA, TSLA)</span>
            <span class="m3-chip" style="font-size: 1.05rem;">🇦🇺 ASX Equities (CBA.AX, BHP.AX)</span>
            <span class="m3-chip" style="font-size: 1.05rem;">🇬🇧 LSE Equities (SHEL.L, AZN.L)</span>
            <span class="m3-chip" style="font-size: 1.05rem;">🇪🇺 EU Equities (SAP.DE)</span>
        </div>
    </div>
    """
    st.markdown(clean_html(landing_html), unsafe_allow_html=True)
