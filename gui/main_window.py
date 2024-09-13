from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt
from gui.charts_window import *
from modules.stock_data import *
from modules.prediction import *
from modules.indicators import *
from modules.macroeconomy import *
from modules.stock_news import *
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Analysis App")
        self.setGeometry(100, 100, 800, 600)
        symbol = 'AAPL'
        period = '1y'
        interval = '1d'

        # Fetch stock data
        self.stock_data = fetch_stock_data(symbol, period, interval)
        self.stock_predict_data = fetch_data_from_yf_predic(symbol, period, interval)
        self.predictions = plot_prediction(self.stock_predict_data)
        self.macroeconomics = analyze_macroeconomic_data()
        self.news_sentiment = get_news_sentiment(symbol)

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and add widgets for each section
        self.indicator_label = QLabel("Indicators will be shown here")
        self.macro_label = QLabel("Macroeconomic Analysis will be shown here")
        self.news_label = QLabel("News will be shown here")

        # Add widgets to layout
        layout.addWidget(QLabel("Financial Indicators:"))
        layout.addWidget(self.indicator_label)
        layout.addWidget(QLabel("Macroeconomic Analysis:"))
        layout.addWidget(self.macro_label)
        layout.addWidget(QLabel("News Sentiment:"))
        layout.addWidget(self.news_label)

        # Add button to open Charts Window
        self.open_charts_button = QPushButton("Open Charts Window")
        self.open_charts_button.clicked.connect(self.open_charts_window)
        layout.addWidget(self.open_charts_button)

        # Set section contents
        self.update_sections()

    def update_sections(self):
        # Update the indicators section
        indicators_data = calculate_indicators(self.stock_data)
        latest_indicators = indicators_data.iloc[-1]  # Get the latest row of indicators

        indicators_str = ""
        for column, value in latest_indicators.items():
            if isinstance(value, (int, float)):  # Numeric values
                indicators_str += f"{column}: {value:.2f}\n"
            elif isinstance(value, pd.Timestamp):  # Timestamps
                indicators_str += f"{column}: {value.strftime('%Y-%m-%d')}\n"
            else:
                indicators_str += f"{column}: {value}\n"  # Other types (e.g., strings)

        self.indicator_label.setText("Indicators:\n" + indicators_str.strip())

        # Update the macroeconomic analysis section
        self.macro_label.setText("Macroeconomic Analysis: " + str(self.macroeconomics))

        # Update the news section
        self.news_label.setText("News Sentiment: " + str(self.news_sentiment))

    def open_charts_window(self):
        if hasattr(self, 'stock_data') and hasattr(self, 'predictions'):
            print(self.stock_data.head())  # Check stock data
            print(self.predictions)       # Check predictions data
            self.charts_window = ChartsWindow(self.stock_data, self.predictions)
            self.charts_window.show()
        else:
            print("No data available to display in charts.")
