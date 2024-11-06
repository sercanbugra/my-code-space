import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import HTTPError
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import time
import random
from datetime import datetime, timedelta

# Download the VADER lexicon
nltk.download('vader_lexicon')

# Function to parse date strings
def parse_date(date_str):
    if date_str == "Today":
        return datetime.now().date()
    elif date_str == "Yesterday":
        return datetime.now().date() - timedelta(1)
    else:
        return pd.to_datetime(date_str).date()

# Function to fetch S&P 100 stock tickers
def get_sp100_tickers():
    sp100_url = 'https://en.wikipedia.org/wiki/S%26P_100'
    html = urlopen(sp100_url)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find_all('table')[2]
    tickers = []
    for row in table.find_all('tr')[1:]:
        ticker = row.find_all('td')[0].text.strip()
        tickers.append(ticker)
    return tickers

# Function to fetch RSI values using yfinance
def get_rsi(ticker, period=14):
    data = yf.download(ticker, period='1mo', interval='1d')
    delta = data['Adj Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]  # Return the most recent RSI value

# Parameters
n = 3  # Number of recent news to consider
tickers = get_sp100_tickers()

# List of user agents to rotate
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0'
]

# Function to fetch news tables
def fetch_news_tables(tickers):
    finwiz_url = 'https://finviz.com/quote.ashx?t='
    news_tables = {}
    for ticker in tickers:
        encoded_ticker = quote(ticker)
        url = finwiz_url + encoded_ticker
        user_agent = random.choice(user_agents)
        req = Request(url=url, headers={'user-agent': user_agent})
        try:
            resp = urlopen(req)
            html = BeautifulSoup(resp, features="lxml")
            news_table = html.find(id='news-table')
            news_tables[ticker] = news_table
        except HTTPError as e:
            print(f"HTTPError for {ticker}: {e}")
        time.sleep(random.uniform(1, 3))  # Add delay
    return news_tables

# Function to parse news headlines and dates
def parse_news(news_tables):
    parsed_news = []
    for file_name, news_table in news_tables.items():
        if news_table is None:
            continue
        for x in news_table.findAll('tr')[:n]:
            text = x.a.get_text()
            date_scrape = x.td.text.split()

            if len(date_scrape) == 1:
                time = date_scrape[0]
                date = "Today"  # Assuming single time means today's news
            else:
                date = date_scrape[0]
                time = date_scrape[1]

            ticker = file_name
            parsed_news.append([ticker, date, time, text])
    return parsed_news

# Sentiment Analysis
def calculate_sentiment(parsed_news):
    analyzer = SentimentIntensityAnalyzer()
    columns = ['Ticker', 'Date', 'Time', 'Headline']
    news = pd.DataFrame(parsed_news, columns=columns)
    news['Date'] = news['Date'].apply(parse_date)
    scores = news['Headline'].apply(analyzer.polarity_scores).tolist()
    df_scores = pd.DataFrame(scores)
    news = news.join(df_scores)
    return news

# Main Function
def main():
    # Fetch news tables
    news_tables = fetch_news_tables(tickers)

    # Parse news headlines and dates
    parsed_news = parse_news(news_tables)

    # Calculate sentiment scores
    news_sentiment = calculate_sentiment(parsed_news)

    # Calculate RSI values
    news_sentiment['RSI'] = news_sentiment['Ticker'].apply(lambda x: get_rsi(x))

    # Output to Excel file
    news_sentiment.to_excel("sentiment_scores_with_rsi.xlsx", index=False)

    # Pick top and bottom 10 stocks based on average sentiment scores
    avg_sentiment = news_sentiment.groupby('Ticker')['compound'].mean().sort_values()
    top_10 = avg_sentiment.tail(10)
    bottom_10 = avg_sentiment.head(10)

    # Plot sentiment scores
    plt.figure(figsize=(12, 6))
    plt.bar(top_10.index, top_10.values, color='green', label='Top 10 Stocks')
    plt.bar(bottom_10.index, bottom_10.values, color='red', label='Bottom 10 Stocks')
    plt.title('Average Sentiment Scores for S&P 100 Stocks')
    plt.xlabel('Ticker')
    plt.ylabel('Average Sentiment Score')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
