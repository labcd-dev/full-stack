"""Public error tracking endpoints (config + frontend report)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status

from backend_api.db.models import User
from backend_api.http.dependencies import get_optional_user
from backend_api.http.schemas.error_tracking import ErrorReportRequest, ErrorTrackingSettings
from backend_api.http.services import error_tracking_service

router = APIRouter(prefix="/errors", tags=["errors"])


@router.get("/config", response_model=ErrorTrackingSettings)
def get_error_tracking_config() -> ErrorTrackingSettings:
    cfg = error_tracking_service.get_cached_config()
    return ErrorTrackingSettings(
        enabled=cfg.enabled,
        frontend=cfg.frontend,
        backend=cfg.backend,
        api=cfg.api,
    )


@router.post("/report", status_code=status.HTTP_204_NO_CONTENT)
def report_frontend_error(
    body: ErrorReportRequest,
    request: Request,
    user: User | None = Depends(get_optional_user),
) -> Response:
    if not error_tracking_service.should_track("frontend"):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    error_tracking_service.record_error_best_effort(
        source="frontend",
        message=body.message,
        stack_trace=body.stack_trace,
        path=body.path,
        method=body.method,
        status_code=body.status_code,
        user_id=user.id if user else None,
        user_agent=request.headers.get("user-agent"),
        page_url=body.page_url,
        extra=body.extra,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
