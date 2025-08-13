from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from typing import Tuple
from urllib.parse import quote
from email.utils import parsedate_to_datetime

import httpx
from app.infra.http.s3_sign import sign_v4, sha256_hex
from app.infra.settings import Settings
from app.infra.errors import NotFound, Conflict


def _encode_key(k: str) -> str:
    return quote(k, safe="/-_.~")


class S3HttpStorage:
    def __init__(self, settings: Settings):
        if not settings.s3_endpoint or not settings.s3_bucket:
            raise ValueError("S3 endpoint/bucket must be configured")

        self.endpoint = settings.s3_endpoint.rstrip("/")
        self.region = settings.s3_region
        self.bucket = settings.s3_bucket
        self.ak = settings.s3_access_key
        self.sk = settings.s3_secret_key
        self.st = settings.s3_session_token or ""
        self.path_style = bool(settings.s3_force_path_style)

        self.client = httpx.Client(timeout=10.0)

    def _bucket_base(self) -> str:
        if self.path_style:
            return f"{self.endpoint}/{self.bucket}"
        if "://" in self.endpoint:
            scheme, rest = self.endpoint.split("://", 1)
            return f"{scheme}://{self.bucket}.{rest}"
        return f"https://{self.bucket}.{self.endpoint}"

    def _final_key(self, blob_id: str) -> str:
        h = hashlib.sha256(blob_id.encode("utf-8")).hexdigest()
        return f"data/{h[:2]}/{h[2:4]}/{h}__{blob_id}"

    def _exists(self, key: str) -> bool:
        url = f"{self._bucket_base()}/{_encode_key(key)}"
        signed = sign_v4("HEAD", url, self.region, self.ak, self.sk, self.st)
        r = self.client.request("HEAD", url, headers=signed)
        if r.status_code == 404:
            return False
        if r.status_code >= 300:
            raise RuntimeError(f"S3 HEAD failed {r.status_code}: {r.text}")
        return True

    def save(self, blob_id: str, data: bytes) -> Tuple[int, datetime]:
        key = self._final_key(blob_id)
        if self._exists(key):
            raise Conflict(f"Blob '{blob_id}' already exists")

        url = f"{self._bucket_base()}/{_encode_key(key)}"
        payload_hash = sha256_hex(data)
        headers = {
            "content-type": "application/octet-stream",
            "content-length": str(len(data)),
        }
        signed = sign_v4("PUT", url, self.region, self.ak, self.sk, self.st, headers, payload_hash)
        r = self.client.put(url, content=data, headers=signed)
        if r.status_code >= 300:
            raise RuntimeError(f"S3 PUT failed {r.status_code}: {r.text}")

        return len(data), datetime.now(timezone.utc)

    def get(self, blob_id: str) -> Tuple[bytes, int, datetime]:
        key = self._final_key(blob_id)
        url = f"{self._bucket_base()}/{_encode_key(key)}"
        signed = sign_v4("GET", url, self.region, self.ak, self.sk, self.st)
        r = self.client.get(url, headers=signed)
        if r.status_code == 404:
            raise NotFound(f"Blob '{blob_id}' not found")
        if r.status_code >= 300:
            raise RuntimeError(f"S3 GET failed {r.status_code}: {r.text}")

        b = r.content
        lm_hdr = r.headers.get("Last-Modified")
        if lm_hdr:
            try:
                created_at = parsedate_to_datetime(lm_hdr)
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                else:
                    created_at = created_at.astimezone(timezone.utc)
            except Exception:
                created_at = datetime.now(timezone.utc)
        else:
            created_at = datetime.now(timezone.utc)

        return b, len(b), created_at

    def delete(self, blob_id: str) -> None:
        key = self._final_key(blob_id)
        url = f"{self._bucket_base()}/{_encode_key(key)}"
        signed = sign_v4("DELETE", url, self.region, self.ak, self.sk, self.st)
        r = self.client.delete(url, headers=signed)
        if r.status_code not in (200, 202, 204, 404):
            raise RuntimeError(f"S3 DELETE failed {r.status_code}: {r.text}")
