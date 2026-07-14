"""Case study listing routes."""

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend_api.http.config import CASE_STUDIES_DIR
from backend_api.http.services.mulo_service import (
    get_mulo_default_objectives,
    list_mulo_case_studies,
    load_mulo_case_study,
)
from backend_api.MuloDesigner.GaAgent.data import get_available_case_studies

router = APIRouter(prefix="/case-studies", tags=["case-studies"])


@router.get("")
def list_case_studies() -> dict:
    py_dir = CASE_STUDIES_DIR / "py"
    m_dir = CASE_STUDIES_DIR / "m"
    ga_dir = Path(__file__).resolve().parents[2] / "MuloDesigner" / "GaAgent" / "case_studies" / "json"

    return {
        "python": sorted(file_name[:-3] for file_name in os.listdir(py_dir) if file_name.endswith(".py"))
        if py_dir.exists()
        else [],
        "matlab": sorted(file_name[:-2] for file_name in os.listdir(m_dir) if file_name.endswith(".m"))
        if m_dir.exists()
        else [],
        "ga_json": get_available_case_studies(ga_dir),
        "mulo": list_mulo_case_studies(),
        "mulo_objectives": get_mulo_default_objectives(),
    }


@router.get("/mulo/{name}")
def get_mulo_case_study(name: str) -> dict:
    try:
        return load_mulo_case_study(name)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
