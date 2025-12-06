# DhanGyan – AI-Driven Unified Investment Guidance Platform

A Unified AI-powered platform that integrates Real Estate, Gold, Stocks, and Cryptocurrencies into one intelligent investment advisory system.

# 📌 Overview

DhanGyan solves India’s most common investment challenge: confusion due to scattered platforms and lack of intelligent, comparative guidance across asset classes.
This system aggregates live market data, performs AI-driven analysis, and generates personalized investment recommendations using ML + NLP + financial indicators.

The platform brings all major asset categories in one dashboard with interactive visual insights and investor-specific strategy suggestions.

# 🚀 Key Features

| Feature                         | Description                                           |
| ------------------------------- | ----------------------------------------------------- |
| 🏦 Unified Investment Dashboard | Real estate, gold, stocks, and crypto in one platform |
| 🤖 AI Investment Advisor        | Personalized guidance using ML + OpenAI/LangChain     |
| 📊 Comparative Analytics        | Interactive charts & risk–return comparisons          |
| 📡 Real-Time Data Fusion        | Financial APIs + live scraping for up-to-date values  |
| 🧠 Smart Risk Profiling         | AI suggests assets based on behavior & goals          |
| 📈 Trend & Growth Visualization | Asset trend charts via Chart.js / D3.js               |
| 🔐 Secure User Experience       | Encrypted storage and authenticated access            |

# 🏗️ System Architecture

# 🔗 Architecture Link:
https://app.eraser.io/workspace/NOYc7NTlXcV0x2z8GpYa?origin=share

# 🛠️ Tech Stack
## Backend

- Flask / FastAPI

- MySQL

- Selenium + BeautifulSoup (scheduled scraping)

## Frontend

- Jinja2

- HTML / CSS / JavaScript

- Bootstrap / Tailwind CSS

- Chart.js / D3.js

## AI & ML Layer

- Pandas, NumPy

- Scikit-learn / TensorFlow Lite

- OpenAI API / LangChain

## Data Sources

- Financial APIs: Alpha Vantage, CoinGecko, RealEstateMall

- Web scraping (property indexes, gold rates, crypto tickers, NSE/BSE)

# 📦 Installation & Setup
# Clone the repo
git clone https://github.com/DETROIT-221204/pkp.git

cd pkp/pkp

# Create virtual environment
python -m venv venv 
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env variables
DB_USER=...
DB_PASS=...
API_KEY=...
SECRET_KEY=...

# Start server
flask run   # or: uvicorn main:app --reload


# 📊 How It Works

- System fetches real-time prices & historical values.

- Scraper + APIs clean & consolidate market datasets.

ML models perform:

- trend forecasting

- risk analysis

- asset scoring

OpenAI/LangChain generates investment recommendations in natural language.

User receives:

- Comparative charts

- Portfolio suggestions

- Risk advisory & diversification tips

# 🆚 Existing Platforms & Comparison
| Platform              | Limitation                                  |
| --------------------- | ------------------------------------------- |
| Zerodha / Groww       | No crypto/real estate integration           |
| CoinDCX / CoinSwitch  | No traditional assets like gold/real estate |
| MagicBricks / 99acres | Only listings, no AI advisory or analytics  |

DhanGyan = all four integrated + AI advisory + visuals

# 📌 Future Scope

- Robo-advisory automation

- Voice-based investment chat assistant

- Real-time anomaly alerts & market prediction

# 🤝 Contribution Guidelines
1. Fork the repo
2. Create a feature branch
3. Commit changes with meaningful messages
4. Open a Pull Request

# 👨‍💻 Team

## Dot Developers

- Mohammad Ali Ansari

- Huzaifa Zahid Shah

- Hannan Shemle  

- Shaan Sakharkar

# 📄 License

This project is licensed under the MIT License.
Feel free to use, modify, and distribute with credit.
