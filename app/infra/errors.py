from fastapi import status
from fastapi.responses import JSONResponse


class AppError(Exception):
    code = "app_error"
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BadRequest(AppError):
    code = "bad_request"
    http_status = status.HTTP_400_BAD_REQUEST


class NotFound(AppError):
    code = "not_found"
    http_status = status.HTTP_404_NOT_FOUND


class Conflict(AppError):
    code = "conflict"
    http_status = status.HTTP_409_CONFLICT


def app_error_handler(_, exc: AppError):
    return JSONResponse(
        status_code=exc.http_status, content={"error": exc.code, "message": exc.message}
    )
