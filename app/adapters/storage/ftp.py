from __future__ import annotations
import hashlib, io, os
from ftplib import FTP, FTP_TLS, error_perm
from typing import Tuple
from datetime import datetime, timezone

from app.infra.errors import NotFound, Conflict
from app.infra.settings import Settings

class FtpStorage:
    def __init__(self, settings: Settings):
        self.host = settings.ftp_host
        self.port = settings.ftp_port
        self.user = settings.ftp_user
        self.password = settings.ftp_password
        self.tls = bool(settings.ftp_tls)
        self.base_dir = settings.ftp_base_dir or "/"
        self.timeout = float(settings.ftp_timeout)

    def _connect(self):
        ftp = FTP_TLS(timeout=self.timeout) if self.tls else FTP(timeout=self.timeout)
        ftp.connect(self.host, self.port)
        if isinstance(ftp, FTP_TLS):
            ftp.login(self.user, self.password)
            ftp.prot_p()
        else:
            ftp.login(self.user, self.password)

        ftp.set_pasv(True)
        if self.base_dir and self.base_dir != "/":
            ftp.cwd(self.base_dir)
        return ftp

    def _final_path(self, blob_id: str) -> str:
        h = hashlib.sha256(blob_id.encode("utf-8")).hexdigest()
        return f"data/{h[:2]}/{h[2:4]}/{h}__{blob_id}"

    def _ensure_dirs(self, ftp: FTP, path: str) -> None:
        parts = path.split("/")[:-1]
        cur = ""
        for p in parts:
            if not p:
                continue
            cur = f"{cur}/{p}" if cur else p
            try:
                ftp.mkd(cur)
            except error_perm as e:
                if not str(e).startswith("550"):
                    raise

    def save(self, blob_id: str, data: bytes) -> Tuple[int, datetime]:
        key = self._final_path(blob_id)
        ftp = self._connect()
        try:
            try:
                ftp.size(key)
                raise Conflict(f"Blob '{blob_id}' already exists")
            except error_perm as e:
                if not str(e).startswith("550"):
                    raise

            self._ensure_dirs(ftp, key)

            rnd = hashlib.md5(os.urandom(16)).hexdigest()
            tmp = f"{key}.tmp-{rnd}"

            buf = io.BytesIO(data)
            ftp.storbinary(f"STOR {tmp}", buf)

            try:
                ftp.rename(tmp, key)
            except Exception:
                try:
                    ftp.delete(tmp)
                except Exception:
                    pass
                raise

            return len(data), datetime.now(timezone.utc)
        finally:
            try:
                ftp.quit()
            except Exception:
                try:
                    ftp.close()
                except Exception:
                    pass

    def get(self, blob_id: str) -> Tuple[bytes, int, datetime]:
        key = self._final_path(blob_id)
        ftp = self._connect()
        try:
            try:
                size = ftp.size(key)
            except error_perm as e:
                if str(e).startswith("550"):
                    raise NotFound(f"Blob '{blob_id}' not found")
                raise

            created_at = datetime.now(timezone.utc)
            try:
                resp = ftp.sendcmd(f"MDTM {key}")
                if resp.startswith("213 "):
                    ts = resp.split()[1]
                    created_at = datetime.strptime(ts, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            except Exception:
                pass

            buf = io.BytesIO()
            ftp.retrbinary(f"RETR {key}", buf.write)
            data = buf.getvalue()
            return data, (size if isinstance(size, int) else len(data)), created_at
        finally:
            try:
                ftp.quit()
            except Exception:
                try:
                    ftp.close()
                except Exception:
                    pass

    def delete(self, blob_id: str) -> None:
        key = self._final_path(blob_id)
        ftp = self._connect()
        try:
            try:
                ftp.delete(key)
            except error_perm as e:
                if not str(e).startswith("550"):
                    raise
        finally:
            try:
                ftp.quit()
            except Exception:
                try:
                    ftp.close()
                except Exception:
                    pass
