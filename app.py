"""
Aegis Equity Terminal - Streamlit Web Application
Material Design 3 Dark themed multi-factor stock analysis workstation.
"""
import streamlit as st
import plotly.graph_objects as go
import time
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

# ─── Material Design 3 Dark Palette & Custom CSS ───
M3_DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');

:root {
    --md-bg: #0F0E17;
    --md-surface: #1A1827;
    --md-surface-high: #252238;
    --md-surface-highest: #322E4A;
    --md-border: #3A3554;
    --md-text-primary: #F4F3F9;
    --md-text-secondary: #B8B3CE;
    --md-text-muted: #8C86A8;
    --md-primary: #D0BCFF;
    --md-on-primary: #1D0047;
    --md-primary-container: #4F378B;
    --md-on-primary-container: #EADDFF;
    --md-accent: #A855F7;
    --md-font-brand: 'Google Sans', sans-serif;
    --md-font-plain: 'Roboto', sans-serif;
}

/* Global App Styling */
.stApp {
    background-color: var(--md-bg) !important;
    color: var(--md-text-primary) !important;
    font-family: var(--md-font-plain) !important;
    font-size: 1.05rem !important;
}

[data-testid="stSidebar"] {
    background-color: var(--md-surface) !important;
    border-right: 1px solid var(--md-border) !important;
}

