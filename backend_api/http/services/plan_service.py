"""Plan CRUD and default-registration-plan settings."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from backend_api.db.models import AppSetting, Plan, User
from backend_api.http.config import DEFAULT_LLM_MODELS
from backend_api.http.services.auth_service import ensure_actions

DEFAULT_PLAN_SETTING_KEY = "default_plan_id"


def normalize_plan_models(models: list[str] | None) -> list[str]:
    """Keep known catalog models only, preserving DEFAULT_LLM_MODELS order."""
    catalog = set(DEFAULT_LLM_MODELS)
    selected = {item.strip() for item in (models or []) if item and item.strip()}
    unknown = sorted(selected - catalog)
    if unknown:
        raise ValueError(f"Unknown model(s): {', '.join(unknown)}")
    return [model for model in DEFAULT_LLM_MODELS if model in selected]


def get_setting(db: Session, key: str) -> str | None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else None


def set_setting(db: Session, key: str, value: str) -> None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if row is None:
        row = AppSetting(key=key, value=value)
    else:
        row.value = value
    db.add(row)
    db.commit()


def get_default_plan_id(db: Session) -> int | None:
    raw = get_setting(db, DEFAULT_PLAN_SETTING_KEY)
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def get_default_plan(db: Session) -> Plan | None:
    plan_id = get_default_plan_id(db)
    if plan_id is None:
        return None
    return db.query(Plan).filter(Plan.id == plan_id).first()


def set_default_plan(db: Session, plan_id: int) -> Plan:
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if plan is None:
        raise ValueError("Plan not found")
    if not plan.is_active:
        raise ValueError("Default plan must be active")
    set_setting(db, DEFAULT_PLAN_SETTING_KEY, str(plan.id))
    return plan


def list_plans(db: Session, *, active_only: bool = False) -> list[Plan]:
    query = db.query(Plan)
    if active_only:
        query = query.filter(Plan.is_active.is_(True))
    return query.order_by(Plan.price, Plan.name).all()


def get_plan(db: Session, plan_id: int) -> Plan | None:
    return db.query(Plan).filter(Plan.id == plan_id).first()


def get_plan_by_name(db: Session, name: str) -> Plan | None:
    return db.query(Plan).filter(Plan.name == name.strip()).first()


def create_plan(
    db: Session,
    *,
    name: str,
    description: str = "",
    price: Decimal | float | str = Decimal("0.00"),
    action_codes: list[str] | None = None,
    models: list[str] | None = None,
    is_active: bool = True,
) -> Plan:
    normalized = name.strip()
    if not normalized:
        raise ValueError("Plan name is required")
    if get_plan_by_name(db, normalized) is not None:
        raise ValueError("A plan with this name already exists")
    plan = Plan(
        name=normalized,
        description=description.strip(),
        price=Decimal(str(price)),
        is_active=is_active,
        allowed_models=normalize_plan_models(models),
    )
    db.add(plan)
    db.flush()
    if action_codes:
        plan.actions = ensure_actions(db, action_codes)
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(
    db: Session,
    plan: Plan,
    *,
    name: str | None = None,
    description: str | None = None,
    price: Decimal | float | str | None = None,
    action_codes: list[str] | None = None,
    models: list[str] | None = None,
    is_active: bool | None = None,
) -> Plan:
    if name is not None:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Plan name is required")
        existing = get_plan_by_name(db, normalized)
        if existing is not None and existing.id != plan.id:
            raise ValueError("A plan with this name already exists")
        plan.name = normalized
    if description is not None:
        plan.description = description.strip()
    if price is not None:
        plan.price = Decimal(str(price))
    if is_active is not None:
        plan.is_active = is_active
        if not is_active and get_default_plan_id(db) == plan.id:
            raise ValueError("Cannot deactivate the default registration plan")
    if action_codes is not None:
        plan.actions = ensure_actions(db, action_codes)
    if models is not None:
        plan.allowed_models = normalize_plan_models(models)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def delete_plan(db: Session, plan: Plan) -> None:
    if get_default_plan_id(db) == plan.id:
        raise ValueError("Cannot delete the default registration plan")
    assigned = db.query(User).filter(User.plan_id == plan.id).count()
    if assigned > 0:
        raise ValueError("Cannot delete a plan that is assigned to users")
    db.delete(plan)
    db.commit()


def set_user_plan(db: Session, user: User, plan_id: int | None) -> User:
    if plan_id is None:
        user.plan_id = None
    else:
        plan = get_plan(db, plan_id)
        if plan is None:
            raise ValueError("Plan not found")
        if not plan.is_active:
            raise ValueError("Cannot assign an inactive plan")
        user.plan = plan
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def plan_out_dict(plan: Plan) -> dict:
    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "price": float(plan.price),
        "is_active": plan.is_active,
        "actions": plan.action_codes(),
        "models": plan.model_ids(),
        "created_at": plan.created_at,
    }
