import pprint
from datetime import datetime

from src.classes.asset import Stock
from src.classes.holding import Holding
from src.classes.portfolio import Portfolio
from src.classes.company import Company

from src.data.download_remote_data import download_ticker_data

"""
Overall Portfolio structure::
    
    Portfolio[List[Holding[Stock]]]
"""

symbols = ["AAPL", "META", "GM", "TSLA"]
stock_data = {}

for symbol in symbols:
    data = download_ticker_data(
        symbol=symbol,
        period="5d",
        include_metadata=True,
        use_cache=True
    )
    stock_data[symbol] = data

aapl = stock_data["AAPL"]
aapl_metadata = aapl["metadata"]
aapl_market_data = aapl["market_data"]

# pprint.pprint(aapl_metadata)
#
# pprint.pprint(aapl_market_data)

aapl_company = Company(
    symbol=aapl_metadata["symbol"],
    company_name=aapl_metadata["longName"],
    sector=aapl_metadata["sector"],
    industry=aapl_metadata["industry"],
    business_summary=aapl_metadata["longBusinessSummary"],
    country=aapl_metadata["country"],
    employee_count=aapl_metadata["fullTimeEmployees"],
    market_cap=aapl_metadata["marketCap"],
    float_shares=aapl_metadata["floatShares"],
    is_esg_populated=aapl_metadata["isEsgPopulated"]
)

aapl_stock = Stock(
    symbol=aapl_metadata["symbol"],
    company=aapl_company
)

aapl_holding = Holding(
    stock=aapl_stock,
    qty_owned=10,
    date_purchased=datetime.now()
)

