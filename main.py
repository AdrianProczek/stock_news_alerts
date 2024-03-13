import requests
import datetime as dt
from twilio.rest import Client
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_MARKET_API_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_MARKET_API_KEY = str(os.environ.get("STOCK_MARKET_API_KEY"))

NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = str(os.environ.get("NEWS_API_KEY"))

ACCOUNT_SID = str(os.environ.get("TWILIO_ACCOUNT_SID"))
AUTH_TOKEN = str(os.environ.get("TWILIO_AUTH_TOKEN"))

FROM_NUMBER = str(os.environ.get("FORM_NUMBER"))
TO_NUMBER = str(os.environ.get("TO_NUMBER"))


def send_sms(stock_mess, news_to_send):
    for news in news_to_send:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=f"{stock_mess}\n\n"
                 f"Headline: {news['title']}\n\n"
                 f"Brief: {news['description']}",
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )


parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_MARKET_API_KEY
}

response = requests.get(url=STOCK_MARKET_API_ENDPOINT, params=parameters)
response.raise_for_status()
stock_price = response.json()["Time Series (Daily)"]

yesterday = dt.datetime.now().date() - dt.timedelta(days=1)
day_before_yesterday = dt.datetime.now().date() - dt.timedelta(days=2)

stock_price_yesterday = float(stock_price[str(yesterday)]["4. close"])
stock_price_day_before_yesterday = float(stock_price[str(day_before_yesterday)]["4. close"])

parameters = {
    "q": COMPANY_NAME,
    "from": yesterday,
    "sortBy": "popularity",
    "apiKey": NEWS_API_KEY
}

response = requests.get(url=NEWS_API_ENDPOINT, params=parameters)
response.raise_for_status()
all_news = response.json()["articles"]
news_to_send = []

for i in range(3):
    news_to_send.append(all_news[i])

stock_diff = ((float(stock_price_yesterday) - float(stock_price_day_before_yesterday)) / stock_price_yesterday) * 100
if stock_diff > 0:
    stock_mess = f"{STOCK} up by {abs(stock_diff)}%"
else:
    stock_mess = f"{STOCK} down by {abs(stock_diff)}%"

if stock_diff > 5:
    send_sms(stock_mess, news_to_send)
