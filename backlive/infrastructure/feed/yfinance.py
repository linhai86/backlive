import time
from collections.abc import Iterator
from datetime import datetime, timedelta
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
                symbol=symbol,
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

    @override
    def stream_candles(self, symbol: str, interval: str = "1m") -> Iterator[Candle]:
        try:
            while True:
                # TODO: check for trading hours
                end = datetime.now()
                start = end - timedelta(seconds=60)
                candles = yf.download(
                    symbol, period="1d", start=start, end=end, group_by="ticker", progress=False, prepost=True
                )
                last_candle = candles.iloc[-1].get(symbol)
                if candles:
                    timestamp = datetime.now()
                    yield Candle(
                        symbol=symbol,
                        timestamp=timestamp,
                        open=last_candle["Open"],
                        high=last_candle["High"],
                        low=last_candle["Low"],
                        close=last_candle["Close"],
                        volume=last_candle["Volume"],
                    )
                time.sleep(60)
        except KeyboardInterrupt:
            print("Streaming stopped.")
