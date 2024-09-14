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
import sys
import os
from datetime import datetime
import re

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Analysis App")
        self.setGeometry(100, 100, 1200, 800)

        symbol = 'AAPL'
        period = '1y'
        interval = '1d'

        # Fetch stock data
        self.stock_data = fetch_stock_data(symbol, period, interval)
        self.stock_predict_data = fetch_data_from_yf_predic(symbol, period, interval)
        self.predictions = plot_prediction(self.stock_predict_data)
        self.macroeconomics, self.macroeconomic_sentiment = analyze_macroeconomic_data()
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
        content_label = QLabel("Content will be shown here")
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
            macroeconomic_str = "<div style='color: #f1f1f1;'>Macroeconomic Analysis:<br>"
            for key, value in self.macroeconomics.items():
                macroeconomic_str += f"<b>{key}:</b> {value}<br>"
            self.macro_frame.findChild(QLabel).setText(macroeconomic_str.strip())
        else:
            self.macro_frame.findChild(QLabel).setText(f"<div style='color: #f1f1f1;'>Macroeconomic Analysis:<br>{self.macroeconomics}</div>")

        # Add sentiment information if needed
        self.macro_frame.findChild(QLabel).setText(self.macro_frame.findChild(QLabel).text() + f"<br><b>Sentiment:</b> {self.macroeconomic_sentiment}")

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
            self.prediction_frame.findChild(QLabel).setText(f"<div style='color: #f1f1f1;'>Prediction:<br>{self.predictions}</div>")


    def open_charts_window(self):
        self.charts_window = ChartsWindow(self.stock_data, self.predictions)
        self.charts_window.show()
