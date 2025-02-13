from types import TracebackType
from typing import Self

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .repository import SQLAlchemyTickerRepository


class UnitOfWork:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)

    def __enter__(self) -> Self:
        self.session = self.Session()
        self.repository = SQLAlchemyTickerRepository(self.session)
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool | None:
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
        return None

    def commit(self) -> None:
        self.session.commit()
