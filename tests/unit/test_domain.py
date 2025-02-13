from datetime import datetime

from backlive.domain.models import Candle, Ticker


def test_ticker_creation() -> None:
    """Test the creation of a Ticker domain model."""
    ticker = Ticker(symbol="AAPL", name="Apple Inc.", candles=[])
    assert ticker.symbol == "AAPL"
    assert ticker.name == "Apple Inc."
    assert len(ticker.candles) == 0


def test_candle_creation() -> None:
    """Test the creation of an Candle domain model."""
    timestamp = datetime.now()
    candle = Candle(timestamp=timestamp, open=100.0, high=105.0, low=95.0, close=102.0, volume=1000)
    assert candle.timestamp == timestamp
    assert candle.open == 100.0
    assert candle.high == 105.0
    assert candle.low == 95.0
    assert candle.close == 102.0
    assert candle.volume == 1000
