from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.io as pio
from modules.prediction import *

class ChartsWindow(QMainWindow):
    def __init__(self, stock_data, predictions):
        super().__init__()
        self.setWindowTitle("Stock Charts")
        self.setGeometry(200, 200, 900, 700)

        # Create layout and widget
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        
        # Generate chart using Plotly
        fig = make_subplots(rows=2, cols=1)

        # Example plot (replace with your actual logic)
        stock_data.rename(columns={'timestamp': 'Date', 'close': 'Close'}, inplace=True)
        stock_data.reset_index(inplace=True)
        fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Close'], name="Stock Price"), row=1, col=1)

        if predictions is not None:
            fig.add_trace(go.Scatter(x=predictions['Date'], y=predictions['Prediction'], name="Prediction"), row=2, col=1)
        else:
            print("Error: Predictions data is None.")
            # Handle this case, perhaps by showing a message or default chart

        # Render chart in the app window
        chart_html = pio.to_html(fig, full_html=False)
        chart_view = QWebEngineView()
        chart_view.setHtml(chart_html)
        
        layout.addWidget(chart_view)


    def create_charts(symbol):
        periods = ['1y', '6mo', '1d']
        intervals = ['1d', '1d', '1m']

        for period, interval in zip(periods, intervals):
            data = fetch_data_from_yf(symbol, period, interval)
            if data is None or data.empty:
                print(f"No data available for {symbol} with period {period} and interval {interval}")
                continue

            # Calculate indicators
            data = calculate_indicators(data)

            # Create traces for plotly
            traces = []

            # Closing price trace
            traces.append(go.Scatter(x=data['timestamp'], y=data['close'], mode='lines', name='Close', line=dict(color='#00B2E2')))

            # Bollinger Bands traces
            traces.append(go.Scatter(x=data['timestamp'], y=data['Bollinger_Upper'], mode='lines', name='Bollinger Upper Band', line=dict(color='red', dash='dash')))
            traces.append(go.Scatter(x=data['timestamp'], y=data['Bollinger_Lower'], mode='lines', name='Bollinger Lower Band', line=dict(color='red', dash='dash')))

            # Moving Averages traces
            traces.append(go.Scatter(x=data['timestamp'], y=data['MA_20'], mode='lines', name='MA 20', line=dict(color='green')))
            traces.append(go.Scatter(x=data['timestamp'], y=data['MA_50'], mode='lines', name='MA 50', line=dict(color='orange')))
            traces.append(go.Scatter(x=data['timestamp'], y=data['MA_200'], mode='lines', name='MA 200', line=dict(color='purple')))

            # Create figure
            fig = go.Figure(data=traces)

            # Update layout for interactive features
            fig.update_layout(
                title=f'{symbol} - {period} {interval}',
                xaxis_title='Date',
                yaxis_title='Value',
                template='plotly_dark',  # Dark theme
                hovermode='x unified'
            )

            # Show the plot
            fig.show()
