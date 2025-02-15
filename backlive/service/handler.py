from ..domain.commands import DownloadCandleCommand
from ..domain.events import CandleDownloadedEvent
from ..domain.models import Ticker
from ..feed.base import IFeed
from ..repository.unit_of_work import IUnitOfWork
from .message_bus import InMemoryMessageBus


class DownloadCandleHandler:
    def __init__(self, uow: IUnitOfWork, feed: IFeed, message_bus: InMemoryMessageBus):
        self.uow = uow
        self.feed = feed
        self.message_bus = message_bus

    def handle(self, command: DownloadCandleCommand) -> None:
        candles = self.feed.fetch_candles(command.symbol)

        with self.uow:
            ticker = self.uow.repository.get_ticker(command.symbol)
            if not ticker:
                ticker = Ticker(symbol=command.symbol, name=command.symbol, candles=[])
                self.uow.repository.add_ticker(ticker)

            self.uow.repository.add_candles(command.symbol, candles)

            self.uow.commit()
            ticker.candles.extend(candles)

        self.message_bus.handle(CandleDownloadedEvent(symbol=command.symbol, candles=candles))
