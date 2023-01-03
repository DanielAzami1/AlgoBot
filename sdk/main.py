from entities.asset import Stock
from data.models import fetch_from_company_table
import datetime


ticker = "aapl"
company = fetch_from_company_table(ticker)[0]
stock = Stock(ticker, company)

print(stock)

daily_returns = stock.get_returns(interval='daily')

print(type(stock.metrics['daily_returns']))

std = stock.get_std()
print(std)

d = datetime.date(2000, 1, 4)

print(stock.get_price(d=d))
