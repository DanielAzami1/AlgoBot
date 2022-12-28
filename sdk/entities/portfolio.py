import random
from typing import Optional, List
from loguru import logger
from datetime import date, datetime

from sdk.data.request_data import download_index_constituents
from sdk.entities.asset import Stock, Holding
from sdk.entities.transaction import Transaction, MarketBuy, MarketSell
from sdk.misc.enums import StockPool
from sdk.misc.utils import currency
from sdk.data import models


class Portfolio:
    def __init__(
        self,
        name: str,
        free_cash: float = 1_00_000.00,
        holdings: Optional[List[Holding]] = None,
        value_history: Optional[List] = None,
        transaction_history: Optional[List[Transaction]] = None,
    ):
        self.name = name
        self.free_cash = free_cash
        self.holdings = {holding.symbol: holding for holding in holdings} if holdings else {}
        self.value_history = value_history if value_history else []
        self.transaction_history = transaction_history if transaction_history else []

        if not all((holdings, value_history, transaction_history)):
            try:
                self.__load()  # try to look for local data for this portfolio
            except Exception as err:  # //TODO <find a better error to catch lul>
                logger.warning(err)

        self.value = None

    def purchase_asset(self, buy_order: MarketBuy, stock: Stock) -> None:
        """
        :param stock: Stock object to be used for instantiating new Holding obj if not already owned.
        :param buy_order: Market buy order to be executed.
        :return: None
        """
        if buy_order.market_value > self.free_cash:
            raise ValueError(f"Insufficient funds to execute ({buy_order}).")
        self.free_cash -= buy_order.market_value

        if self.__holding_in_portfolio(buy_order.symbol):
            self.holdings[buy_order.symbol].qty_owned += buy_order.qty
            logger.success(
                f"Added {buy_order.qty} shares to holding {buy_order.symbol}."
            )
        else:
            new_holding = Holding(
                symbol=buy_order.symbol, stock=stock, qty_owned=buy_order.qty
            )
            self.holdings[new_holding.stock.symbol] = new_holding
        logger.success(f"Added {buy_order.symbol} to {self.name} portfolio holdings.")
        self.transaction_history.append(buy_order)

    def sell_asset(self, sell_order: MarketSell) -> None:
        """
        :param: sell_order: Market sell order to be executed.
        :return: None
        //TODO change logic so that if we liquidate an entire position, that asset gets totally removed from the table.
        """
        if not self.__holding_in_portfolio(sell_order.symbol):
            raise ValueError(
                f"holding of {sell_order.symbol} not present in portfolio."
            )
        holding = self.holdings[sell_order.symbol]
        if holding.qty_owned < sell_order.qty:
            raise ValueError(f"Insufficient shares owned to execute ({sell_order})")
        self.free_cash += sell_order.market_value

        if holding.qty_owned == sell_order.qty:
            del self.holdings[sell_order.symbol]
            logger.success(
                f"Position in {sell_order.symbol} liquidated ({sell_order.qty} shares)."
            )
        else:
            holding.qty_owned -= sell_order.qty
            logger.success(f"Sold {sell_order.qty} shares of {sell_order.symbol}")
        self.transaction_history.append(sell_order)

    def __holding_in_portfolio(self, symbol: str) -> bool:
        """
        :param: symbol: symbol to check.
        :return: T/F.
        """
        try:
            _ = self.holdings[symbol]
            return True
        except KeyError:
            return False

    def get_value_of_holdings(self, d: datetime.date = None) -> float:
        """
        Get total market value of all holdings in portfolio.
        :param: date: optional date to get value of holdings on given date
        :return: value of holdings
        """
        val = 0.0
        for holding in self.holdings.keys():
            val += self.holdings[holding].get_market_value(d=d)
        return val

    def get_total_value(self) -> float:
        """
        :return: value of holdings + free cash.
        """
        return self.free_cash + self.get_value_of_holdings()

    def get_num_holdings(self) -> int:
        """
        :return: number of unique holdings in this portfolio.
        """
        return len(self.holdings) if self.holdings else 0

    def __load(self) -> None:
        """
        Load holdings, value, and transaction history for this portfolio from db.
        :return: None.
        """
        #  holdings
        found_holdings = models.fetch_from_holdings_table(portfolio=self.name)
        for holding in found_holdings:
            company = models.fetch_from_company_table(holding.symbol)[0]
            stock = Stock(symbol=holding.symbol, company=company)
            holding.stock = stock
            self.holdings[holding.symbol] = holding
        self.free_cash -= self.get_value_of_holdings()
        # transactions
        found_transactions = models.fetch_from_transactions_table(portfolio=self.name)
        for t in found_transactions:
            self.transaction_history.append(t)
        # value history
        found_values = models.fetch_from_portfolio_table(portfolio=self.name)
        for v in found_values:
            self.value_history.append(v)
        logger.success(f"Retrieved local data for portfolio {self.name}.")

    def __save(self) -> None:
        models.insert_into_portfolio_table(
            portfolio=self.name, value=self.get_total_value(), timestamp=datetime.now()
        )
        models.insert_into_transactions_table(
            *self.transaction_history, portfolio=self.name
        )
        models.insert_into_holdings_table(
            *self.holdings.values(), portfolio=self.name
        )
        logger.success(f"Saved data for portfolio {self.name}")

    def __str__(self):
        return (
            f"Portfolio [{self.name}]: {self.get_num_holdings()} unique holdings"
            f" ({currency(self.get_value_of_holdings())})"
            f" | {currency(self.free_cash)} cash."
        )

    def __repr__(self):
        return "Portfolio<name, free_cash, holdings, value_history>"


class PortfolioBuilder:
    def __init__(self, portfolio: Portfolio, stock_pool: StockPool):
        self.portfolio = portfolio
        self.name = f"{portfolio.name}_builder"
        self._stock_pool = stock_pool.value
        _stock_pool = download_index_constituents(index_url=self._stock_pool)
        _stock_pool = models.fetch_from_company_table(*_stock_pool)
        self.stocks = [
            Stock(symbol=company.symbol, company=company) for company in _stock_pool
        ]
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
        self._filtered_pool = filter(
            lambda stock: stock.company.sector == sector, self.stocks
        )

    def filter_by_industry(self, industry: str):
        """
        :param industry: key (attr) to filter companies.
        :return: None
        """
        self._filtered_pool = filter(
            lambda stock: stock.company.industry == industry, self.stocks
        )

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
                bo = MarketBuy(
                    date=datetime.now(),
                    symbol=new_stock.symbol,
                    price=new_stock.get_price(),
                    qty=qty,
                )
                p.purchase_asset(buy_order=bo, stock=new_stock)
            except Exception as e:
                logger.warning(e)
                continue
        if purchase == "q":
            continue_building = False

    print(p)
