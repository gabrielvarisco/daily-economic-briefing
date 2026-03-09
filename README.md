# 📊 Daily Economic Briefing

Automated **global market intelligence system** that generates a daily briefing covering:

* 🌍 Global macro
* 🇧🇷 Brazil equities
* 🇺🇸 US markets
* ₿ Crypto markets
* 📈 Quantitative market summary
* 📰 Financial news

The system automatically distributes the report to:

* **Telegram**
* **GitHub Pages dashboard**
* **Historical archive**

Live dashboard:
👉 https://gabrielvarisco.github.io/daily-economic-briefing/

---

# 🧠 What This Project Does

Every day the system:

1. Collects market data using **Yahoo Finance**
2. Calculates market metrics:

   * daily returns
   * weekly momentum
   * rolling volatility
   * moving averages
3. Builds a **market regime analysis**
4. Generates a **daily research briefing**
5. Sends the report to **Telegram**
6. Publishes the report as an **HTML dashboard**

The result is a **lightweight automated market intelligence platform**.

---

# 🌐 Live Dashboard

The site contains:

* Latest market report
* Historical archive
* Market regime summary
* Cross-asset monitoring

Example pages:

Dashboard
https://gabrielvarisco.github.io/daily-economic-briefing/

Daily report example

```
/daily_report_YYYY-MM-DD.html
```

---

# 📦 Project Structure

```
daily-economic-briefing
│
├─ Scripts/
│   ├─ brazil_market.py
│   ├─ usa_market.py
│   ├─ crypto_market.py
│   ├─ macro_global.py
│   ├─ quant_summary.py
│   ├─ market_take.py
│   ├─ html_report.py
│   └─ news_fetcher.py
│
├─ tickers/
│   ├─ brazil_stocks.py
│   └─ usa_stocks.py
│
├─ reports/
│   ├─ index.html
│   └─ daily_report_YYYY-MM-DD.html
│
├─ main.py
├─ build_site.py
└─ requirements.txt
```

---

# ⚙️ Workflows (GitHub Actions)

The system runs automatically through GitHub Actions.

### 1️⃣ Daily Market Briefing

File:

```
.github/workflows/daily.yml
```

Runs:

```
python main.py
```

Purpose:

* generates the daily report
* sends it to **Telegram**

---

### 2️⃣ Crypto Monitor

```
.github/workflows/crypto.yml
```

Runs the crypto monitoring script.

---

### 3️⃣ Brazil Market Monitor

```
.github/workflows/brazil.yml
```

Tracks Brazilian equities and index metrics.

---

### 4️⃣ Website Deployment

```
.github/workflows/pages.yml
```

Runs:

```
python build_site.py
```

Purpose:

* generates HTML reports
* publishes the dashboard via **GitHub Pages**

---

# 📊 Data Sources

Market data is collected using:

* **Yahoo Finance API (yfinance)**
* **Financial news feeds**
* **On-chain / crypto market metrics**

Assets monitored include:

### Global Macro

* Dollar Index (DXY)
* US 10Y Yield
* Gold
* Oil
* VIX

### US Market

* S&P 500
* Nasdaq
* Dow Jones
* Russell 2000
* Major tech stocks

### Brazil

* IBOVESPA
* USD/BRL
* Major Brazilian equities

### Crypto

* BTC
* ETH
* SOL
* DeFi assets

---

# 📈 Quantitative Metrics

The system calculates:

* Daily returns
* Weekly momentum
* 21-day volatility
* Moving averages
* Market breadth
* Cross-asset leadership
* Risk regime detection

Example regime outputs:

```
Risk-on
Risk-off
Neutral
```

---

# 🚀 Running Locally

Clone the repository:

```
git clone https://github.com/gabrielvarisco/daily-economic-briefing.git
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the daily briefing:

```
python main.py
```

Generate the website locally:

```
python build_site.py
```

Open:

```
reports/index.html
```

---

# 🔐 Environment Variables

The Telegram integration requires:

```
TELEGRAM_TOKEN
CHAT_ID
```

Add them as **GitHub Secrets** or local environment variables.

---

# 🧩 Tech Stack

* Python
* Pandas
* NumPy
* yfinance
* GitHub Actions
* GitHub Pages
* HTML / CSS dashboard

---

# 🧠 Future Improvements

Potential upgrades for the platform:

* Interactive charts
* Market heatmaps
* Economic calendar integration
* Portfolio tracking
* Risk indicators
* Macro regime modeling

---

# 📜 License

MIT License
