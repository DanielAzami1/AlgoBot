from typing import Optional, List
from loguru import logger
from datetime import datetime
from src.classes.holding import Holding
from src.classes.asset import Stock
from src.classes.transaction import Transaction, MarketBuy, MarketSell
from src.misc.utils import currency


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
        self.value_history = value_history if value_history else []
        self.transaction_history = transaction_history if transaction_history else []
        self.holdings = {}
        if holdings:
            for holding in holdings:
                self.holdings[holding.stock.symbol] = holding

    def purchase_asset(self, buy_order: MarketBuy, stock: Stock):
        """
        :param stock: Stock object to be used for instantiating new Holding obj if not already owned.
        :param buy_order: Market buy order to be executed.
        :return: None
        """
        if buy_order.market_value > self.free_cash:
            raise ValueError(f"Insufficient funds to execute {buy_order}.")
        self.free_cash -= buy_order.market_value

        if self._holding_present_in_portfolio(buy_order.symbol):
            self.holdings[buy_order.symbol].qty_owned += buy_order.qty
            logger.success(f"Added {buy_order.qty} shares to holding {buy_order.symbol}.")
        else:
            new_holding = Holding(stock, buy_order.qty)
            self.holdings[new_holding.stock.symbol] = new_holding
        logger.success(f"Added {buy_order.symbol} to {self.name} portfolio holdings.")
        self.transaction_history.append(buy_order)

    def sell_asset(self, sell_order: MarketSell):
        """
        :param sell_order: Market sell order to be executed.
        :return: None
        """
        if not self._holding_present_in_portfolio(sell_order.symbol):
            raise ValueError(f"holding of {sell_order.symbol} not present in portfolio.")
        holding = self.holdings[sell_order.symbol]
        if holding.qty_owned < sell_order.qty:
            raise ValueError(f"Insufficient shares owned to execute {sell_order}")
        self.free_cash += sell_order.market_value

        if holding.qty_owned == sell_order.qty:
            del self.holdings[sell_order.symbol]
            logger.success(f"Position in {sell_order.symbol} liquidated.")
        else:
            holding.qty_owned -= sell_order.qty
            logger.success(f"Sold {sell_order.qty} shares of {sell_order.symbol}")
        self.transaction_history.append(sell_order)

    def get_value_of_holdings(self, date: datetime = None):
        val = 0
        if not date:
            for holding in self.holdings:
                val += self.holdings[holding].get_market_value()
        return val

    def _holding_present_in_portfolio(self, symbol: str) -> bool:
        try:
            _ = self.holdings[symbol]
            return True
        except KeyError:
            return False

    def get_num_holdings(self):
        return len(self.holdings) if self.holdings else None

    def get_free_cash(self):
        return f"(Cash) {currency(self.free_cash)}"

    def print_holdings(self):
        print("Holdings:\n")
        for holding in self.holdings:
            print(self.holdings[holding])

    def print_transaction_history(self):
        print("Transactions:\n")
        for transaction in self.transaction_history:
            print(transaction)

    def print_value_history(self):
        print("Value history:\n")
        for value in self.value_history:
            print(value)

    def __str__(self):
        return f"Portfolio [{self.name}]: {self.get_num_holdings()} unique holdings" \
               f" ({currency(self.get_value_of_holdings())})" \
               f" | {currency(self.free_cash)} cash."

    def __repr__(self):
        return "Portfolio<name, free_cash, holdings, value_history>"


class Holding:
    def __init__(self, stock: Stock, qty_owned: int, date_purchased: datetime = datetime.now()):
        assert qty_owned > 0
        assert date_purchased <= datetime.today()
        self.qty_owned = qty_owned
        self.date_purchased = date_purchased
        self.stock = stock

    def get_market_value(self):
        return self.stock.get_live_price() * self.qty_owned

    def __str__(self):
        return f"[Holding] {self.stock.company.company_name} ({self.stock.symbol}) | {self.qty_owned} shares @ " \
               f"{currency(self.stock.get_live_price())} | " \
               f"Market Value: {currency(self.get_market_value())} | " \
               f" purchased {format_datetime_12h(self.date_purchased)}"

    def __repr__(self):
        return "Holding<Stock, qty_owned, date_purchased>"