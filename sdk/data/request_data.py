import yfinance as yf
import requests_cache
from typing import Optional, Dict, List
from datetime import date
from loguru import logger
import pandas as pd
import pathlib
import os
from sdk.misc.utils import load_cfg, normalize_symbol, timed

VALID_PERIODS = ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
VALID_INTERVALS = (
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "60m",
    "90m",
    "1h",
    "1d",
    "5d",
    "1wk",
    "1mo, 3mo",
)

module_path = pathlib.Path(__file__).parent.resolve()
cfg = load_cfg(prepend_path=os.path.join(module_path, ".."))
TICKER_DATA_PATH = os.path.join(module_path, cfg["TICKER_DATA_PATH"])


@timed
def download_multiple_ticker_data(
    *symbols: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    period: Optional[str] = "max",
    interval: Optional[str] = "1d",
) -> pd.DataFrame:
    """
    Fetch market data for multiple stocks.
    :param symbols: symbols to retrieve market data for.
    :param start_date: start date of market data.
    :param end_date: optional end date (default to date.today())
    :param period: alternative to start/end date - max, 1w, etc.
    :param interval: time between data points - 1w, 1mo, etc.
    :return: pd.DataFrame
    """
    if start_date and not end_date:
        end_date = date.today()
    if period and period not in VALID_PERIODS:
        raise ValueError(f"Period '{period}' invalid - Options: {VALID_PERIODS}")
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Interval '{interval}' invalid - Options: {VALID_INTERVALS}")
    symbols = map(normalize_symbol, symbols)
    tickers_joined = " ".join(symbols)
    logger.debug(f"Fetching data for {len(symbols)} symbols.")
    ticker_data: pd.DataFrame = yf.download(
        tickers_joined,
        start=start_date,
        end=end_date,
        group_by="ticker",
        period=period,
        interval=interval,
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
    append_data: Optional[bool] = False,
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
    :return: Dict[metadata, market_data]
    """
    if start_date and not end_date:
        end_date = date.today()
    if period and period not in VALID_PERIODS:
        raise ValueError(f"Period '{period}' invalid - Options: {VALID_PERIODS}")
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Interval '{interval}' invalid - Options: {VALID_INTERVALS}")
    if use_cache:
        session = requests_cache.CachedSession("yfinance.cache")
        session.headers["User-agent"] = "algobot/1.0"
    else:
        session = None
    symbol = normalize_symbol(symbol)
    stock_data = yf.Ticker(symbol, session=session)
    metadata = stock_data.info if include_metadata else None
    if metadata and metadata.get("longName", None) is None:
        logger.warning(f"Metadata missing for symbol download {symbol}")
        return {}
    market_data = stock_data.history(
        start=start_date, end=end_date, period=period, interval=interval
    )
    if not os.path.exists(os.path.join(TICKER_DATA_PATH, f"{symbol}.csv")):
        save_ticker_market_data_to_csv(symbol, market_data)
    if append_data:
        save_ticker_market_data_to_csv(symbol, market_data, append=True)
    return {"metadata": metadata, "market_data": market_data}


def download_index_constituents(index_url: str) -> List[str]:
    """
    Fetch constituents list for a given stock index. Default to snp500.
    :param: index_url: url to page where list of symbols can be read.
    :return: list[symbols]
    """
    table = pd.read_html(index_url)
    df = table[0]
    tickers = df["Symbol"]
    return list(tickers)


def save_ticker_market_data_to_csv(
    symbol: str, market_data: pd.DataFrame, append: bool = False
) -> None:
    """
    Save downloaded market data for given ticker to local csv.
    :param: symbol: corresponding stock ticker (will be name of csv).
    :param: market_data: data to save.
    :param: append: if append, new data will be appended to the csv file.
    :return: None.
    """
    symbol = normalize_symbol(symbol)
    path = os.path.join(TICKER_DATA_PATH, f"{symbol}.csv")
    if append:
        market_data.to_csv(path_or_buf=path, mode="a", header=False)
    else:
        market_data.to_csv(path_or_buf=path)
    logger.debug(
        f"Saved market data ({len(market_data.index)} rows) for {symbol} to {path}"
    )


def load_ticker_data_csv(symbol: str) -> pd.DataFrame:
    """
    Load downloaded market data for given ticker (from csv).
    :param symbol: corresponding stock ticker (will be name of csv).
    :return: pd.DataFrame (market data).
    """
    symbol = normalize_symbol(symbol)
    path = os.path.join(TICKER_DATA_PATH, f"{symbol}.csv")
    market_data = pd.read_csv(filepath_or_buffer=path, index_col="Date")
    return market_data
