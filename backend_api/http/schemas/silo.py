"""SiloDesigner API schemas."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class SiloStartRequest(BaseModel):
    config: Dict[str, Any]
    control_objective: Optional[str] = None
    project_id: Optional[int] = None


class SiloObjectiveRequest(BaseModel):
    objective: str
