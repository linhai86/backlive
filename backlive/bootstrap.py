from backlive.application.handler import DownloadCandleHandler
from backlive.application.message_bus import InMemoryMessageBus
from backlive.domain.commands import DownloadCandleCommand
from backlive.infrastructure.database.unit_of_work import UnitOfWork
from backlive.infrastructure.feed.yfinance import YFinanceFeed


def bootstrap(url: str) -> InMemoryMessageBus:
    feed = YFinanceFeed()
    uow = UnitOfWork(url)

    message_bus = InMemoryMessageBus()

    # Command Handlers
    download_candle_handler = DownloadCandleHandler(uow, feed, message_bus=message_bus)

    # Register Handlers
    message_bus.register_handler(DownloadCandleCommand, download_candle_handler.handle)

    return message_bus
