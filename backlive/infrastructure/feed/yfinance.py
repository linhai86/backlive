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
        self, symbols: list[str], start: datetime, end: datetime, interval: str = "1d", limit: int = 1000
    ) -> dict[str, list[Candle]]:
        tickers = yf.Tickers(" ".join(symbols))
        history = tickers.history(
            start=start, end=end, interval=interval, group_by="ticker", actions=False, progress=False
        )
        history = history.head(n=limit)
        history = {
            ticker: history[ticker].reset_index().to_dict(orient="records") for ticker in history.columns.levels[0]
        }
        candles = {
            symbol: [
                Candle(
                    symbol=symbol,
                    timestamp=record["Date"],
                    open=record["Open"],
                    high=record["High"],
                    low=record["Low"],
                    close=record["Close"],
                    volume=record["Volume"],
                )
                for record in records
            ]
            for symbol, records in history.items()
        }
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
