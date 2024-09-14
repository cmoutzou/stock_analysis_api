from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.io as pio
from gui.charts_window import *
from modules.stock_data import *
from modules.prediction import *
from modules.indicators import *
from modules.macroeconomy import *
from modules.stock_news import *

class ChartsWindow(QMainWindow):
    def __init__(self, stock_data, predictions):
        super().__init__()
        self.setWindowTitle("Charts Window")
        self.setGeometry(200, 200, 1200, 800)

        # Store the data
        self.stock_data = stock_data
        self.predictions = predictions

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and set up QWebEngineView
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Generate and display the chart figure
        fig = self.create_figure(self.stock_data, self.predictions)
        self.display_chart(fig)


        

    def create_figure(self, stock_data, predictions):
        """
        Creates a Plotly figure for stock data and predictions.
        """
        fig = make_subplots(rows=2, cols=1)

        # Ensure stock data is in the correct format
        stock_data.rename(columns={'timestamp': 'Date', 'close': 'Close'}, inplace=True)
        stock_data.reset_index(inplace=True)

        # Add stock price trace
        fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Close'], name="Stock Price"), row=1, col=1)
        print("Predictions Data:", self.predictions)
        # Add prediction trace if available
        if predictions is not None:
            fig.add_trace(go.Scatter(x=predictions['Date'], y=predictions['Prediction'], name="Prediction"), row=2, col=1)
        else:
            print("Warning: Predictions data is None. Skipping prediction plot.")

        # Customize layout (dark theme, labels)
        fig.update_layout(
            title="Stock Price and Predictions",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",  # Bloomberg-style dark theme
            height=700,
            hovermode='x unified'
        )

        return fig

    def create_figure(self, stock_data, predictions):
        """
        Creates a Plotly figure for stock data and predictions.
        """
        fig = make_subplots(rows=2, cols=1)

        # Ensure stock data is in the correct format
        stock_data.rename(columns={'timestamp': 'Date', 'close': 'Close'}, inplace=True)
        stock_data.reset_index(inplace=True)

        # Debugging: Print column names to ensure they are correct
        print("Stock Data Columns:", stock_data.columns)
        
        # Add stock price trace
        if 'Date' in stock_data.columns and 'Close' in stock_data.columns:
            fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Close'], name="Stock Price"), row=1, col=1)
        else:
            print("Error: 'Date' or 'Close' columns not found in stock_data.")
        
        # Add prediction trace if available
        if predictions is not None:
            if 'Date' in predictions.columns and 'Prediction' in predictions.columns:
                fig.add_trace(go.Scatter(x=predictions['Date'], y=predictions['Prediction'], name="Prediction"), row=2, col=1)
            else:
                print("Error: 'Date' or 'Prediction' columns not found in predictions.")
        else:
            print("Warning: Predictions data is None. Skipping prediction plot.")

        # Customize layout
        fig.update_layout(
            title="Stock Price and Predictions",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=700,
            hovermode='x unified'
        )

        return fig

    def display_chart(self, fig):
        chart_html = pio.to_html(fig, full_html=False)
        self.browser.setHtml(chart_html)