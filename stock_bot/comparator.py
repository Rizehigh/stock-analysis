"""
Stock Comparator Engine - Side-by-Side Multi-Factor Comparison
Compares 2 equities across Composite Scores, 6-Pillar breakdowns, Valuation Multiples, and Bull/Bear catalysts.
"""
import plotly.graph_objects as go
from stock_bot.config import format_currency

def build_comparison_pillar_chart(sig_a, sig_b, sym_a, sym_b):
    """Creates a side-by-side Plotly grouped bar chart comparing pillar scores."""
    categories = [
        "Fundamentals", "Valuation", "Technicals", 
        "Sentiment", "Analyst", "Macro & Moat"
    ]
    keys = ["fundamentals", "valuation", "technicals", "sentiment", "analyst", "macro_moat"]
    
    scores_a = [sig_a["pillar_scores"][k] for k in keys]
    scores_b = [sig_b["pillar_scores"][k] for k in keys]
    
    fig = go.Figure(data=[
        go.Bar(name=sym_a, x=categories, y=scores_a, marker_color="#CBA6F7"),
        go.Bar(name=sym_b, x=categories, y=scores_b, marker_color="#86EFAC")
    ])
    
    fig.update_layout(
        barmode="group",
        height=340,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#E2E8F0", size=14)),
        xaxis=dict(tickfont=dict(color="#E2E8F0", size=13), gridcolor="#383854"),
        yaxis=dict(range=[0, 100], tickfont=dict(color="#E2E8F0", size=13), gridcolor="#383854", title="Pillar Score (0-100)"),
        font=dict(family="Inter, sans-serif")
    )
    return fig

def render_comparison_table(data_a, sig_a, data_b, sig_b):
    """Generates an HTML comparison table between two stocks."""
    curr_a = data_a.get("currency", "USD")
    curr_b = data_b.get("currency", "USD")
    
    sym_a = data_a["symbol"]
    sym_b = data_b["symbol"]
    
    def fmt(val, fmt_str=".1f", suffix="", prefix=""):
        if val is None: return "N/A"
        try: return f"{prefix}{val:{fmt_str}}{suffix}"
        except: return "N/A"
        
    metrics = [
        ("Composite Score", f"{sig_a['composite_score']} / 100", f"{sig_b['composite_score']} / 100"),
        ("Signal & Confidence", f"{sig_a['signal']} ({sig_a['confidence_pct']}%)", f"{sig_b['signal']} ({sig_b['confidence_pct']}%)"),
        ("Current Price", format_currency(data_a.get("current_price"), curr_a), format_currency(data_b.get("current_price"), curr_b)),
        ("Market Cap", format_currency(data_a.get("market_cap"), curr_a), format_currency(data_b.get("market_cap"), curr_b)),
        ("P/E Ratio (TTM)", fmt(data_a.get("pe_ratio")), fmt(data_b.get("pe_ratio"))),
        ("Forward P/E", fmt(data_a.get("forward_pe")), fmt(data_b.get("forward_pe"))),
        ("PEG Ratio", fmt(data_a.get("peg_ratio"), ".2f"), fmt(data_b.get("peg_ratio"), ".2f")),
        ("Price to Sales (P/S)", fmt(data_a.get("price_to_sales"), ".2f"), fmt(data_b.get("price_to_sales"), ".2f")),
        ("Profit Margin", fmt(data_a.get("profit_margins") * 100 if data_a.get("profit_margins") else None, ".1f", "%"),
                          fmt(data_b.get("profit_margins") * 100 if data_b.get("profit_margins") else None, ".1f", "%")),
        ("Return on Equity (ROE)", fmt(data_a.get("return_on_equity") * 100 if data_a.get("return_on_equity") else None, ".1f", "%"),
                                   fmt(data_b.get("return_on_equity") * 100 if data_b.get("return_on_equity") else None, ".1f", "%")),
        ("Revenue Growth", fmt(data_a.get("revenue_growth") * 100 if data_a.get("revenue_growth") else None, ".1f", "%"),
                           fmt(data_b.get("revenue_growth") * 100 if data_b.get("revenue_growth") else None, ".1f", "%")),
        ("Dividend Yield", fmt(data_a.get("dividend_yield_pct"), ".2f", "%"), fmt(data_b.get("dividend_yield_pct"), ".2f", "%")),
        ("Debt to Equity", fmt(data_a.get("debt_to_equity")), fmt(data_b.get("debt_to_equity"))),
        ("Analyst Consensus", str(data_a.get("recommendation_key", "N/A")).upper(), str(data_b.get("recommendation_key", "N/A")).upper()),
        ("Implied Target Upside", fmt(data_a.get("implied_upside_pct"), "+.1f", "%"), fmt(data_b.get("implied_upside_pct"), "+.1f", "%")),
    ]
    
    html = f"""
    <div class="m3-table-container">
        <table class="m3-table">
            <thead>
                <tr>
                    <th style="width: 34%;">Metric</th>
                    <th style="width: 33%; color: #CBA6F7;">{sym_a} ({data_a.get('company_name', sym_a)})</th>
                    <th style="width: 33%; color: #86EFAC;">{sym_b} ({data_b.get('company_name', sym_b)})</th>
                </tr>
            </thead>
            <tbody>
    """
    for m, val_a, val_b in metrics:
        html += f"<tr><td><strong>{m}</strong></td><td>{val_a}</td><td>{val_b}</td></tr>"
    html += "</tbody></table></div>"
    return html
