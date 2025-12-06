import requests
from bs4 import BeautifulSoup

def get_stock_price(ticker):
    url = f'https://www.google.com/finance/quote/{ticker}:NSE'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find(class_='YMlKec fxKbKc')
        return price_tag.text.strip() if price_tag else "Price not available"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock price: {e}")
        return "Error fetching price"