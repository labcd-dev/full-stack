"""CSV exports for admin panel modules."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from backend_api.common.csv_utils import rows_to_csv
from backend_api.db.models import User
from backend_api.http.services import (
    error_tracking_service,
    monitoring_service,
    plan_service,
    project_service,
    survey_service,
)
from backend_api.http.services.profile_service import user_out


def _iso(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat()


def _join(values: list[str] | None) -> str:
    if not values:
        return ""
    return ";".join(values)


def export_users_csv(db: Session) -> str:
    users = db.query(User).order_by(User.email).all()
    fieldnames = [
        "id",
        "email",
        "is_admin",
        "is_active",
        "plan_id",
        "plan_name",
        "modules",
        "created_at",
    ]
    rows = []
    for user in users:
        out = user_out(user)
        rows.append(
            {
                "id": out.id,
                "email": out.email,
                "is_admin": out.is_admin,
                "is_active": out.is_active,
                "plan_id": out.plan_id if out.plan_id is not None else "",
                "plan_name": out.plan_name or "",
                "modules": _join(out.actions),
                "created_at": _iso(out.created_at),
            }
        )
    return rows_to_csv(rows, fieldnames)


def export_plans_csv(db: Session) -> str:
    default_plan = plan_service.get_default_plan(db)
    default_plan_id = default_plan.id if default_plan else None
    fieldnames = [
        "id",
        "name",
        "description",
        "price",
        "is_active",
        "is_default",
        "modules",
        "models",
        "created_at",
    ]
    rows = []
    for plan in plan_service.list_plans(db):
        data = plan_service.plan_out_dict(plan)
        rows.append(
            {
                "id": data["id"],
                "name": data["name"],
                "description": data["description"],
                "price": data["price"],
                "is_active": data["is_active"],
                "is_default": plan.id == default_plan_id,
                "modules": _join(data["actions"]),
                "models": _join(data["models"]),
                "created_at": _iso(data["created_at"]),
            }
        )
    return rows_to_csv(rows, fieldnames)


def export_projects_csv(
    db: Session,
    *,
    user_id: int | None = None,
    pipeline_type: str | None = None,
) -> str:
    projects = project_service.list_all_projects(
        db,
        user_id=user_id,
        pipeline_type=pipeline_type,
    )
    fieldnames = [
        "id",
        "user_id",
        "owner_email",
        "title",
        "pipeline_type",
        "status",
        "file_name",
        "file_type",
        "has_results",
        "job_id",
        "created_at",
        "updated_at",
    ]
    rows = []
    for project in projects:
        data = project_service.project_to_summary(project, include_owner=True)
        rows.append(
            {
                "id": data["id"],
                "user_id": data["user_id"],
                "owner_email": data["owner_email"] or "",
                "title": data["title"],
                "pipeline_type": data["pipeline_type"],
                "status": data["status"],
                "file_name": data["file_name"],
                "file_type": data["file_type"],
                "has_results": data["has_results"],
                "job_id": data["job_id"] or "",
                "created_at": _iso(data["created_at"]),
                "updated_at": _iso(data["updated_at"]),
            }
        )
    return rows_to_csv(rows, fieldnames)


def export_monitoring_csv() -> str:
    snapshot = monitoring_service.collect_snapshot()
    fieldnames = [
        "collected_at",
        "uptime_seconds",
        "cpu_percent",
        "memory_percent",
        "memory_used_bytes",
        "memory_total_bytes",
        "disk_percent",
        "disk_used_bytes",
        "disk_total_bytes",
        "network_sent_rate_bps",
        "network_recv_rate_bps",
        "network_bytes_sent",
        "network_bytes_recv",
        "api_avg_latency_ms",
        "api_p50_latency_ms",
        "api_p95_latency_ms",
        "api_error_rate_percent",
        "api_requests_in_window",
    ]
    rows = []
    for item in snapshot["history"]:
        rows.append(_monitoring_row(item))
    return rows_to_csv(rows, fieldnames)


def _monitoring_row(item: dict[str, Any]) -> dict[str, Any]:
    memory = item["memory"]
    disk = item["disk"]
    network = item["network"]
    api = item["api"]
    return {
        "collected_at": item["collected_at"],
        "uptime_seconds": item["uptime_seconds"],
        "cpu_percent": item["cpu_percent"],
        "memory_percent": memory["percent"],
        "memory_used_bytes": memory["used_bytes"],
        "memory_total_bytes": memory["total_bytes"],
        "disk_percent": disk["percent"],
        "disk_used_bytes": disk["used_bytes"],
        "disk_total_bytes": disk["total_bytes"],
        "network_sent_rate_bps": network["sent_rate_bps"],
        "network_recv_rate_bps": network["recv_rate_bps"],
        "network_bytes_sent": network["bytes_sent"],
        "network_bytes_recv": network["bytes_recv"],
        "api_avg_latency_ms": api["avg_latency_ms"],
        "api_p50_latency_ms": api["p50_latency_ms"],
        "api_p95_latency_ms": api["p95_latency_ms"],
        "api_error_rate_percent": api["error_rate_percent"],
        "api_requests_in_window": api["requests_in_window"],
    }


def _csv_section(name: str, content: str) -> str:
    body = content.strip()
    if not body:
        return f"# section: {name}\n"
    return f"# section: {name}\n{body}\n"


def _overview_summary_csv(db: Session) -> str:
    users = db.query(User).order_by(User.email).all()
    plans = plan_service.list_plans(db)
    projects = project_service.list_all_projects(db)
    default_plan = plan_service.get_default_plan(db)
    active_users = sum(1 for user in users if user.is_active)
    admin_count = sum(1 for user in users if user.is_admin)
    active_plans = sum(1 for plan in plans if plan.is_active)
    max_modules = max((len(plan.action_codes()) for plan in plans), default=0)
    rows = [
        {"metric": "total_users", "value": len(users)},
        {"metric": "active_users", "value": active_users},
        {"metric": "admin_users", "value": admin_count},
        {"metric": "active_plans", "value": active_plans},
        {"metric": "total_plans", "value": len(plans)},
        {"metric": "total_projects", "value": len(projects)},
        {"metric": "default_plan_id", "value": default_plan.id if default_plan else ""},
        {"metric": "default_plan_name", "value": default_plan.name if default_plan else ""},
        {"metric": "max_modules_on_plan", "value": max_modules},
    ]
    return rows_to_csv(rows, ("metric", "value"))


def export_overview_csv(db: Session) -> str:
    """Combine all admin module exports into one multi-section CSV file."""
    sections = [
        _csv_section("summary", _overview_summary_csv(db)),
        _csv_section("users", export_users_csv(db)),
        _csv_section("plans", export_plans_csv(db)),
        _csv_section("projects", export_projects_csv(db)),
        _csv_section("monitoring", export_monitoring_csv()),
        _csv_section("profile_survey", export_profile_survey_csv(db)),
        _csv_section("feedback_survey", export_feedback_survey_csv(db)),
        _csv_section("errors", error_tracking_service.export_csv(db)),
    ]
    return "\n".join(sections)


def export_profile_survey_csv(db: Session) -> str:
    fieldnames = [
        "user_id",
        "email",
        "university",
        "degree",
        "major",
        "matlab_experience",
        "control_design_experience",
        "completed_at",
    ]
    rows = []
    for user in survey_service.list_profile_responses(db):
        rows.append(
            {
                "user_id": user.id,
                "email": user.email,
                "university": user.university or "",
                "degree": user.degree or "",
                "major": user.major or "",
                "matlab_experience": user.matlab_experience or "",
                "control_design_experience": user.control_design_experience or "",
                "completed_at": _iso(user.profile_survey_completed_at),
            }
        )
    return rows_to_csv(rows, fieldnames)


def export_feedback_survey_csv(db: Session) -> str:
    fieldnames = [
        "user_id",
        "email",
        "satisfaction",
        "ease_of_use",
        "product_value",
        "confidence",
        "reuse_intention",
        "willingness_to_pay",
        "main_problems",
        "created_at",
    ]
    rows = []
    for response, user in survey_service.list_feedback_responses(db):
        rows.append(
            {
                "user_id": user.id,
                "email": user.email,
                "satisfaction": response.satisfaction,
                "ease_of_use": response.ease_of_use,
                "product_value": response.product_value,
                "confidence": response.confidence,
                "reuse_intention": response.reuse_intention,
                "willingness_to_pay": response.willingness_to_pay,
                "main_problems": response.main_problems or "",
                "created_at": _iso(response.created_at),
            }
        )
    return rows_to_csv(rows, fieldnames)
