from __future__ import annotations
from typing import Optional
import pandas as pd
import pathlib
import os
from loguru import logger
from datetime import date, datetime, timedelta
import textwrap
from sdk.misc.enums import AssetType
from sdk.misc.utils import normalize_symbol, currency, load_cfg, format_datetime_12h
from sdk.data.request_data import (
    download_ticker_data,
    load_ticker_data_csv,
)
from sdk.factors.technical_indicators import TechnicalIndicators


class Stock:
    def __init__(
        self,
        symbol: str,
        company: Optional[Company] = None,
        market_data: Optional[pd.DataFrame] = None,
    ):
        self.asset_type = AssetType.Stock
        self.symbol = normalize_symbol(symbol)
        self.company = company
        module_path = pathlib.Path(__file__).parent.resolve()
        cfg = load_cfg(prepend_path=os.path.join(module_path, ".."))
        ticker_data_path = os.path.join(module_path, "..", "data", cfg["TICKER_DATA_PATH"])
        __path = os.path.join(ticker_data_path, f"{normalize_symbol(symbol)}.csv")
        if market_data is None:
            if not os.path.exists(__path):
                self.__refresh_market_data(replace=True)
            market_data = load_ticker_data_csv(symbol=symbol)
        self.market_data = market_data
        self.__market_data_path = __path
        self.metrics = {}

    def get_price(self, d: datetime.date = None) -> float:
        """
        :return: stock price on date d. Most recent price is returned if d not supplied.
        """
        now = datetime.now()
        #  check to see if local csv data needs to be updated.
        data_lag = now - datetime.fromtimestamp(os.path.getmtime(self.__market_data_path))
        if data_lag > timedelta(days=1):
            self.__refresh_market_data()
        if not d:
            price = self.market_data["Close"].iloc[-1]
        else:
            price = self.market_data.loc[str(d) + " 00:00:00-05:00", 'Close']  # saved all the data with a timestamp :(
        return price

    def get_returns(self, interval: str = 'daily') -> pd.Series:
        """
        :param interval: specifies the interval to calculate returns over (daily, monthly, yearly)
        :return: returns bucketed via interval based on close prices.
        """
        try:
            return self.metrics[f'{interval}_returns']
        except KeyError:
            pass
        prices = self.market_data['Close']
        if interval == 'yearly':
            period = 252
        elif interval == 'monthly':
            period = 21
        else:
            period = 1
        returns = prices.pct_change(periods=period)
        self.metrics[f'{interval}_returns'] = returns
        return returns

    def get_std(self):
        """
        :return: standard deviation of % returns.
        """
        try:
            return self.metrics["std"]
        except KeyError:
            pass
        std = self.get_returns().std()
        self.metrics["std"] = std
        return std

    def __refresh_market_data(self, replace: bool = False):
        """
        :param replace: if no csv is found, or we just want to populate the csv file with entirely new data.
        Update the ticker market data csv file if more than 1 day has elapsed since refresh
        (assuming not intraday data).
        """
        logger.debug(f"Refreshing data for {self.symbol}.")
        if replace:
            download_ticker_data(symbol=self.symbol)
        else:
            last_date = pd.to_datetime(
                self.market_data.index[-1]
            ).to_pydatetime() + timedelta(days=1)
            download_ticker_data(
                symbol=self.symbol, start_date=last_date, append_data=True
            )
        self.market_data = load_ticker_data_csv(self.symbol)

    def __str__(self):
        return (
            f"          [Stock] \n"
            f"      Symbol: {self.symbol:} \n"
            f"     Company: {self.company.company_name if self.company else None} \n"
            f"  Live Price: {currency(self.get_price())} \n"
        )

    def __repr__(self):
        return "Stock<asset_type=AssetType.Stock, symbol, Company, live_price>"


class Holding:
    def __init__(
        self,
        symbol: str,
        stock=None,
        qty_owned: int = 0,
        date_purchased: datetime = datetime.now(),
    ):
        assert qty_owned >= 0
        self.symbol = symbol
        self.stock = stock
        self.qty_owned = qty_owned
        self.date_purchased = date_purchased

    def get_market_value(self, d: datetime.date) -> float:
        return self.stock.get_price(d=d) * self.qty_owned

    def __str__(self):
        return (
            f"[Holding] {self.stock.company.company_name} ({self.stock.symbol}) | {self.qty_owned} shares @ "
            f"{currency(self.stock.get_price())} | "
            f"Market Value: {currency(self.get_market_value())} | "
            f" purchased {format_datetime_12h(self.date_purchased)}"
        )

    def __repr__(self):
        return "Holding<Stock, qty_owned, date_purchased>"


class Company:
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
        is_esg_populated: bool,
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
        return (
            f"[Company]\n"
            f"{self.company_name} ({self.symbol})\n"
            f"[{self.industry}, {self.sector}]\n"
            f"{textwrap.shorten(self.business_summary, width=140, placeholder='...')}\n\n"
            f"Market Cap : {currency(self.market_cap)}\n"
            f"Floated Shares : {self.float_shares:,}\n"
        )

    def __repr__(self):
        return (
            "\nCompany<company_name, symbol, sector, industry, business_summary, country, employee_count, "
            "market_cap, float_shares, is_esg_populated> "
        )