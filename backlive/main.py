from backlive.feed.yfinance import YFinanceFeed
from backlive.repository.database_initializer import DatabaseInitializer
from backlive.repository.unit_of_work import UnitOfWork
from backlive.service.service import TickerService


def main() -> None:
    DATABASE_URL = "sqlite:///tickers.db"

    db_initializer = DatabaseInitializer(DATABASE_URL)
    db_initializer.initialize_database()

    feed = YFinanceFeed()
    uow = UnitOfWork(DATABASE_URL)

    ticker_service = TickerService(uow, feed)
    ticker = ticker_service.fetch_and_save_candles("AAPL")
    print(f"Saved ticker: {ticker.symbol} with {len(ticker.candles)} candle records")


if __name__:
    main()
