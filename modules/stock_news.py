
import yfinance as yf
from textblob import TextBlob




def fetch_news(symbol):
    stock = yf.Ticker(symbol)
    news_list = stock.news
    if not news_list:
        return []

    news_data = []
    for news_item in news_list:
        headline = news_item['title']
        url = news_item['link']
        news_data.append((headline, url))
    return news_data

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'

def get_news_sentiment(symbol):
    news_data = fetch_news(symbol)
    if not news_data:
        return "No news available for this symbol."

    sentiment_results = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for headline, url in news_data:
        sentiment = analyze_sentiment(headline)
        sentiment_results[sentiment] += 1

    # Determine the most dominant sentiment
    max_sentiment = max(sentiment_results, key=sentiment_results.get)
    return max_sentiment
