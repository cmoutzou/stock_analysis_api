import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import warnings
from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler


#Prediction models chart
def fetch_data_from_yf_predic(symbol, period, interval):
    data = yf.download(symbol, interval=interval, period=period, progress=False)
    data = data[['Close']]
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')  # Coerce invalid values to NaN
    data.dropna(subset=['Close'], inplace=True)  # Drop rows where 'Close' is NaN
    print(data.head())
    return data

def plot_prediction(data):
    # Split the data into training and testing sets
    train_size = int(len(data) * 0.8)
    train_data = data[:train_size]
    test_data = data[train_size:]

    # ARIMA Model
    model = ARIMA(train_data['Close'], order=(5, 1, 0))
    arima_result = model.fit()

    # Make ARIMA predictions
    arima_pred = arima_result.predict(start=len(train_data), end=len(data)-1, typ='levels')

    # Extend ARIMA predictions into the future
    future_steps = len(test_data)
    arima_future_pred = arima_result.forecast(steps=future_steps)

    # Scale the data for LSTM
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Create sequences for LSTM
    def create_sequences(data, sequence_length):
        sequences = []
        labels = []
        for i in range(len(data) - sequence_length):
            sequences.append(data[i:i + sequence_length])
            labels.append(data[i + sequence_length])
        return np.array(sequences), np.array(labels)

    sequence_length = min(60, int(train_size * 0.2))
    X_train, y_train = create_sequences(scaled_data[:train_size], sequence_length)
    X_test, y_test = create_sequences(scaled_data[train_size:], sequence_length)
    print(f"X_train: {X_train.shape}, X_test: {X_test.shape}")

    # Reshape for LSTM
    print(f"Shape of X_test before reshape: {X_test.shape}")
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    if X_test.shape[0] > 0:
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    else:
        raise ValueError("X_test is too small for reshaping. Consider adjusting the sequence length or the data split.")

    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))

    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(X_train, y_train, batch_size=64, epochs=20)

    # Predict using the LSTM model
    lstm_pred = model.predict(X_test)
    lstm_pred = scaler.inverse_transform(lstm_pred)

    # Extend LSTM predictions into the future
    future_sequence = scaled_data[-sequence_length:]
    future_predictions = []

    for _ in range(future_steps):
        pred = model.predict(future_sequence.reshape(1, sequence_length, 1))
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

    # Create traces for plotly
    traces = []

    # Plot actual train and test data
    traces.append(go.Scatter(x=train_data.index, y=train_data['Close'], mode='lines', name='Train Data', line=dict(color='#00B2E2')))
    traces.append(go.Scatter(x=test_data.index, y=test_data['Close'], mode='lines', name='Test Data', line=dict(color='#FF6600')))
    
    # ARIMA Predictions
    traces.append(go.Scatter(x=test_data.index, y=test_data['ARIMA'], mode='lines', name='ARIMA Predictions', line=dict(color='purple', dash='dash')))

    # LSTM Predictions
    traces.append(go.Scatter(x=test_data.index, y=test_data['LSTM'], mode='lines', name='LSTM Predictions', line=dict(color='green', dash='dash')))

    # Future ARIMA Predictions
    traces.append(go.Scatter(x=future_df.index, y=future_df['ARIMA'], mode='lines', name='Future ARIMA Predictions', line=dict(color='purple', dash='dot')))

    # Future LSTM Predictions
    traces.append(go.Scatter(x=future_df.index, y=future_df['LSTM'], mode='lines', name='Future LSTM Predictions', line=dict(color='green', dash='dot')))

    # Create figure
    fig = go.Figure(data=traces)

    # Update layout for interactive features
    fig.update_layout(
        title='Prediction Analysis',
        xaxis_title='Date',
        yaxis_title='Close Price USD ($)',
        template='plotly_dark',  # Dark theme
        hovermode='x unified'
    )

    # Show the plot
    fig.show()


