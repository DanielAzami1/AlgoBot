import pandas as pd
import numpy as np
import datetime


class TechnicalIndicators:
    """
    Grouping for various technical indicator calculation methods. Ideally will provide an abstract enough implementation
    to support using these methods for both individual stocks and portfolios.
    """
    @classmethod
    def std(cls, pct_returns: pd.Series):
        """
        :param pct_returns: percent returns of close prices
        :return: standard deviation (decimal)
        """
        return pct_returns.std()

    @classmethod
    def sma(cls, close_prices: pd.Series, window: int = 30):
        """
        :param close_prices: stock close prices
        :param window: number of days within window
        :return: simple moving average (rolling arithmetic mean)
        """
        return close_prices.rolling(window=window, min_periods=1).mean()

    @classmethod
    def ema(cls, close_prices: pd.Series, window: int = 30):
        """
        :param close_prices: stock close_prices
        :param window: number of days within window
        :return: exponential moving average (rolling weighted average)
        """
        smoothing_factor = 2 / (window + 1)



