import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import HTTPError
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import time
import random
from datetime import datetime
import concurrent.futures

# Download the VADER lexicon
nltk.download('vader_lexicon')

# Set up user agents to rotate for each request
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    # Add more user agents if needed
]

# Fetch S&P 100 stock tickers from Wikipedia
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

# Fetch news headlines and RSI values for a single ticker
def fetch_news_and_rsi(ticker):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    encoded_ticker = quote(ticker)
    url = finviz_url + encoded_ticker
    user_agent = random.choice(user_agents)
    req = Request(url=url, headers={'user-agent': user_agent})
    try:
        resp = urlopen(req)
        html = BeautifulSoup(resp, features="lxml")
        news_table = html.find(id='news-table')
        
        # Updated from `find(text='RSI (14)')` to `find(string='RSI (14)')`
        rsi_text = html.find(string='RSI (14)').find_next(class_='snapshot-td2').text
        rsi = float(rsi_text)
        return ticker, news_table, rsi
    except HTTPError as e:
        print(f"HTTPError for {ticker}: {e}")
        return ticker, None, None
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return ticker, None, None
    finally:
        time.sleep(random.uniform(1, 3))  # Delay to avoid request blocking

# Calculate sentiment score for each news headline
def calculate_sentiment(parsed_news):
    analyzer = SentimentIntensityAnalyzer()
    columns = ['Ticker', 'Date', 'Time', 'Headline', 'RSI']
    news = pd.DataFrame(parsed_news, columns=columns)
    scores = news['Headline'].apply(analyzer.polarity_scores).tolist()
    df_scores = pd.DataFrame(scores)
    news = news.join(df_scores)
    return news

# Main function to run analysis on S&P 100 stocks
def main():
    tickers = get_sp100_tickers()
    parsed_news = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(fetch_news_and_rsi, tickers)
        
        for ticker, news_table, rsi in results:
            if news_table and rsi is not None:
                for row in news_table.findAll('tr'):
                    headline = row.a.text
                    date_scrape = row.td.text.split()
                    if len(date_scrape) == 1:
                        time_scrape = date_scrape[0]
                    else:
                        date_scrape, time_scrape = date_scrape[0], date_scrape[1]
                    parsed_news.append([ticker, date_scrape, time_scrape, headline, rsi])

    # Calculate sentiment scores and analyze
    news_sentiment = calculate_sentiment(parsed_news)
    
    # Group by ticker to calculate average sentiment and RSI
    avg_sentiment = news_sentiment.groupby('Ticker')['compound'].mean()
    avg_rsi = news_sentiment.groupby('Ticker')['RSI'].first()

    # Select top and bottom 10 based on sentiment score
    top_10 = avg_sentiment.nlargest(10)
    bottom_10 = avg_sentiment.nsmallest(10)
    top_10_rsi = avg_rsi[top_10.index]
    bottom_10_rsi = avg_rsi[bottom_10.index]

    # Plotting the sentiment scores and RSI values
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Plot sentiment scores
    color = 'tab:blue'
    ax1.set_xlabel('Ticker')
    ax1.set_ylabel('Average Sentiment Score', color=color)
    ax1.bar(top_10.index, top_10.values, color='green', label='Top 10 Stocks')
    ax1.bar(bottom_10.index, bottom_10.values, color='red', label='Bottom 10 Stocks')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend(loc='upper left')

    # Create a secondary y-axis for RSI values
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('RSI', color=color)
    ax2.plot(top_10.index, top_10_rsi, color='blue', marker='o', linestyle='dashed', label='Top 10 Stocks RSI')
    ax2.plot(bottom_10.index, bottom_10_rsi, color='blue', marker='*', linestyle='dashed', label='Bottom 10 Stocks RSI')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.axhline(70, color='grey', linestyle='--', linewidth=0.7)
    ax2.axhline(30, color='grey', linestyle='--', linewidth=0.7)

    fig.tight_layout()
    plt.title('Average Sentiment Scores and RSI for Top and Bottom 10 S&P 100 Stocks')
    plt.xticks(rotation=45, ha='right')
    fig.legend(loc='lower left', bbox_to_anchor=(1,0.85))
    plt.show()

if __name__ == "__main__":
    main()
