import requests
import re
from bs4 import BeautifulSoup
def  get_nifty():
    url = 'https://www.google.com/finance/'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    price_tags = soup.find_all(class_='YMlKec')

    amounts = []
    for tag in price_tags:
        raw_text = tag.text.strip()
        # Remove any currency symbols and commas
        cleaned = re.sub(r'[₹$,]', '', raw_text)
        try:
            amounts.append(float(cleaned))
        except ValueError:
            continue  # Skip values that can't be converted
    n_amount = []
    for i in range(len(amounts[:10])):
        if i % 2 != 0:
            n_amount.append(amounts[i])
    return n_amount

def process_nifty_index(name, index_info):
    """Processes a Nifty/Sensex index: CSV load, chart, scraping, price, news."""
    import pandas as pd
    import plotly.express as px
    import requests, time
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    # Load dataset
    csv_path = index_info[name]['csv']
    data = pd.read_csv(csv_path, parse_dates=['Date'], dayfirst=True)

    # Plot chart
    fig = px.line(data, x='Date', y='High', title=f'{name} High Price History')
    fig.update_layout(template="plotly_dark")
    fig_html = fig.to_html(full_html=False)

    # ---------- Scrape News ----------
    headlines = []
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(index_info[name]['news'])
        time.sleep(3)

        anchors = driver.find_elements(By.CSS_SELECTOR, "div.z4rs2b > a")
        for a in anchors[:10]:
            text = a.text.strip()
            link = a.get_attribute("href")
            if text:
                headlines.append((text, link))
        driver.quit()
    except Exception as e:
        print(f"Error fetching financial news: {e}")

    # ---------- Scrape Current Price ----------
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = index_info[name]['url']
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find(class_='YMlKec fxKbKc')
        price = price_tag.text.strip() if price_tag else 'N/A'
    except Exception as e:
        price = f"Error: {str(e)}"

    return {
        "fig_html": fig_html,
        "price": price,
        "headlines": headlines
    }