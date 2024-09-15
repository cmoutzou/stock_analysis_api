import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from modules.data_preparation import prepare_prediction_data
from modules.prediction import *
from modules.indicators import *

class ChartsWindow(QMainWindow):
    def __init__(self, stock_symbol):
        super().__init__()
        self.setWindowTitle("Charts Window")
        self.setGeometry(200, 200, 1200, 800)

        # Store the data
        self.stock_data, self.train_data, self.test_data, self.arima_pred, self.arima_future_pred, self.lstm_pred, self.lstm_future_pred, indicators = prepare_prediction_data(stock_symbol, '1y', '1d')

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and set up QWebEngineView
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Generate and display the chart figure
        fig, chart_html = self.create_figure(self.stock_data, self.test_data, self.arima_future_pred, self.lstm_future_pred)
        self.display_chart(chart_html)

    def create_figure(self, stock_data, test_data, arima_future_pred, lstm_future_pred):
        """
        Creates a Plotly figure for stock data and predictions.
        """
        fig = make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.7, 0.3],  # Adjust these values to set row heights; total should be 1
            vertical_spacing=0.1     # Adjust vertical spacing between rows
        )

        indicators = calculate_indicators(stock_data)
        # Ensure stock data is in the correct format
        stock_data.reset_index(inplace=True)
        indicators.reset_index(inplace=True)

        # Add stock price trace
        fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Close'], name="Stock Price"), row=1, col=1)
        # Bollinger Bands traces
        fig.add_trace(go.Scatter(x=indicators['Date'], y=indicators['Bollinger_Upper'], mode='lines', name='Bollinger Upper Band', line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter(x=indicators['Date'], y=indicators['Bollinger_Lower'], mode='lines', name='Bollinger Lower Band', line=dict(color='red', dash='dash')))

        # Moving Averages traces
        fig.add_trace(go.Scatter(x=indicators['Date'], y=indicators['MA_20'], mode='lines', name='MA 20', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=indicators['Date'], y=indicators['MA_50'], mode='lines', name='MA 50', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=indicators['Date'], y=indicators['MA_200'], mode='lines', name='MA 200', line=dict(color='purple')))

        # Convert predictions to numpy arrays if necessary
        arima_future_pred = np.array(arima_future_pred).flatten()
        lstm_future_pred = np.array(lstm_future_pred).flatten()

        # Add ARIMA future predictions trace
        if arima_future_pred is not None:
            fig.add_trace(go.Scatter(x=test_data.index, y=arima_future_pred, name="ARIMA Future Predictions"), row=2, col=1)

        # Add LSTM future predictions trace
        if lstm_future_pred is not None:
            fig.add_trace(go.Scatter(x=test_data.index, y=lstm_future_pred, name="LSTM Future Predictions"), row=2, col=1)

        # Customize layout
        fig.update_layout(
            title="Stock Price and Predictions",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=1500,
            hovermode='x unified'
        )

        # Convert Plotly figure to HTML string
        chart_html = pio.to_html(fig, full_html=False)
        fig.show()
        return fig, chart_html

    def display_chart(self, chart_html):
        # Set the HTML content in QWebEngineView
        self.browser.setHtml(chart_html)
