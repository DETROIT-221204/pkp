import yfinance as yf

# Define indices
tickers = {
    'NIFTY_50': '^NSEI',
    'SENSEX': '^BSESN',
    'NIFTY_BANK': '^NSEBANK',
    'NIFTY_IT': '^CNXIT',
    'BSE_SmallCap': '^BSE-MIDCAP'  # Try ^BSE500 or similar if this fails
}

# Download historical data
for name, symbol in tickers.items():
    data = yf.download(symbol, start="2005-01-01", end="2024-12-31")
    data.to_csv(f"{name}_history.csv")
    print(f"Saved {name} data")