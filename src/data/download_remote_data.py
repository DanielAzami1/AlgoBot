import yfinance as yf
import requests_cache
from typing import Optional, Dict, List
from datetime import date
from loguru import logger
import pandas as pd
import pathlib
import os
from src.misc.utils import load_cfg, normalize_symbol, timed

VALID_PERIODS = ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
VALID_INTERVALS = ("1m", "2m", "5m", "15m", "30m", "60m",
                   "90m", "1h", "1d", "5d", "1wk", "1mo, 3mo")

module_path = pathlib.Path(__file__).parent.resolve()
cfg = load_cfg(prepend_path=os.path.join(module_path, '..'))
TICKER_DATA_PATH = os.path.join(module_path, cfg["TICKER_DATA_PATH"])


@timed
def mass_download_data(
        *symbols: str,
        start_date: date = None,
        end_date: Optional[date] = date.today(),
        period: Optional[str] = None,
        interval: Optional[str] = "1d"
) -> pd.DataFrame:
    """
    Fetch ticker market data for multiple stocks. Period (e.g. 1d) can be passed in-leu of start & end date.
    """
    assert start_date or period, "Must pass in either a start date or a period"
    if start_date and not end_date:
        end_date = date.today()
    if period and period not in VALID_PERIODS:
        raise ValueError(f"Period '{period}' invalid - Options: {VALID_PERIODS}")
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Interval '{interval}' invalid - Options: {VALID_INTERVALS}")
    symbols = map(normalize_symbol, symbols)
    tickers_joined = " ".join(symbols)
    logger.debug(f"Fetching data for {symbols}")
    ticker_data: pd.DataFrame = yf.download(
        tickers_joined, start=start_date, end=end_date, group_by="ticker",
        period=period, interval=interval
    )
    return ticker_data


@timed
def download_ticker_data(
        symbol: str,
        start_date: date = None,
        end_date: Optional[date] = None,
        period: Optional[str] = "max",
        interval: Optional[str] = "1d",
        include_metadata: Optional[bool] = False,
        use_cache: Optional[bool] = True,
        append_data: Optional[bool] = False
) -> Dict:
    """
    Fetch market and optionally meta data for given stock. Period (e.g. 1d) can be passed in-leu of start & end date
    :param symbol: symbol to retrieve data for.
    :param start_date: optional start date.
    :param end_date: optional end date.
    :param period: alternative to start&end date (e.g. 1d).
    :param interval: time between each record (e.g. for intraday data).
    :param include_metadata: include information about the company.
    :param use_cache: use requests_cache to store api call.
    :param append_data: append data to the corresponding data csv file.
    :return: None
    """
    assert start_date or period
    if start_date and not end_date:
        end_date = date.today()
    if period and period not in VALID_PERIODS:
        raise ValueError(f"Period '{period}' invalid - Options: {VALID_PERIODS}")
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Interval '{interval}' invalid - Options: {VALID_INTERVALS}")
    if use_cache:
        session = requests_cache.CachedSession('yfinance.cache')
        session.headers['User-agent'] = 'algobot/1.0'
    else:
        session = None
    symbol = normalize_symbol(symbol)
    stock_data = yf.Ticker(
        symbol, session=session
    )
    metadata = stock_data.info if include_metadata else None
    if metadata and metadata.get("longName", None) is None:
        logger.warning(f"Metadata missing for symbol download {symbol}")
        return {}
    market_data = stock_data.history(start=start_date, end=end_date, period=period, interval=interval)
    if not os.path.exists(os.path.join(TICKER_DATA_PATH, f"{symbol}.csv")):
        save_ticker_market_data_to_csv(symbol, market_data)
    if append_data:
        save_ticker_market_data_to_csv(symbol, market_data, append=True)
    return {
        "metadata": metadata,
        "market_data": market_data
    }


@timed
def download_index_constituents(
        index_url: str = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
) -> List[str]:
    """Fetch constituents list (symbols) for given index (default is snp500)."""
    table = pd.read_html(index_url)
    df = table[0]
    tickers = df['Symbol']
    return list(tickers)


def save_ticker_market_data_to_csv(symbol: str, market_data: pd.DataFrame, append: bool = False) -> None:
    """
    Save downloaded market data for given ticker.
    """
    symbol = normalize_symbol(symbol)
    path = os.path.join(TICKER_DATA_PATH, f'{symbol}.csv')
    if append:
        market_data.to_csv(path_or_buf=path, mode='a', header=False)
    else:
        market_data.to_csv(path_or_buf=path)
    logger.debug(f"Saved market data ({len(market_data.index)} rows) for {symbol} to {path}")


def load_ticker_market_data_from_csv(symbol: str) -> pd.DataFrame:
    """
    Load downloaded market data for given ticker (from csv).
    """
    symbol = normalize_symbol(symbol)
    path = os.path.join(TICKER_DATA_PATH, f'{symbol}.csv')
    market_data = pd.read_csv(filepath_or_buffer=path, index_col="Date")
    return market_data


if __name__ == "__main__":
    # tickers = ["aapl ", " msft", " meta", "  g m "]
    # data = mass_download_data(*tickers, start_date=date(2017, 1, 1))
    # print(type(data))
    # cfg = load_cfg()
    # ticker_data_path = cfg["TICKER_DATA_PATH"] + "test"
    # data.to_csv(ticker_data_path)
    # ticker = " aapl"
    # data = download_ticker_data(
    #     ticker, period="5d", include_metadata=True
    # )
    # print(data['market_data'])
    # ticks = download_index_constituents()
    # ticks_data = use_threadpool_exec(download_ticker_data, ticks)
    pass


