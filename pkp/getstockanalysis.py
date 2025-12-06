from datetime import datetime, timedelta
import pandas as pd
import requests
from io import StringIO
import plotly.express as px
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.by import By


data_df = pd.read_csv('NSE Symbols.CSV') # Renamed to data_df to avoid conflict with 'data' variable in index function
name_company1 = [{'company': data_df['Company Name'][_], 'code': data_df['Scrip'][_]} for _ in range(len(data_df))]

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
def get_company_news(company):
    headlines = []
    driver = None

    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)

        # Extract the first word of the company name
        first_word = company.strip().lower().split()[0]

        scrip_code = None
        for entry in name_company1:
            company_first_word = entry['company'].strip().lower().split()[0]
            if company_first_word == first_word:
                scrip_code = entry['code']
                break  # ✅ Exit loop when found

        if not scrip_code:
            raise ValueError(f"No scrip code found for {company}")

        # ✅ Fix the malformed URL (no spaces, correct format)
        url = f'https://www.google.com/finance/quote/{scrip_code}:NSE'

        driver.get(url)
        time.sleep(3)

        anchor_elements = driver.find_elements(By.CSS_SELECTOR, "div.z4rs2b > a")
        for a in anchor_elements[:10]:
            text = a.text.strip()
            link = a.get_attribute("href")
            if text and link:
                headlines.append((text, link))

    except Exception as e:
        print(f"Error fetching financial news: {e}")
    finally:
        if driver:
            driver.quit()

    return headlines
def get_stock_analysis(company,months):
    scrip_code = None
    trend = None
    return_percentage = None
    table_data = None
    fig_html = None
    error = None

    average_return = None
    avg_volatility = None
    best_month = None
    worst_month = None
    max_vol_row = None
    suggestion = None

    # Default dates
    end_date_obj = datetime.now()
    start_date_obj = end_date_obj - timedelta(days=365)
    start_date_str_display = start_date_obj.strftime('%Y/%m/%d')
    end_date_str_display = end_date_obj.strftime('%Y/%m/%d')

    # Get scrip code
    if company:
        first_word = company.strip().lower().split()[0]
    else:
        return "Invalid company input", 400
    for entry in name_company1:
        company_first_word = entry['company'].strip().lower().split()[0]
        if company_first_word == first_word:
            scrip_code = entry['code']
            break


    ticker = scrip_code + '.BSE' if scrip_code else None

    try:
        if ticker:
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={ticker}&apikey=VBPRQMIQP3MSWHT9&datatype=csv'
            r = requests.get(url)
            df = pd.read_csv(StringIO(r.text))
            df = df.head(months)
            df = df[::-1]

            if not df.empty:
                if 'high' in df.columns:
                    fig = px.line(df, x='timestamp', y='high', title=f'{company} Monthly High Prices')
                    fig_html = fig.to_html(full_html=False)

                table_data = df.to_html(classes="table table-bordered table-dark table-striped text-center small", justify='center', border=0)
                df['monthly_return_%'] = df['close'].pct_change() * 100
                average_return = df['monthly_return_%'].mean()
                df['range'] = df['high'] - df['low']
                avg_volatility = df['range'].mean()

                trend = "uptrend" if df['close'].iloc[0] < df['close'].iloc[-1] else "downtrend"
                best_month = df.loc[df['monthly_return_%'].idxmax()]
                worst_month = df.loc[df['monthly_return_%'].idxmin()]
                max_vol_row = df.loc[df['volume'].idxmax()]

                if trend == "uptrend" and average_return > 2:
                    suggestion = "📈 Positive momentum with healthy returns."
                elif trend == "downtrend" and average_return < -2:
                    suggestion = "📉 Negative momentum and falling prices."
                else:
                    suggestion = "⚖️ Mixed signals. Consider waiting for clearer trends."

                start_price = df['close'].iloc[0]
                end_price = df['close'].iloc[-1]
                if start_price != 0:
                    return_percentage = round(((end_price - start_price) / start_price) * 100, 2)
                else:
                    error = "Start price is 0. Cannot compute return."

    except Exception as e:
        error = f"Error fetching data from Alpha Vantage: {e}"

    price = get_stock_price(scrip_code)
    headlines = get_company_news(company)

    return {
        "company": company,
        "scrip_code": scrip_code,
        "table_data": table_data,
        "fig_html": fig_html,
        "error": error,
        "start_date_display": start_date_str_display,
        "end_date_display": end_date_str_display,
        "price": price,
        "months": months,
        "trend": trend,
        "average_return": average_return,
        "avg_volatility": avg_volatility,
        "best_month": best_month,
        "worst_month": worst_month,
        "max_vol_row": max_vol_row,
        "suggestion": suggestion,
        "headlines": headlines,
        "return_percentage": return_percentage
    }
