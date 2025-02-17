from datetime import datetime

from backlive.domain.models import Candle

from .conftest import FakeUnitOfWork


def test_add_candles(fake_uow: FakeUnitOfWork) -> None:
    """Test adding candles to a ticker."""
    timestamp = datetime.now()
    candle = Candle(symbol="AAPL", timestamp=timestamp, open=100.0, high=105.0, low=95.0, close=102.0, volume=1000)
    fake_uow.candle_repository.add_candles([candle])

    retrieved_candles = fake_uow.candle_repository.get_candles("AAPL")
    assert retrieved_candles is not None
    assert len(retrieved_candles) == 1
    assert retrieved_candles[0].symbol == "AAPL"
    assert retrieved_candles[0].timestamp == timestamp
    assert retrieved_candles[0].open == 100.0
    assert retrieved_candles[0].high == 105.0
    assert retrieved_candles[0].low == 95.0
    assert retrieved_candles[0].close == 102.0
    assert retrieved_candles[0].volume == 1000
