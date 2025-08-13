from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies import get_blob_service
from app.api.models import BlobIn, BlobOut
from app.api.auth import require_auth
from app.domain.services.blob_service import BlobService

router = APIRouter(prefix="/v1/blobs", tags=["blobs"])


@router.post(
    "",
    response_model=BlobOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_auth)],
)
def store_blob(body: BlobIn, svc: BlobService = Depends(get_blob_service)):
    return svc.save(body.id, body.data)


@router.get(
    "/{blob_id:path}", response_model=BlobOut, dependencies=[Depends(require_auth)]
)
def get_blob(blob_id: str, svc: BlobService = Depends(get_blob_service)):
    return svc.get(blob_id)
