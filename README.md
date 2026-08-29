# 🛡️ Aegis Equity Terminal

A multi-factor stock analysis engine & **Material Design 3 Dark** web application supporting both **US** (e.g. `AAPL`, `NVDA`, `TSLA`) and **International** stock equities (e.g. `CBA.AX`, `SHEL.L`, `SAP.DE`).

Synthesizes live market data across **6 analytical pillars** into a composite score (0–100), explicit recommendation signal (`BUY` / `SELL` / `HOLD`), confidence level, Plotly gauge visualizers, financial health metrics, technical indicators, news/Reddit sentiment, analyst price targets, and macro/moat modeling.

---

## 🎨 Material Design 3 (M3) Dark Web Interface

- **M3 Dark Palette**: Deep background surface (`#121318`), surface containers (`#1E1F25`), primary tokens (`#D0BCFF`), and high-contrast text typography.
- **Full Font Size & Contrast Enhancement**: Enlarged metric values, table cells, pillar progress bars, and header cards for maximum readability.
- **HTML Rendering Engine**: Custom line-stripping algorithm prevents Markdown parsers from escaping custom M3 HTML cards.
- **Clean Ticker Presets**: Dropdown selectbox and custom text input pattern without Streamlit session state collisions.
- **Interactive Plotly Gauge**: Score gauge with M3 dark threshold steps.

---

## 🚀 Option A: Deploy to Streamlit Community Cloud (FREE)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "feat: upgrade to Aegis Equity Terminal with M3 Dark Theme"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud (2 minutes)
1. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
2. Click **"New app"**.
3. Fill in the form:
   - **Repository:** `YOUR_USERNAME/stock-analysis`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy!"**.

🎉 **Your web terminal will be live at `https://YOUR_APP.streamlit.app`!**

---

## 💻 Option B: Run Locally

### 1. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch Streamlit Web App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### 3. Or Run Local CLI Launcher
```bash
# Analyze US stock
./analyse.py AAPL

# Analyze Australian stock
./analyse.py CBA.AX
```

---

## 📊 6-Pillar Analytical Model

| Pillar | Weight | Indicators Measured |
|---|---|---|
| 🏦 **Financial Fundamentals** | 25% | Debt-to-Equity, ROE, Profit Margins, Revenue Growth, Free Cash Flow |
| 🏷️ **Valuation Multiples** | 20% | Trailing P/E, Forward P/E, PEG Ratio, Price-to-Sales, EV/EBITDA |
| 📈 **Technical Momentum** | 15% | 14-day RSI, 50/200-day Moving Average Crossovers, MACD, 52-week position |
| 📰 **News & Social Sentiment** | 15% | Real-time news & Reddit headline sentiment polarity indexing |
| 🎯 **Analyst Consensus** | 15% | Wall Street price targets, upside/downside %, rating distribution |
| 🛡️ **Macro, Moat & Industry** | 10% | Economic moat rating, monetary policy sensitivity, market expectation pricing |

---

## 📂 Project Structure

```
├── app.py                          # Streamlit M3 Dark Web Terminal
├── analyse.py                      # Executable CLI Launcher with auto venv self-exec
├── analyze.py                      # Alias wrapper script
├── .streamlit/
│   └── config.toml                 # Streamlit M3 Dark color tokens
├── requirements.txt                # Python package dependencies
├── README.md                       # Documentation & deployment guide
├── .gitignore                      # Git ignore rules
└── stock_bot/                      # Core Python analytical modules
    ├── config.py                   # Exchange currencies & monetary policy metadata
    ├── data_fetcher.py             # Financial ratios & yfinance data extractor
    ├── technical_analysis.py      # RSI, SMA moving averages & MACD engine
    ├── sentiment_analysis.py      # News & Reddit headline sentiment analyzer
    ├── qualitative_analysis.py    # Economic moat & macro expectation modeling
    ├── scoring_engine.py          # 6-Pillar composite score calculator
    └── report_generator.py        # Terminal formatting & HTML/MD report generators
```

---

## 📜 Disclaimer
*This tool is for educational and research purposes only. It does not constitute financial advice.*