def analyze_company_data(company, name_company1, request):
    """Processes company stock analysis and returns all computed results."""
    import requests
    import pandas as pd
    from io import StringIO
    from datetime import datetime, timedelta

    table_data = fig_html = error = None
    months = average_return = avg_volatility = None
    best_month = worst_month = max_vol_row = None
    suggestion = trend = return_percentage = None
    scrip_code = None

    # Default dates
    end_date_obj = datetime.now()
    start_date_obj = end_date_obj - timedelta(days=365)

    # Find scrip code
    first_word = company.strip().lower().split()[0]
    for entry in name_company1:
        if entry['company'].strip().lower().split()[0] == first_word:
            scrip_code = entry['code']
            break

    # If POST → run full analysis
    if request.method == 'POST':
        ticker_input = request.form['ticker']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        months = int(request.form['no_month'])
        ticker = ticker_input + '.BSE'

        try:
            # Fetch Alpha Vantage data
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={ticker}&apikey=VBPRQMIQP3MSWHT9&datatype=csv'
            r = requests.get(url)
            df = pd.read_csv(StringIO(r.text))
            df = df.head(months)[::-1]

            if df.empty:
                error = f"No data available for {scrip_code}."
            else:
                # Plot High Values
                if 'high' in df.columns:
                    fig = px.line(df, x='timestamp', y='high', title=f'{company} Monthly High Prices')
                    fig_html = fig.to_html(full_html=False)

                table_data = df.to_html(
                    classes="table table-bordered table-dark table-striped text-center small",
                    justify='center', border=0
                )

                # Monthly Return %
                df['monthly_return_%'] = df['close'].pct_change() * 100
                average_return = df['monthly_return_%'].mean()

                # Volatility
                df['range'] = df['high'] - df['low']
                avg_volatility = df['range'].mean()

                # Trend
                trend = "uptrend" if df['close'].iloc[0] < df['close'].iloc[-1] else "downtrend"

                best_month = df.loc[df['monthly_return_%'].idxmax()]
                worst_month = df.loc[df['monthly_return_%'].idxmin()]
                max_vol_row = df.loc[df['volume'].idxmax()]

                # Suggestions
                if trend == "uptrend" and average_return > 2:
                    suggestion = "📈 Positive momentum — could be a good time to consider investing."
                elif trend == "downtrend" and average_return < -2:
                    suggestion = "📉 Falling prices — exercise caution."
                else:
                    suggestion = "⚖️ Mixed signals — wait for clearer trends."

                # Return %
                start_price = df['close'].iloc[0]
                end_price = df['close'].iloc[-1]
                if start_price != 0:
                    return_percentage = round(((end_price - start_price) / start_price) * 100, 2)

        except Exception as e:
            error = f"Error fetching data from Alpha Vantage: {e}"

    return {
        "table_data": table_data,
        "fig_html": fig_html,
        "error": error,
        "months": months,
        "trend": trend,
        "average_return": average_return,
        "avg_volatility": avg_volatility,
        "best_month": best_month,
        "worst_month": worst_month,
        "max_vol_row": max_vol_row,
        "suggestion": suggestion,
        "return_percentage": return_percentage,
        "scrip_code": scrip_code,
        "start_date_display": start_date_obj.strftime('%Y/%m/%d'),
        "end_date_display": end_date_obj.strftime('%Y/%m/%d'),
    }
