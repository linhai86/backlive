from datetime import datetime

from backlive.domain.models import Candle, Ticker

from .conftest import FakeUnitOfWork


def test_add_ticker(fake_uow: FakeUnitOfWork) -> None:
    """Test adding a ticker to the repository."""
    ticker = Ticker(symbol="AAPL", name="Apple Inc.", candles=[])
    fake_uow.repository.add_ticker(ticker)

    retrieved_ticker = fake_uow.repository.get_ticker("AAPL")
    assert retrieved_ticker is not None
    assert retrieved_ticker.symbol == "AAPL"
    assert retrieved_ticker.name == "Apple Inc."


def test_add_candles(fake_uow: FakeUnitOfWork) -> None:
    """Test adding candles to a ticker."""
    ticker = Ticker(symbol="AAPL", name="Apple Inc.", candles=[])
    fake_uow.repository.add_ticker(ticker)

    timestamp = datetime.now()
    candle = Candle(timestamp=timestamp, open=100.0, high=105.0, low=95.0, close=102.0, volume=1000)
    fake_uow.repository.add_candles("AAPL", [candle])

    retrieved_ticker = fake_uow.repository.get_ticker("AAPL")
    assert retrieved_ticker is not None
    assert len(retrieved_ticker.candles) == 1
    assert retrieved_ticker.candles[0].timestamp == timestamp
    assert retrieved_ticker.candles[0].open == 100.0
    assert retrieved_ticker.candles[0].high == 105.0
    assert retrieved_ticker.candles[0].low == 95.0
    assert retrieved_ticker.candles[0].close == 102.0
    assert retrieved_ticker.candles[0].volume == 1000
