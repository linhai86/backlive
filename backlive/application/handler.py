from ..domain.commands import DownloadCandleCommand, PlaceOrderCommand, RunBacktestCommand
from ..domain.events import (
    BacktestCompletedEvent,
    CandleDownloadedEvent,
    CandleReceivedEvent,
    OrderFilledEvent,
    OrderPlacedEvent,
)
from ..domain.models import Order, OrderSide, OrderStatus, OrderType, Portfolio
from ..infrastructure.database.unit_of_work import IUnitOfWork
from ..infrastructure.feed.base import IFeed
from .message_bus import InMemoryMessageBus
from .strategy import MovingAverageCrossoverStrategy


class DownloadCandleHandler:
    def __init__(self, uow: IUnitOfWork, feed: IFeed, message_bus: InMemoryMessageBus):
        self.uow = uow
        self.feed = feed
        self.message_bus = message_bus

    def handle(self, command: DownloadCandleCommand) -> None:
        candles = self.feed.fetch_candles(command.symbols, command.start, command.end, command.interval, command.limit)

        with self.uow:
            self.uow.candle_repository.add_candles([record for records in candles.values() for record in records])

            self.uow.commit()

        self.message_bus.handle(CandleDownloadedEvent(candles=candles))


class PlaceOrderHandler:
    def __init__(self, uow: IUnitOfWork, message_bus: InMemoryMessageBus):
        self.uow = uow
        self.message_bus = message_bus

    def handle(self, command: PlaceOrderCommand) -> None:
        with self.uow:
            order = Order(
                symbol=command.symbol,
                quantity=command.quantity,
                price=command.price,
                order_type=command.order_type,
                side=command.side,
            )

            self.uow.order_repository.add(order)
            self.message_bus.handle(OrderPlacedEvent(order))


class ExecutionHandler:
    def __init__(self, uow: IUnitOfWork, message_bus: InMemoryMessageBus):
        self.uow = uow
        self.message_bus = message_bus

    def handle(self, event: CandleReceivedEvent) -> None:
        with self.uow:
            candle = event.candle
            pending_orders = self.uow.order_repository.list_pending()

            for order in pending_orders:
                if order.status == OrderStatus.PENDING:
                    current_price = candle.close
                    # Check if the order can be filled
                    if order.symbol == candle.symbol and (
                        (order.quantity > 0 and current_price <= order.price)
                        or (order.quantity < 0 and current_price >= order.price)
                    ):
                        order.status = OrderStatus.FILLED
                        self.uow.order_repository.add(order)

                        self.message_bus.handle(OrderFilledEvent(order=order, fill_price=current_price))


class OrderFilledHandler:
    def __init__(self, uow: IUnitOfWork, message_bus: InMemoryMessageBus, portfolio: Portfolio):
        self.uow = uow
        self.message_bus = message_bus
        self.portfolio = portfolio

    def handle(self, event: OrderFilledEvent) -> None:
        with self.uow:
            order = event.order

            self.portfolio.update_position(symbol=order.symbol, quantity=order.quantity, price=event.fill_price)


class BacktestHandler:
    def __init__(self, uow: IUnitOfWork, message_bus: InMemoryMessageBus, portfolio: Portfolio):
        self.uow = uow
        self.message_bus = message_bus
        self.portfolio = portfolio

    def handle(self, command: RunBacktestCommand) -> None:
        with self.uow:
            candles = self.uow.candle_repository.get_candles(command.symbol)

            strategy = MovingAverageCrossoverStrategy(short_window=10, long_window=50)
            for candle in candles:
                self.message_bus.handle(CandleReceivedEvent(candle))

                signal = strategy.generate_signal(candle)
                if signal == OrderSide.BUY:
                    self._place_order(
                        symbol=command.symbol, quantity=1, price=candle.close, order_type=OrderType.LIMIT, side=signal
                    )
                elif signal == OrderSide.SELL:
                    self._place_order(
                        symbol=command.symbol, quantity=-1, price=candle.close, order_type=OrderType.LIMIT, side=signal
                    )
            self.message_bus.handle(BacktestCompletedEvent(self.portfolio))

    def _place_order(self, symbol: str, quantity: float, price: float, order_type: OrderType, side: OrderSide) -> None:
        self.message_bus.handle(
            PlaceOrderCommand(symbol=symbol, quantity=quantity, price=price, order_type=order_type, side=side)
        )


class BacktestResultHandler:
    def handle(self, event: BacktestCompletedEvent) -> None:
        results = event.portfolio.balance
        print("Backtesting Complete. Results:")
        print(results)
