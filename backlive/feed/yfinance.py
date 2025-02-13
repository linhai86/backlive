import yfinance as yf  # type: ignore[import-untyped]

from ..domain.models import Candle
from .base import IFeed


class YFinanceFeed(IFeed):
    def fetch_candles(self, symbol: str) -> list[Candle]:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1y")
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
