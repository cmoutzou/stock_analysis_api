import re
import requests
import yfinance as yf
import pandas as pd
import numpy as np
#pip install fredapi
from fredapi import Fred
import matplotlib.pyplot as plt
from textblob import TextBlob
from bs4 import BeautifulSoup
import seaborn as sns
#pip install plotly
import plotly.graph_objects as go


from contextlib import contextmanager

symbol='AAPL'
interval='1d'
period='1y'

df = yf.download(symbol, interval=interval, period=period, progress=False)
print(df.columns)
def calculate_indicators(df):
    if df.empty:
        return df

    # Moving Average
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Volatility
    df['Volatility'] = df['Close'].rolling(window=20).std()

    # MACD
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df['Bollinger_Middle'] = df['Close'].rolling(window=20).mean()
    df['Bollinger_Upper'] = df['Bollinger_Middle'] + 2 * df['Close'].rolling(window=20).std()
    df['Bollinger_Lower'] = df['Bollinger_Middle'] - 2 * df['Close'].rolling(window=20).std()

    # Average True Range (ATR)
    df['High'].fillna(df['High'].mean(), inplace=True)
    df['Low'].fillna(df['Low'].mean(), inplace=True)
    df.dropna(subset=['High', 'Low'], inplace=True)

    df['High-Low'] = df['High'] - df['Low']
    df['High-Close'] = np.abs(df['High'] - df['Close'].shift())
    df['Low-Close'] = np.abs(df['Low'] - df['Close'].shift())
    df['True_Range'] = df[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
    df['ATR'] = df['True_Range'].rolling(window=14).mean()

    def fetch_pe_ratio(symbol):
        stock = yf.Ticker(symbol)
        try:
            info = stock.info
            pe_ratio = info.get('forwardEps') / info.get('currentPrice') if info.get('currentPrice') else None
            return pe_ratio
        except Exception as e:
            print(f"Error fetching P/E ratio for {symbol}: {e}")
            return None

    df['pe-ratio']=fetch_pe_ratio(symbol)

    return df


def print_colored(text, feeling):
        """
        Prints text with a specific color and bold effect based on the feeling.
        """
        color_code = {
            'Positive': '32',  # Green
            'Negative': '31',  # Red
            'Neutral': '33'    # Yellow
        }.get(feeling, '37')  # Default to white if feeling is not recognized
        return f"\033[1;{color_code}m{text}\033[0m"

def remove_ansi_codes(text):
    ansi_escape = re.compile(r'\x1b[^m]*m')
    return ansi_escape.sub('', text)
    
    
def print_colored_html(text, feeling):
    """
    Returns HTML-formatted text with a specific color based on the feeling.
    """
    color_code = {
        'Positive': '#32CD32',  # LimeGreen
        'Negative': '#FF6347',  # Tomato
        'Neutral': '#FFD700'    # Gold
    }.get(feeling, '#FFFFFF')  # Default to white if feeling is not recognized
    return f"<font color='{color_code}'>{text}</font>"


def explain_indicators(df, source=""):

    explanations = {}

    def add_explanation(indicator, value, explanation, feeling):
        explanations[indicator] = {
            'value': value,
            'description': explanation,
            'feeling': feeling
        }

    """
    Explain the indicators and provide a rationale for whether the signal is Positive, Negative, or Neutral.
    """
    latest_data = df.tail().iloc[-1]
    print(f"\n{source} Indicator Explanation:")

    # Moving Averages
    print(f"MA_20: {latest_data['MA_20']:.2f} (20-day Moving Average)")
    add_explanation('MA_20', latest_data['MA_20'],
        "The current price is above the 20-day moving average- Positive signal.",
        "Positive" if latest_data['Close'] > latest_data['MA_20'] else "Negative")

    if latest_data['Close'] > latest_data['MA_20']:
        print("The current price is above the 20-day moving average- Positive signal.")
    else:
        print("The current price is below the 20-day moving average- Negative signal.")

    # RSI
    if latest_data['RSI'] < 30:
        add_explanation('RSI', latest_data['RSI'], "RSI is below 30, stock might be oversold- Positive signal.", "Positive")
    elif latest_data['RSI'] > 70:
        add_explanation('RSI', latest_data['RSI'], "RSI is above 70, stock might be overbought- Negative signal.", "Negative")
    else:
        add_explanation('RSI', latest_data['RSI'], "RSI is between 30 and 70- Neutral stance.", "Neutral")

    print(f"RSI: {latest_data['RSI']:.2f} (Relative Strength Index)")
    if latest_data['RSI'] < 30:
        print(print_colored("RSI is below 30, stock might be oversold- Positive signal.", '32'))
    elif latest_data['RSI'] > 70:
        print(print_colored("RSI is above 70, stock might be overbought- Negative signal.", '31'))
    else:
        print(print_colored("RSI is between 30 and 70- Neutral stance.", '33'))
    
    # MACD
    print(f"MACD: {latest_data['MACD']:.2f}")
    add_explanation('MACD', latest_data['MACD'], 
        "MACD is above the signal line,- Positive momentum signal.",
        "Positive" if latest_data['MACD'] > latest_data['MACD_Signal'] else "Negative")

    print(f"MACD Signal Line: {latest_data['MACD_Signal']:.2f}")
    if latest_data['MACD'] > latest_data['MACD_Signal']:
        print(print_colored("MACD is above the signal line, Positive momentum signal.", '32'))
    else:
        print(print_colored("MACD is below the signal line, Negative momentum signal.", '31'))

    # Bollinger Bands
    print(f"Bollinger Upper Band: {latest_data['Bollinger_Upper']:.2f}")
    print(f"Bollinger Lower Band: {latest_data['Bollinger_Lower']:.2f}")
    if latest_data['Close'] < latest_data['Bollinger_Lower']:
        add_explanation('Bollinger_Lower', latest_data['Close'], "Price is below lower Bollinger Band, -Positive buying opportunity.", "Positive")
        print(print_colored("Price is below the lower Bollinger Band, Positive buying opportunity.", '32'))
    elif latest_data['Close'] > latest_data['Bollinger_Upper']:
        add_explanation('Bollinger_Upper', latest_data['Close'], "Price is above upper Bollinger Band- overbought condition- Negative.", "Negative")
        print(print_colored("Price is above the upper Bollinger Band, which might indicate an overbought condition- Negative.", '31'))
    else:
        print(print_colored("Price is within the Bollinger Bands, Neutral outlook.", '33'))
        add_explanation('Bollinger_Upper', latest_data['Close'], "Price is within the Bollinger Bands, Neutral outlook.", "Neutral")
        add_explanation('Bollinger_Lower', latest_data['Close'], "Price is within the Bollinger Bands, Neutral outlook.", "Neutral")

    # ATR (Volatility)
    print(f"ATR: {latest_data['ATR']:.2f} (Average True Range)")
    add_explanation('ATR', latest_data['ATR'], 
        "High ATR suggests increased volatility, which can be a risk factor.",
        "Negative" if latest_data['ATR'] > df['ATR'].mean() else "Positive")

    if latest_data['ATR'] > df['ATR'].mean():
        print("High ATR suggests increased volatility, which can be a risk factor.")
    else:
        print("Low ATR suggests lower volatility, which could imply stability.")

    # Average True Range Components
    print(f"High-Low: {latest_data['High-Low']:.2f}")
    print(f"High-Close: {latest_data['High-Close']:.2f}")
    print(f"Low-Close: {latest_data['Low-Close']:.2f}")
    print(f"True Range: {latest_data['True_Range']:.2f}")
    add_explanation('High-Low', latest_data['High-Low'], "Difference between the high and low prices of the day.", "Neutral")
    add_explanation('High-Close', latest_data['High-Close'], "Difference between the high price and the previous close price.", "Neutral")
    add_explanation('Low-Close', latest_data['Low-Close'], "Difference between the low price and the previous close price.", "Neutral")
    add_explanation('True_Range', latest_data['True_Range'], "Maximum of High-Low, High-Close, and Low-Close - represents volatility.", "Neutral")

    # Volume
    try:
        print(f"Volume: {latest_data['Volume']:.2f}")
        add_explanation('Volume', latest_data['Volume'], 
            "Volume measures the total number of shares traded during a specific period. High volume indicates strong investor interest, while low volume may indicate weak interest.",
            "Positive" if latest_data['Volume'] > df['Volume'].mean() else "Negative")

        if latest_data['Volume'] > df['Volume'].mean():
            print(print_colored("High trading volume indicates strong investor interest - Positive signal.", '32'))
        else:
            print(print_colored("Low trading volume indicates weak investor interest - Negative signal.", '31'))

    except:
        pass    

    # Volatility
    print(f"Volatility: {latest_data['Volatility']:.2f}")
    add_explanation('Volatility', latest_data['Volatility'], 
        "Volatility measures the dispersion of returns. High volatility suggests more risk and price fluctuations, while low volatility suggests stability.",
        "Negative" if latest_data['Volatility'] > df['Volatility'].mean() else "Positive")

    if latest_data['Volatility'] > df['Volatility'].mean():
        print(print_colored("High volatility indicates increased risk - Negative signal.", '31'))
    else:
        print(print_colored("Low volatility suggests stability - Positive signal.", '32'))

    # EMA-12 and EMA-26 Combined
    print(f"EMA-12: {latest_data['EMA_12']:.2f}")
    print(f"EMA-26: {latest_data['EMA_26']:.2f}")
    if latest_data['EMA_12'] > latest_data['EMA_26']:
        add_explanation('EMA_12_26', None, 
            "EMA-12 is above EMA-26 indicating a bullish trend, suggesting potential upward momentum.", 
            "Positive")
        print(print_colored("EMA-12 is above EMA-26, indicating a bullish trend - Positive signal.", '32'))
    else:
        add_explanation('EMA_12_26', None, 
            "EMA-12 is below EMA-26 indicating a bearish trend, suggesting potential downward momentum.", 
            "Negative")
        print(print_colored("EMA-12 is below EMA-26, indicating a bearish trend - Negative signal.", '31'))

    # P/E Ratio
    if latest_data['pe-ratio']:
        add_explanation('pe-ratio', latest_data['pe-ratio'], 
            "A low P/E ratio might indicate that the stock is undervalued- Positive signal.",
            "Positive" if latest_data['pe-ratio'] < 20 
            else "Negative" if latest_data['pe-ratio'] > 30 
            else "Neutral")
        print(f"P/E Ratio: {latest_data['pe-ratio']:.2f}")
        if latest_data['pe-ratio'] < 20:
            print(print_colored("P/E Ratio is low, stock might be undervalued - Positive signal.", '32'))
        elif latest_data['pe-ratio'] > 30:
            print(print_colored("P/E Ratio is high, stock might be overvalued - Negative signal.", '31'))
        else:
            print(print_colored("P/E Ratio is in the neutral range.", '33'))
            
    '''
    # Dividend Yield
    if latest_data['dividend-yield']:
        add_explanation('dividend-yield', latest_data['dividend-yield'],
            "A higher dividend yield might indicate that the stock is providing good returns to investors - Positive signal.",
            "Positive" if latest_data['dividend-yield'] > 0.05 
            else "Neutral")
        print(f"Dividend Yield: {latest_data['dividend-yield']:.2f}")
        if latest_data['dividend-yield'] > 0.05:
            print(print_colored("Dividend Yield is high, indicating good returns to investors - Positive signal.", '32'))
        else:
            print(print_colored("Dividend Yield is in the neutral range.", '33'))'''

    return explanations





explanations = explain_indicators(calculate_indicators(df))