/* High Contrast Primary Button */
.stButton > button, div.stButton > button[kind="primary"] {
    background-color: var(--md-primary) !important;
    color: var(--md-on-primary) !important;
    font-family: var(--md-font-brand) !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 14px 28px !important;
    border-radius: 14px !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(208, 188, 255, 0.25) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover, div.stButton > button[kind="primary"]:hover {
    background-color: #EADDFF !important;
    color: #1D0047 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(208, 188, 255, 0.4) !important;
}

/* Cards */
.m3-card {
    background: var(--md-surface);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 24px;
    border: 1px solid var(--md-border);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}

.m3-header {
    background: linear-gradient(135deg, #2D1B4E 0%, #1A1827 100%);
    color: #FFFFFF;
    border-radius: 28px;
    padding: 36px;
    margin-bottom: 28px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
    border: 1px solid #6750A4;
}

.m3-header h1 {
    font-family: var(--md-font-brand) !important;
    font-weight: 700;
    font-size: 3rem !important;
    letter-spacing: -0.5px;
    margin: 0;
    color: #F4F3F9;
}

/* Signal Badges & Chips */
.m3-signal-badge {
    font-size: 2rem !important;
    font-weight: 700;
    padding: 14px 32px;
    border-radius: 20px;
    display: inline-block;
    letter-spacing: 1.5px;
}

.m3-signal-buy { background: #143A27; color: #4ADE80; border: 2px solid #22C55E; }
.m3-signal-sell { background: #3E1619; color: #F87171; border: 2px solid #EF4444; }
.m3-signal-hold { background: #3B270A; color: #FBBF24; border: 2px solid #F59E0B; }

.m3-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    border-radius: 12px;
    font-size: 1rem !important;
    font-weight: 600;
}

.m3-chip-buy { background: #143A27; color: #4ADE80; border: 1px solid #22C55E; }
.m3-chip-sell { background: #3E1619; color: #F87171; border: 1px solid #EF4444; }
.m3-chip-hold { background: #3B270A; color: #FBBF24; border: 1px solid #F59E0B; }

/* Pillar Bars */
.m3-pillar-container {
    margin-bottom: 18px;
}

.m3-pillar-label {
    font-size: 1.08rem !important;
    font-weight: 500;
    color: var(--md-text-primary);
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.m3-pillar-bar-bg {
    background: var(--md-surface-high);
    height: 14px;
    border-radius: 7px;
    overflow: hidden;
    margin-bottom: 18px;
    border: 1px solid var(--md-border);
}

.m3-pillar-bar-fill {
    background: linear-gradient(90deg, #A855F7 0%, #D0BCFF 100%);
    height: 100%;
    border-radius: 7px;
}

/* Bull & Bear items */
.m3-bull-item {
    padding: 14px 20px;
    background: #142E1F;
    border-radius: 14px;
    margin-bottom: 12px;
    font-size: 1.05rem !important;
    color: #DCFCE7;
    border-left: 5px solid #22C55E;
    line-height: 1.5;
}

.m3-bear-item {
    padding: 14px 20px;
    background: #331518;
    border-radius: 14px;
    margin-bottom: 12px;
    font-size: 1.05rem !important;
    color: #FEE2E2;
    border-left: 5px solid #EF4444;
    line-height: 1.5;
}

.m3-headline-item {
    padding: 14px 20px;
    background: var(--md-surface-high);
    border-radius: 14px;
    margin-bottom: 12px;
    font-size: 1.05rem !important;
    color: var(--md-text-primary);
    border-left: 5px solid var(--md-primary);
    line-height: 1.5;
}

/* Table styling */
.m3-table-container {
    overflow-x: auto;
    margin-bottom: 24px;
}

.m3-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid var(--md-border);
    background: var(--md-surface);
}

.m3-table th {
    background: var(--md-primary-container);
    color: var(--md-on-primary-container);
    font-weight: 700;
    font-size: 1.02rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 18px 22px;
    text-align: left;
    border-bottom: 2px solid var(--md-border);
}

.m3-table td {
    padding: 18px 22px;
    border-bottom: 1px solid var(--md-border);
    font-size: 1.1rem !important;
    color: var(--md-text-primary);
}

.m3-table tr:last-child td {
    border-bottom: none;
}

.m3-section-title {
    font-family: var(--md-font-brand) !important;
    font-weight: 700;
    font-size: 1.6rem !important;
    color: var(--md-primary);
    margin: 28px 0 18px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.m3-footer {
    text-align: center;
    font-size: 0.95rem !important;
    color: var(--md-text-muted);
    margin-top: 60px;
    padding: 28px;
    border-top: 1px solid var(--md-border);
}

/* Hide default Streamlit clutter */
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
    """Creates a Plotly gauge chart with clean M3 dark colors."""
    if score >= 70:
        bar_color = "#4ADE80"
    elif score >= 40:
        bar_color = "#FBBF24"
    else:
        bar_color = "#F87171"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"size": 22, "family": "Google Sans, sans-serif", "color": "#B8B3CE"}},
        number={"font": {"size": 52, "family": "Google Sans, sans-serif", "color": "#F4F3F9"}, "suffix": "/100"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 2, "tickcolor": "#8C86A8", "dtick": 20, "tickfont": {"color": "#B8B3CE", "size": 14}},
            "bar": {"color": bar_color, "thickness": 0.35},
            "bgcolor": "#252238",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "#3E1619"},
                {"range": [30, 55], "color": "#3B270A"},
                {"range": [55, 75], "color": "#252238"},
                {"range": [75, 100], "color": "#143A27"},
            ],
            "threshold": {
                "line": {"color": "#D0BCFF", "width": 4},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=270,
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
                <p style="margin: 8px 0 0 0; color: #EADDFF; font-size: 1.45rem; font-weight: 500;">{data.get('company_name', symbol)}</p>
                <p style="margin: 6px 0 0 0; color: #B8B3CE; font-size: 1.1rem;">{data['exchange_info']['exchange']} ({data['exchange_info']['country']}) &bull; {data.get('sector', 'N/A')} &bull; {data.get('industry', 'N/A')}</p>
            </div>
            <div style="text-align: right;">
                {get_signal_badge(sig['signal'])}
                <p style="margin: 12px 0 0 0; color: #EADDFF; font-size: 1.15rem;">Confidence: <strong>{sig['confidence_pct']}%</strong></p>
            </div>
        </div>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.18); margin: 26px 0 20px 0;">
        <div style="display: flex; gap: 48px; flex-wrap: wrap;">
            <div><span style="color: #B8B3CE; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Current Price</span><br><span style="font-size: 1.7rem; font-weight: 700; color: #FFFFFF;">{price_str}</span></div>
            <div><span style="color: #B8B3CE; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Market Cap</span><br><span style="font-size: 1.7rem; font-weight: 700; color: #FFFFFF;">{mcap_str}</span></div>
            <div><span style="color: #B8B3CE; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Composite Score</span><br><span style="font-size: 1.7rem; font-weight: 700; color: #D0BCFF;">{sig['composite_score']} / 100</span></div>
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
        bull_html = '<div class="m3-card"><div class="m3-section-title" style="color: #4ADE80;"><span class="material-symbols-outlined">trending_up</span> Bull Catalysts</div>'
        for p in sig.get("key_positives", []):
            bull_html += f'<div class="m3-bull-item">✅ {p}</div>'
        bull_html += '</div>'
        st.markdown(clean_html(bull_html), unsafe_allow_html=True)
    with col_bear:
        bear_html = '<div class="m3-card"><div class="m3-section-title" style="color: #F87171;"><span class="material-symbols-outlined">trending_down</span> Bear Risks</div>'
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
            tech_html += f'<p style="margin: 12px 0; font-size: 1.08rem;">{item}</p>'
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
        analyst_html += f'<p style="margin: 12px 0; font-size: 1.08rem;"><strong>Target Price:</strong> {target_mean} ({target_low} &ndash; {target_high})</p>'
        analyst_html += f'<p style="margin: 12px 0; font-size: 1.08rem;"><strong>Implied Upside:</strong> {upside}</p>'
        analyst_html += f'<p style="margin: 12px 0; font-size: 1.08rem;"><strong>Wall St Rating:</strong> {get_chip(rec_key)}</p>'
        analyst_html += f'<p style="margin: 14px 0 0 0; font-size: 1.05rem; color: #B8B3CE;">Buy: {rec_b.get("buy", 0) + rec_b.get("strongBuy", 0)} &bull; Hold: {rec_b.get("hold", 0)} &bull; Sell: {rec_b.get("sell", 0) + rec_b.get("underperform", 0)}</p>'
        analyst_html += '</div>'
        st.markdown(clean_html(analyst_html), unsafe_allow_html=True)

    # ── Sentiment Analysis ──
    st.markdown(clean_html('<div class="m3-section-title"><span class="material-symbols-outlined">newspaper</span> News & Social Sentiment</div>'), unsafe_allow_html=True)
    sent_html = f'<div class="m3-card">'
    sent_html += f'<p style="font-size: 1.1rem; margin-bottom: 18px;"><strong>Sentiment Rating:</strong> {get_chip(sent["label"])} &nbsp; <strong>Score:</strong> {sent["sentiment_score"]:.1f}/100 &nbsp; <strong>Polarity Index:</strong> {sent["combined_polarity"]}</p>'
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
    qual_html += f'<p style="font-size: 1.1rem; margin-bottom: 18px;"><strong>Economic Moat:</strong> {get_chip(qual["moat"]["moat_tier"])} &nbsp; <strong>Valuation Pricing:</strong> {get_chip(qual["priced_in"]["valuation_tier"])}</p>'
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
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(M3_DARK_CSS, unsafe_allow_html=True)

# ── Sidebar Setup ──
with st.sidebar:
    st.markdown(clean_html("""
    <div style="padding: 16px 0 8px 0;">
        <h2 style="font-family: 'Google Sans', sans-serif; color: #D0BCFF; font-size: 1.9rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 12px;">
            <span class="material-symbols-outlined" style="font-size: 2.4rem;">shield</span> Aegis Equity
        </h2>
        <p style="color: #B8B3CE; font-size: 0.95rem; margin: 6px 0 0 0;">Multi-Factor Stock Intelligence</p>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### Stock Search")

    ticker_input = st.text_input(
        "Enter Ticker Symbol",
        placeholder="e.g. AAPL, NVDA, CBA.AX",
        help="Supports US (AAPL, TSLA) and International equities (CBA.AX, SHEL.L, SAP.DE)"
    )

    submit_btn = st.button("🔍  Run Analysis", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown(clean_html("""
    <div style="font-size: 0.9rem; color: #B8B3CE; line-height: 1.7;">
        <strong>6 Analytical Pillars:</strong><br>
        1. Financial Fundamentals (25%)<br>
        2. Valuation Multiples (20%)<br>
        3. Technical Momentum (15%)<br>
        4. News & Sentiment (15%)<br>
        5. Analyst Consensus (15%)<br>
        6. Macro & Moat (10%)
    </div>
    """), unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Aegis Equity Engine v2.0")

# ── Main Content Area ──
target_ticker = ticker_input.strip().upper() if ticker_input else None

if submit_btn and target_ticker:
    try:
        data, tech, sent, qual, sig = run_analysis(target_ticker)
        render_report(data, tech, sent, qual, sig)
    except Exception as e:
        st.error(f"Error executing analysis for '{target_ticker}': {e}")
else:
    # Welcome Landing Page
    landing_html = """
    <div style="text-align: center; padding: 80px 20px;">
        <div style="display: inline-block; background: #322E4A; border: 1px solid #4F378B; border-radius: 36px; padding: 28px; margin-bottom: 28px; box-shadow: 0 8px 24px rgba(0,0,0,0.4);">
            <span class="material-symbols-outlined" style="font-size: 4.5rem; color: #D0BCFF;">shield_with_house</span>
        </div>
        <h1 style="font-family: 'Google Sans', sans-serif; color: #F4F3F9; font-weight: 700; font-size: 3.2rem; margin-bottom: 18px;">Aegis Equity Terminal</h1>
        <p style="color: #B8B3CE; font-size: 1.3rem; max-width: 720px; margin: 0 auto 36px auto; line-height: 1.6;">Enter any equity ticker symbol in the sidebar to execute a complete 6-pillar quantitative report covering financial health, valuation multiples, technical momentum, news sentiment, analyst targets, and macroeconomic positioning.</p>
        <div style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
            <span class="m3-chip m3-chip-buy" style="font-size: 1.05rem;">🇺🇸 US Equities (AAPL, NVDA, TSLA)</span>
            <span class="m3-chip m3-chip-buy" style="font-size: 1.05rem;">🇦🇺 ASX Equities (CBA.AX, BHP.AX)</span>
            <span class="m3-chip m3-chip-buy" style="font-size: 1.05rem;">🇬🇧 LSE Equities (SHEL.L, AZN.L)</span>
            <span class="m3-chip m3-chip-buy" style="font-size: 1.05rem;">🇪🇺 EU Equities (SAP.DE)</span>
        </div>
    </div>
    """
    st.markdown(clean_html(landing_html), unsafe_allow_html=True)
