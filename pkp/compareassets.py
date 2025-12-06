

import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

import plotly.graph_objects as go

import plotly.offline as pyo

from getstockanalysis import get_stock_analysis,analyze_company_data

from gold import calculate_gold_investment

from  realestateinsight import get_real_estate_insight


def process_compare_assets(request):
    selected_assets = []
    selections = {}
    stock_data = None
    gold_data = None
    insight = None
    months = None
    years = None
    nfig_html = None
    return_percentage = None
    location = None
    graph_div = None
    rsno_years = None
    summary = None

    if request.method == "POST":
        selected_assets = request.form.getlist("assets")

        stock_choice = request.form.get("stock")
        location_choice = request.form.get("location_option")
        gold_choice = request.form.get("gold")
        crypto_choice = request.form.get("crypto")

        if stock_choice:
            selections["Stock"] = stock_choice
            months = int(request.form['no_month'])

        if location_choice:
            selections["Real Estate"] = location_choice
            rsno_years = int(request.form['rsno_years'])
            location = selections["Real Estate"]

        if gold_choice:
            selections["Gold"] = gold_choice
            years = int(request.form['no_years'])

        if crypto_choice:
            selections["Crypto"] = crypto_choice

        # ---- Stock Analysis ----
        if selections.get("Stock"):
            stock_data = get_stock_analysis(selections["Stock"], months=months)

        # ---- Gold Analysis ----
        if selections.get("Gold"):
            gold_data_raw = pd.read_csv('new_goldprice_yearly.csv', skiprows=1, names=['Year', 'Rate'])
            gold_data_raw['Rate'] = gold_data_raw['Rate'].str.replace(',', '').astype(int)
            gold_data_raw['Year'] = gold_data_raw['Year'].astype(int)
            gold_data_raw = gold_data_raw.sort_values(by='Year').tail(years)

            initial_price = gold_data_raw.iloc[0]['Rate']
            final_price = gold_data_raw.iloc[-1]['Rate']
            return_percentage = ((final_price - initial_price) / initial_price) * 100

            # Gold graph
            nfig = go.Figure()
            nfig.add_trace(go.Scatter(x=gold_data_raw['Year'], y=gold_data_raw['Rate'], mode='lines+markers'))
            nfig.update_layout(title='Gold Price (Yearly)', template='plotly_dark')
            nfig_html = nfig.to_html(full_html=False)

            # More gold data
            try:
                data_df = pd.read_csv('gold_data.csv')
                data_df['Date'] = pd.to_datetime(data_df['Date'], dayfirst=True)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data_df['Date'], y=data_df['High'], mode='lines'))
                fig.update_layout(title='Gold Price (Last 10 Years)', template='plotly_dark')

                fig_html = fig.to_html(full_html=False)

                gold_prices = {
                    2025: 102000, 2024: 78245, 2023: 63203, 2022: 55017, 2021: 48099, 2020: 50151,
                    2019: 39108, 2018: 31391, 2017: 29156, 2016: 27445, 2015: 24931, 2014: 26703,
                    2013: 28422, 2012: 30859, 2011: 27329, 2010: 20728, 2009: 16686, 2008: 13630,
                    2007: 10598, 2006: 9265, 2005: 7638, 2004: 6307, 2003: 5600, 2002: 4990,
                    2001: 4300, 2000: 4400
                }

                investment_result = None
                if 'year' in request.form and 'amount' in request.form:
                    year = int(request.form['year'])
                    amount = float(request.form['amount'])
                    investment_result = calculate_gold_investment(year, amount, gold_prices)

                gold_data = {
                    "fig_html": fig_html,
                    "investment_result": investment_result
                }

            except Exception as e:
                print("❌ Error (Gold):", e)

        # ---- Real Estate Analysis ----
        if selections.get("Real Estate"):
            insight = get_real_estate_insight(selections["Real Estate"])

            dta = pd.read_csv('dataset/NHDMumbai.csv')
            dta.columns = dta.columns.str.strip()

            selected = []
            for _, row in dta.iterrows():
                try:
                    price = float(str(row['Avg Price (₹/sq.ft)']).replace('INR', '').replace(',', '').strip())
                    selected.append({'location': row['Locality'].strip(), 'year': int(row['Year']), 'price': price})
                except:
                    continue

            selected = [i for i in selected if i['location'] == location]
            selected.sort(key=lambda x: x['year'])

            selected = selected[-rsno_years:]
            years_list = [i['year'] for i in selected]
            prices = [i['price'] for i in selected]

            return_percentage = round(((prices[-1] - prices[0]) / prices[0]) * 100, 2)

            historical_trace = go.Scatter(x=years_list, y=prices, mode='lines+markers')
            layout = go.Layout(title=f'Price Trend for {location}',
                               xaxis=dict(title='Year'),
                               yaxis=dict(title='Avg Price (₹/sq.ft)'),
                               template='plotly_dark')
            graph_div = pyo.plot(go.Figure(data=[historical_trace], layout=layout), output_type='div')

        # ---- Summary ----
        gold_return_percentage = return_percentage if selections.get("Gold") else None
        real_estate_return = insight['return_percentage'] if insight else None
        stock_return = stock_data['return_percentage'] if stock_data else None

        summary = {
            "Gold": gold_return_percentage,
            "Real Estate": real_estate_return,
            "Stocks": stock_return
        }

    # Return everything
    return {
        "selected_assets": selected_assets,
        "selections": selections,
        "stock_data": stock_data,
        "gold_data": gold_data,
        "gold_price_chart": nfig_html,
        "return_percentage": return_percentage,
        "real_estate_graph": graph_div,
        "insight": insight,
        "months": months,
        "summary": summary
    }
