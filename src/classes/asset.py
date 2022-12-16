from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
import pathlib
import os
from loguru import logger
from datetime import datetime, timedelta
from src.classes.company import Company
from src.misc.enums import AssetType
from src.misc.utils import normalize_symbol, currency, load_cfg
from src.data.download_remote_data import download_ticker_data, load_ticker_market_data_from_csv
from src.data.models import fetch_from_company_table


class Asset(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class Stock(Asset):
    module_path = pathlib.Path(__file__).parent.resolve()
    cfg = load_cfg(prepend_path=os.path.join(module_path, '..'))
    TICKER_DATA_PATH = os.path.join(module_path, '..', 'data', cfg["TICKER_DATA_PATH"])

    def __init__(
            self,
            symbol: str,
            company: Optional[Company] = None,
            market_data: Optional[pd.DataFrame] = None
    ):
        self.asset_type = AssetType.Stock
        self.symbol = normalize_symbol(symbol)
        if company is None:
            company = fetch_from_company_table(symbol)[0]
        self.company = company
        _path = os.path.join(Stock.TICKER_DATA_PATH, f"{normalize_symbol(symbol)}.csv")
        if market_data is None:
            if not os.path.exists(_path):
                logger.warning(f"Market data for symbol {symbol} has no corresponding csv file ({_path}).")
                self._refresh_market_data(replace=True)
            market_data = load_ticker_market_data_from_csv(symbol=symbol)
        self.market_data = market_data
        self._market_data_path = _path

    def get_live_price(self) -> float:
        """
        :return: Most recent (and available) stock price.
        """
        if self.market_data is None or self.market_data.empty:
            return 0.00
        now = datetime.now()
        data_lag = now - self._get_last_data_refresh_time()
        if data_lag > timedelta(days=1):
            logger.warning(f"Local data for {self.symbol} is behind by ({data_lag}).")
            self._refresh_market_data()

        return self.market_data['Close'].iloc[-1]

    def _get_last_data_refresh_time(self) -> datetime:
        """
        Get the last modification time of the respective csv market data file to see
        if data refresh is necessary.
        """
        return datetime.fromtimestamp(os.path.getmtime(self._market_data_path))

    def _refresh_market_data(self, replace: bool = False):
        """
        :param replace: if no csv is found or we just want to populate the csv file with entirely new data.
        Update the ticker market data csv file if more than 1 day has elapsed since restart
        (assuming not intraday data).
        """
        logger.debug(f"Refreshing data for {self.symbol}.")
        if replace:
            download_ticker_data(symbol=self.symbol)
        else:
            last_date = pd.to_datetime(self.market_data.index[-1]).to_pydatetime()
            download_ticker_data(symbol=self.symbol, start_date=last_date, append_data=True)

    def __str__(self):
        return (f"          [Stock] \n"
                f"      Symbol: {self.symbol:} \n"
                f"     Company: {self.company.company_name if self.company else None} \n"
                f"  Live Price: {currency(self.get_live_price())} \n"
                )

    def __repr__(self):
        return "Stock<asset_type=AssetType.Stock, symbol, Company, live_price>"


if __name__ == "__main__":
    ticker = " gm "
    stock = Stock(symbol=ticker, market_data=load_ticker_market_data_from_csv(ticker))
    print(stock)
