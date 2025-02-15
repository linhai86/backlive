from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self, override

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .repository import ITickerRepository, SQLAlchemyTickerRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def repository(self) -> ITickerRepository:
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
        self._repository: SQLAlchemyTickerRepository | None = None

    @override
    @property
    def repository(self) -> SQLAlchemyTickerRepository:
        if self._repository is None:
            raise ValueError("UnitOfWork has not been entered.")
        return self._repository

    @override
    def __enter__(self) -> Self:
        self.session = self.Session()
        self._repository = SQLAlchemyTickerRepository(self.session)
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
