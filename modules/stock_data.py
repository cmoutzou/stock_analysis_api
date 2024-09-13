import yfinance as yf
import pandas as pd
import numpy as np

def fetch_stock_data(symbol,period,interval):
    try:
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        if df.empty:
            print(f"No data returned for {symbol}")
            return None

        df['symbol'] = symbol
        df.reset_index(inplace=True)
        df.rename(columns={
            'Datetime': 'timestamp',
            'Date': 'timestamp',
            'timestamp': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Adj Close': 'adj_close',
            'Volume': 'volume'
        }, inplace=True)
        print(df.columns)
        return df

    except Exception as e:
        print(f"Error fetching data from Yahoo Finance for {symbol}: {e}")
        return None


fetch_stock_data('AAPL','1y','1d')