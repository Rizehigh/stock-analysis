# 📈 DeepSeek Stock Analysis Bot & Material 3 Web App

A multi-factor stock analysis bot and interactive **Material Design 3 (M3)** web application supporting both **US** (e.g. `AAPL`, `NVDA`) and **International** stock tickers (e.g. `CBA.AX`, `SHEL.L`, `SAP.DE`).

It synthesizes live market data across **6 analytical pillars** into a composite score (0-100), explicit recommendation signal (`BUY` / `SELL` / `HOLD`), confidence level, Plotly gauge visualizers, financial health metrics, technical indicators, news/Reddit sentiment, analyst price targets, and macro/moat qualitative modeling.

---

## 🎨 Material Design 3 (M3) Web Interface

The web interface is built with **Streamlit** and styled using **Google Material Design 3** design tokens:
- **Surface elevation cards** and rounded corner containers (16px / 28px tokens)
- **Dynamic color tokens**: M3 Primary (`#6750A4`), Surface Variant (`#E7E0EC`), and M3 Status Badges for Signals
- **Interactive Plotly Score Gauge**
- **Live multi-ticker analysis**: Enter any valid ticker dynamically — no hardcoded watchlists!
- **Sidebar Quick Tickers** for instant selection (`AAPL`, `NVDA`, `MSFT`, `TSLA`, `CBA.AX`, `SHEL.L`)

---

## 🚀 Option A: Deploy to Streamlit Community Cloud (FREE)

Streamlit Community Cloud hosts Python web applications for free directly from your GitHub repository.

### Step 1: Push Repository to GitHub
```bash
git add .
git commit -m "feat: add Streamlit app with Material 3 design theme"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud (2 minutes)
1. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
2. Click **"New app"**.
3. Fill in the deployment form:
   - **Repository:** `YOUR_USERNAME/stock-analysis`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy!"**.

🎉 **Your app will be live at a public URL like `https://YOUR_APP.streamlit.app` where anyone can input any stock ticker and receive live 6-pillar analysis reports!**

---

## 💻 Option B: Run Locally

### 1. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch Streamlit M3 App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your web browser.

### 3. Or Run Local CLI Launcher
```bash
# Analyze US stock
./analyse.py AAPL

# Analyze Australian stock
./analyse.py CBA.AX
```
Generated CLI reports are saved to `reports/` in both `.html` and `.md` formats.

---

## 📊 6-Pillar Composite Scoring Architecture

| Pillar | Weight | Key Indicators Measured |
|---|---|---|
| 🏦 **Financial Fundamentals** | 25% | Debt-to-Equity, ROE, Profit Margins, Revenue Growth, Free Cash Flow |
| 🏷️ **Valuation Multiples** | 20% | Trailing P/E, Forward P/E, PEG Ratio, Price-to-Sales, EV/EBITDA |
| 📈 **Technical Momentum** | 15% | 14-day RSI, 50/200-day Moving Average Crossovers, MACD, 52-week position |
| 📰 **News & Reddit Sentiment** | 15% | Real-time news & Reddit headline sentiment polarity indexing |
| 🎯 **Analyst Consensus** | 15% | Wall Street price targets, upside/downside %, rating distribution |
| 🛡️ **Macro, Moat & Industry** | 10% | Economic moat rating, monetary policy sensitivity, market expectation pricing |

---

## 📂 Project Structure

```
├── app.py                          # Streamlit Web App with Material 3 UI
├── analyse.py                      # Executable CLI Launcher with auto venv self-exec
├── analyze.py                      # Alias wrapper script
├── .streamlit/
│   └── config.toml                 # Streamlit M3 color tokens & server config
├── requirements.txt                # Python package dependencies
├── README.md                       # Documentation & deployment guide
├── .gitignore                      # Git ignore rules
├── stock_bot/                      # Core Python analytical modules
│   ├── config.py                   # Exchange currencies & monetary policy metadata
│   ├── data_fetcher.py             # Financial ratios & yfinance data extractor
│   ├── technical_analysis.py      # RSI, SMA moving averages & MACD engine
│   ├── sentiment_analysis.py      # News & Reddit headline sentiment analyzer
│   ├── qualitative_analysis.py    # Economic moat & macro expectation modeling
│   ├── scoring_engine.py          # 6-Pillar composite score calculator
│   └── report_generator.py        # Terminal formatting & HTML/MD report generators
└── reports/                        # Output directory for generated CLI reports
```

---

## 📜 Disclaimer
*This stock analysis bot is for educational and research purposes only. It does not constitute financial or investment advice. Always perform your own due diligence.*