from backlive.application.handler import (
    BacktestHandler,
    BacktestResultHandler,
    DownloadCandleHandler,
    ExecutionHandler,
    OrderFilledHandler,
    PlaceOrderHandler,
)
from backlive.application.message_bus import InMemoryMessageBus
from backlive.domain.commands import DownloadCandleCommand, PlaceOrderCommand, RunBacktestCommand
from backlive.domain.events import BacktestCompletedEvent, CandleReceivedEvent, OrderFilledEvent
from backlive.domain.models import Portfolio
from backlive.infrastructure.database.unit_of_work import UnitOfWork
from backlive.infrastructure.feed.base import IFeed
from backlive.infrastructure.feed.local_database import LocalDatabaseFeed


def bootstrap(url: str, feed: IFeed) -> InMemoryMessageBus:
    message_bus = InMemoryMessageBus()

    portfolio = Portfolio(balance=10000, positions={})

    # Command Handlers
    download_candle_handler = DownloadCandleHandler(UnitOfWork(url), feed, message_bus=message_bus)

    place_order_handler = PlaceOrderHandler(UnitOfWork(url), message_bus)
    order_filled_handler = OrderFilledHandler(UnitOfWork(url), message_bus, portfolio)
    execution_handler = ExecutionHandler(UnitOfWork(url), message_bus)
    backtest_handler = BacktestHandler(UnitOfWork(url), LocalDatabaseFeed(url), message_bus, portfolio)
    backtest_result_handler = BacktestResultHandler()

    # Register Handlers
    message_bus.register_handler(DownloadCandleCommand, download_candle_handler.handle)

    message_bus.register_handler(PlaceOrderCommand, place_order_handler.handle)
    message_bus.register_handler(CandleReceivedEvent, execution_handler.handle)
    message_bus.register_handler(OrderFilledEvent, order_filled_handler.handle)
    message_bus.register_handler(RunBacktestCommand, backtest_handler.handle)
    message_bus.register_handler(BacktestCompletedEvent, backtest_result_handler.handle)

    return message_bus
