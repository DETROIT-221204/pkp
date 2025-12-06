import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go


def get_gold_price():
    url = 'https://economictimes.indiatimes.com/commoditysummary/symbol-GOLD.cms'
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find(class_='commodityPrice')
        return price_tag.text.strip()

    except requests.RequestException as e:
        return e
def get_gold_average():
    data = pd.read_csv('dataset/10year_gold_price_history.csv')
    return data.to_html(classes='table table-dark table-striped', index=False, escape=False)
def gold_growth():

    data = pd.read_csv('new_goldprice_yearly.csv', skiprows=1, names=['Year', 'Rate'])

    # Clean 'Rate': remove commas, convert to integer
    data['Rate'] = data['Rate'].str.replace(',', '').astype(int)

    # Clean 'Year': convert to int (important for correct sorting and plotting)
    data['Year'] = data['Year'].astype(int)

    # Sort by year in ascending order (just to be safe)
    data = data.sort_values(by='Year')

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Year'], y=data['Rate'], mode='lines+markers', name='Gold Price'))

    fig.update_layout(
        title='Gold Price (Yearly)',
        xaxis_title='Year',
        yaxis_title='Price (₹)',
        template='plotly_dark',
        width=500,
        height=400
    )
    fig_html = fig.to_html(full_html=False)
    return fig_html
def get_gold_news():
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}
    links = [
        # 'https://www.hindustantimes.com/india-news/gold-rates-in-india-continue-to-decline-in-major-cities-check-citywise-rates-101749618060733.html',
        'https://economictimes.indiatimes.com/commoditysummary/symbol-GOLD.cms',
        'https://www.livemint.com/market/stock-market-news/gold-price-in-india-gold-rate-prediction-gold-market-analysis-safe-haven-assets-us-china-trade-talks-us-economy-11749725683434.html',

    ]
    for i in links:
        response = requests.get(i, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.text.strip()
        news.append({'title': title, 'url': i})
    return news
def generate_gold_advice():
    """Calls OpenRouter and returns gold investment advice."""
    import requests, json

    API_KEY = ""
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    user_message = "Should I invest in gold in Mumbai?"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://www.yoursite.com",
        "X-Title": "FlaskChatApp"
    }

    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": user_message}]
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        return reply
    except Exception as e:
        return f"Error: {str(e)}"
def calculate_gold_investment(year, amount, gold_prices):
    """
    Calculate gold investment returns.
    Args:
        year (int): Year of investment
        amount (float): Investment amount
        gold_prices (dict): Year-wise gold prices per 10g
    Returns:
        dict: Investment result with grams, current value, profit, percent return
    """
    if year not in gold_prices:
        raise ValueError("Invalid year")

    price_then_10g = gold_prices[year]
    price_now_10g = gold_prices[2025]

    price_then_per_g = price_then_10g / 10
    price_now_per_g = price_now_10g / 10

    gold_bought_grams = amount / price_then_per_g
    current_value = gold_bought_grams * price_now_per_g

    profit = current_value - amount
    return_percent = (profit / amount) * 100

    return {
        "year": year,
        "amount": amount,
        "grams": round(gold_bought_grams, 2),
        "current_value": round(current_value, 2),
        "profit": round(profit, 2),
        "percent_return": round(return_percent, 2)
    }