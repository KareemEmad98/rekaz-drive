from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session

from app.domain.entities.blob_metadata import BlobMeta
from .models import BlobMetaModel
from app.infra.errors import Conflict


class SqlAlchemyMetadataRepository:
    def __init__(self, session: Session):
        self.session = session

    def exists(self, blob_id: str) -> bool:
        return self.session.get(BlobMetaModel, blob_id) is not None

    def create(self, meta: BlobMeta) -> None:
        if self.exists(meta.id):
            raise Conflict(f"Blob '{meta.id}' already exists")
        row = BlobMetaModel(
            id=meta.id,
            size=meta.size,
            created_at=meta.created_at,
            backend=meta.backend,
            checksum=meta.checksum,
        )
        self.session.add(row)
        self.session.flush()

    def get(self, blob_id: str) -> Optional[BlobMeta]:
        row = self.session.get(BlobMetaModel, blob_id)
        if not row:
            return None
        return BlobMeta(
            id=row.id,
            size=row.size,
            created_at=row.created_at,
            backend=row.backend,
            checksum=row.checksum,
        )
