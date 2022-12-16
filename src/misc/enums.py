from enum import Enum, auto


class AssetType(Enum):
    Stock = auto()


class Direction(Enum):
    Buy = "BUY"
    Sell = "SELL"


class OrderType(Enum):
    Market = "MARKET"
    Limit = "LIMIT"


class StockPool(Enum):
    SNP500 = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
