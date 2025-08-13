from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timezone
from typing import Any

from app.domain.ports.storage import StoragePort
from app.domain.ports.metadata_repo import MetadataRepository, BlobMeta
from app.infra.errors import BadRequest, NotFound, Conflict


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _decode_base64(b64: str) -> bytes:
    try:
        return base64.b64decode(b64, validate=True)
    except Exception:
        raise BadRequest("Invalid base64 'data'")


def _to_datetime(val: Any) -> datetime:
    if isinstance(val, datetime):
        return val.astimezone(timezone.utc)
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return _utc_now()


class BlobService:
    def __init__(
        self,
        storage: StoragePort,
        meta_repo: MetadataRepository,
        backend_name: str,
        uow=None,
    ):
        self.storage = storage
        self.meta = meta_repo
        self.backend = backend_name
        self.uow = uow

    def save(self, blob_id: str, b64: str) -> dict:
        if self.meta.exists(blob_id):
            raise Conflict(f"Blob '{blob_id}' already exists")

        raw = _decode_base64(b64)
        checksum = hashlib.sha256(raw).hexdigest()

        size, created_at_val = self.storage.save(blob_id, raw)
        created_at = _to_datetime(created_at_val)

        meta = BlobMeta(
            id=blob_id,
            size=size,
            created_at=created_at,
            backend=self.backend,
            checksum=checksum,
        )

        def _write_meta() -> None:
            self.meta.create(meta)

        if self.uow:
            with self.uow:
                try:
                    _write_meta()
                    self.uow.commit()
                except Exception:
                    self.uow.rollback()
                    try:
                        self.storage.delete(blob_id)
                    except Exception:
                        pass
                    raise
        else:
            try:
                _write_meta()
            except Exception:
                try:
                    self.storage.delete(blob_id)
                except Exception:
                    pass
                raise

        return {
            "id": blob_id,
            "data": b64,
            "size": size,
            "created_at": created_at.replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        }

    def get(self, blob_id: str) -> dict:
        meta = self.meta.get(blob_id)
        if not meta:
            raise NotFound(f"Blob '{blob_id}' not found")
        data, size, _created_at_val = self.storage.get(blob_id)
        return {
            "id": blob_id,
            "data": base64.b64encode(data).decode("ascii"),
            "size": size,
            "created_at": meta.created_at.replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        }
