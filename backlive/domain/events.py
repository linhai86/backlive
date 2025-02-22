from dataclasses import dataclass

from .models import Candle, Order, Portfolio


class Event:
    pass


@dataclass
class CandleDownloadedEvent(Event):
    candles: dict[str, list[Candle]]


@dataclass
class CandleReceivedEvent(Event):
    candle: Candle


@dataclass
class OrderPlacedEvent(Event):
    order: Order


@dataclass
class OrderFilledEvent(Event):
    order: Order
    fill_price: float


@dataclass
class OrderCanceledEvent(Event):
    order: Order


@dataclass
class OrderRejectedEvent(Event):
    order: Order
    reason: str


@dataclass
class BacktestCompletedEvent(Event):
    portfolio: Portfolio
