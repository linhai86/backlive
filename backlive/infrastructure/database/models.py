from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


@dataclass
class Base(DeclarativeBase):
    pass


@dataclass
class TickerModel(Base):
    """SQLAlchemy model for the Stock entity."""

    __tablename__ = "ticker"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    candles: Mapped[list["CandleModel"]] = relationship(back_populates="ticker")


@dataclass
class CandleModel(Base):
    __tablename__ = "candle"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False, index=True)
    open: Mapped[float] = mapped_column(nullable=False)
    high: Mapped[float] = mapped_column(nullable=False)
    low: Mapped[float] = mapped_column(nullable=False)
    close: Mapped[float] = mapped_column(nullable=False)
    volume: Mapped[float] = mapped_column(nullable=False)

    ticker: Mapped["TickerModel"] = relationship(back_populates="candles")

    __table_args__ = (UniqueConstraint("ticker_id", "timestamp"),)


class OrderData(Base):
    __tablename__ = "order"

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(nullable=False)
    order_type: Mapped[int] = mapped_column(nullable=False)
    side: Mapped[int] = mapped_column(nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=True)  # Limit price
    status: Mapped[int] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)


class PositionData(Base):
    __tablename__ = "position"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    average_price: Mapped[float] = mapped_column(nullable=False)
