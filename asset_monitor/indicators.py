import pandas as pd

def rolling_high_drawdown(close: pd.Series, window: int) -> pd.Series:
    close = close.dropna().sort_index()
    rh = close.rolling(window=window, min_periods=1).max()
    dd = (close - rh) / rh
    return dd


def rolling_low_surge(close: pd.Series, window: int) -> pd.Series:
    close = close.dropna().sort_index()
    rl = close.rolling(window=window, min_periods=1).min()
    surge = (close - rl) / rl
    return surge
