from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Status = Literal["PENDING", "COMMITTED", "FAILED"]


@dataclass
class BlobMeta:
    id: str
    size: int
    created_at: datetime
    backend: str
    checksum: str
