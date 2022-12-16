"""
Class definition for 'holdings' of assets. 
Represents the ownership details of a given asset (e.g. price bought at, time held, number of shares held, etc.)
"""
from datetime import datetime
from src.misc.utils import format_datetime_12h, currency


class Holding:
    def __init__(self, stock, qty_owned: int, date_purchased: datetime = datetime.now()):
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

