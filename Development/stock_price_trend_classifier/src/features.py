import pandas as pd
import numpy as np


def compute_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def compute_moving_average(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window).mean()


def compute_volatility(close: pd.Series, window: int = 10) -> pd.Series:
    returns = close.pct_change()
    volatility = returns.rolling(window).std()
    return volatility
