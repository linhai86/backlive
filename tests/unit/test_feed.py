from datetime import datetime

from backlive.feed.base import IFeed


def test_fetch_candles(fake_feed: IFeed) -> None:
    """Test fetching candles from the fake feed."""
    candles = fake_feed.fetch_candles(symbol="AAPL", start=datetime.now(), end=datetime.now())

    assert len(candles) == 1
    assert candles[0].open == 100.0
    assert candles[0].high == 105.0
    assert candles[0].low == 95.0
    assert candles[0].close == 102.0
    assert candles[0].volume == 1000
    assert isinstance(candles[0].timestamp, datetime)
