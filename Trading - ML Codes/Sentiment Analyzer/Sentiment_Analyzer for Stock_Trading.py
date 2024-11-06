import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import time
import random
from datetime import datetime, timedelta

# Download the VADER lexicon
nltk.download('vader_lexicon')

# Parameters 
n = 5 
tickers = ['HOLO','DELL','SOUN','BABA','SMCI','MSFT','CVX','AMZN','ETN','AVGO','AMD']

# List of user agents to rotate
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0'
]

# Function to parse date strings
def parse_date(date_str):
    if date_str == "Today":
        return datetime.now().date()
    elif date_str == "Yesterday":
        return datetime.now().date() - timedelta(1)
    else:
        return pd.to_datetime(date_str).date()

# Get Data
finwiz_url = 'https://finviz.com/quote.ashx?t='
news_tables = {}

for ticker in tickers:
    url = finwiz_url + ticker
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

# Print Recent News Headlines
try:
    for ticker in tickers:
        df = news_tables[ticker]
        if df is None:
            print(f"No news for {ticker}")
            continue
        df_tr = df.findAll('tr')

        print('\n')
        print(f'Headers for {ticker}: ')

        for i, table_row in enumerate(df_tr):
            a_text = table_row.a.text
            td_text = table_row.td.text.strip()
            print(a_text, '(', td_text, ')')
            if i == n-1:
                break
except KeyError:
    pass

# Iterate through the news
parsed_news = []
for file_name, news_table in news_tables.items():
    if news_table is None:
        continue
    for x in news_table.findAll('tr'):
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

# Sentiment Analysis
analyzer = SentimentIntensityAnalyzer()

columns = ['Ticker', 'Date', 'Time', 'Headline']
news = pd.DataFrame(parsed_news, columns=columns)

# Convert 'Date' column to actual dates
news['Date'] = news['Date'].apply(parse_date)

scores = news['Headline'].apply(analyzer.polarity_scores).tolist()
df_scores = pd.DataFrame(scores)
news = news.join(df_scores, rsuffix='_right')

# View Data 
unique_ticker = news['Ticker'].unique().tolist()
news_dict = {name: news.loc[news['Ticker'] == name] for name in unique_ticker}

values = []
for ticker in tickers:
    dataframe = news_dict.get(ticker)
    if dataframe is None or dataframe.empty:
        print(f"No news data for {ticker}")
        continue
    dataframe = dataframe.set_index('Ticker')
    dataframe = dataframe.drop(columns=['Headline'])
    print('\n')
    print(dataframe.head())

    mean = round(dataframe['compound'].mean(), 2)
    values.append(mean)

df = pd.DataFrame(list(zip(tickers, values)), columns=['Ticker', 'Avg Sentiment'])
df = df.set_index('Ticker')
df = df.sort_values('Avg Sentiment', ascending=False)
print('\n')
print(df)

# Plot Mean Sentiment Scores
df.plot(kind='bar')
plt.title('Avg Sentiment Scores for Tickers')
plt.xlabel('Ticker')
plt.ylabel('Avg Sentiment Scores')
plt.show()
