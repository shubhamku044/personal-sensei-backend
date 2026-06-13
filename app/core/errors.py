"""Application error hierarchy and FastAPI exception handlers.

Raise these from any layer (services, repositories, agents). The registered
handlers translate them into consistent JSON error responses, so route
handlers never have to build error responses by hand.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger("app.errors")


class ErrorResponse(BaseModel):
    """Wire format for every error the API returns."""

    code: str
    message: str
    details: dict[str, Any] = {}


class AppError(Exception):
    """Base class for all expected, domain-level application errors.

    Subclass it to add new failure modes; set the class attributes to control
    the HTTP status, the stable machine-readable ``code`` and the default
    message. Pass ``details`` for structured, per-instance context.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Create an error, optionally overriding the default message/details."""
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)

    def to_response(self) -> ErrorResponse:
        """Build the response body for this error."""
        return ErrorResponse(code=self.code, message=self.message, details=self.details)


class NotFoundError(AppError):
    """A requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "The requested resource was not found."


class ValidationError(AppError):
    """The request was structurally valid but failed business rules."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "validation_error"
    message = "The request was invalid."


class ConflictError(AppError):
    """The request conflicts with the current state of a resource."""

    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    message = "The request conflicts with the current state."


class UnauthorizedError(AppError):
    """Authentication is missing or invalid."""

    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    message = "Authentication is required."


class ForbiddenError(AppError):
    """The caller is authenticated but not allowed to perform the action."""

    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"
    message = "You do not have permission to perform this action."


class ExternalServiceError(AppError):
    """A downstream dependency (LLM, datastore, ...) failed."""

    status_code = status.HTTP_502_BAD_GATEWAY
    code = "external_service_error"
    message = "An upstream service failed to respond."


def register_exception_handlers(app: FastAPI) -> None:
    """Wire the application's exception handlers onto ``app``."""

    @app.exception_handler(AppError)
    async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        log = (
            logger.warning
            if exc.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR
            else logger.error
        )
        log(
            "%s %s -> %d %s: %s",
            request.method,
            request.url.path,
            exc.status_code,
            exc.code,
            exc.message,
        )
        return JSONResponse(status_code=exc.status_code, content=exc.to_response().model_dump())

    @app.exception_handler(RequestValidationError)
    async def _handle_request_validation(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning("%s %s -> 422 request validation", request.method, request.url.path)
        body = ErrorResponse(
            code="request_validation_error",
            message="Request validation failed.",
            details={"errors": exc.errors()},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=body.model_dump(),
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("%s %s -> 500 unhandled: %r", request.method, request.url.path, exc)
        body = ErrorResponse(code="internal_error", message="An unexpected error occurred.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=body.model_dump(),
        )
