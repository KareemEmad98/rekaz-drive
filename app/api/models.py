from pydantic import BaseModel, Field


class BlobIn(BaseModel):
    id: str = Field(min_length=1, max_length=512)
    data: str


class BlobOut(BaseModel):
    id: str
    data: str
    size: int
    created_at: str
