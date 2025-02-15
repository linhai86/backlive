from datetime import datetime
from typing import override

import yfinance as yf  # type: ignore[import-untyped]

from ...domain.models import Candle
from .base import IFeed


class YFinanceFeed(IFeed):
    @override
    def fetch_candles(
        self, symbol: str, start: datetime, end: datetime, interval: str = "1d", limit: int = 1000
    ) -> list[Candle]:
        ticker = yf.Ticker(symbol)
        history = ticker.history(start=start, end=end, interval=interval)
        history = history.head(n=limit)
        candles = [
            Candle(
                timestamp=timestamp,
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
            )
            for timestamp, row in history.iterrows()
        ]
        return candles
