from copy import deepcopy
from datetime import datetime
from types import TracebackType
from typing import Self

import pytest

from backlive.domain.models import Candle, Ticker
from backlive.feed.base import IFeed
from backlive.repository.repository import ITickerRepository
from backlive.repository.unit_of_work import IUnitOfWork


class FakeTickerRepository(ITickerRepository):
    def __init__(self) -> None:
        self.tickers: dict[str, Ticker] = {}

    def add_ticker(self, ticker: Ticker) -> None:
        self.tickers[ticker.symbol] = deepcopy(ticker)

    def get_ticker(self, symbol: str) -> Ticker | None:
        return self.tickers.get(symbol)

    def add_candles(self, symbol: str, candles: list[Candle]) -> None:
        ticker = self.get_ticker(symbol)
        if ticker:
            ticker.candles.extend(candles)


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self._repository = FakeTickerRepository()
        self.committed = False

    @property
    def repository(self) -> ITickerRepository:
        return self._repository

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


class FakeFeed(IFeed):
    def fetch_candles(self, symbol: str) -> list[Candle]:
        return [
            Candle(
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
