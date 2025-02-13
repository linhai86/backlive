from ..domain.models import Ticker
from ..feed.base import IFeed
from ..repository.unit_of_work import IUnitOfWork


class TickerService:
    def __init__(self, uow: IUnitOfWork, feed: IFeed):
        self.uow = uow
        self.feed = feed

    def fetch_and_save_candles(self, symbol: str) -> Ticker:
        candles = self.feed.fetch_candles(symbol)

        with self.uow:
            ticker = self.uow.repository.get_ticker(symbol)
            if not ticker:
                ticker = Ticker(symbol=symbol, name=symbol, candles=[])
                self.uow.repository.add_ticker(ticker)

            self.uow.repository.add_candles(symbol, candles)

            self.uow.commit()
            ticker.candles.extend(candles)

        return ticker
