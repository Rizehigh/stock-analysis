"""
DeepSeek Stock Analysis Bot - Streamlit Web Application
Material Design 3 themed interactive stock analysis terminal.
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

# ─── Material Design 3: Custom CSS Injection ───
M3_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');

:root {
    --md-sys-color-primary: #6750A4;
    --md-sys-color-on-primary: #FFFFFF;
    --md-sys-color-primary-container: #EADDFF;
    --md-sys-color-on-primary-container: #21005D;
    --md-sys-color-secondary: #625B71;
    --md-sys-color-secondary-container: #E8DEF8;
    --md-sys-color-tertiary: #7D5260;
    --md-sys-color-tertiary-container: #FFD8E4;
    --md-sys-color-surface: #FFFBFE;
    --md-sys-color-surface-variant: #E7E0EC;
    --md-sys-color-on-surface: #1C1B1F;
    --md-sys-color-on-surface-variant: #49454F;
    --md-sys-color-outline: #79747E;
    --md-sys-color-outline-variant: #CAC4D0;
    --md-sys-color-error: #B3261E;
    --md-sys-color-error-container: #F9DEDC;
    --md-sys-color-success: #1B6B2E;
    --md-sys-color-success-container: #C4EED0;
    --md-sys-color-warning: #7C5800;
    --md-sys-color-warning-container: #FFDDB3;
    --md-ref-typeface-brand: 'Google Sans', 'Roboto', sans-serif;
    --md-ref-typeface-plain: 'Roboto', sans-serif;
}

[data-theme="dark"] :root,
[data-testid="stAppViewContainer"][style*="dark"] {
    --md-sys-color-primary: #D0BCFF;
    --md-sys-color-on-primary: #381E72;
    --md-sys-color-primary-container: #4F378B;
    --md-sys-color-surface: #1C1B1F;
    --md-sys-color-on-surface: #E6E1E5;
}

.stApp {
    font-family: var(--md-ref-typeface-plain) !important;
}

.m3-card {
    background: var(--md-sys-color-surface);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    border: 1px solid var(--md-sys-color-outline-variant);
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
}

.m3-card-elevated {
    background: var(--md-sys-color-surface);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15), 0 1px 3px rgba(0,0,0,0.1);
    border: none;
}

.m3-header {
    background: linear-gradient(135deg, #6750A4 0%, #381E72 100%);
    color: white;
    border-radius: 28px;
    padding: 32px;
    margin-bottom: 24px;
    box-shadow: 0 6px 12px rgba(103, 80, 164, 0.3);
}

.m3-header h1 {
    font-family: var(--md-ref-typeface-brand) !important;
    font-weight: 500;
    letter-spacing: -0.5px;
    margin: 0;
}

.m3-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 16px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    border: 1px solid var(--md-sys-color-outline);
}

.m3-chip-buy {
    background: var(--md-sys-color-success-container);
    color: var(--md-sys-color-success);
    border-color: var(--md-sys-color-success);
}

.m3-chip-sell {
    background: var(--md-sys-color-error-container);
    color: var(--md-sys-color-error);
    border-color: var(--md-sys-color-error);
}

.m3-chip-hold {
    background: var(--md-sys-color-warning-container);
    color: var(--md-sys-color-warning);
    border-color: var(--md-sys-color-warning);
}

.m3-signal-badge {
    font-size: 1.8rem;
    font-weight: 700;
    padding: 12px 28px;
    border-radius: 16px;
    display: inline-block;
    letter-spacing: 1px;
}

.m3-signal-buy { background: #C4EED0; color: #0D3B1A; }
.m3-signal-sell { background: #F9DEDC; color: #8C1D18; }
.m3-signal-hold { background: #FFDDB3; color: #4A3800; }

.m3-metric-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--md-sys-color-on-surface-variant);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
}

.m3-metric-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--md-sys-color-on-surface);
    font-family: var(--md-ref-typeface-brand);
}

.m3-pillar-label {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--md-sys-color-on-surface);
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
}

.m3-pillar-bar-bg {
    background: var(--md-sys-color-surface-variant);
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 14px;
}

.m3-pillar-bar-fill {
    background: var(--md-sys-color-primary);
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}

.m3-bull-item {
    padding: 8px 14px;
    background: var(--md-sys-color-success-container);
    border-radius: 12px;
    margin-bottom: 8px;
    font-size: 0.9rem;
    color: var(--md-sys-color-success);
}

.m3-bear-item {
    padding: 8px 14px;
    background: var(--md-sys-color-error-container);
    border-radius: 12px;
    margin-bottom: 8px;
    font-size: 0.9rem;
    color: var(--md-sys-color-error);
}

.m3-headline-item {
    padding: 10px 14px;
    background: var(--md-sys-color-secondary-container);
    border-radius: 12px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: var(--md-sys-color-on-surface);
}

.m3-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--md-sys-color-outline-variant);
}

.m3-table th {
    background: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
    font-weight: 500;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 12px 16px;
    text-align: left;
}

.m3-table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--md-sys-color-outline-variant);
    font-size: 0.92rem;
}

.m3-table tr:last-child td {
    border-bottom: none;
}

.m3-divider {
    border: none;
    border-top: 1px solid var(--md-sys-color-outline-variant);
    margin: 20px 0;
}

.m3-section-title {
    font-family: var(--md-ref-typeface-brand) !important;
    font-weight: 500;
    font-size: 1.25rem;
    color: var(--md-sys-color-on-surface);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.m3-footer {
    text-align: center;
    font-size: 0.8rem;
    color: var(--md-sys-color-on-surface-variant);
    margin-top: 40px;
    padding: 20px;
}

/* Hide default Streamlit branding elements */
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
    return f"""
    <div class="m3-pillar-label"><span>{name} ({weight})</span><span>{score:.1f}</span></div>
    <div class="m3-pillar-bar-bg"><div class="m3-pillar-bar-fill" style="width: {score}%;"></div></div>
    """


def build_gauge_chart(score: float, title: str = "Composite Score"):
    """Creates a Plotly gauge chart with M3 colors."""
    if score >= 70:
        bar_color = "#1B6B2E"
    elif score >= 40:
        bar_color = "#7C5800"
    else:
        bar_color = "#B3261E"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"size": 16, "family": "Google Sans, Roboto, sans-serif", "color": "#49454F"}},
        number={"font": {"size": 42, "family": "Google Sans, Roboto, sans-serif", "color": "#1C1B1F"}, "suffix": "/100"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#CAC4D0", "dtick": 20},
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": "#F3EDF7",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "#F9DEDC"},
                {"range": [30, 55], "color": "#FFDDB3"},
                {"range": [55, 75], "color": "#EADDFF"},
                {"range": [75, 100], "color": "#C4EED0"},
            ],
            "threshold": {
                "line": {"color": "#6750A4", "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Google Sans, Roboto, sans-serif"},
    )
    return fig


def run_analysis(ticker: str):
    """Executes the full 6-pillar analysis pipeline for a given ticker."""
    prog = st.progress(0, text="Fetching market & financial data...")
    data = fetch_stock_data(ticker)
    prog.progress(20, text="Computing technical indicators...")
    tech = analyze_technicals(data)
    prog.progress(45, text="Analyzing news & social sentiment...")
    sent = analyze_sentiment(ticker, data.get("company_name", ticker))
    prog.progress(65, text="Qualitative, macro & moat modeling...")
    qual = analyze_qualitative_factors(data)
    prog.progress(85, text="Computing 6-pillar composite score...")
    sig = compute_overall_signal(data, tech, sent, qual)
    prog.progress(100, text="Analysis complete!")
    time.sleep(0.4)
    prog.empty()
    return data, tech, sent, qual, sig


def render_report(data, tech, sent, qual, sig):
    """Renders the full Material Design 3 stock analysis report."""
    curr = data.get("currency", "USD")
    symbol = data["symbol"]
    price_str = format_currency(data.get("current_price"), curr)
    mcap_str = format_currency(data.get("market_cap"), curr)

    # ── Header Card ──
    st.markdown(f"""
    <div class="m3-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <h1 style="font-size: 2rem;">{symbol}</h1>
                <p style="margin: 6px 0 0 0; opacity: 0.85; font-size: 1.1rem;">{data.get('company_name', symbol)}</p>
                <p style="margin: 4px 0 0 0; opacity: 0.7; font-size: 0.88rem;">{data['exchange_info']['exchange']} ({data['exchange_info']['country']}) &bull; {data.get('sector', 'N/A')} &bull; {data.get('industry', 'N/A')}</p>
            </div>
            <div style="text-align: right;">
                {get_signal_badge(sig['signal'])}
                <p style="margin: 8px 0 0 0; opacity: 0.85; font-size: 0.95rem;">Confidence: <strong>{sig['confidence_pct']}%</strong></p>
            </div>
        </div>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0 14px 0;">
        <div style="display: flex; gap: 32px; flex-wrap: wrap;">
            <div><span style="opacity: 0.7; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px;">Current Price</span><br><span style="font-size: 1.3rem; font-weight: 700;">{price_str}</span></div>
            <div><span style="opacity: 0.7; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px;">Market Cap</span><br><span style="font-size: 1.3rem; font-weight: 700;">{mcap_str}</span></div>
            <div><span style="opacity: 0.7; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px;">Composite Score</span><br><span style="font-size: 1.3rem; font-weight: 700;">{sig['composite_score']} / 100</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown(pillar_html, unsafe_allow_html=True)

    # ── Bull / Bear Cases ──
    col_bull, col_bear = st.columns(2)
    with col_bull:
        bull_html = '<div class="m3-card"><div class="m3-section-title"><span class="material-symbols-outlined">trending_up</span> Bull Catalysts</div>'
        for p in sig.get("key_positives", []):
            bull_html += f'<div class="m3-bull-item">✅ {p}</div>'
        bull_html += '</div>'
        st.markdown(bull_html, unsafe_allow_html=True)
    with col_bear:
        bear_html = '<div class="m3-card"><div class="m3-section-title"><span class="material-symbols-outlined">trending_down</span> Bear Risks</div>'
        for r in sig.get("key_risks", []):
            bear_html += f'<div class="m3-bear-item">⚠️ {r}</div>'
        bear_html += '</div>'
        st.markdown(bear_html, unsafe_allow_html=True)

    # ── Financial Metrics Table ──
    st.markdown('<div class="m3-section-title"><span class="material-symbols-outlined">account_balance</span> Financial Fundamentals & Valuation</div>', unsafe_allow_html=True)

    tbl = '<table class="m3-table"><thead><tr><th>Metric</th><th>Value</th><th>Metric</th><th>Value</th></tr></thead><tbody>'
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
    tbl += '</tbody></table>'
    st.markdown(tbl, unsafe_allow_html=True)
    st.markdown('<hr class="m3-divider">', unsafe_allow_html=True)

    # ── Technical Analysis + Analyst Consensus ──
    col_tech, col_analyst = st.columns(2)

    with col_tech:
        tech_html = '<div class="m3-card"><div class="m3-section-title"><span class="material-symbols-outlined">candlestick_chart</span> Technical Analysis</div>'
        tech_items = [
            f"<strong>RSI (14-day):</strong> {tech['rsi_14']:.1f} ({tech['rsi_status']})",
            f"<strong>50-day SMA:</strong> {tech.get('sma_50') if tech.get('sma_50') else 'N/A'}",
            f"<strong>200-day SMA:</strong> {tech.get('sma_200') if tech.get('sma_200') else 'N/A'}",
            f"<strong>SMA Cross:</strong> {tech['cross_status']}",
            f"<strong>MACD:</strong> {tech['macd_data']['crossover']}",
            f"<strong>52-Week Position:</strong> {tech['fifty_two_week_pos_pct']:.1f}%",
        ]
        for item in tech_items:
            tech_html += f'<p style="margin: 8px 0; font-size: 0.92rem;">{item}</p>'
        if tech.get("signals"):
            for s in tech["signals"][:3]:
                tech_html += f'<div class="m3-headline-item">{s}</div>'
        tech_html += '</div>'
        st.markdown(tech_html, unsafe_allow_html=True)

    with col_analyst:
        target_mean = format_currency(data.get("target_mean"), curr)
        target_high = format_currency(data.get("target_high"), curr)
        target_low = format_currency(data.get("target_low"), curr)
        upside = fmt_val(data.get('implied_upside_pct'), "+.1f", "%") if data.get('implied_upside_pct') and data['implied_upside_pct'] > 0 else fmt_val(data.get('implied_upside_pct'), ".1f", "%")
        rec_key = str(data.get('recommendation_key', 'N/A')).upper()
        rec_b = data.get("rec_breakdown", {})

        analyst_html = f'<div class="m3-card"><div class="m3-section-title"><span class="material-symbols-outlined">groups</span> Analyst Consensus</div>'
        analyst_html += f'<p style="margin: 8px 0;"><strong>Avg Target:</strong> {target_mean} ({target_low} &ndash; {target_high})</p>'
        analyst_html += f'<p style="margin: 8px 0;"><strong>Implied Upside:</strong> {upside}</p>'
        analyst_html += f'<p style="margin: 8px 0;"><strong>Consensus:</strong> {get_chip(rec_key)}</p>'
        analyst_html += f'<p style="margin: 8px 0;">Strong Buy: {rec_b.get("strongBuy", 0)} &bull; Buy: {rec_b.get("buy", 0)} &bull; Hold: {rec_b.get("hold", 0)} &bull; Sell: {rec_b.get("sell", 0)}</p>'
        analyst_html += '</div>'
        st.markdown(analyst_html, unsafe_allow_html=True)

    st.markdown('<hr class="m3-divider">', unsafe_allow_html=True)

    # ── Sentiment Analysis ──
    st.markdown('<div class="m3-section-title"><span class="material-symbols-outlined">newspaper</span> News & Social Sentiment</div>', unsafe_allow_html=True)
    sent_html = f'<div class="m3-card">'
    sent_html += f'<p><strong>Classification:</strong> {get_chip(sent["label"])} &nbsp; <strong>Score:</strong> {sent["sentiment_score"]:.1f}/100 &nbsp; <strong>Polarity:</strong> {sent["combined_polarity"]} &nbsp; <strong>Headlines:</strong> {sent["headline_count"]}</p>'
    if sent.get("positive_highlights"):
        for h in sent["positive_highlights"][:3]:
            sent_html += f'<div class="m3-bull-item">📰 {h}</div>'
    if sent.get("negative_highlights"):
        for h in sent["negative_highlights"][:3]:
            sent_html += f'<div class="m3-bear-item">📰 {h}</div>'
    sent_html += '</div>'
    st.markdown(sent_html, unsafe_allow_html=True)

    st.markdown('<hr class="m3-divider">', unsafe_allow_html=True)

    # ── Qualitative / Macro / Moat ──
    st.markdown('<div class="m3-section-title"><span class="material-symbols-outlined">shield</span> Qualitative, Macro & Competitive Moat</div>', unsafe_allow_html=True)
    qual_html = '<div class="m3-card">'
    qual_html += f'<p style="margin-bottom: 12px;"><strong>Economic Moat:</strong> {get_chip(qual["moat"]["moat_tier"])} &nbsp; <strong>Valuation Pricing:</strong> {get_chip(qual["priced_in"]["valuation_tier"])}</p>'
    for pt in qual.get("priced_in", {}).get("priced_in_points", []):
        qual_html += f'<div class="m3-headline-item">🔹 {pt}</div>'
    for m in qual.get("macro_policy", {}).get("macro_factors", []):
        qual_html += f'<div class="m3-headline-item">🌍 {m}</div>'
    for r in qual.get("macro_policy", {}).get("policy_risks", []):
        qual_html += f'<div class="m3-bear-item">⚖️ {r}</div>'
    qual_html += '</div>'
    st.markdown(qual_html, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown(f'<div class="m3-footer">Analysis generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by DeepSeek Stock Analysis Bot.<br>This tool is for educational purposes only and does not constitute financial advice.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MAIN STREAMLIT PAGE LAYOUT
# ═══════════════════════════════════════════

st.set_page_config(
    page_title="DeepSeek Stock Analysis Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(M3_CSS, unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("""
    <div style="padding: 16px 0;">
        <h2 style="font-family: 'Google Sans', sans-serif; color: #6750A4; margin: 0;">📈 Stock Bot</h2>
        <p style="color: #49454F; font-size: 0.85rem; margin: 4px 0 0 0;">Multi-Factor Analysis Engine</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="m3-divider">', unsafe_allow_html=True)

    ticker_input = st.text_input(
        "Enter Stock Ticker",
        placeholder="e.g. AAPL, NVDA, CBA.AX, SHEL.L",
        help="Supports US (AAPL, MSFT) and international tickers (CBA.AX, SHEL.L, SAP.DE)",
        key="ticker_input"
    )

    analyze_btn = st.button("🔍  Run Analysis", use_container_width=True, type="primary")

    st.markdown('<hr class="m3-divider">', unsafe_allow_html=True)

    st.markdown("**Quick Tickers:**")
    qcols = st.columns(3)
    quick_tickers = ["AAPL", "NVDA", "MSFT", "TSLA", "CBA.AX", "SHEL.L", "AMZN", "GOOGL", "BHP.AX"]
    for i, qt in enumerate(quick_tickers):
        if qcols[i % 3].button(qt, key=f"qt_{qt}", use_container_width=True):
            st.session_state["ticker_input"] = qt
            st.session_state["run_ticker"] = qt

    st.markdown('<hr class="m3-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.78rem; color: #49454F; padding: 8px 0;">
        <strong>6 Analytical Pillars:</strong><br>
        1. Financial Fundamentals (25%)<br>
        2. Valuation Multiples (20%)<br>
        3. Technical Momentum (15%)<br>
        4. News & Sentiment (15%)<br>
        5. Analyst Consensus (15%)<br>
        6. Macro, Moat & Industry (10%)
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="m3-divider">', unsafe_allow_html=True)
    st.caption("Built with Streamlit & yfinance")

# ── Main Content Area ──
run_ticker = st.session_state.get("run_ticker", None)
if analyze_btn and ticker_input:
    run_ticker = ticker_input.strip().upper()
if run_ticker:
    st.session_state["run_ticker"] = None  # reset after use
    try:
        data, tech, sent, qual, sig = run_analysis(run_ticker)
        render_report(data, tech, sent, qual, sig)
    except Exception as e:
        st.error(f"Error analyzing {run_ticker}: {e}")
else:
    # Landing page
    st.markdown("""
    <div style="text-align: center; padding: 80px 20px;">
        <div style="font-size: 4rem; margin-bottom: 16px;">📈</div>
        <h1 style="font-family: 'Google Sans', sans-serif; color: #6750A4; font-weight: 500; margin-bottom: 12px;">DeepSeek Stock Analysis Bot</h1>
        <p style="color: #49454F; font-size: 1.1rem; max-width: 600px; margin: 0 auto 24px auto;">Enter any stock ticker in the sidebar to generate a comprehensive, multi-factor analysis report covering financials, technicals, sentiment, analyst consensus, and macro environment.</p>
        <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; margin-top: 20px;">
            <span class="m3-chip" style="font-size: 0.9rem;">🇺🇸 US Stocks (AAPL, NVDA, TSLA)</span>
            <span class="m3-chip" style="font-size: 0.9rem;">🇦🇺 ASX Stocks (CBA.AX, BHP.AX)</span>
            <span class="m3-chip" style="font-size: 0.9rem;">🇬🇧 LSE Stocks (SHEL.L)</span>
            <span class="m3-chip" style="font-size: 0.9rem;">🇪🇺 EU Stocks (SAP.DE)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
