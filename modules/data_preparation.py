import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from modules.indicators import *


def fetch_data_from_yf(symbol, period, interval):
    data = yf.download(symbol, interval=interval, period=period, progress=False)
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')  # Coerce invalid values to NaN
    data.dropna(subset=['Close'], inplace=True)  # Drop rows where 'Close' is NaN
    return data

def prepare_prediction_data(symbol, period, interval):
    # Fetch data
    data = fetch_data_from_yf(symbol, period, interval)

    # Split the data into training and testing sets
    train_size = int(len(data) * 0.8)
    train_data = data[:train_size]
    test_data = data[train_size:]

    # Use only the 'Close' column for ARIMA (univariate)
    train_close = train_data['Close']
    test_close = test_data['Close']

    # Calculate indicators
    indicators = calculate_indicators(data)

    # ARIMA Model
    model = ARIMA(train_close, order=(5, 1, 0))
    arima_result = model.fit()

    # Make ARIMA predictions
    arima_pred = arima_result.predict(start=len(train_close), end=len(data)-1, typ='levels')

    # Extend ARIMA predictions into the future
    future_steps = len(test_data)
    arima_future_pred = arima_result.forecast(steps=future_steps)

    # Scale the data for LSTM (you may want to use 'Close' as well)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[['Close']])

    # Create sequences for LSTM
    def create_sequences(data, sequence_length):
        sequences = []
        labels = []
        for i in range(len(data) - sequence_length):
            sequences.append(data[i:i + sequence_length])
            labels.append(data[i + sequence_length])
        return np.array(sequences), np.array(labels)

    sequence_length = 40
    X_train, y_train = create_sequences(scaled_data[:train_size], sequence_length)
    X_test, y_test = create_sequences(scaled_data[train_size:], sequence_length)

    # Debugging: Print the shapes before reshaping
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"Train size: {train_size}")
    print(f"Test size: {len(test_data)}")
    print(f"Sequence length: {sequence_length}")

    # Check if there is enough data for LSTM sequences
    if X_train.size == 0 or X_test.size == 0:
        print("Not enough data for LSTM sequences. Try reducing the sequence length.")
        return

    # Reshape for LSTM
    try:
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    except ValueError as e:
        print(f"Reshape error: {e}")
        print(f"X_train shape before reshape: {X_train.shape}")
        print(f"X_test shape before reshape: {X_test.shape}")
        return

    # Build the LSTM model
    lstm_model = Sequential()
    lstm_model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    lstm_model.add(LSTM(50, return_sequences=False))
    lstm_model.add(Dense(25))
    lstm_model.add(Dense(1))

    # Compile the model
    lstm_model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    lstm_model.fit(X_train, y_train, batch_size=64, epochs=20)

    # Predict using the LSTM model
    lstm_pred = lstm_model.predict(X_test)
    lstm_pred = scaler.inverse_transform(lstm_pred)

    # Extend LSTM predictions into the future
    future_sequence = scaled_data[-sequence_length:]
    future_predictions = []

    for _ in range(future_steps):
        pred = lstm_model.predict(future_sequence.reshape(1, sequence_length, 1))
        future_predictions.append(pred[0, 0])
        future_sequence = np.append(future_sequence[1:], pred)

    lstm_future_pred = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    # Create DataFrame for test_data including predictions
    test_data = test_data.copy()
    test_data['ARIMA'] = np.nan
    test_data['LSTM'] = np.nan

    # Correct length calculation for assignment
    arima_pred_series = pd.Series(arima_pred, index=test_data.index[sequence_length:])
    lstm_pred_series = pd.Series(lstm_pred.flatten(), index=test_data.index[sequence_length:])

    test_data.loc[test_data.index[sequence_length:], 'ARIMA'] = arima_pred_series
    test_data.loc[test_data.index[sequence_length:], 'LSTM'] = lstm_pred_series

    # Generate future dates and match the length with predictions
    last_date = test_data.index[-1]
    future_dates = [last_date + pd.DateOffset(days=i) for i in range(1, future_steps + 1)]
    future_df = pd.DataFrame(index=future_dates, data={'Close': np.nan, 'ARIMA': arima_future_pred, 'LSTM': lstm_future_pred.flatten()})

    return pd.DataFrame(data), train_data, test_data, arima_pred, arima_future_pred, lstm_pred, lstm_future_pred, indicators



result = prepare_prediction_data('AAPL', '1y', '1d')
print(result)  # This will print all the returned values