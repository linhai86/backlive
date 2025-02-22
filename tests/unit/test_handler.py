from datetime import datetime

from backlive.application.handler import DownloadCandleHandler
from backlive.application.message_bus import InMemoryMessageBus
from backlive.domain.commands import DownloadCandleCommand
from backlive.infrastructure.feed.base import IFeed

from .conftest import FakeUnitOfWork


def test_fetch_and_save_stock_data(fake_uow: FakeUnitOfWork, fake_feed: IFeed) -> None:
    """Test fetching and saving stock data."""
    message_bus = InMemoryMessageBus()
    message_bus.register_handler(DownloadCandleCommand, DownloadCandleHandler.handle)
    handler = DownloadCandleHandler(fake_uow, fake_feed, message_bus=message_bus)
    handler.handle(
        DownloadCandleCommand(symbols=["AAPL"], start=datetime.now(), end=datetime.now(), interval="1d", limit=1000)
    )

    assert fake_uow.committed is True
