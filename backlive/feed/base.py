from abc import ABC, abstractmethod
from datetime import datetime

from ..domain.models import Candle


class IFeed(ABC):
    @abstractmethod
    def fetch_candles(
        self, symbol: str, start: datetime, end: datetime, interval: str = "1d", limit: int = 1000
    ) -> list[Candle]:
        pass
