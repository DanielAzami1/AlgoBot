from typing import Optional, List, Dict
from loguru import logger
from datetime import datetime
from src.classes.holding import Holding
from src.classes.asset import Stock
from src.classes.transaction import Transaction, MarketBuy, MarketSell
from src.misc.utils import currency
from src.data import models


class Portfolio:
    def __init__(
            self,
            name: str,
            free_cash: float = 1_00_000.00,
            holdings: List[Holding] = None,
            value_history: Optional[List] = None,
            transaction_history: Optional[List[Transaction]] = None
    ):

        self.name = name
        self.free_cash = free_cash
        self.holdings = {}
        if holdings:
            self.holdings = {holding.symbol: holding for holding in holdings}
        else:
            try:
                self._load_holdings()  # try to load previously stored holdings for this portfolio.
            except Exception as err:
                logger.warning(err)
        self.value_history = value_history if value_history else []
        self.transaction_history = transaction_history if transaction_history else []

    def _load_holdings(self) -> None:
        """
        Load holdings stored in local db from this portfolio to populate holdings attr.
        :return: None.
        """
        logger.debug(f"Retrieving holdings for portfolio {self.name}.")
        _found_holdings = models.fetch_from_holdings_table(portfolio=self.name)
        if not _found_holdings:
            raise ValueError(f"Could not locate stored holdings for {self.name}.")
        for _holding in _found_holdings:
            _company = models.fetch_from_company_table(_holding.symbol)[0]
            _stock = Stock(symbol=_holding.symbol, company=_company)
            _holding.stock = _stock
            self.holdings[_holding.symbol] = _holding
        self.free_cash -= self.get_value_of_holdings()
        logger.debug(f"Populated {self.name} with {len(self.holdings)} holdings.")

    def purchase_asset(self, buy_order: MarketBuy, stock: Stock) -> None:
        """
        :param stock: Stock object to be used for instantiating new Holding obj if not already owned.
        :param buy_order: Market buy order to be executed.
        :return: None
        """
        if buy_order.market_value > self.free_cash:
            raise ValueError(f"Insufficient funds to execute ({buy_order}).")
        self.free_cash -= buy_order.market_value

        if self._holding_present_in_portfolio(buy_order.symbol):
            self.holdings[buy_order.symbol].qty_owned += buy_order.qty
            logger.success(f"Added {buy_order.qty} shares to holding {buy_order.symbol}.")
        else:
            new_holding = Holding(symbol=buy_order.symbol, stock=stock, qty_owned=buy_order.qty)
            self.holdings[new_holding.stock.symbol] = new_holding
        logger.success(f"Added {buy_order.symbol} to {self.name} portfolio holdings.")
        self.transaction_history.append(buy_order)

    def sell_asset(self, sell_order: MarketSell) -> None:
        """
        :param: sell_order: Market sell order to be executed.
        :return: None
        """
        if not self._holding_present_in_portfolio(sell_order.symbol):
            raise ValueError(f"holding of {sell_order.symbol} not present in portfolio.")
        holding = self.holdings[sell_order.symbol]
        if holding.qty_owned < sell_order.qty:
            raise ValueError(f"Insufficient shares owned to execute ({sell_order})")
        self.free_cash += sell_order.market_value

        if holding.qty_owned == sell_order.qty:
            del self.holdings[sell_order.symbol]
            logger.success(f"Position in {sell_order.symbol} liquidated ({sell_order.qty} shares).")
        else:
            holding.qty_owned -= sell_order.qty
            logger.success(f"Sold {sell_order.qty} shares of {sell_order.symbol}")
        self.transaction_history.append(sell_order)

    def _holding_present_in_portfolio(self, symbol: str) -> bool:
        """
        :param: symbol: symbol to check.
        :return: T/F.
        """
        try:
            _ = self.holdings[symbol]
            return True
        except KeyError:
            return False

    def get_value_of_holdings(self) -> float:
        """
        Get total market value of all holdings in portfolio.
        :param: date: optional date to get value of holdings on given date. (NOT IMPLEMENTED)
        :return: value of holdings
        """
        val = 0
        for holding in self.holdings:
            val += self.holdings[holding].get_market_value()
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

    def save_portfolio_state(self) -> None:
        models.insert_into_portfolio_table(portfolio=self.name, value=self.get_total_value(), timestamp=datetime.now())

    def save_portfolio_transactions(self) -> None:
        models.insert_into_transactions_table(*self.transaction_history, portfolio=self.name)

    def save_holdings(self) -> None:
        models.insert_into_holdings_table(*self.holdings.values(), portfolio=self.name)

    def __str__(self):
        return f"Portfolio [{self.name}]: {self.get_num_holdings()} unique holdings" \
               f" ({currency(self.get_value_of_holdings())})" \
               f" | {currency(self.free_cash)} cash."

    def __repr__(self):
        return "Portfolio<name, free_cash, holdings, value_history>"


if __name__ == "__main__":
    p = Portfolio(name="MyPortfolio")
    p.save_holdings()
    p.save_portfolio_state()
    p.save_portfolio_transactions()
    print(p)