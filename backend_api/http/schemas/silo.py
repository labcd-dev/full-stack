"""SiloDesigner API schemas."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SiloStartRequest(BaseModel):
    config: Dict[str, Any]
    control_objective: Optional[str] = None


class SiloObjectiveRequest(BaseModel):
    objective: str
