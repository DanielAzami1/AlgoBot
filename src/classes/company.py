from src.misc.utils import currency
import textwrap


class Company:
    """All params for this object will come from yfinance or loaded from stored yfinance queries."""

    def __init__(
            self,
            symbol: str,
            company_name: str,
            sector: str,
            industry: str,
            business_summary: str,
            country: str,
            employee_count: int,
            market_cap: float,
            float_shares: float,
            is_esg_populated: bool
    ):
        self.symbol = symbol
        self.company_name = company_name
        self.sector = sector
        self.industry = industry
        self.business_summary = business_summary
        self.country = country
        self.employee_count = employee_count
        self.market_cap = market_cap
        self.float_shares = float_shares
        self.is_esg_populated = is_esg_populated

    def __str__(self):
        return (f"[Company]\n"
                f"{self.company_name} ({self.symbol})\n"
                f"[{self.industry}, {self.sector}]\n"
                f"{textwrap.shorten(self.business_summary, width=140, placeholder='...')}\n\n"
                f"Market Cap : {currency(self.market_cap)}\n"
                f"Floated Shares : {self.float_shares:,}\n")

    def __repr__(self):
        return "\nCompany<company_name, symbol, sector, industry, business_summary, country, employee_count, " \
               "market_cap, float_shares, is_esg_populated> "
