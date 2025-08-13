from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.storage.db import DbBlobStorage
from app.adapters.storage.ftp import FtpStorage
from app.adapters.storage.local_fs import LocalFsStorage
from app.adapters.storage.s3 import S3HttpStorage

from app.infra.db import Base, make_engine, make_session_factory
from app.infra.settings import get_settings, Settings
from app.infra.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.infra.repositories.metadata.repository import SqlAlchemyMetadataRepository
from app.domain.services.blob_service import BlobService

_engine = None
_SessionFactory: sessionmaker | None = None
_bootstrapped = False


def _bootstrap_db(database_url: str) -> None:
    global _engine, _SessionFactory, _bootstrapped
    if _engine is None:
        _engine = make_engine(database_url)
        _SessionFactory = make_session_factory(_engine)

    if not _bootstrapped:
        Base.metadata.create_all(bind=_engine)
        _bootstrapped = True


def get_session(settings: Settings = Depends(get_settings)):
    _bootstrap_db(settings.database_url)
    session: Session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_storage(
    settings: Settings = Depends(get_settings), session: Session = Depends(get_session)
):
    backend = (
        getattr(settings, "active_backend", None) or getattr(settings, "storage", "fs")
    ).lower()
    if backend == "fs":
        return LocalFsStorage(settings.fs_base_path)
    if backend == "db":
        return DbBlobStorage(session)
    if backend == "s3":
        return S3HttpStorage(settings)
    if backend == "ftp":
        return FtpStorage(settings)
    raise ValueError(f"Unsupported backend: {backend!r}")


def get_blob_service(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
    storage=Depends(get_storage),
) -> BlobService:
    meta_repo = SqlAlchemyMetadataRepository(session)
    uow = SqlAlchemyUnitOfWork(session) if settings.storage.lower() == "db" else None
    return BlobService(
        storage=storage,
        meta_repo=meta_repo,
        backend_name=settings.storage,
        uow=uow,
    )
