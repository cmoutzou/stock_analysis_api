import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol, period='1y', interval='1d'):
    """
    Fetches and preprocesses stock data from Yahoo Finance.
    """
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
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Adj Close': 'adj_close',
            'Volume': 'volume'
        }, inplace=True)
        print(df.columns)
        return df

    except Exception as e:
        print(f"Error fetching data from Yahoo Finance for {symbol}: {e}")
        return None
