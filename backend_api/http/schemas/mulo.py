"""MuloDesigner API schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MuloStartRequest(BaseModel):
    run_config: Dict[str, Any]
    controller_structure: List[Dict[str, Any]]
    system_identification: Dict[str, Any]
    trimming_result: Dict[str, Any]
    equation: str
