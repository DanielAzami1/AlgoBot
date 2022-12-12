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
        return (f"Company\n\n"
                f"{self.company_name} ({self.symbol})\n\n"
                f"[{self.industry}, {self.sector}]\n\n"
                f"{textwrap.shorten(self.business_summary, width=140, placeholder='...')}\n\n"
                f"Market Cap : {currency(self.market_cap)}\n"
                f"Floated Shares : {self.float_shares:,}\n")

    def __repr__(self):
        return "\nCompany<company_name, symbol, sector, industry, business_summary, country, employee_count, " \
               "market_cap, float_shares, is_esg_populated> "


if __name__ == "__main__":
    """Testing"""
    import yfinance as yf

    msft = yf.Ticker("MSFT")
    info = msft.info
    company_name = info['shortName']
    symbol = info['symbol']
    sector = info['sector']
    industry = info['industry']
    business_summary = info['longBusinessSummary']
    country = info['country']
    employee_count = info['fullTimeEmployees']
    market_cap = info['marketCap']
    float_shares = info['floatShares']
    is_esg_populated = info['isEsgPopulated']

    msft_company = Company(
        company_name=company_name,
        symbol=symbol,
        sector=sector,
        industry=industry,
        business_summary=business_summary,
        country=country,
        employee_count=employee_count,
        market_cap=market_cap,
        float_shares=float_shares,
        is_esg_populated=is_esg_populated
    )

    from loguru import logger

    logger.debug(repr(msft_company))

    logger.info(list(vars(msft_company).values()))
