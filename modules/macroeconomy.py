import yfinance as yf
import pandas as pd
import numpy as np
from fredapi import Fred

def analyze_macroeconomic_data():
    # Fetching GDP data (GDP is the identifier for the Gross Domestic Product in FRED)
    # MacroEconomics Indicators
    fred = Fred(api_key='38a85b8262a0044479cc6200b3c2c99f')
    macro_data = {}
    descriptions = {}

    # Fetching GDP data (GDP is the identifier for the Gross Domestic Product in FRED)
    try:
        gdp_data = fred.get_series('GDP')
        macro_data['gdp_data'] = gdp_data.iloc[-1]
        descriptions['gdp_data'] = 'Positive'
    except Exception as e:
        print(f"Error fetching GDP data: {e}")
        gdp_data = None

    # Inflation Rate (CPI/PPI)
    try:
        cpi_data = fred.get_series('CPIAUCNS')
        macro_data['cpi_data'] = cpi_data.iloc[-1]
        descriptions['cpi_data'] = 'Negative' if macro_data['cpi_data'] > 2 else 'Neutral'
    except Exception as e:
        cpi_data = None

    try:
        ppi_data = fred.get_series('PPIACO')
        macro_data['ppi_data'] = ppi_data.iloc[-1]
        descriptions['ppi_data'] = 'Negative' if macro_data['ppi_data'] > 2 else 'Neutral'
    except Exception as e:
        ppi_data = None

    # Unemployment Rate
    try:
        unemployment_data = fred.get_series('UNRATE')
        macro_data['unemployment_data'] = unemployment_data.iloc[-1]
        descriptions['unemployment_data'] = 'Positive' if macro_data['unemployment_data'] < 5 else 'Negative'
    except Exception as e:
        unemployment_data = None

    # Interest Rates
    try:
        fed_funds_rate = fred.get_series('FEDFUNDS')
        macro_data['fed_funds_rate'] = fed_funds_rate.iloc[-1]
        descriptions['fed_funds_rate'] = 'Positive' if macro_data['fed_funds_rate'] < 2 else 'Negative'
    except Exception as e:
        fed_funds_rate = None

    # Consumer Confidence Index
    try:
        consumer_confidence_data = fred.get_series('CONCCONF')
        macro_data['consumer_confidence_data'] = consumer_confidence_data.iloc[-1]
        descriptions['consumer_confidence_data'] = 'Positive' if macro_data['consumer_confidence_data'] > 100 else 'Neutral'
    except Exception as e:
        consumer_confidence_data = None

    # PMI (Purchasing Managers' Index)
    try:
        pmi_data = fred.get_series('ISM/MAN_PMI')
        macro_data['pmi_data'] = pmi_data.iloc[-1]
        descriptions['pmi_data'] = 'Positive' if macro_data['pmi_data'] > 50 else 'Negative'
    except Exception as e:
        pmi_data = None

    if not macro_data:
        return "Neutral"

    positive_indicators = 0
    negative_indicators = 0

    # Evaluate indicators
    if macro_data.get('gdp_data'):
        positive_indicators += 1

    if macro_data.get('cpi_data') and macro_data['cpi_data'] > 2:
        negative_indicators += 1
    if macro_data.get('ppi_data') and macro_data['ppi_data'] > 2:
        negative_indicators += 1

    if macro_data.get('unemployment_data') and macro_data['unemployment_data'] < 5:
        positive_indicators += 1
    else:
        negative_indicators += 1

    if macro_data.get('fed_funds_rate') and macro_data['fed_funds_rate'] < 2:
        positive_indicators += 1
    else:
        negative_indicators += 1

    if macro_data.get('consumer_confidence_data') and macro_data['consumer_confidence_data'] > 100:
        positive_indicators += 1

    if macro_data.get('pmi_data') and macro_data['pmi_data'] > 50:
        positive_indicators += 1
    else:
        negative_indicators += 1

    if positive_indicators > negative_indicators:
        overall_sentiment = "Positive"
    elif negative_indicators > positive_indicators:
        overall_sentiment = "Negative"
    else:
        overall_sentiment = "Neutral"

    return macro_data, descriptions, overall_sentiment
