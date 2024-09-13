import yfinance as yf
import pandas as pd
import numpy as np

def process_symbol(symbol, period, interval):
    print(f"\n***{symbol}***")
    print("\n***news***")
    for i in fetch_news(symbol):
        print(i)

    # Fetch and analyze news sentiment
    news_sentiment = get_news_sentiment(symbol)

    # Suppress output from fetching financial data
    df_alpha_vantage = suppress_output(fetch_data_from_alpha_vantage, symbol)
    df_yf = suppress_output(fetch_data_from_yf, symbol, period, interval)
    alpha_vantage_recommendation = None
    yf_recommendation = None

    pe_ratio = fetch_pe_ratio(symbol)

    if df_alpha_vantage is not None and not df_alpha_vantage.empty:
        df_alpha_vantage = calculate_indicators(df_alpha_vantage)
        alpha_vantage_recommendation = make_recommendation(df_alpha_vantage, pe_ratio)
        print("\nAlpha Vantage Data Indicators:")
        print(df_alpha_vantage.tail())
        explain_indicators(df_alpha_vantage.tail().iloc[-1], pe_ratio, source="Alpha Vantage")

    if df_yf is not None and not df_yf.empty:
        df_yf = calculate_indicators(df_yf)
        yf_recommendation = make_recommendation(df_yf, pe_ratio)
        print("\nYahoo Finance Data Indicators:")
        explain_indicators(df_yf.tail().iloc[-1], pe_ratio, source="Yahoo Finance")

    # Fetch and analyze macroeconomic data
    macro_sentiment = analyze_macroeconomic_data(macro_data)

    # Determine overall financial analysis sentiment
    financial_analysis_sentiment = "Neutral"
    if alpha_vantage_recommendation == "Buy" or yf_recommendation == "Buy":
        financial_analysis_sentiment = "Positive"
    elif alpha_vantage_recommendation == "Sell" or yf_recommendation == "Sell":
        financial_analysis_sentiment = "Negative"

    # Print consolidated results
    print("\nRecommendations:")
    print(f"Financial Analysis: {print_colored(financial_analysis_sentiment, '32' if financial_analysis_sentiment == 'Positive' else '31' if financial_analysis_sentiment == 'Negative' else '33')}")
    print(f"Macroeconomic Analysis: {print_colored(macro_sentiment, '32' if macro_sentiment == 'Positive' else '31' if macro_sentiment == 'Negative' else '33')}")
    print(f"News Sensitivity Analysis: {print_colored(news_sentiment, '32' if news_sentiment == 'Positive' else '31' if news_sentiment == 'Negative' else '33')}")

    # Create and show charts
    create_charts(symbol)
