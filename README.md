# 📈 DeepSeek Stock Analysis Bot & Web Terminal

A multi-factor stock analysis bot and interactive Web Terminal supporting both **US** (e.g. `AAPL`, `NVDA`) and **International** stock tickers (e.g. `CBA.AX`, `BHP.AX`, `SHEL.L`).

It synthesizes live market data across **6 analytical pillars** into a composite score (0-100), explicit signal (`BUY` / `SELL` / `HOLD`), confidence level, bull/bear highlights, and generates both `.html` dashboards and `.md` reports.

---

## 🌟 Key Features

- **6-Pillar Composite Scoring Model**:
  - 🏦 **Financial Fundamentals (25%)**: Debt-to-Equity, ROE, Profit Margins, Revenue Growth.
  - 🏷️ **Valuation Multiples (20%)**: Trailing P/E, Forward P/E, PEG Ratio, P/S Ratio.
  - 📈 **Technical Momentum (15%)**: 14-day RSI, 50/200-day Moving Average Crossovers, MACD, 52-week position.
  - 📰 **Sentiment Analysis (15%)**: Real-time news headlines & sentiment polarity indexing.
  - 🎯 **Wall Street Analyst Consensus (15%)**: Target price upside/downside & rating distribution.
  - 🌍 **Qualitative, Macro & Moat Modeling (10%)**: Economic moat rating, market expectation pricing, interest rate policy sensitivity.
- **Multi-Currency & Regional Support**:
  - Auto-detects exchange suffixes (`.AX`, `.L`, `.TO`, `.DE`) to set native currency symbols (`$`, `A$`, `£`, `€`, `CA$`) and central bank monetary policies (Fed, RBA, ECB, BOE, BOC).
- **Dual Report Exporter**:
  - Generates standalone, styled HTML reports (`reports/<SYMBOL>_analysis_<YYYY-MM-DD>.html`) and Markdown files (`.md`).
- **Web Terminal Interface (GitHub Pages)**:
  - Includes a dark-themed financial workstation Web Terminal (`index.html`) to run analyses, view pre-built reports, or run client-side simulations.
- **Automated GitHub Actions Integration**:
  - Scheduled daily workflow automatically analyzes a watchlist of tickers, commits updated reports back to the repository, and deploys the latest site to GitHub Pages.

---

## 🚀 Quick Start (Local CLI Execution)

### 1. Installation
```bash
git clone https://github.com/YOUR_USERNAME/stock-analysis.git
cd stock-analysis

# Create virtual environment and install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Running an Analysis
You can run the executable script directly. It features an automatic launcher that self-re-executes inside `.venv`:

```bash
# Analyze US Stock (e.g. Apple)
./analyse.py AAPL

# Analyze Australian Stock (e.g. Commonwealth Bank of Australia)
./analyse.py CBA.AX

# Forwarding wrapper alias
./analyze.py NVDA
```

All generated reports are saved under `reports/` in both `.md` and `.html` formats.

---

## 🛠️ GitHub Repository & GitHub Pages Setup

Follow these exact steps to push this code to GitHub and enable the automated GitHub Actions workflows:

### Step 1: Initialize Git and Push to GitHub
```bash
git init
git add .
git commit -m "feat: initial commit for stock analysis bot & web terminal"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis.git
git push -u origin main
```

### Step 2: Enable GitHub Actions Commit Permissions (CRITICAL)
To allow GitHub Actions to commit updated reports back to your repository, you must grant write permissions:
1. Go to your GitHub Repository -> **Settings**.
2. In the left sidebar, click **Actions** -> **General**.
3. Scroll down to **Workflow permissions**.
4. Select **Read and write permissions**.
5. Check the box **"Allow GitHub Actions to create and approve pull requests"**.
6. Click **Save**.

### Step 3: Enable GitHub Pages
1. Go to your GitHub Repository -> **Settings**.
2. In the left sidebar, click **Pages**.
3. Under **Build and deployment** -> **Source**, select **GitHub Actions**.
4. Trigger the workflow manually under **Actions** tab -> **Deploy Web Terminal to GitHub Pages** -> **Run workflow**.
5. Your live Web Terminal URL will be: `https://YOUR_USERNAME.github.io/stock-analysis/`.

---

## 📂 Project Structure

```
├── analyse.py                      # Primary CLI Launcher with auto venv self-exec
├── analyze.py                      # Forwarding wrapper script
├── index.html                      # Interactive Web Terminal for GitHub Pages
├── requirements.txt                # Python package dependencies
├── README.md                       # Documentation & setup guide
├── .gitignore                      # Git ignore rules
├── .github/
│   └── workflows/
│       ├── scheduled-analysis.yml  # Daily CRON workflow to analyze tickers & commit reports
│       └── deploy-pages.yml        # GitHub Pages build & deployment workflow
├── stock_bot/                      # Core Python modules
│   ├── config.py                   # Exchange currencies & monetary policy metadata
│   ├── data_fetcher.py             # Financial ratios & yfinance data extractor
│   ├── technical_analysis.py      # RSI, SMA moving averages & MACD engine
│   ├── sentiment_analysis.py      # News & Reddit headline sentiment analyzer
│   ├── qualitative_analysis.py    # Economic moat & macro expectation modeling
│   ├── scoring_engine.py          # 6-Pillar composite score calculator
│   └── report_generator.py        # Terminal formatting & HTML/MD report generators
└── reports/                        # Output folder for generated .html & .md reports
```

---

## 📜 License
MIT License - Feel free to adapt and expand for your personal investment workflow.