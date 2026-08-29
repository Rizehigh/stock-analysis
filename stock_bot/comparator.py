"""
Stock Comparator Engine - Multi-Equity Comparison (up to 6 stocks)
Compares 1 to 6 equities side-by-side across Composite Scores, 6-Pillar breakdowns, Valuation Multiples, and Bull/Bear catalysts.
"""
import plotly.graph_objects as go
from stock_bot.config import format_currency

PALETTE = ["#CBA6F7", "#86EFAC", "#FDE047", "#93C5FD", "#F9A8D4", "#F97316"]

def build_multi_pillar_chart(sig_map: dict):
    """Creates a grouped bar chart comparing 6 pillar scores for up to 6 stocks."""
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
        height=450,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#1E1E2E",
        font={"family": "Inter, sans-serif", "color": "#E2E8F0", "size": 14},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=14, color="#E2E8F0")
        ),
        xaxis=dict(
            gridcolor="#383854",
            tickfont=dict(size=13, color="#A6ADC8")
        ),
        yaxis=dict(
            range=[0, 100],
            gridcolor="#383854",
            title="Score (0 - 100)",
            tickfont=dict(size=13, color="#A6ADC8")
        )
    )
    return fig

def render_multi_comparison_table(data_map: dict, sig_map: dict) -> str:
    """Renders dynamic HTML table comparing metrics side-by-side for up to 6 stocks."""
    tickers = list(data_map.keys())
    
    html = '<div class="m3-table-container"><table class="m3-table"><thead><tr><th>Metric</th>'
    for idx, sym in enumerate(tickers):
        color = PALETTE[idx % len(PALETTE)]
        html += f'<th style="color: {color}; text-align: center;">{sym}</th>'
    html += '</tr></thead><tbody>'
    
    metrics = [
        ("Company Name", lambda sym: data_map[sym].get("company_name", sym)[:20]),
        ("Sector", lambda sym: data_map[sym].get("sector", "N/A")),
        ("Current Price", lambda sym: format_currency(data_map[sym].get("current_price"), data_map[sym].get("currency", "USD"))),
        ("Market Cap", lambda sym: format_currency(data_map[sym].get("market_cap"), data_map[sym].get("currency", "USD"))),
        ("P/E Ratio (TTM)", lambda sym: f"{data_map[sym].get('pe_ratio'):.1f}" if data_map[sym].get('pe_ratio') else "N/A"),
        ("Forward P/E", lambda sym: f"{data_map[sym].get('forward_pe'):.1f}" if data_map[sym].get('forward_pe') else "N/A"),
        ("PEG Ratio", lambda sym: f"{data_map[sym].get('peg_ratio'):.2f}" if data_map[sym].get('peg_ratio') else "N/A"),
        ("P/S Ratio", lambda sym: f"{data_map[sym].get('price_to_sales'):.2f}" if data_map[sym].get('price_to_sales') else "N/A"),
        ("Profit Margin", lambda sym: f"{data_map[sym]['profit_margins']*100:.1f}%" if data_map[sym].get('profit_margins') else "N/A"),
        ("Revenue Growth", lambda sym: f"{data_map[sym]['revenue_growth']*100:.1f}%" if data_map[sym].get('revenue_growth') else "N/A"),
        ("Return on Equity", lambda sym: f"{data_map[sym]['return_on_equity']*100:.1f}%" if data_map[sym].get('return_on_equity') else "N/A"),
        ("Dividend Yield", lambda sym: f"{data_map[sym]['dividend_yield_pct']:.2f}%" if data_map[sym].get('dividend_yield_pct') else "N/A"),
        ("Wall St Consensus", lambda sym: str(data_map[sym].get('recommendation_key', 'N/A')).upper()),
        ("Analyst Upside", lambda sym: f"{data_map[sym]['implied_upside_pct']:+.1f}%" if data_map[sym].get('implied_upside_pct') else "N/A"),
        ("RSI (14-day)", lambda sym: f"{sig_map[sym]['pillar_scores']['technicals']:.1f}"),
        ("Overall Composite", lambda sym: f"<strong>{sig_map[sym]['composite_score']} / 100</strong>"),
    ]
    
    for label, extractor in metrics:
        html += f'<tr><td><strong>{label}</strong></td>'
        for sym in tickers:
            val = extractor(sym)
            html += f'<td style="text-align: center;">{val}</td>'
        html += '</tr>'
        
    html += '</tbody></table></div>'
    return html
