from loguru import logger
import random
from datetime import datetime
from src.classes.portfolio import Portfolio
from src.classes.asset import Stock
from src.classes.transaction import MarketBuy
from src.misc.enums import StockPool
from src.data.download_remote_data import download_index_constituents
from src.data.models import fetch_from_company_table


class PortfolioBuilder:
    def __init__(self, portfolio: Portfolio, stock_pool: StockPool):
        self.portfolio = portfolio
        self.name = f"{portfolio.name}_builder"
        self._stock_pool = stock_pool.value
        _stock_pool = download_index_constituents(index_url=self._stock_pool)
        _stock_pool = fetch_from_company_table(*_stock_pool)
        self.stocks = [Stock(symbol=company.symbol, company=company) for company in _stock_pool]
        self._filtered_pool = None

    def fetch_new_stock(self):
        if self._filtered_pool:
            return random.choice(self._filtered_pool)
        return random.choice(self.stocks)

    def filter_by_sector(self, sector: str):
        """
        :param sector: key (attr) to filter companies
        :return: None
        """
        self._filtered_pool = filter(lambda stock: stock.company.sector == sector, self.stocks)

    def filter_by_industry(self, industry: str):
        """
        :param industry: key (attr) to filter companies.
        :return: None
        """
        self._filtered_pool = filter(lambda stock: stock.company.industry == industry, self.stocks)

    def drop_filter(self):
        self._filtered_pool = None


if __name__ == "__main__":
    p = Portfolio(name="MyPortfolio")
    pb = PortfolioBuilder(portfolio=p, stock_pool=StockPool.SNP500)
    print(p)
    continue_building = True
    while continue_building:
        new_stock = pb.fetch_new_stock()
        print(new_stock)
        purchase = input("Add to portfolio? (y/n)\n").lower().strip()
        if purchase == "y":
            qty = int(input("Enter number of shares:\n"))
            try:
                buy_order = MarketBuy(
                    date=datetime.now(),
                    symbol=new_stock.symbol,
                    price=new_stock.get_live_price(),
                    qty=qty
                )
                p.purchase_asset(buy_order=buy_order, stock=new_stock)
            except Exception as e:
                logger.warning(e)
                continue
        if purchase == "q":
            continue_building = False

    print(p)
    for hldn in p.holdings:
        print(hldn)

    from IPython import embed
    embed()


