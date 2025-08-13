from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, LargeBinary, DateTime

from app.infra.db import Base


def _utcnow():
    return datetime.now(timezone.utc)


class BlobDataModel(Base):
    __tablename__ = "blob_data"
    id: Mapped[str] = mapped_column(String(512), primary_key=True)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
