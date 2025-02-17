from copy import deepcopy
from datetime import datetime
from types import TracebackType
from typing import Self, override

import pytest

from backlive.domain.models import Candle, Order, OrderStatus
from backlive.infrastructure.database.repository import ICandleRepository, IOrderRepository
from backlive.infrastructure.database.unit_of_work import IUnitOfWork
from backlive.infrastructure.feed.base import IFeed


class FakeCandleRepository(ICandleRepository):
    def __init__(self) -> None:
        self.candles: dict[str, list[Candle]] = {}

    @override
    def get_candles(self, symbol: str) -> list[Candle]:
        return self.candles.get(symbol, list())

    @override
    def get_latest_candle(self, symbol: str) -> Candle | None:
        candles = self.get_candles(symbol)
        if candles:
            return candles[-1]  # Assume the last one is the latest one
        return None

    @override
    def add_candles(self, candles: list[Candle]) -> None:
        for candle in candles:
            if candle.symbol not in self.candles:
                self.candles[candle.symbol] = []
            self.candles[candle.symbol].append(candle)


class FakeOrderRepository(IOrderRepository):
    def __init__(self) -> None:
        self.orders: list[Order]

    @override
    def add(self, order: Order) -> None:
        if not order.order_id:
            order_data = deepcopy(order)
            order_data.order_id = len(self.orders)
            self.orders.append(order_data)
        else:
            order_data = self.orders[order.order_id]
            order_data.status = order.status

    @override
    def get(self, order_id: int) -> Order | None:
        try:
            return self.orders[order_id]
        except IndexError:
            return None

    @override
    def list_pending(self) -> list[Order]:
        return [order for order in self.orders if order.status == OrderStatus.PENDING]


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self._candle_repository = FakeCandleRepository()
        self._order_repository = FakeOrderRepository()
        self.committed = False

    @override
    @property
    def candle_repository(self) -> ICandleRepository:
        return self._candle_repository

    @override
    @property
    def order_repository(self) -> IOrderRepository:
        return self._order_repository

    @override
    def __enter__(self) -> Self:
        return self

    @override
    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()

    @override
    def commit(self) -> None:
        self.committed = True

    @override
    def rollback(self) -> None:
        pass


class FakeFeed(IFeed):
    @override
    def fetch_candles(
        self, symbol: str, start: datetime, end: datetime, interval: str = "1d", limit: int = 1000
    ) -> list[Candle]:
        return [
            Candle(
                symbol=symbol,
                timestamp=datetime.now(),
                open=100.0,
                high=105.0,
                low=95.0,
                close=102.0,
                volume=1000,
            )
        ]


# Fixtures


@pytest.fixture
def fake_uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def fake_feed() -> IFeed:
    return FakeFeed()
