from datetime import datetime

from backlive.domain.commands import DownloadCandleCommand
from backlive.feed.base import IFeed
from backlive.service.handler import DownloadCandleHandler
from backlive.service.message_bus import InMemoryMessageBus

from .conftest import FakeUnitOfWork


def test_fetch_and_save_stock_data(fake_uow: FakeUnitOfWork, fake_feed: IFeed) -> None:
    """Test fetching and saving stock data."""
    message_bus = InMemoryMessageBus()
    message_bus.register_handler(DownloadCandleCommand, DownloadCandleHandler.handle)
    handler = DownloadCandleHandler(fake_uow, fake_feed, message_bus=message_bus)
    handler.handle(
        DownloadCandleCommand(symbol="AAPL", start=datetime.now(), end=datetime.now(), interval="1d", limit=1000)
    )

    assert fake_uow.committed is True
