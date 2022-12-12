"""
Class definition for 'holdings' of assets. 
Represents the ownership details of a given asset (e.g. price bought at, time held, number of shares held, etc.)
"""
from datetime import datetime
from typing import Optional
from src.misc.utils import format_datetime_12h
from src.classes.asset import Stock


class Holding:
    def __init__(self, stock: Stock, qty_owned: int, date_purchased: datetime = datetime.now()):
        assert qty_owned > 0
        assert date_purchased <= datetime.today()
        self.qty_owned = qty_owned
        self.date_purchased = date_purchased
        self.stock = stock

    def __str__(self):
        return f"Holding: {self.stock.symbol} stock; {self.qty_owned} shares;" \
               f" purchased on {format_datetime_12h(self.date_purchased)}"

    def __repr__(self):
        return "Holding<Stock, qty_owned, date_purchased>"

