from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.infra.settings import settings

bearer = HTTPBearer(auto_error=True)


def require_auth(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> None:
    if creds.credentials != settings.auth_bearer_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
