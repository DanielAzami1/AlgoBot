from loguru import logger
import random
from src.classes.asset import Stock
from src.classes.portfolio import Portfolio
from src.classes.company import Company
from src.classes.transaction import Transaction
from src.data.download_remote_data import download_index_constituents, load_ticker_market_data_from_csv,\
    download_ticker_data
from src.data.models import fetch_from_company_table, insert_into_transactions_table

"""
Overall Portfolio structure::
    
    Portfolio[List[Holding[Stock]]]
"""


# def view_stocks_for_portfolio(p: Portfolio):
#     stock_pool = download_index_constituents()
#     continue_viewing_stocks: bool = True
#     while continue_viewing_stocks:
#         symbol = random.choice(stock_pool)
#         try:
#             company: Company = fetch_from_company_table(symbol)[0]
#         except IndexError as e:
#             logger.warning(e)
#             continue
#
#         try:
#             market_data = load_ticker_market_data_from_csv(symbol)
#             stock: Stock = Stock(symbol=symbol, company=company, market_data=market_data)
#         except Exception as err:
#             logger.warning(err)
#             continue
#
#         print(stock)
#         print(p.get_free_cash())
#         purchase = input("Add to portfolio? (Y/N) - QUIT to stop\n").upper()
#         if purchase == 'Y':
#             qty = int(input("Number of shares:\n"))
#             try:
#                 p.purchase_asset(stock, qty)
#             except ValueError as err:
#                 logger.warning(err)
#                 continue
#         elif purchase == 'QUIT':
#             continue_viewing_stocks = False
#
#     return portfolio
#
#
# portfolio: Portfolio = Portfolio(name="MyFirstPortfolio")
#
# portfolio = view_stocks_for_portfolio(portfolio)
# print("\n\n")
# print(portfolio)
# portfolio.print_holdings()
# portfolio.print_transaction_history()
# print("\n\n")
# portfolio.sell_asset()
# def save_transactions(transactions: List[Transaction]):
#     insert_into_transactions_table(*transactions)

symbol = "aapl"
market_data = download_ticker_data(symbol=symbol, interval="1m")
print(market_data)




