from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import override

from sqlalchemy import desc, insert, select
from sqlalchemy.orm import Session

from ...domain.models import Candle, Order, OrderSide, OrderStatus, OrderType
from .models import CandleModel, OrderData, TickerModel


class ICandleRepository(ABC):
    @abstractmethod
    def get_candles(self, symbol: str) -> list[Candle]:
        pass

    @abstractmethod
    def get_latest_candle(self, symbol: str) -> Candle | None:
        pass

    @abstractmethod
    def add_candles(self, candles: list[Candle]) -> None:
        pass


class SQLAlchemyCandleRepository(ICandleRepository):
    def __init__(self, session: Session):
        self.session = session

    @override
    def get_candles(self, symbol: str) -> list[Candle]:
        ticker_model = self.session.scalars(select(TickerModel).where(TickerModel.symbol == symbol)).one_or_none()
        if ticker_model:
            candles = [
                Candle(
                    symbol=ticker_model.symbol,
                    timestamp=candle.timestamp,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume,
                )
                for candle in ticker_model.candles
            ]
            return candles
        return []

    @override
    def get_latest_candle(self, symbol: str) -> Candle | None:
        candle_model = self.session.scalars(
            select(CandleModel)
            .join(CandleModel.ticker)
            .where(TickerModel.symbol == symbol)
            .order_by(desc(CandleModel.timestamp))
            .limit(1)
        ).one_or_none()
        if candle_model:
            return Candle(
                symbol=symbol,
                timestamp=candle_model.timestamp,
                open=candle_model.open,
                high=candle_model.high,
                low=candle_model.low,
                close=candle_model.close,
                volume=candle_model.volume,
            )
        return None

    @override
    def add_candles(self, candles: list[Candle]) -> None:
        symbols = {candle.symbol for candle in candles}

        stmt = select(TickerModel).where(TickerModel.symbol.in_(symbols))
        existing_tickers = self.session.scalars(stmt).all()
        ticker_map: dict[str, TickerModel] = {ticker.symbol: ticker for ticker in existing_tickers}

        # For symbols not found in the database, create new TickerModel entries.
        missing_symbols = symbols - ticker_map.keys()
        new_tickers = []
        for symbol in missing_symbols:
            # Create a new ticker. Here, we use the symbol as the name by default.
            new_ticker = TickerModel(symbol=symbol, name=symbol)
            self.session.add(new_ticker)
            new_tickers.append(new_ticker)

        # Flush to assign ids to new tickers.
        if new_tickers:
            self.session.flush()
            for ticker in new_tickers:
                ticker_map[ticker.symbol] = ticker

        # Convert each domain Candle into a CandleModel
        data = [dict(**asdict(candle), ticker_id=ticker_map[candle.symbol].id) for candle in candles]
        self.session.execute(insert(CandleModel), data)


class IOrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> None:
        pass

    @abstractmethod
    def get(self, order_id: int) -> Order | None:
        pass

    @abstractmethod
    def list_pending(self) -> list[Order]:
        pass


class SQLAlchemyOrderRepository(IOrderRepository):
    def __init__(self, session: Session):
        self.session = session

    @override
    def add(self, order: Order) -> None:
        if not order.order_id:
            self.session.add(
                OrderData(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    price=order.price,
                    order_type=order.order_type.value,
                    side=order.side.value,
                    status=order.status.value,
                    timestamp=order.timestamp,
                )
            )
        else:
            # When order_id is provided, update the order in the database
            order_data = self.session.scalars(select(OrderData).where(OrderData.order_id == order.order_id)).one()
            order_data.status = order.status.value

    @override
    def get(self, order_id: int) -> Order | None:
        order_data = self.session.scalars(select(OrderData).where(OrderData.order_id == order_id)).one_or_none()
        if order_data:
            return Order(
                symbol=order_data.symbol,
                quantity=order_data.quantity,
                price=order_data.price,
                order_type=OrderType(order_data.order_type),
                side=OrderSide(order_data.side),
                status=OrderStatus(order_data.status),
                order_id=order_data.order_id,
                timestamp=order_data.timestamp,
            )
        return None

    @override
    def list_pending(self) -> list[Order]:
        orders = self.session.scalars(select(OrderData).where(OrderData.status == OrderStatus.PENDING.value)).all()
        return [
            Order(
                symbol=order.symbol,
                quantity=order.quantity,
                price=order.price,
                order_type=OrderType(order.order_type),
                side=OrderSide(order.side),
                status=OrderStatus(order.status),
                order_id=order.order_id,
                timestamp=order.timestamp,
            )
            for order in orders
        ]
