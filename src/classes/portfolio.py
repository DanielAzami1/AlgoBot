from typing import Optional, List
from src.classes.asset import Stock
from src.classes.holding import Holding


class Portfolio:
    def __init__(self, name: str, holdings: List[Holding], value_history: Optional[List] = None):
        if not holdings:
            holdings = []
        self.name = name
        self.holdings = holdings
        self.value_history = value_history

    def get_num_holdings(self):
        return len(self.holdings)

    def __str__(self):
        return f"Portfolio {self.name}: {self.get_num_holdings()} holdings."

    def __repr__(self):
        return "Portfolio<name, holdings, value_history>"
