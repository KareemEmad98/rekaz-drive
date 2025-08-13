from __future__ import annotations
from typing import Protocol, Optional

from app.domain.entities.blob_metadata import BlobMeta


class MetadataRepository(Protocol):
    def create(self, meta: BlobMeta) -> None: ...

    def get(self, blob_id: str) -> Optional[BlobMeta]: ...

    def exists(self, blob_id: str) -> bool: ...
