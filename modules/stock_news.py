import yfinance as yf
from textblob import TextBlob

def fetch_news(symbol):
    stock = yf.Ticker(symbol)
    news_list = stock.news
    #print(news_list)  # Debugging line
    if not news_list:
        return []

    news_data = []
    for news_item in news_list:
        news_data.append({
            'title': news_item['title'],
            'publisher': news_item['publisher'],
            'link': news_item['link'],
            'thumbnail': news_item['thumbnail']['resolutions'][0]['url'] if 'thumbnail' in news_item else '',
            'providerPublishTime': news_item['providerPublishTime']
        })
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
    for news_item in news_data:
        #print(news_item)
        sentiment = analyze_sentiment(news_item['title'])
        #print(sentiment)
        sentiment_results[sentiment] += 1
    max_sentiment = max(sentiment_results, key=sentiment_results.get)
    return max_sentiment

