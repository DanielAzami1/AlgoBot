from datetime import datetime
from src.misc.utils import format_datetime_12h, currency


class Holding:
    def __init__(self, symbol: str, stock=None, qty_owned: int = 0, date_purchased: datetime = datetime.now()):
        assert qty_owned >= 0
        self.symbol = symbol
        self.stock = stock
        self.qty_owned = qty_owned
        self.date_purchased = date_purchased

    def get_market_value(self):
        return self.stock.get_live_price() * self.qty_owned

    def __str__(self):
        return f"[Holding] {self.stock.company.company_name} ({self.stock.symbol}) | {self.qty_owned} shares @ " \
               f"{currency(self.stock.get_live_price())} | " \
               f"Market Value: {currency(self.get_market_value())} | " \
               f" purchased {format_datetime_12h(self.date_purchased)}"

    def __repr__(self):
        return "Holding<Stock, qty_owned, date_purchased>"

