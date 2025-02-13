from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import override

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from ..domain.models import Candle, Ticker
from .models import CandleModel, TickerModel


class ITickerRepository(ABC):
    @abstractmethod
    def add_ticker(self, ticker: Ticker) -> None:
        pass

    @abstractmethod
    def get_ticker(self, symbol: str) -> Ticker | None:
        pass

    @abstractmethod
    def add_candles(self, symbol: str, candles: list[Candle]) -> None:
        pass


class SQLAlchemyTickerRepository(ITickerRepository):
    def __init__(self, session: Session):
        self.session = session

    @override
    def add_ticker(self, ticker: Ticker) -> None:
        ticker_model = TickerModel(symbol=ticker.symbol, name=ticker.name)
        self.session.add(ticker_model)

    @override
    def get_ticker(self, symbol: str) -> Ticker | None:
        ticker_model = self.session.scalars(select(TickerModel).where(TickerModel.symbol == symbol)).one_or_none()
        if ticker_model:
            candles = [
                Candle(
                    timestamp=candle.timestamp,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume,
                )
                for candle in ticker_model.candles
            ]
            return Ticker(symbol=ticker_model.symbol, name=ticker_model.name, candles=candles)
        return None

    @override
    def add_candles(self, symbol: str, candles: list[Candle]) -> None:
        ticker_model = self.session.scalars(select(TickerModel).where(TickerModel.symbol == symbol)).one_or_none()
        if ticker_model:
            data = [dict(**asdict(candle), ticker_id=ticker_model.id) for candle in candles]
            self.session.execute(insert(CandleModel), data)
