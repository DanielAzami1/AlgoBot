import pandas as pd
import numpy as np
import pandas_ta as ta

class Metrics:
    """
    Grouping for various Metrics calculations methods.
    """
    @classmethod
    def percent_returns(cls, prices_or_values: pd.Series, interval: str = 'daily') -> pd.Series:
        """
        :param prices_or_values: close prices of stock or total values of portfolio
        :param interval: specifies the interval to calculate returns over (daily, monthly, yearly)
        :return: percent returns bucketed via interval
        """
        if interval == 'yearly':
            period = 252
        elif interval == 'monthly':
            period = 21
        else:
            period = 1
        percent_returns = prices_or_values.pct_change(periods=period)
        percent_returns.name = "pct_returns"
        return percent_returns.fillna(0)

    @classmethod
    def log_returns(cls, prices_or_values: pd.Series):
        """
        :param prices_or_values: close prices of stock or total values of portfolio
        :return: log returns
        """
        log_returns = np.log(prices_or_values) - np.log(prices_or_values.shift(1))
        log_returns.name = "log_returns"
        return log_returns.fillna(0)

    @classmethod
    def rolling_std(cls, pct_returns: pd.Series, window: int = 30) -> pd.Series:
        """
        :param pct_returns: percent returns of close prices
        :param window: number of days within window
        :return: standard deviation (decimal)
        """
        rolling_std = pct_returns.rolling(window=window, min_periods=1).std()
        rolling_std.name = "rolling_std"
        return rolling_std

    @classmethod
    def sma(cls, prices_or_values: pd.Series, window: int = 30) -> pd.Series:
        """
        :param prices_or_values: close prices of stock or total values of portfolio
        :param window: number of days within window
        :return: simple moving average (rolling arithmetic mean)
        """
        sma = prices_or_values.rolling(window=window, min_periods=1).mean()
        sma.name = "sma"
        return sma

    @classmethod
    def ema(cls, prices_or_values: pd.Series, window: int = 30) -> pd.Series:
        """
        :param prices_or_values: close prices of stock or total values of portfolio
        :param window: number of days within window
        :return: exponential moving average (rolling weighted average)
        """
        smoothing_factor = 2 / (window + 1)
        ema = prices_or_values.ewm(alpha=smoothing_factor).mean()
        ema.name = "ema"
        return ema

    @classmethod
    def std(cls, pct_returns: pd.Series) -> float:
        """
        :param pct_returns: close prices of stock or total values of portfolio
        :return: standard deviation (decimal)
        """
        return pct_returns.std()

    @classmethod
    def max_drawdown(cls, prices_or_values: pd.Series) -> float:
        """
        :param prices_or_values: close prices of stock or total values of portfolio
        :return: max drawdown over given timeframe according to this link: (decimal fraction)
        https://quant.stackexchange.com/questions/18094/how-can-i-calculate-the-maximum-drawdown-mdd-in-python
        """
        rolling_max = prices_or_values.cummax()
        daily_drawdown = prices_or_values / rolling_max - 1
        return min(daily_drawdown.cummin())


class TechnicalIndicators:
    """
    Grouping for various technical indicator calculation methods.
    Using this link for inspo for now:
    https://www.investopedia.com/top-7-technical-analysis-tools-4773275
    """

    @classmethod
    def obv(cls, prices_and_volume: pd.DataFrame) -> pd.Series:
        """
        {{ On-Balance Volume }}
        When OBV is rising, it shows that buyers are willing to step in and push
        the price higher. When OBV is falling, the selling volume is outpacing buying volume,
        which indicates lower prices. In this way, it acts like a trend confirmation tool.
        If price and OBV are rising, that helps indicate a continuation of the trend.
        :param prices_and_volume: df consisting of a close price column and a volume column
        :return: On Balance Volume according to this link:
        https://stackoverflow.com/questions/52671594/calculating-stockss-on-balance-volume-obv-in-python
        """
        obv = (np.sign(prices_and_volume['Close'].diff()) * prices_and_volume['Volume']).fillna(0).cumsum()
        obv.name = "obv"
        return obv

    @classmethod
    def ad_line(cls, hlcv_price_data: pd.DataFrame) -> pd.Series:
        """
        {{ Accumulation / Distribution Line }}
        Similar to the on-balance volume indicator (OBV), but instead of considering only the
        closing price of the security for the period, it also takes into account the trading
        range for the period and where the close is in relation to that range. If a stock finishes
        near its high, the indicator gives volume more weight than if it closes near the midpoint of its range.
        :param hlcv_price_data: High, Low, Close, Volume price data
        :return:  Accumulation/Distribution Line
        """
        close = hlcv_price_data['Close']
        low = hlcv_price_data['Low']
        high = hlcv_price_data['High']
        volume = hlcv_price_data['Volume']
        # Money Flow Multiplier (MFM)
        mfm = ((close - low) - (high - close)) / (high - low)
        # Money Flow Volume (MFV)
        mfv = mfm * volume
        ad = mfv.cumsum()
        ad.name = "ad"
        return ad

    @classmethod
    def atr(cls, hlc_price_data: pd.DataFrame) -> pd.Series:
        """
        {{ Average True Range }}
        measures market volatility by decomposing the entire range of an asset price
        for that period, typically derived from the 14-day simple moving average of a series of true range indicators.
        :param n: periods used to calculate the average true range
        :param hlc_price_data: High, Low, Close price data
        :return: Average True Range
        """
        n = 14
        tr = pd.DataFrame({
            'hl': hlc_price_data['High'] - hlc_price_data['Low'],
            'hc': abs(hlc_price_data['High'] - hlc_price_data['Close'].shift(-1)),
            'lc': abs(hlc_price_data['Low'] - hlc_price_data['Close'].shift(-1))
        }).max(axis=1)
        atr = tr.cumsum() / n
        atr.name = "atr"
        return atr

    @classmethod
    def adx(cls, hlc_price_data: pd.DataFrame) -> pd.Series:
        """
        {{ Average Directional Index }}
        The ADX is the main line on the indicator, usually colored black. There are two additional lines that can be
        optionally shown. These are DI+ and DI-. These lines are often colored red and green, respectively. All three
        lines work together to show the direction of the trend as well as the momentum of the trend.
        :param hlc_price_data: High, Low, Close price data
        :return: Average Directional Index
        """
        n = 14
        dm_pos = hlc_price_data['High'].shift(1) - hlc_price_data['High']
        smoothed_dm_pos = dm_pos.cumsum()
        dm_neg = hlc_price_data['Low'] - hlc_price_data['Low'].shift(1)
