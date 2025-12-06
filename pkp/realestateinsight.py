
import pandas as pd

import plotly.graph_objects as go

import plotly.offline as pyo

from prophet import Prophet

def get_real_estate_insight(location):


    # Load and clean dataset
    df = pd.read_csv('dataset/realestate/NewMumbai.csv')
    df.columns = df.columns.str.strip()
    df = df[df['Locality'] == location]

    # Clean price column
    df['Avg Price (?/sq.ft)'] = (
        df['Avg Price (?/sq.ft)']
        .astype(str)
        .str.replace('INR', '', regex=False)
        .str.replace(',', '', regex=False)
        .str.strip()
        .astype(float)
    )

    # Prophet prediction
    df_prophet = df.rename(columns={'Year': 'ds', 'Avg Price (?/sq.ft)': 'y'})
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'], format='%Y')
    df_prophet.drop(columns=['Locality'], inplace=True)

    model = Prophet(daily_seasonality=False, yearly_seasonality=False)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=5, freq='Y')
    forecast = model.predict(future)

    forecast_after_2025 = forecast[forecast['ds'].dt.year > 2025]
    future_years = forecast_after_2025['ds'].dt.year
    future_prices = forecast_after_2025['yhat']

    # Future price chart
    future_trace = go.Scatter(
        x=future_years,
        y=future_prices,
        mode='lines+markers',
        name=f"{location} (Forecast)",
        line=dict(color='violet')
    )
    future_layout = go.Layout(
        title=f'Forecasted Price Trend for {location} (After 2025)',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Avg Price (₹/sq.ft)'),
        template='plotly_dark'
    )
    future_graph_div = pyo.plot(go.Figure(data=[future_trace], layout=future_layout), output_type='div')

    # Historical price trend
    df_sorted = df.sort_values(by='Year')
    years = df_sorted['Year'].tolist()
    prices = df_sorted['Avg Price (?/sq.ft)'].tolist()

    # Yield values
    latest_yield = round(df_sorted['Monthly Yield(sq. ft.)'].iloc[-1], 2)

    # Return percentage calculation
    return_percentage = round(((prices[-1] - prices[0]) / prices[0]) * 100, 2)

    # Growth trend advice
    price_diff = df_sorted['Avg Price (?/sq.ft)'].diff().dropna()
    positive_growth = sum(price_diff > 0)
    negative_growth = sum(price_diff < 0)

    if positive_growth > negative_growth:
        advice = '📈 Overall Positive momentum with healthy returns. Could be a good time to consider investing.'
    elif negative_growth > positive_growth:
        advice = '📉 Overall Negative momentum and falling prices. Exercise caution before investing.'
    else:
        advice = '⚖️ Mixed signals. Consider waiting for clearer trends or consult a financial advisor.'

    # Historical price chart
    price_trace = go.Scatter(
        x=years,
        y=prices,
        mode='lines+markers',
        name='Avg Price (₹/sq.ft)',
        line=dict(color='violet')
    )
    price_layout = go.Layout(
        title=f'Historical Price Trend for {location}',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Avg Price (₹/sq.ft)'),
        template='plotly_dark'
    )
    graph_div = pyo.plot(go.Figure(data=[price_trace], layout=price_layout), output_type='div')

    # Data table
    df_display = df_sorted[['Year', 'Avg Price (?/sq.ft)', 'Monthly Yield(sq. ft.)', 'Residence Yield(sq.ft.)']].copy()
    df_display.columns = ['Year', 'Avg Price (₹/sq.ft)', 'Monthly Yield (₹/sq.ft)', 'Residence Yield (₹/sq.ft)']
    table_html = df_display.to_html(index=False, classes='table table-dark table-striped', border=0)

    # External link
    web_location = location.split()[0].lower()
    link = f'https://www.magicbricks.com/property-for-sale-in-{web_location}-mumbai-pppfs'

    return {
        'graph_div': graph_div,
        'future_graph_div': future_graph_div,
        'return_percentage': return_percentage,
        'advice': advice,
        'link': link,
        'location': location,
        'latest_yield': latest_yield,
        'table': table_html
    }