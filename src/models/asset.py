"""
Class definitions for financial s'assets'. 
"""
from abc import ABC, abstractmethod
from loguru import logger
from datetime import date
import sys

sys.path.append('..')
"""Local imports"""
from misc.enums import AssetType
from misc.utils import normalize_symbol, currency

class Asset(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def load_price_history(self, start_date: date, end_date: date, freq=None):
        pass

    @abstractmethod
    def download_price_data(self, start_date: date, end_date: date, freq=None):
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
        company_name: str,
        live_price: float
    ):
        self.asset_type = AssetType.Stock
        self.symbol = normalize_symbol(symbol)
        self.company_name = company_name
        self.live_price = live_price
        logger.success(f"Stock obj with symbol {symbol} successfully created.")
    
    def load_price_history(self, start_date: date, end_date: date, freq=None):
        return super().load_price_history(start_date, end_date, freq)
    
    def download_price_data(self, start_date: date, end_date: date, freq=None):
        return super().download_price_data(start_date, end_date, freq)

    def __str__(self):
        return (f"          [Stock] \n" 
                f"      Symbol: {self.symbol:} \n"
                f"     Company: {self.company_name} \n"
                f"  Live Price: {currency(self.live_price)} \n"
            )

    def __repr__(self):
        return "Stock<asset_type=AssetType.Stock, symbol, company_name, live_price>"




if __name__ == "__main__":
    symbol = " aapl "
    company_name = "Apple Inc."
    live_price = 145.677
    stock = Stock(symbol=symbol, company_name=company_name, live_price=live_price)
    print(stock)

