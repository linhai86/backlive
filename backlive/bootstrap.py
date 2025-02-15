from backlive.domain.commands import DownloadCandleCommand
from backlive.feed.yfinance import YFinanceFeed
from backlive.repository.unit_of_work import UnitOfWork
from backlive.service.handler import DownloadCandleHandler
from backlive.service.message_bus import InMemoryMessageBus


def bootstrap(url: str) -> InMemoryMessageBus:
    feed = YFinanceFeed()
    uow = UnitOfWork(url)

    message_bus = InMemoryMessageBus()

    # Command Handlers
    download_candle_handler = DownloadCandleHandler(uow, feed, message_bus=message_bus)

    # Register Handlers
    message_bus.register_handler(DownloadCandleCommand, download_candle_handler.handle)

    return message_bus
