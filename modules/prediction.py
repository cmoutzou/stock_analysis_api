import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
from modules.data_preparation import *

#Prediction models chart
def fetch_data_from_yf_predic(symbol, period, interval):
    data = yf.download(symbol, interval=interval, period=period, progress=False)
    data = data[['Close']]
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')  # Coerce invalid values to NaN
    data.dropna(subset=['Close'], inplace=True)  # Drop rows where 'Close' is NaN
    print(data.head())
    return data

def plot_prediction(symbol, period, interval):
    # Retrieve the prepared data
    stock_data,train_data, test_data, arima_pred, arima_future_pred, lstm_pred,lstm_future_pred,indicators = prepare_prediction_data(symbol, period, interval)


    # Adjust LSTM predictions to match test data length
    lstm_start_index = len(test_data) - len(lstm_pred)  # Calculate starting index for LSTM predictions
    test_data['LSTM'] = pd.Series([None] * lstm_start_index + lstm_pred.flatten().tolist(), index=test_data.index)

    # Add ARIMA predictions
    test_data['ARIMA'] = pd.Series(arima_pred, index=test_data.index)

    # Generate future dates
    future_steps = len(arima_future_pred)
    last_date = test_data.index[-1]
    future_dates = [last_date + pd.DateOffset(days=i) for i in range(1, future_steps + 1)]
    future_df = pd.DataFrame(index=future_dates, data={'ARIMA': arima_future_pred, 'LSTM': lstm_future_pred.flatten()})

    # Create traces for plotly
    traces = []

    # Plot actual train and test data
    traces.append(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Train Data', line=dict(color='#00B2E2')))
    traces.append(go.Scatter(x=test_data.index, y=test_data['Close'], mode='lines', name='Test Data', line=dict(color='#FF6600')))
    
    # ARIMA and LSTM Predictions
    traces.append(go.Scatter(x=test_data.index, y=test_data['ARIMA'], mode='lines', name='ARIMA Predictions', line=dict(color='purple', dash='dash')))
    traces.append(go.Scatter(x=test_data.index, y=test_data['LSTM'], mode='lines', name='LSTM Predictions', line=dict(color='green', dash='dash')))

    # Future Predictions
    traces.append(go.Scatter(x=future_df.index, y=future_df['ARIMA'], mode='lines', name='Future ARIMA Predictions', line=dict(color='purple', dash='dot')))
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

    return fig

# Example usage:
#plot_prediction('AAPL', '1y', '1d')
