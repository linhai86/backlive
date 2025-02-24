from dataclasses import dataclass
from datetime import datetime

from .models import OrderSide, OrderType


class Command:
    pass


@dataclass
class DownloadCandleCommand(Command):
    symbols: list[str]
    start: datetime
    end: datetime
    interval: str
    limit: int


@dataclass
class PlaceOrderCommand(Command):
    symbol: str
    quantity: float
    price: float
    order_type: OrderType
    side: OrderSide


@dataclass
class CancelOrderCommand(Command):
    order_id: int


@dataclass
class RunBacktestCommand(Command):
    symbols: list[str]
    start: datetime
    end: datetime
