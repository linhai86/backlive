from dataclasses import dataclass
from datetime import datetime

from .models import Candle


class Event:
    pass


@dataclass
class CandleDownloadedEvent(Event):
    symbol: str
    candles: list[Candle]


@dataclass
class OrderPlacedEvent(Event):
    symbol: str
    quantity: float
    price: float
    order_type: str  # e.g., "buy", "sell"


@dataclass
class TradeExecutedEvent(Event):
    symbol: str
    quantity: float
    price: float
    timestamp: datetime
    order_type: str
