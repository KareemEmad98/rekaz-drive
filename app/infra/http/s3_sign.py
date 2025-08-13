from __future__ import annotations
import datetime, hashlib, hmac
from urllib.parse import urlparse, quote
from typing import Dict, Tuple

_ALGO = "AWS4-HMAC-SHA256"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _amz_dates(region: str, service: str = "s3") -> Tuple[str, str, str]:
    now = datetime.datetime.utcnow()
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    scope = f"{datestamp}/{region}/{service}/aws4_request"
    return amz_date, datestamp, scope


def _canonical_uri(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return quote(path, safe="/-_.~")


def _canonical_headers(headers: Dict[str, str]) -> Tuple[str, str]:
    items = [
        (k.lower().strip(), " ".join(v.strip().split())) for k, v in headers.items()
    ]
    items.sort()
    return "".join(f"{k}:{v}\n" for k, v in items), ";".join(k for k, _ in items)


def _hmac(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _signing_key(
    secret: str, datestamp: str, region: str, service: str = "s3"
) -> bytes:
    k_date = _hmac(("AWS4" + secret).encode(), datestamp)
    k_region = hmac.new(k_date, region.encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service.encode(), hashlib.sha256).digest()
    return hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()


def sign_v4(
    method: str,
    url: str,
    region: str,
    access_key: str,
    secret_key: str,
    session_token: str = "",
    extra_headers: Dict[str, str] | None = None,
    payload_hash: str = "UNSIGNED-PAYLOAD",
) -> Dict[str, str]:
    extra_headers = extra_headers or {}
    u = urlparse(url)
    host = u.netloc
    amz_date, datestamp, scope = _amz_dates(region)

    headers = {
        "host": host,
        "x-amz-date": amz_date,
        "x-amz-content-sha256": payload_hash,
        **extra_headers,
    }
    if session_token:
        headers["x-amz-security-token"] = session_token

    canonical_request = "\n".join(
        [
            method.upper(),
            _canonical_uri(u.path or "/"),
            "",
            *_canonical_headers(headers),
            payload_hash,
        ]
    )

    string_to_sign = "\n".join(
        [
            _ALGO,
            amz_date,
            scope,
            hashlib.sha256(canonical_request.encode()).hexdigest(),
        ]
    )

    signing_key = _signing_key(secret_key, datestamp, region)
    signature = hmac.new(
        signing_key, string_to_sign.encode(), hashlib.sha256
    ).hexdigest()

    headers["Authorization"] = (
        f"{_ALGO} Credential={access_key}/{scope}, "
        f"SignedHeaders={_canonical_headers(headers)[1]}, "
        f"Signature={signature}"
    )
    return headers
