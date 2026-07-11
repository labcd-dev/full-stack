"""Runtime configuration for the FastAPI service."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = Path(os.getenv("RESULTS_DIR", PROJECT_ROOT / "results"))
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", PROJECT_ROOT / "uploads"))
CASE_STUDIES_DIR = Path(os.getenv("CASE_STUDIES_DIR", PROJECT_ROOT / "case_studies"))

API_PREFIX = "/api/v1"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    if origin.strip()
]

DEFAULT_LLM_MODELS = [
    "gpt-oss-120b",
    "gpt-5.5",
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-4o",
    "gpt-4o-mini",
]

RAG_MODEL_OPTIONS = ["gpt-5.5", "gpt-5.4", "gpt-5.4-mini", "gpt-4o", "gpt-4o-mini"]

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
