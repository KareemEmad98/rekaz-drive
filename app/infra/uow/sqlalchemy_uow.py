from __future__ import annotations
from sqlalchemy.orm import Session


class SqlAlchemyUnitOfWork:

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def commit(self) -> None:
        self.session.flush()

    def rollback(self) -> None:
        self.session.rollback()
