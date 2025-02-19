from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import datetime

from ...domain.models import Candle


class IFeed(ABC):
    @abstractmethod
    def fetch_candles(
        self, symbol: str, start: datetime, end: datetime, interval: str = "1d", limit: int = 1000
    ) -> list[Candle]:
        pass

    @abstractmethod
    def stream_candles(self, symbol: str, interval: str = "1m") -> Iterator[Candle]:
        pass
