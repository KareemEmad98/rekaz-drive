from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer

from app.infra.db import Base


class BlobMetaModel(Base):
    __tablename__ = "blob_metadata"
    id: Mapped[str] = mapped_column(String(512), primary_key=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    backend: Mapped[str] = mapped_column(String(50), nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
