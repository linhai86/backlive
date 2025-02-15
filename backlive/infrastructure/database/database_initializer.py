from sqlalchemy import create_engine

from .models import Base


class DatabaseInitializer:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=True)

    def initialize_database(self) -> None:
        Base.metadata.create_all(self.engine)
