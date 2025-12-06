import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
fund_news = {
    'Aditya':'https://www.moneycontrol.com/mutual-funds/nav/aditya-birla-sun-life-banking-psu-debt-fund-direct-plan-md-/MBS906#google_vignette',
    'Canara':'https://www.angelone.in/news/mutual-funds/canara-robeco-large-cap-fund-delivers-over-6x-returns-in-15-years',
    'Invesco':'https://economictimes.indiatimes.com/invesco-india-largecap-fund-direct-plan/mffactsheet/schemeid-16712.cms?from=mdr',
    'SBI':'https://economictimes.indiatimes.com/defaultinterstitial.cms',
    'DSP':'https://economictimes.indiatimes.com/dsp-large-cap-fund-direct-plan/mffactsheet/schemeid-16456.cms?from=mdr',
    'ICICI':'https://economictimes.indiatimes.com/icici-prudential-large-mid-cap-fund/mffactsheet/schemeid-534.cms?from=mdr'
}
def process_mutual_fund(fund_name):
    import os

    # Extract first word
    first_word = fund_name.split()[0]

    # ---------------- NEWS FETCHING ----------------
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}
    link = fund_news.get(first_word)

    if link:
        try:
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.text.strip() if soup.title else "News Article"
            news.append({'title': title, 'url': link})
        except Exception as e:
            news.append({'title': f"Error fetching news: {e}", 'url': link})
    else:
        news.append({'title': "No news source available", 'url': "#"})

    # ---------------- CSV FILE DETECTION ----------------
    dataset_dir = "dataset/mutualfunds/"
    csv_file = None

    for file in os.listdir(dataset_dir):
        if file.startswith(first_word) and file.endswith(".csv"):
            csv_file = os.path.join(dataset_dir, file)
            break

    fund_data = None
    fig_html = None
    total_return = None
    return_summary = {}

    if csv_file:
        fund_data = pd.read_csv(csv_file)

        # ----------- DATE PARSING -------------
        try:
            fund_data["date"] = pd.to_datetime(fund_data["date"], format="%d-%m-%Y")
        except ValueError:
            try:
                fund_data["date"] = pd.to_datetime(fund_data["date"], format="%Y-%m-%d")
            except ValueError:
                fund_data["date"] = pd.to_datetime(fund_data["date"], dayfirst=True, errors="coerce")

        fund_data = fund_data.sort_values("date").reset_index(drop=True)

        # ----------- RETURNS -------------------
        fund_data["daily_return_%"] = fund_data["nav"].pct_change() * 100

        first_nav = fund_data["nav"].iloc[0]
        last_nav = fund_data["nav"].iloc[-1]
        total_return = ((last_nav - first_nav) / first_nav) * 100

        def calc_return(days):
            if len(fund_data) > days:
                past_nav = fund_data["nav"].iloc[-days]
                recent_nav = fund_data["nav"].iloc[-1]
                return ((recent_nav - past_nav) / past_nav) * 100
            return None

        return_summary = {
            "1_year": calc_return(365),
            "5_year": calc_return(365 * 5),
            "10_year": calc_return(365 * 9),
        }

        # ----------- PLOT -------------------
        fig = px.line(fund_data, x="date", y="nav", title=f"{fund_name} - NAV Trend")
        fig.update_layout(template="plotly_dark")
        fig_html = fig.to_html(full_html=False)

    return {
        "first_word": first_word,
        "fig_html": fig_html,
        "total_return": total_return,
        "return_summary": return_summary,
        "news": news
    }
