from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto


class OrderType(Enum):
    MARKET = auto()
    LIMIT = auto()


class OrderSide(Enum):
    BUY = auto()
    SELL = auto()


class OrderStatus(Enum):
    PENDING = auto()
    FILLED = auto()
    CANCELLED = auto()
    REJECTED = auto()


@dataclass(frozen=True, slots=True)
class Candle:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class Ticker:
    symbol: str
    name: str


@dataclass(slots=True)
class Order:
    symbol: str
    quantity: float
    price: float
    order_type: OrderType
    side: OrderSide
    status: OrderStatus = OrderStatus.PENDING
    order_id: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class Position:
    symbol: str
    quantity: float
    average_price: float


@dataclass(slots=True)
class Portfolio:
    balance: float
    positions: dict[str, Position]  # {symbol: position}

    def update_position(self, symbol: str, quantity: float, price: float) -> None:
        self.balance -= quantity * price

        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol, quantity=quantity, average_price=price)
        else:
            existing_position = self.positions[symbol]

            # Only update average price if adding to position
            if quantity > 0:
                # Only need to recalculate average price when buying
                total_value = (existing_position.quantity * existing_position.average_price) + quantity * price
                total_shares = existing_position.quantity + quantity
                existing_position.average_price = total_value / total_shares

            existing_position.quantity += quantity

            if existing_position.quantity == 0:
                del self.positions[symbol]  # Clean up empty positions
