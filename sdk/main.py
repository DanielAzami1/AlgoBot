from entities.asset import Stock
from data.models import fetch_from_company_table
import datetime
import pprint as pp
import pandas as pd
import pandas_ta as ta
from sdk.factors.technical_indicators import Metrics, TechnicalIndicators

ticker = "aapl"
company = fetch_from_company_table(ticker)[0]
aapl = Stock(ticker, company)
close_prices = aapl.market_data['Close']





# aapl.metrics['pct_returns'] = Metrics.percent_returns(prices_or_values=aapl.market_data['Close'])
# aapl.metrics['rolling_std'] = Metrics.rolling_std(pct_returns=aapl.metrics['pct_returns'])
# aapl.metrics['sma'] = Metrics.sma(prices_or_values=aapl.market_data['Close'])
# aapl.metrics['ema'] = Metrics.ema(prices_or_values=aapl.market_data['Close'])
#
#
# metrs = pd.DataFrame.from_dict(aapl.metrics)
# print(metrs)
#
# print(Metrics.max_drawdown(aapl.market_data['Close']))
