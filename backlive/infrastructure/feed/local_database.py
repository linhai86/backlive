from collections.abc import Iterator
from datetime import datetime
from typing import override

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, joinedload

from ...domain.models import Candle
from ..database.models import TickerModel
from .base import IFeed


class LocalDatabaseFeed(IFeed):
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=True)
        self.session: Session = Session(bind=self.engine)

    @override
    def fetch_candles(
        self, symbols: list[str], start: datetime, end: datetime, interval: str = "1d", limit: int = 1000
    ) -> dict[str, list[Candle]]:
        ticker_models = (
            self.session.scalars(
                select(TickerModel).where(TickerModel.symbol.in_(symbols)).options(joinedload(TickerModel.candles))
            )
            .unique()
            .all()
        )
        if ticker_models:
            candles = {
                ticker_model.symbol: [
                    Candle(
                        symbol=ticker_model.symbol,
                        timestamp=candle.timestamp,
                        open=candle.open,
                        high=candle.high,
                        low=candle.low,
                        close=candle.close,
                        volume=candle.volume,
                    )
                    for candle in ticker_model.candles
                ]
                for ticker_model in ticker_models
            }
            return candles
        return {}

    @override
    def stream_candles(self, symbol: str, interval: str = "1m") -> Iterator[Candle]:
        raise NotImplementedError("Streaming is not implemented for local database.")
