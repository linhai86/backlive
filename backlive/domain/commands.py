from dataclasses import dataclass
from datetime import datetime


class Command:
    pass


@dataclass
class DownloadCandleCommand(Command):
    symbol: str
    start: datetime
    end: datetime
    interval: str
    limit: int


@dataclass
class PlaceOrderCommand(Command):
    symbol: str
    quantity: float
    price: float
    order_type: str
