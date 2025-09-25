from datetime import datetime, timezone
from typing import Optional
import requests
import pandas as pd


def fetch_binance_klines(symbol: str = 'BTCUSDT', interval: str = '1d', limit: int = 400) -> pd.Series:
    url = 'https://api.binance.com/api/v3/klines'
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    rows = []
    for k in data:
        close_ts = int(k[6]) // 1000
        close_dt = datetime.fromtimestamp(close_ts, tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        rows.append((close_dt, float(k[4])))
    s = pd.Series({dt: val for dt, val in rows}).sort_index()
    s.name = symbol
    return s


def fetch_yf_close(ticker: str, period: str = '6mo') -> pd.Series:
    try:
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + ticker
        params = {'range': period, 'interval': '1d', 'includePrePost': 'false'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        chart = data['chart']['result'][0]
        timestamps = chart['timestamp']
        closes = chart['indicators']['quote'][0]['close']
        valid_data = []
        for ts, price in zip(timestamps, closes):
            if price is not None:
                date = datetime.fromtimestamp(ts, tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                valid_data.append((date, price))
        if not valid_data:
            raise RuntimeError(f'No valid data for {ticker}')
        dates, prices = zip(*valid_data)
        s = pd.Series(prices, index=pd.to_datetime(dates))
        s.index = s.index.tz_localize(None)
        s = s.sort_index()
        s.name = ticker
        return s
    except Exception as e:
        raise RuntimeError(f'Failed to fetch data for {ticker}: {e}')
