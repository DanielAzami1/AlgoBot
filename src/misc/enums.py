from enum import Enum, auto


class AssetType(Enum):
    Stock = auto()


class Direction(Enum):
    Buy = "buy"
    Sell = "sell"


class OrderType(Enum):
    Market = "market"
    Limit = "limit"
