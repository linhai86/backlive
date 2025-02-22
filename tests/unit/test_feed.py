from datetime import datetime

from backlive.infrastructure.feed.base import IFeed


def test_fetch_candles(fake_feed: IFeed) -> None:
    """Test fetching candles from the fake feed."""
    candles = fake_feed.fetch_candles(symbols=["AAPL"], start=datetime.now(), end=datetime.now())

    assert len(candles) == 1
    assert candles["AAPL"][0].open == 100.0
    assert candles["AAPL"][0].high == 105.0
    assert candles["AAPL"][0].low == 95.0
    assert candles["AAPL"][0].close == 102.0
    assert candles["AAPL"][0].volume == 1000
    assert isinstance(candles["AAPL"][0].timestamp, datetime)
