import yfinance as yf
import pandas as pd
import numpy as np
from fredapi import Fred

def analyze_macroeconomic_data():
    fred = Fred(api_key='38a85b8262a0044479cc6200b3c2c99f')
    macro_data = {}

    # Fetching GDP data (GDP is the identifier for the Gross Domestic Product in FRED)
    try:
        gdp_data = fred.get_series('GDP')
        macro_data['gdp_data'] = gdp_data.iloc[-1]
    except Exception as e:
        print(f"Error fetching GDP data: {e}")
        gdp_data = None

    if not macro_data:
        return "Neutral"

    positive_indicators = 0
    negative_indicators = 0

    # GDP is generally considered a positive indicator
    if macro_data.get('gdp_data'):
        positive_indicators += 1

    # CPI and PPI: Inflationary indicators; high values can be negative
    if macro_data.get('cpi_data') and macro_data['cpi_data'] > 2:
        negative_indicators += 1
    if macro_data.get('ppi_data') and macro_data['ppi_data'] > 2:
        negative_indicators += 1

    # Unemployment Rate: Lower is generally better
    if macro_data.get('unemployment_data') and macro_data['unemployment_data'] < 5:
        positive_indicators += 1
    else:
        negative_indicators += 1

    # Federal Funds Rate: Higher rates are often seen as negative
    if macro_data.get('fed_funds_rate') and macro_data['fed_funds_rate'] < 2:
        positive_indicators += 1
    else:
        negative_indicators += 1

    # Consumer Confidence Index: Higher is better
    if macro_data.get('consumer_confidence_data') and macro_data['consumer_confidence_data'] > 100:
        positive_indicators += 1

    # PMI: Higher indicates economic growth
    if macro_data.get('pmi_data') and macro_data['pmi_data'] > 50:
        positive_indicators += 1
    else:
        negative_indicators += 1

    if positive_indicators > negative_indicators:
        return macro_data,"Positive"
    elif negative_indicators > positive_indicators:
        return macro_data,"Negative"
    else:
        return macro_data,"Neutral"