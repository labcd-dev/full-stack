"""Recommender API schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RecommenderStartRequest(BaseModel):
    file_content: str
    file_name: str
    model: str = "gpt-oss-120b"
    step: str = "initial_run"


class RagDecisionRequest(BaseModel):
    flags: List[str] = Field(default_factory=list)
    model: str = "gpt-4o"


class RecommenderHandoffRequest(BaseModel):
    chosen_controller: Optional[str] = None


class RecommenderHandoffResponse(BaseModel):
    file_content: str
    chosen_controller: str
    trimming_params: Dict[str, Any]
    states_inputs: List[str]
