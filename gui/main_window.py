import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QGridLayout, QFrame, QScrollArea, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImage
from gui.charts_window import *
from modules.stock_data import *
from modules.prediction import *
from modules.indicators import *
from modules.macroeconomy import *
from modules.stock_news import *
import pandas as pd
import requests 
from datetime import datetime
import re

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Analysis App")
        self.setGeometry(100, 100, 1200, 1000)

        self.symbol = 'AAPL'
        period = '1y'
        interval = '1d'

        # Fetch stock data
        self.stock_data = fetch_stock_data(symbol, period, interval)
        self.stock_predict_data = fetch_data_from_yf_predic(symbol, period, interval)
        self.predictions = plot_prediction(symbol, period, interval)
        self.macroeconomics, self.macroeconomic_descriptions, self.macroeconomic_sentiment = analyze_macroeconomic_data()
        self.news_data = fetch_news(symbol)
        self.news_sentiment = get_news_sentiment(symbol)

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Styling
        font = QFont('Segoe UI', 12)
        section_style = "background-color: #2e2e2e; color: #e0e0e0; padding: 15px; border-radius: 5px;"

        # Create and add widgets for each section
        self.indicator_frame = self.create_scrollable_section("Financial Indicators ", section_style)
        self.macro_frame = self.create_section("Macroeconomic Analysis \n", section_style, font)
        self.news_frame = self.create_scrollable_section("News Sentiment", section_style)
        self.prediction_frame = self.create_section("Prediction\n", section_style, font)

        # Create labels for predictions
        self.arima_prediction_label = QLabel("ARIMA Prediction: N/A")
        self.lstm_prediction_label = QLabel("LSTM Prediction: N/A")

        # Add labels to prediction_frame
        self.prediction_frame.layout().addWidget(self.arima_prediction_label)
        self.prediction_frame.layout().addWidget(self.lstm_prediction_label)        

        # Add widgets to layout
        layout.addWidget(self.indicator_frame, 0, 0, 1, 1)
        layout.addWidget(self.news_frame, 0, 1, 1, 1)
        layout.addWidget(self.macro_frame, 1, 0, 1, 1)
        layout.addWidget(self.prediction_frame, 1, 1, 1, 1)

        # Add button to open Charts Window
        self.open_charts_button = QPushButton("Open Charts Window")
        self.open_charts_button.setStyleSheet("background-color: #007acc; color: white; padding: 10px; border-radius: 5px;")
        self.open_charts_button.clicked.connect(self.open_charts_window)
        layout.addWidget(self.open_charts_button, 2, 0, 1, 2, Qt.AlignCenter)
        
       # Set section contents
        self.update_sections()
        print(dir(self))  # Αυτό θα εμφανίσει όλα τα χαρακτηριστικά του αντικειμένου




    def create_indicators(self, indicators, explanations):
        # Create a scrollable section for indicators
        indicator_str = ""
        for column, value in indicators.items():
            if isinstance(value, (int, float)):  # Numeric values
                explanation = explanations.get(column, {})
                description = remove_ansi_codes(explanation.get('description', ''))
                feeling = explanation.get('feeling', 'Neutral')
                indicator_str += f"<div style='color: #f1f1f1;'><b>{column}:</b> {value:.2f} - {print_colored_html(description, feeling)}</div>"
            else:
                indicator_str += f"<b>{column}:</b> {value}<br>"

        # Find and update the content label inside the scrollable indicator frame
        scroll_area_content = self.indicator_frame.findChild(QScrollArea).widget()
        content_label = QLabel(f"<div style='color: #f1f1f1;'>{indicator_str.strip()}</div>")
        content_label.setTextFormat(Qt.RichText)
        scroll_area_content.layout().addWidget(content_label)
    

    def create_section(self, title, style, font):
        frame = QFrame()
        frame.setStyleSheet(style)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Reduce spacing between widgets

        # Create a bold font for the title
        bold_font = QFont(font)
        bold_font.setBold(True)

        # Create and style the title label
        title_label = QLabel(title)
        title_label.setFont(bold_font)  # Apply the bold font
        title_label.setStyleSheet("margin-bottom: 5px;")  # Small margin below the title
        layout.addWidget(title_label)

        # Create and style the content label
        content_label = QLabel("")
        content_label.setWordWrap(True)
        content_label.setFont(font)  # Use the regular font for content
        layout.addWidget(content_label)

        return frame

    def create_scrollable_section(self, title, style):
        frame = QFrame()
        frame.setStyleSheet(style)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Reduce spacing between widgets

        # Create and style the title label
        title_label = QLabel(title)
        title_font = QFont('Arial', 14)
        title_font.setBold(True)
        title_label.setFont(title_font)  # Apply the bold font
        title_label.setStyleSheet("color: #f1f1f1; margin-bottom: 5px;")  # Light color for dark background
        layout.addWidget(title_label)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)
        scroll_area_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        scroll_area_layout.setSpacing(2)  # Reduce spacing between widgets
        scroll_area_content.setLayout(scroll_area_layout)
        scroll_area.setWidget(scroll_area_content)

        # Add scroll area to frame layout
        layout.addWidget(scroll_area)
        return frame
    

    def update_prediction_section(self):
        # Fetch prediction data
        result = prepare_prediction_data(self.symbol, '1y', '1d')
        data, train_data, test_data, arima_pred, arima_future_pred, lstm_pred, lstm_future_pred, indicators = result
        
        # Convert to numpy arrays if needed
        if isinstance(arima_future_pred, pd.Series):
            arima_future_pred = arima_future_pred.to_numpy()
        if isinstance(lstm_future_pred, pd.Series):
            lstm_future_pred = lstm_future_pred.to_numpy()

        # Handle empty predictions
        if arima_future_pred.size > 0:
            predicted_price_arima = arima_future_pred[-1]  # Latest ARIMA prediction
        else:
            predicted_price_arima = 'N/A'  # Handle case with no predictions

        if lstm_future_pred.size > 0:
            predicted_price_lstm = lstm_future_pred[-1]    # Latest LSTM prediction
        else:
            predicted_price_lstm = 'N/A'  # Handle case with no predictions

        # Format the predictions correctly
        if isinstance(predicted_price_arima, (int, float)):
            predicted_price_arima = f"${predicted_price_arima:.2f}"
        elif isinstance(predicted_price_arima, str):
            predicted_price_arima = predicted_price_arima

        if isinstance(predicted_price_lstm, (int, float)):
            predicted_price_lstm = f"${predicted_price_lstm:.2f}"
        elif isinstance(predicted_price_lstm, str):
            predicted_price_lstm = predicted_price_lstm

        # Update the labels or text fields with predictions
        self.arima_prediction_label.setText(f"ARIMA Prediction: {predicted_price_arima}")
        self.lstm_prediction_label.setText(f"LSTM Prediction: {predicted_price_lstm}")

        # Update indicators
        self.update_indicators(indicators)

        # Remove test data and other non-relevant info from prediction_frame
        self.prediction_frame.findChild(QLabel).setText("")  # Clear out any old content in the prediction frame



    def update_prediction_charts(self, test_data, arima_pred, lstm_pred):
        # Assuming prediction_frame contains a QLabel for displaying predictions
        prediction_label = self.prediction_frame.findChild(QLabel)
        if prediction_label:
            prediction_label.setText(f"Test Data: {test_data}\nARIMA Prediction: {arima_pred}\nLSTM Prediction: {lstm_pred}")
        else:
            print("Error: prediction_frame does not contain a QLabel for updating.")

    def update_indicators(self, indicators):
        for indicator in indicators:
            label = getattr(self, f'{indicator}_label', None)
            if label:
                label.setText(f"{indicator}: {value:.2f}")
            else:
                print(f"Warning: {indicator}_label not found.")

  

    def update_sections(self):

        # Path to the default icon (replace with your own path or URL)
        default_icon_path = r'C:\\Users\\Sissy\\Desktop\\python\\projects\\ETL\\stock_analysis_api\\resources\\default_news.png'

        # Update the indicators section
        indicators_data = calculate_indicators(self.stock_data)
        indicators_explanations = explain_indicators(indicators_data)  # Fetch the explanations for the indicators
        latest_indicators = indicators_data.iloc[-1]  # Get the latest row of indicators

        # Create a scrollable section for indicators
        indicator_str = ""
        for column, value in latest_indicators.items():
            if isinstance(value, (int, float)):  # Numeric values
                explanation = indicators_explanations.get(column, {})
                description = remove_ansi_codes(explanation.get('description', ''))
                feeling = explanation.get('feeling', 'Neutral')
                indicator_str += f"<div style='color: #f1f1f1;'><b>{column}:</b> {value:.2f} - {print_colored_html(description, feeling)}</div>"
            else:
                indicator_str += f"<b>{column}:</b> {value}<br>"

        # Find and update the content label inside the scrollable indicator frame
        scroll_area_content = self.indicator_frame.findChild(QScrollArea).widget()
        content_label = QLabel(f"<div style='color: #f1f1f1;'>{indicator_str.strip()}</div>")
        content_label.setTextFormat(Qt.RichText)
        scroll_area_content.layout().addWidget(content_label)



        # Handle macroeconomic data
        
        if isinstance(self.macroeconomics, dict):
            description = self.macroeconomic_sentiment
            sentiment_color  = 'yellow'  # Default color for neutral
            if description == 'Positive':
                sentiment_color  = '#32CD32'
            elif description == 'Negative':
                sentiment_color  = '#FF6347'
            macroeconomic_str = (
                f"<div style='color: #f1f1f1;'>"
                f"<h3 style='color:{sentiment_color}; font-size:16px; font-weight:normal;'>"
                f"Sentiment: {self.macroeconomic_sentiment}</h3>"
        )
            for key, value in self.macroeconomics.items():
                description = self.macroeconomic_descriptions.get(key, 'Neutral')
                sentiment_color  = 'yellow'  # Default color for neutral
                if description == 'Positive':
                    sentiment_color  = '#32CD32'
                elif description == 'Negative':
                    sentiment_color  = '#FF6347'
                
                # Corrected the HTML style string
                macroeconomic_str += (
                f"<div style='font-size: 14px; margin-bottom: 6px;'>"
                f"<b>{key}:</b> <span style='color: #f1f1f1;'>{value}</span> "
                f"<span style='color: {sentiment_color }; font-size: 12px;'>{description}</span>"
                f"</div>"
        )

                macroeconomic_str += "</div>"

            # Apply the formatted string to the QLabel in the macro_frame
            self.macro_frame.findChild(QLabel).setText(macroeconomic_str)
        else:
            self.macro_frame.findChild(QLabel).setText(f"<div style='color: #f1f1f1;'>Macroeconomic Analysis:<br>{self.macroeconomics}</div>")

       



        # Update the news section
        if isinstance(self.news_data, list) and self.news_data:
            sentiment_styles = {
                'positive': 'color: #00FF00; font-weight: bold;',  # Green for positive
                'negative': 'color: #FF0000; font-weight: bold;',  # Red for negative
                'neutral': 'color: #FFFF00;'  # Yellow for neutral
            }

            # Set the style based on the sentiment
            sentiment_style = sentiment_styles.get(self.news_sentiment.lower(), 'color: #FFFF00;')
            news_str = ""
            
            # Create and add the sentiment info label on top
            sentiment_timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            sentiment_info = QLabel(f"<div style='{sentiment_style}'>News sentiment {sentiment_timestamp}: {self.news_sentiment.capitalize()}</div>")
            sentiment_info.setTextFormat(Qt.RichText)
            sentiment_info.setWordWrap(True)
            
            # Add sentiment info to the layout
            scroll_area_content = self.news_frame.findChild(QScrollArea).widget()
            scroll_area_content.layout().addWidget(sentiment_info)

            for news_item in self.news_data:
                thumbnail = news_item.get('thumbnail', '')
                title = news_item.get('title', 'No Title')
                publisher = news_item.get('publisher', 'No Publisher')
                link = news_item.get('link', '#')

                # Create a horizontal layout for each news item
                news_layout = QHBoxLayout()

                # Add thumbnail if available, otherwise use a default icon
                width = 80  # Set width of the image
                height = 80  # Set height of the image
                thumbnail_label = QLabel()
                if thumbnail:
                    image = QImage()
                    image.loadFromData(requests.get(thumbnail).content)
                    pixmap = QPixmap.fromImage(image)
                else:
                    # Load the default icon if no thumbnail is available
                    pixmap = QPixmap(default_icon_path)

                thumbnail_label.setPixmap(pixmap.scaled(width, height, Qt.KeepAspectRatio))
                news_layout.addWidget(thumbnail_label)

                # Add title and publisher
                news_info = QLabel(f"<a href='{link}' style='color: #4a90e2;'>{title}</a><br><span style='color: #f1f1f1;'>{publisher}</span>")
                news_info.setTextFormat(Qt.RichText)
                news_info.setOpenExternalLinks(True)
                news_info.setWordWrap(True)
                news_layout.addWidget(news_info)

                # Add the layout to the scroll area content
                scroll_area_content.layout().addLayout(news_layout)

            # Reduce spacing between news items
            scroll_area_content.layout().setSpacing(5)  # Adjust spacing between news items

        else:
            self.news_frame.findChild(QLabel).setText("<div style='color: #f1f1f1;'>No news available.</div>")

            # Update the prediction section
            #self.prediction_frame.findChild(QLabel).setText(f"<div style='color: #f1f1f1;'>Prediction:<br>{self.predictions}</div>")
        #self.charts_window = ChartsWindow(self.stock_data, self.predictions)
        #self.prediction_frame.addWidget(self.charts_window)
        self.update_prediction_section()


    def open_charts_window(self):
        self.charts_window = ChartsWindow(self.symbol)
        self.charts_window.show()
