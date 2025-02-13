from abc import ABC, abstractmethod

from ..domain.models import Candle


class IFeed(ABC):
    @abstractmethod
    def fetch_candles(self, symbol: str) -> list[Candle]:
        pass
