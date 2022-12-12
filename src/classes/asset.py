"""
Class definitions for financial 'assets'.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from src.classes.company import Company
from src.misc.enums import AssetType
from src.misc.utils import normalize_symbol, currency


class Asset(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class Stock(Asset):
    def __init__(
            self,
            symbol: str,
            live_price: Optional[float] = None,
            company: Optional[Company] = None,
            price_history: Optional[List] = None
    ):
        self.asset_type = AssetType.Stock
        self.symbol = normalize_symbol(symbol)
        self.live_price = live_price
        self.company = company
        self.price_data = price_history

    def __str__(self):
        return (f"          [Stock] \n"
                f"      Symbol: {self.symbol:} \n"
                f"     Company: {self.company.company_name if self.company else None} \n"
                f"  Live Price: {currency(self.live_price if self.live_price else 0.00)} \n"
                )

    def __repr__(self):
        return "Stock<asset_type=AssetType.Stock, symbol, Company, live_price>"


if __name__ == "__main__":
    ticker = " aapl "
    price = 145.677
    stock = Stock(symbol=ticker, live_price=price)
    print(stock)
