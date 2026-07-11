"""Case study listing routes."""

import os
from pathlib import Path

from fastapi import APIRouter

from backend_api.http.config import CASE_STUDIES_DIR
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
    }
