from datetime import datetime
from abc import ABC, abstractmethod

from src.misc.enums import Direction, OrderType
from src.misc.utils import normalize_symbol, currency


class Transaction(ABC):
    @abstractmethod
    def __init__(
            self, date: datetime, symbol: str, direction: Direction, order_type: OrderType, price: float, qty: int
    ):
        today = datetime.today()
        if today > date:
            raise ValueError(f"Given date for new transaction is ahead of current date:\n"
                             f"{date} > {today}")
        if price < 0:
            raise ValueError(f"Price cannot be less than 0: {currency(price)}")
        if qty < 0:
            raise ValueError(f"Quantity cannot be less than 0: {qty}")
        assert (isinstance(direction, Direction) and isinstance(order_type, OrderType))

        self.date = date
        self.symbol = normalize_symbol(symbol)
        self.direction = direction
        self.order_type = order_type
        self.price = price
        self.qty = qty

    def __str__(self):
        return f"Transaction:" \
               f" <{self.date}> {self.order_type} {self.direction} - {self.qty} shares @ {currency(self.price)}"

    def __repr__(self):
        return "Transaction<date, symbol, direction, order_type, price, qty>"


class MarketBuy(Transaction):
    def __init__(
            self, date: datetime, symbol: str, price: float, qty: int
    ):
        super().__init__(
            date=date,
            symbol=symbol,
            direction=Direction.Buy,
            order_type=OrderType.Market,
            price=price,
            qty=qty
        )


class MarketSell(Transaction):
    def __init__(
            self, date: datetime, symbol: str, price: float, qty: int
    ):
        super().__init__(
            date=date,
            symbol=symbol,
            direction=Direction.Sell,
            order_type=OrderType.Market,
            price=price,
            qty=qty
        )


