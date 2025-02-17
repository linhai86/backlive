from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self, override

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .repository import ICandleRepository, IOrderRepository, SQLAlchemyCandleRepository, SQLAlchemyOrderRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def candle_repository(self) -> ICandleRepository:
        pass

    @property
    @abstractmethod
    def order_repository(self) -> IOrderRepository:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        pass


class UnitOfWork(IUnitOfWork):
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session: Session | None = None
        self._candle_repository: SQLAlchemyCandleRepository | None = None
        self._order_repository: SQLAlchemyOrderRepository | None = None

    @override
    @property
    def candle_repository(self) -> SQLAlchemyCandleRepository:
        if self._candle_repository is None:
            raise ValueError("UnitOfWork has not been entered.")
        return self._candle_repository

    @override
    @property
    def order_repository(self) -> SQLAlchemyOrderRepository:
        if self._order_repository is None:
            raise ValueError("UnitOfWork has not been entered.")
        return self._order_repository

    @override
    def __enter__(self) -> Self:
        self.session = self.Session()
        self._candle_repository = SQLAlchemyCandleRepository(self.session)
        self._order_repository = SQLAlchemyOrderRepository(self.session)
        return self

    @override
    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.session is not None:
            if exc_type:
                self.rollback()
            else:
                self.commit()
            self.session.close()

    @override
    def commit(self) -> None:
        if self.session is not None:
            self.session.commit()

    @override
    def rollback(self) -> None:
        if self.session is not None:
            self.session.rollback()
