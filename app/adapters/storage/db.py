from __future__ import annotations
from typing import Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.infra.repositories.blob_data.models import BlobDataModel
from app.infra.errors import NotFound, Conflict


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


class DbBlobStorage:
    def __init__(self, session: Session):
        self.session = session

    def save(self, blob_id: str, data: bytes) -> Tuple[int, str]:
        now = datetime.now(timezone.utc)
        try:
            with self.session.begin_nested():
                if self.session.get(BlobDataModel, blob_id) is not None:
                    raise Conflict(f"Blob '{blob_id}' already exists")

                self.session.add(BlobDataModel(id=blob_id, data=data, created_at=now))
                self.session.flush()
        except IntegrityError:
            raise Conflict(f"Blob '{blob_id}' already exists")

        return len(data), _iso(now)

    def get(self, blob_id: str) -> Tuple[bytes, int, str]:
        row = self.session.get(BlobDataModel, blob_id)
        if row is None:
            raise NotFound(f"Blob '{blob_id}' not found")
        return row.data, len(row.data), _iso(row.created_at)

    def delete(self, blob_id: str) -> None:
        row = self.session.get(BlobDataModel, blob_id)
        if row:
            self.session.delete(row)
