from __future__ import annotations
import os, uuid
from pathlib import Path
from typing import Tuple
from datetime import datetime, timezone
from app.infra.errors import Conflict, NotFound


class LocalFsStorage:
    def __init__(self, root: str):
        self.root = Path(root)

    def _final_path(self, blob_id: str) -> Path:
        p = self.root / blob_id
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def save(self, blob_id: str, data: bytes) -> Tuple[int, datetime]:
        final_path = self._final_path(blob_id)
        if final_path.exists():
            raise Conflict(f"Blob '{blob_id}' already exists")

        tmp_path = final_path.with_suffix(final_path.suffix + f".tmp.{uuid.uuid4().hex}")
        with open(tmp_path, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, final_path)
        created_at = datetime.now(timezone.utc)
        return len(data), created_at

    def get(self, blob_id: str) -> Tuple[bytes, int, datetime]:
        p = self._final_path(blob_id)
        if not p.exists():
            raise NotFound(f"Blob '{blob_id}' not found")
        b = p.read_bytes()
        st = p.stat()
        created_at = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
        return b, len(b), created_at

    def delete(self, blob_id: str) -> None:
        p = self._final_path(blob_id)
        if p.exists():
            p.unlink()
