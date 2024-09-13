import yfinance as yf
import pandas as pd
import numpy as np

def calculate_indicators(df):
    if df.empty:
        return df

    # Moving Average
    df['MA_20'] = df['close'].rolling(window=20).mean()
    df['MA_50'] = df['close'].rolling(window=50).mean()
    df['MA_200'] = df['close'].rolling(window=200).mean()

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Volatility
    df['Volatility'] = df['close'].rolling(window=20).std()

    # MACD
    df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df['Bollinger_Middle'] = df['close'].rolling(window=20).mean()
    df['Bollinger_Upper'] = df['Bollinger_Middle'] + 2 * df['close'].rolling(window=20).std()
    df['Bollinger_Lower'] = df['Bollinger_Middle'] - 2 * df['close'].rolling(window=20).std()

    # Average True Range (ATR)
    df['High-Low'] = df['high'] - df['low']
    df['High-Close'] = np.abs(df['high'] - df['close'].shift())
    df['Low-Close'] = np.abs(df['low'] - df['close'].shift())
    df['True_Range'] = df[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
    df['ATR'] = df['True_Range'].rolling(window=14).mean()

    return df


def explain_indicators(latest_data, pe_ratio, source=""):
    """
    Explain the indicators and provide a rationale for whether the signal is Positive, Negative, or Neutral.
    """
    print(f"\n{source} Indicator Explanation:")

    # Moving Averages
    print(f"MA_20: {latest_data['MA_20']:.2f} (20-day Moving Average)")
    if latest_data['close'] > latest_data['MA_20']:
        print("The current price is above the 20-day moving average, which is generally a Positive signal.")
    else:
        print("The current price is below the 20-day moving average, which can be a Negative signal.")

    # RSI
    print(f"RSI: {latest_data['RSI']:.2f} (Relative Strength Index)")
    if latest_data['RSI'] < 30:
        print(print_colored("RSI is below 30, indicating that the stock might be oversold and could be a Positive signal.", '32'))
    elif latest_data['RSI'] > 70:
        print(print_colored("RSI is above 70, indicating that the stock might be overbought and could be a Negative signal.", '31'))
    else:
        print(print_colored("RSI is between 30 and 70, suggesting a Neutral stance.", '33'))

    # MACD
    print(f"MACD: {latest_data['MACD']:.2f}")
    print(f"MACD Signal Line: {latest_data['MACD_Signal']:.2f}")
    if latest_data['MACD'] > latest_data['MACD_Signal']:
        print(print_colored("MACD is above the signal line, which is a Positive momentum signal.", '32'))
    else:
        print(print_colored("MACD is below the signal line, which indicates a Negative momentum signal.", '31'))

    # Bollinger Bands
    print(f"Bollinger Upper Band: {latest_data['Bollinger_Upper']:.2f}")
    print(f"Bollinger Lower Band: {latest_data['Bollinger_Lower']:.2f}")
    if latest_data['close'] < latest_data['Bollinger_Lower']:
        print(print_colored("Price is below the lower Bollinger Band, which could be a Positive buying opportunity.", '32'))
    elif latest_data['close'] > latest_data['Bollinger_Upper']:
        print(print_colored("Price is above the upper Bollinger Band, which might indicate an overbought condition and could be Negative.", '31'))
    else:
        print(print_colored("Price is within the Bollinger Bands, suggesting a Neutral outlook.", '33'))

    # ATR (Volatility)
    print(f"ATR: {latest_data['ATR']:.2f} (Average True Range)")
    if latest_data['ATR'] > latest_data['ATR'].mean():
        print("High ATR suggests increased volatility, which can be a risk factor.")
    else:
        print("Low ATR suggests lower volatility, which could imply stability.")

    # P/E Ratio
    if pe_ratio:
        print(f"P/E Ratio: {pe_ratio:.2f}")
        if pe_ratio < 20:
            print(print_colored("A low P/E ratio might indicate that the stock is undervalued, which could be a Positive signal.", '32'))
        elif pe_ratio > 30:
            print(print_colored("A high P/E ratio might suggest overvaluation, which could be a Negative signal.", '31'))
        else:
            print(print_colored("P/E ratio is within a Neutral range.", '33'))
    else:
        print("P/E Ratio not available.")
