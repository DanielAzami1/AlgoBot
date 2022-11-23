"""
Class definitions for financial s'assets'. 
"""
from abc import ABC, abstractmethod
from loguru import logger
from datetime import date
from typing import Optional, List
import sys

sys.path.append('..')
"""Local imports"""
from models.company import Company
from misc.enums import AssetType
from misc.utils import normalize_symbol, currency

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
        live_price: float,
        company: Optional[Company],
        price_data: Optional[List] = None
    ):
        self.asset_type = AssetType.Stock
        self.symbol = normalize_symbol(symbol)
        self.live_price = live_price
        self.company = company
        self.price_data = price_data
    
    def __str__(self):
        return (f"          [Stock] \n" 
                f"      Symbol: {self.symbol:} \n"
                f"     Company: {self.company.company_name} \n"
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

