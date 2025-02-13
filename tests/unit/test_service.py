from backlive.feed.base import IFeed
from backlive.service.service import TickerService

from .conftest import FakeUnitOfWork


def test_fetch_and_save_stock_data(fake_uow: FakeUnitOfWork, fake_feed: IFeed) -> None:
    """Test fetching and saving stock data."""
    ticker_service = TickerService(fake_uow, fake_feed)
    ticker = ticker_service.fetch_and_save_candles("AAPL")

    assert ticker.symbol == "AAPL"
    assert len(ticker.candles) == 1
    assert fake_uow.committed is True
