from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import requests
import pandas as pd
from io import StringIO
import numpy as np

def predict_future_price(company, name_company1):
    if not company:
        return "Invalid company input"

    first_word = company.strip().lower().split()[0]
    scrip_code = None
    for entry in name_company1:
        if entry['company'].strip().lower().split()[0] == first_word:
            scrip_code = entry['code']+'.BSE'
            break

    if not scrip_code:
        return "Company not found"

    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={scrip_code}&apikey=VBPRQMIQP3MSWHT9&datatype=csv'
        r = requests.get(url)
        df = pd.read_csv(StringIO(r.text))
        df = df.head(5)[::-1]  # last 5 months in chronological order

        if df.empty:
            return "No data found for prediction"

        close_prices = df['close'].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        scaled_close = scaler.fit_transform(close_prices)

        sequence_length = 3
        x, y = [], []
        for i in range(sequence_length, len(scaled_close)):
            x.append(scaled_close[i - sequence_length:i, 0])
            y.append(scaled_close[i, 0])

        if not x:
            return "Not enough data to make prediction"

        x = np.array(x).reshape(-1, sequence_length, 1)
        y = np.array(y)

        model = Sequential()
        model.add(LSTM(50, input_shape=(sequence_length, 1)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x, y, epochs=200, batch_size=1, verbose=0)

        last_sequence = scaled_close[-sequence_length:].reshape(1, sequence_length, 1)
        predicted_scaled_price = model.predict(last_sequence)
        predicted_price = scaler.inverse_transform(predicted_scaled_price)

        return float(predicted_price[0][0])

    except Exception as e:
        return f"Error during prediction: {e}"