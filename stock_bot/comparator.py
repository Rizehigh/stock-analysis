"""
Stock Comparator Engine - Multi-Equity Comparison (up to 5 stocks)
Compares 1 to 5 equities side-by-side across Composite Scores, 6-Pillar breakdowns, Valuation Multiples, and Bull/Bear catalysts.
"""
import plotly.graph_objects as go
from stock_bot.config import format_currency

PALETTE = ["#CBA6F7", "#86EFAC", "#FDE047", "#93C5FD", "#F9A8D4"]

def build_multi_pillar_chart(sig_map: dict):
    """Creates a grouped bar chart comparing 6 pillar scores for up to 5 stocks."""
    categories = [
        "Fundamentals", "Valuation", "Technicals", 
        "Sentiment", "Analyst", "Macro & Moat"
    ]
    keys = ["fundamentals", "valuation", "technicals", "sentiment", "analyst", "macro_moat"]
    
    fig = go.Figure()
    
    for idx, (sym, sig) in enumerate(sig_map.items()):
        scores = [sig["pillar_scores"][k] for k in keys]
        color = PALETTE[idx % len(PALETTE)]
        fig.add_trace(go.Bar(
            name=sym,
            x=categories,
            y=scores,
            marker_color=color
        ))
        
    fig.update_layout(
        barmode="group",
        height=380,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#E2E8F0", size=14), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickfont=dict(color="#E2E8F0", size=13), gridcolor="#383854"),
        yaxis=dict(range=[0, 100], tickfont=dict(color="#E2E8F0", size=13), gridcolor="#383854", title="Pillar Score (0-100)"),
        font=dict(family="Inter, sans-serif")
    )
    return fig

def render_multi_comparison_table(data_map: dict, sig_map: dict):
    """Generates an HTML comparison table for up to 5 stocks."""
    symbols = list(data_map.keys())
    
    def fmt(val, fmt_str=".1f", suffix="", prefix=""):
        if val is None: return "N/A"
        try: return f"{prefix}{val:{fmt_str}}{suffix}"
        except: return "N/A"
        
    metrics = [
        ("Composite Score", lambda s, d: f"<strong>{s['composite_score']}</strong> / 100"),
        ("Signal & Conf.", lambda s, d: f"{s['signal']} ({s['confidence_pct']}%)"),
        ("Current Price", lambda s, d: format_currency(d.get("current_price"), d.get("currency", "USD"))),
        ("Market Cap", lambda s, d: format_currency(d.get("market_cap"), d.get("currency", "USD"))),
        ("P/E Ratio (TTM)", lambda s, d: fmt(d.get("pe_ratio"))),
        ("Forward P/E", lambda s, d: fmt(d.get("forward_pe"))),
        ("PEG Ratio", lambda s, d: fmt(d.get("peg_ratio"), ".2f")),
        ("Price to Sales", lambda s, d: fmt(d.get("price_to_sales"), ".2f")),
        ("Profit Margin", lambda s, d: fmt(d.get("profit_margins") * 100 if d.get("profit_margins") else None, ".1f", "%")),
        ("Return on Equity", lambda s, d: fmt(d.get("return_on_equity") * 100 if d.get("return_on_equity") else None, ".1f", "%")),
        ("Revenue Growth", lambda s, d: fmt(d.get("revenue_growth") * 100 if d.get("revenue_growth") else None, ".1f", "%")),
        ("Dividend Yield", lambda s, d: fmt(d.get("dividend_yield_pct"), ".2f", "%")),
        ("Debt to Equity", lambda s, d: fmt(d.get("debt_to_equity"))),
        ("Wall St Rating", lambda s, d: str(d.get("recommendation_key", "N/A")).upper()),
        ("Implied Upside", lambda s, d: fmt(d.get("implied_upside_pct"), "+.1f", "%")),
    ]
    
    col_width = int(70 / max(1, len(symbols)))
    
    html = f"""
    <div class="m3-table-container">
        <table class="m3-table">
            <thead>
                <tr>
                    <th style="width: 30%;">Metric</th>
    """
    for idx, sym in enumerate(symbols):
        color = PALETTE[idx % len(PALETTE)]
        c_name = data_map[sym].get("company_name", sym)
        html += f'<th style="width: {col_width}%; color: {color};">{sym}<br><span style="font-size: 0.85rem; text-transform: none; color: #A6ADC8;">{c_name[:18]}</span></th>'
    
    html += "</tr></thead><tbody>"
    
    for row_label, extractor in metrics:
        html += f"<tr><td><strong>{row_label}</strong></td>"
        for sym in symbols:
            html += f"<td>{extractor(sig_map[sym], data_map[sym])}</td>"
        html += "</tr>"
        
    html += "</tbody></table></div>"
    return html
