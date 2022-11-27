from enum import Enum, auto

class AssetType(Enum):
    Stock = auto()
    
class TableType(Enum):
    company = auto()
    ticker = auto()
    holding = auto()
    transaction = auto()
    portfolio = auto()