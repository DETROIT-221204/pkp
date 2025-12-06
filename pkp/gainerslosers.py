import requests
from bs4 import BeautifulSoup
import re


def get_top_gainers():
    top_gainers = {'company': [], 'current_rate': [], 'price_change': []}
    url = 'https://economictimes.indiatimes.com/stocks/marketstats/top-gainers/sensex'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        stock_rows = soup.find_all('tr', class_='MarketTable_fixedTr__vq74z')

        count = 0
        for row in stock_rows:
            if count >= 10:
                break

            company_tag = row.find('a', class_='MarketTable_ellipses__M8PxM')
            company_name = company_tag.text.strip() if company_tag else 'N/A'

            current_price_tag = row.find('span', class_='highlightBg MarketTable_ltp__l0Zdv')
            current_rate = current_price_tag.text.strip() if current_price_tag else 'N/A'
            try:
                current_rate = float(current_rate)
            except ValueError:
                current_rate = 'N/A'

            price_change_tag = row.find('td', class_=re.compile(r'(up|down) numberFonts'))
            price_change = price_change_tag.text.strip() if price_change_tag else 'N/A'
            try:
                price_change = float(price_change)
            except ValueError:
                price_change = 'N/A'

            top_gainers['company'].append(company_name)
            top_gainers['current_rate'].append(current_rate)
            top_gainers['price_change'].append(price_change)

            count += 1
        return top_gainers  # <-- Move return outside the loop
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
def get_top_losers():
    top_gainers = {'company': [], 'current_rate': [], 'price_change': []}
    url = 'https://economictimes.indiatimes.com/stocks/marketstats/top-losers/sensex'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        stock_rows = soup.find_all('tr', class_='MarketTable_fixedTr__vq74z')

        count = 0
        for row in stock_rows:
            if count >= 10:
                break

            company_tag = row.find('a', class_='MarketTable_ellipses__M8PxM')
            company_name = company_tag.text.strip() if company_tag else 'N/A'

            current_price_tag = row.find('span', class_='highlightBg MarketTable_ltp__l0Zdv')
            current_rate = current_price_tag.text.strip() if current_price_tag else 'N/A'
            try:
                current_rate = float(current_rate)
            except ValueError:
                current_rate = 'N/A'

            price_change_tag = row.find('td', class_=re.compile(r'(up|down) numberFonts'))
            price_change = price_change_tag.text.strip() if price_change_tag else 'N/A'
            try:
                price_change = float(price_change)
            except ValueError:
                price_change = 'N/A'

            top_gainers['company'].append(company_name)
            top_gainers['current_rate'].append(current_rate)
            top_gainers['price_change'].append(price_change)

            count += 1
        return top_gainers  # <-- Move return outside the loop
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred during parsing: {e}")